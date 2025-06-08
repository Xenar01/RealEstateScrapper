# تثبيت RealEstateScraper على ويندوز

1. ثبّت Python 3.10 أو أحدث من موقع [python.org](https://python.org).
2. افتح موجه الأوامر وانتقل إلى مجلد المشروع.
3. أنشئ بيئة افتراضية وشغّلها:
   ```bat
   python -m venv venv
   venv\Scripts\activate
   ```
4. ثبّت المتطلبات:
   ```bat
   pip install -r RealEstateScraper\requirements.txt
   ```
5. لتشغيل التطبيق:
   ```bat
   python RealEstateScraper\main.py
   ```
