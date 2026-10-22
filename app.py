from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import swisseph as swe

app = Flask(__name__)
swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANETS = [
    ("সূর্য", swe.SUN), ("চন্দ্র", swe.MOON), ("মঙ্গল", swe.MARS),
    ("বুধ", swe.MERCURY), ("বৃহস্পতি", swe.JUPITER), ("শুক্র", swe.VENUS),
    ("শনি", swe.SATURN), ("রাহু (Mean)", swe.MEAN_NODE)
]
SIGNS = ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"]
SIGN_EN = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NAKSHATRAS = ["অশ্বিনী","ভরণী","কৃত্তিকা","রোহিণী","মৃগশিরা","আর্দ্রা","পুনর্বসু","পুষ্যা","আশ্লেষা","মঘা","পূর্বফাল্গুনী","উত্তরফাল্গুনী","হস্তা","চিত্রা","স্বাতী","বিশাখা","অনুরাধা","জ্যেষ্ঠা","মূলা","পূর্বাষাঢ়া","উত্তরাষাঢ়া","শ্রবণা","ধনিষ্ঠা","শতভিষা","পূর্বভাদ্রপদ","উত্তরভাদ্রপদ","রেবতী"]
DASHA_LORDS = ["কেতু","শুক্র","সূর্য","চন্দ্র","মঙ্গল","রাহু","বৃহস্পতি","শনি","বুধ"]
DASHA_YEARS = [7,20,6,10,7,18,16,19,17]
DASHA_START_INDEX = {name:i for i,name in enumerate(DASHA_LORDS)}
FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

def norm(x): return x % 360.0
def sign_index(lon): return int(norm(lon) // 30)
def deg_in_sign(lon): return norm(lon) % 30
def fmt_deg(x):
    d = int(x); m = int((x-d)*60); s = round((((x-d)*60)-m)*60)
    if s == 60: s=0; m+=1
    if m == 60: m=0; d+=1
    return f"{d}° {m:02d}′ {s:02d}″"
def zodiac(lon):
    si = sign_index(lon)
    return {"sign": SIGNS[si], "sign_index": si, "degree": fmt_deg(deg_in_sign(lon)), "longitude": round(norm(lon), 6)}
def nakshatra(lon):
    nsize = 360/27
    idx = min(26, int(norm(lon)/nsize))
    within = norm(lon) - idx*nsize
    return {"name": NAKSHATRAS[idx], "index": idx, "pada": min(4, int(within/(nsize/4))+1), "remaining_fraction": max(0, min(1, (nsize-within)/nsize))}
def varga_sign(lon, n):
    si = sign_index(lon)
    part = min(n-1, int(deg_in_sign(lon)/(30/n)))
    # Parashara-style commonly used mappings for D9, D10, D60
    if n == 9:
        mode = si % 3
        start = si if mode == 0 else ((si + 8) % 12 if mode == 1 else (si + 4) % 12)
        return (start + part) % 12
    if n == 10:
        start = si if si % 2 == 0 else (si + 8) % 12
        return (start + part) % 12
    if n == 60:
        start = 0 if si % 2 == 0 else 6
        return (start + part) % 12
    return si
def jd_from_local(date_s, time_s, tz_name):
    local = datetime.fromisoformat(f"{date_s}T{time_s}").replace(tzinfo=ZoneInfo(tz_name))
    utc = local.astimezone(timezone.utc)
    hour = utc.hour + utc.minute/60 + utc.second/3600
    jd = swe.julday(utc.year, utc.month, utc.day, hour)
    return jd, local, utc
def planet_calc(jd, lat, lon):
    planets = []
    raw = {}
    for name, pid in PLANETS:
        vals, retflag = swe.calc_ut(jd, pid, FLAGS)
        plon = norm(vals[0])
        raw[name] = plon
        planets.append({
            "name": name, **zodiac(plon), "nakshatra": nakshatra(plon),
            "retrograde": vals[3] < 0, "speed": round(vals[3], 5),
            "d9_sign": SIGNS[varga_sign(plon, 9)],
            "d10_sign": SIGNS[varga_sign(plon, 10)],
            "d60_sign": SIGNS[varga_sign(plon, 60)]
        })
    # Ketu exactly opposite Rahu
    ketu = norm(raw["রাহু (Mean)"] + 180)
    planets.append({"name":"কেতু", **zodiac(ketu), "nakshatra":nakshatra(ketu),
                    "retrograde":True, "speed":None, "d9_sign":SIGNS[varga_sign(ketu,9)],
                    "d10_sign":SIGNS[varga_sign(ketu,10)], "d60_sign":SIGNS[varga_sign(ketu,60)]})
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL)
    asc = norm(ascmc[0])
    mc = norm(ascmc[1])
    asc_sign = sign_index(asc)
    for p in planets:
        p["whole_sign_house"] = (p["sign_index"] - asc_sign) % 12 + 1
    # Whole-sign chart placements
    houses = []
    for h in range(1,13):
        si = (asc_sign + h - 1) % 12
        houses.append({"house":h, "sign":SIGNS[si], "planets":[p["name"] for p in planets if p["whole_sign_house"] == h]})
    return planets, houses, asc, mc
