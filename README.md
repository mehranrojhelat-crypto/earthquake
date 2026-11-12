# Earthquake Intelligence Platform — ایران

سامانه تحلیل و مانیتورینگ زلزله‌های ایران با داده USGS و گسل‌های فعال GEM.

## قابلیت‌ها
- دریافت خودکار زلزله‌های ایران از USGS
- نقشه تعاملی + فیلتر زمانی و بزرگی
- نمایش گسل‌های فعال (GEM)
- آمار و نمودارهای توصیفی
- صفحات اختصاصی شهرهای مهم
- تحلیل فاصله زلزله‌ها تا گسل
- مدل‌های آزمایشی یادگیری ماشین (طبقه‌بندی / رگرسیون / خوشه‌بندی)

## هشدار علمی
مدل‌های ML این پروژه برای پیش‌بینی قطعی زمان یا مکان زلزله آینده نیستند.
خروجی‌ها تحلیل آماری رویدادهای ثبت‌شده هستند.

## نصب
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## اجرا
```bash
streamlit run app.py
```

## ساختار پروژه
```text
earthquake/
├── app.py
├── config.py
├── components/
├── services/
├── models/
├── utils/
├── pages/
└── tests/
```

## منابع داده
- USGS Earthquake Catalog
- GEM Global Active Faults

## توسعه بعدی
- بهینه‌سازی محاسبه فاصله تا گسل
- گزارش‌گیری Excel/PDF
- استقرار آنلاین