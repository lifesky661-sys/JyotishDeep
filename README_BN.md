# জ্যোতিষদীপ — উন্নত বাংলা বৈদিক জ্যোতিষ

## কী আছে
- Flask-ভিত্তিক ওয়েব অ্যাপ
- Swiss Ephemeris (`pyswisseph`) দিয়ে গ্রহের sidereal longitude, Lahiri/Chitrapaksha ayanamsha
- স্থানীয় জন্মসময়কে `zoneinfo` দিয়ে UTC-তে রূপান্তর
- লগ্ন ও MC, সূর্য থেকে শনি, Mean Rahu এবং বিপরীত Ketu
- D1 whole-sign house placements, nakshatra/pada
- D9, D10 ও D60 বিভাগীয় রাশি
- Vimshottari mahadasha timeline এবং জন্ম-মহাদশার antardasha
- JSON report download ও browser print/PDF

## চালানোর নির্দেশ (Python 3.10+)
1. ZIP ফাইলটি extract করুন।
2. টার্মিনাল/কমান্ড প্রম্পটে প্রকল্প ফোল্ডারে যান।
3. ভার্চুয়াল পরিবেশ তৈরি করুন (ঐচ্ছিক কিন্তু সুপারিশকৃত):
   - Windows: `python -m venv .venv` এবং `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` এবং `source .venv/bin/activate`
4. নির্ভরতা ইনস্টল করুন: `pip install -r requirements.txt`
5. চালান: `python app.py`
6. ব্রাউজারে খুলুন: `http://127.0.0.1:5000`

`pyswisseph` ইনস্টল করতে pip-এর ইন্টারনেট সংযোগ লাগতে পারে। কোনো কোনো সিস্টেমে compiler/build tool দরকার হতে পারে।

## স্থানাঙ্ক
ডিফল্ট স্থানাঙ্ক কলকাতার আনুমানিক স্থানাঙ্ক। অন্য জন্মস্থানের জন্য সঠিক অক্ষাংশ/দ্রাঘিমাংশ লিখুন। এই সংস্করণে স্বয়ংক্রিয় place-name geocoding নেই।

## গণনার সীমা ও যাচাই
- Swiss Ephemeris-এ `FLG_SWIEPH`, `FLG_SIDEREAL` ও `SIDM_LAHIRI` ব্যবহৃত।
- Mean Node (Rahu) ব্যবহৃত; Ketu = Rahu + 180°।
- House list হলো whole-sign houses; cusps/Placidus chart নয়।
- D9/D10/D60-এর mapping implementation নির্দিষ্ট, কিন্তু বিভিন্ন জ্যোতিষ-পরম্পরায় divisional chart mapping ভিন্ন হতে পারে।
- Vimshottari timeline-এ 365.2425 দিনের বছর ব্যবহার করা হয়েছে; দাশা তারিখ নির্দিষ্ট commercial software-এর সঙ্গে একদম মিলে যাবে—এমন নিশ্চয়তা নেই।
- পূর্ণ গ্রহদৃষ্টি/যোগ-দোষ rule engine, shadbala, Ashtakavarga, transit, full nested antardasha, automatic geocoding এবং PDF layout engine এখনও অন্তর্ভুক্ত নয়।
- জ্যোতিষীয় ব্যাখ্যা ঐতিহ্যভিত্তিক; বৈজ্ঞানিকভাবে নিশ্চিত ভবিষ্যদ্বাণী নয়। গুরুত্বপূর্ণ জীবন-সিদ্ধান্তের একমাত্র ভিত্তি হিসেবে ব্যবহার করবেন না।

## উৎপাদন-ব্যবহারের আগে
- জন্মতথ্য validation ও error handling পরীক্ষা করুন।
- Swiss Ephemeris license/usage terms আপনার ব্যবহারের সঙ্গে মানানসই কি না যাচাই করুন।
- public deployment-এর আগে production WSGI server, HTTPS, rate limiting, CSRF/security headers এবং privacy policy যোগ করুন।
- জন্মতথ্য লগ বা স্থায়ীভাবে সংরক্ষণ করবেন না, যদি না স্পষ্ট সম্মতি ও নিরাপত্তা ব্যবস্থা থাকে।
