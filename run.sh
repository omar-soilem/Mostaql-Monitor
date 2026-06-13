#!/bin/bash
# الانتقال إلى مجلد السكربت لضمان صحة المسارات للملفات
cd "$(dirname "$(realpath "$0")")"

# تشغيل السكربت الرئيسي باستخدام البيئة الافتراضية
if [ -d "venv" ]; then
    exec ./venv/bin/python3 mostaql_monitor.py
else
    exec python3 mostaql_monitor.py
fi
