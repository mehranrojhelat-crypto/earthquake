markdown
# سامانه تحلیل زلزله ایران 🌍

تحلیل زلزله‌های ایران با داده‌های USGS، نمایش گسل‌های فعال (GEM)، مصورسازی و یادگیری ماشین.

## قابلیت‌ها

- دریافت خودکار زلزله‌های ۱۰ سال اخیر ایران از USGS
- نقشه تعاملی زلزله + گسل‌های فعال
- نمودارهای آماری (سالانه، توزیع شدت، heatmap، انیمیشن)
- طبقه‌بندی (پیش‌بینی magnitude ≥ ۵)
- رگرسیون (پیش‌بینی مقدار magnitude)
- خوشه‌بندی مناطق پرخطر (KMeans)

## ساختار پروژه

```
earthquake/
├── app.py              # داشبورد وب (Streamlit)
├── earthquake.py       # نسخه اسکریپت خط فرمان (اختیاری)
└── README.md
```

## نصب

```bash
pip install streamlit plotly pandas numpy scikit-learn requests
```

اگر به PyPI دسترسی ندارید (مثلاً در ایران):

```bash
pip install streamlit plotly pandas numpy scikit-learn requests -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## اجرا

### داشبورد وب (پیشنهادی)

```bash
streamlit run app.py
```

مرورگر روی `http://localhost:8501` باز می‌شود.

### نسخه خط فرمان

```bash
python earthquake.py
```

نمودارها به صورت HTML ذخیره می‌شوند.

## منابع داده

| منبع | توضیح |
|------|--------|
| [USGS](https://earthquake.usgs.gov/) | کاتالوگ زلزله |
| [GEM Global Active Faults](https://github.com/cossatot/gem-global-active-faults) | گسل‌های فعال (CC BY-SA) |

## نکات

- اولین اجرا ممکن است به دلیل دانلود داده و گسل‌ها کمی طول بکشد.
- داده زلزله و گسل‌ها در حافظه کش Streamlit ذخیره می‌شوند.
- برای Plotly نسخه ۷ از `Scattermap` استفاده شده است.

## توسعه آینده

- پیش‌بینی زمانی (سری زمانی)
- فاصله از نزدیک‌ترین گسل به‌عنوان ویژگی
- هشدار برای مناطق پرخطر
- استقرار آنلاین (Streamlit Cloud / Hugging Face)

## مجوز

کد آزاد است. برای داده گسل‌ها مجوز GEM (CC BY-SA) رعایت شود.