def vimshottari(moon_lon, utc_birth):
    nk = nakshatra(moon_lon)
    start_i = nk["index"] % 9
    lord = DASHA_LORDS[start_i]
    years = DASHA_YEARS[start_i]
    frac_elapsed = 1 - nk["remaining_fraction"]
    balance = years * nk["remaining_fraction"]
    # approximate year length for readable timeline; astronomy remains ephemeris based
    current_start = utc_birth - timedelta(days=frac_elapsed * years * 365.2425)
    result=[]
    idx=start_i
    start=current_start
    for _ in range(9):
        y=DASHA_YEARS[idx]
        end=start+timedelta(days=y*365.2425)
        result.append({"lord":DASHA_LORDS[idx],"years":y,"start":start.date().isoformat(),"end":end.date().isoformat(),
                       "current_balance_note": "জন্মের সময় অবশিষ্ট" if idx==start_i else ""})
        start=end
        idx=(idx+1)%9
    # antardasha sequence in first Mahadasha, proportional years
    antars=[]
    sub_idx=start_i
    start=utc_birth
    md_total=years
    for _ in range(9):
        subyears=years*DASHA_YEARS[sub_idx]/120
        end=start+timedelta(days=subyears*365.2425)
        antars.append({"lord":DASHA_LORDS[sub_idx],"start":start.date().isoformat(),"end":end.date().isoformat()})
        start=end; sub_idx=(sub_idx+1)%9
    return {"birth_nakshatra":nk["name"],"birth_dasha_lord":lord,"balance_years":round(balance,2),
            "mahadasha":result,"first_mahadasha_antardasha":antars}
def calculate(data):
    date_s=data["date"]; time_s=data["time"]; tz=data.get("timezone","Asia/Kolkata")
    lat=float(data["latitude"]); lon=float(data["longitude"])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180): raise ValueError("অক্ষাংশ/দ্রাঘিমাংশের মান বৈধ নয়।")
    jd, local, utc = jd_from_local(date_s,time_s,tz)
    planets,houses,asc,mc=planet_calc(jd,lat,lon)
    moon=next(p for p in planets if p["name"]=="চন্দ্র")
    # Ascendant vargas
    asc_obj={**zodiac(asc),"nakshatra":nakshatra(asc),"d9_sign":SIGNS[varga_sign(asc,9)],
             "d10_sign":SIGNS[varga_sign(asc,10)],"d60_sign":SIGNS[varga_sign(asc,60)]}
    return {"meta":{"local_birth":local.isoformat(),"utc_birth":utc.isoformat(),"timezone":tz,
                    "latitude":lat,"longitude":lon,"ayanamsha":"লাহিড়ী / চিত্রপক্ষ",
                    "julian_day_ut":round(jd,6),"house_system":"Whole-sign (রাশি-ভিত্তিক ভাব)",
                    "engine":"Swiss Ephemeris / pyswisseph"},
            "ascendant":asc_obj,"midheaven":zodiac(mc),"planets":planets,"houses":houses,
            "dasha":vimshottari(moon["longitude"],utc)}
@app.route("/")
def index(): return render_template("index.html")
@app.post("/api/chart")
def api_chart():
    try:
        data=request.get_json(force=True)
        for key in ("date","time","latitude","longitude"):
            if not data.get(key) and data.get(key) != 0: return jsonify({"error":f"{key} তথ্যটি প্রয়োজন।"}),400
        return jsonify(calculate(data))
    except Exception as e:
        return jsonify({"error":str(e)}),400
if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=False)
