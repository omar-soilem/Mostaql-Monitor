#!/bin/bash

# ألوان لتنسيق المخرجات
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}    جاري تثبيت وإعداد برنامج مراقبة مستقل      ${NC}"
echo -e "${BLUE}===============================================${NC}"

# تحديد مسار المجلد الحالي (لضمان نجاح التثبيت في أي مسار)
DIR="$(dirname "$(realpath "$0")")"
cd "$DIR"

# التأكد من وجود بايثون
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[خطأ] بايثون python3 غير مثبت على جهازك! يرجى تثبيته أولاً.${NC}"
    exit 1
fi

# إنشاء بيئة افتراضية لتفادي قيود PEP 668
if [ ! -d "venv" ]; then
    echo -e "${BLUE}[1/5] جاري إنشاء بيئة افتراضية Python (venv)...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[خطأ] فشل إنشاء البيئة الافتراضية. يرجى التأكد من تثبيت python3-venv (مثلاً: sudo apt install python3-venv).${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}[✔] البيئة الافتراضية موجودة بالفعل.${NC}"
fi

# تثبيت المكتبات المطلوبة داخل البيئة الافتراضية
echo -e "${BLUE}[2/5] جاري تثبيت الحزم والمكتبات اللازمة (requests, beautifulsoup4)...${NC}"
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}[خطأ] فشل تثبيت المكتبات اللازمة.${NC}"
    exit 1
fi
echo -e "${GREEN}[✔] تم تثبيت المكتبات بنجاح.${NC}"

# إعطاء صلاحيات التشغيل للملفات
echo -e "${BLUE}[3/5] جاري ضبط صلاحيات التشغيل للملفات...${NC}"
chmod +x mostaql_monitor.py
chmod +x run.sh
chmod +x mostaql-cli.sh
echo -e "${GREEN}[✔] تم ضبط الصلاحيات.${NC}"

# إعداد ملف التشغيل التلقائي عند إقلاع النظام (Autostart)
echo -e "${BLUE}[4/5] جاري إعداد التشغيل التلقائي عند بدء تشغيل الجهاز...${NC}"
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

# كتابة ملف .desktop باستخدام المسار الديناميكي
cat << EOF > "$AUTOSTART_DIR/mostaql_monitor.desktop"
[Desktop Entry]
Type=Application
Name=Mostaql Project Monitor
Comment=Monitors Mostaql for new logo and branding projects
Exec="$DIR/run.sh"
Icon=preferences-desktop-notification
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
EOF

chmod +x "$AUTOSTART_DIR/mostaql_monitor.desktop"
echo -e "${GREEN}[✔] تم إنشاء ملف بدء التشغيل التلقائي بنجاح في: $AUTOSTART_DIR/mostaql_monitor.desktop${NC}"

# إعداد سطر الأوامر (mostaql)
echo -e "${BLUE}[5/5] جاري إعداد أمر mostaql في الطرفية...${NC}"
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"
ln -sf "$DIR/mostaql-cli.sh" "$LOCAL_BIN/mostaql"

# التأكد من أن المسار في PATH
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo -e "${RED}[تحذير] المجلد $LOCAL_BIN ليس في متغير PATH.${NC}"
    echo -e "يُفضل إضافة السطر التالي إلى ملف ~/.bashrc الخاص بك:"
    echo -e "export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
echo -e "${GREEN}[✔] تم إضافة أمر mostaql للطرفية بنجاح.${NC}"

# اختبار إرسال إشعار وصوت تنبيه للتأكد من نجاح الإعداد
echo -e "${BLUE}-----------------------------------------------${NC}"
echo -e "${BLUE}جاري اختبار نظام الإشعارات وتنبيه الصوت...${NC}"

# إرسال إشعار اختبار
if command -v notify-send &> /dev/null; then
    notify-send -i preferences-desktop-notification -t 8000 "🔔 تم تفعيل مراقبة مستقل!" "البرنامج يعمل الآن في الخلفية، وسيقوم بفحص المشاريع الجديدة تلقائياً عند تشغيل الكمبيوتر."
    echo -e "${GREEN}[✔] تم إرسال إشعار اختبار لسطح المكتب.${NC}"
else
    echo -e "${RED}[تحذير] أداة notify-send غير مثبتة! لن تتمكن من تلقي إشعارات سطح المكتب (يرجى تثبيت libnotify-bin).${NC}"
fi

# تشغيل صوت اختبار
SOUND_PATH="/usr/share/sounds/freedesktop/stereo/complete.oga"
if [ -f "$SOUND_PATH" ]; then
    if command -v paplay &> /dev/null; then
        paplay "$SOUND_PATH" &
    elif command -v canberra-gtk-play &> /dev/null; then
        canberra-gtk-play --file="$SOUND_PATH" &
    fi
    echo -e "${GREEN}[✔] تم تشغيل صوت تنبيه اختبار.${NC}"
fi

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}      تهانينا! اكتمل التثبيت والإعداد بنجاح!   ${NC}"
echo -e "${BLUE}===============================================${NC}"
echo -e "البرنامج سيعمل تلقائياً في الخلفية في كل مرة تفتح فيها جهازك."
echo -e "أصبح بإمكانك استخدام الأمر التالي للتحكم في البرنامج:"
echo -e "  ${BLUE}mostaql start${NC}  (للتشغيل في الخلفية)"
echo -e "  ${BLUE}mostaql stop${NC}   (للإيقاف)"
echo -e "  ${BLUE}mostaql status${NC} (لمعرفة حالة البرنامج)"
echo -e "  ${BLUE}mostaql logs${NC}   (لعرض السجلات)"
echo -e "-----------------------------------------------"
