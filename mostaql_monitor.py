#!/usr/bin/env python3
import os
import re
import sys
import json
import time
import logging
import subprocess
import requests
from bs4 import BeautifulSoup

# ضبط الإعدادات الأساسية للمجلد والملفات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
SEEN_FILE = os.path.join(BASE_DIR, "seen_projects.json")
LOG_FILE = os.path.join(BASE_DIR, "monitor.log")

# إعداد نظام تسجيل السجلات (Logging)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def load_config():
    """تحميل الإعدادات من ملف config.json"""
    default_config = {
        "check_interval_seconds": 120,
        "keywords": [
            "شعار", "شعارات", "هوية", "هويات", "بصرية", "براند", "لوجو", "لوقو", 
            "تصميم هوية", "هويه", "logo", "branding", "visual identity", "brand identity"
        ],
        "enable_sound": True,
        "sound_file": "/usr/share/sounds/freedesktop/stereo/complete.oga"
    }
    
    if not os.path.exists(CONFIG_FILE):
        logging.warning("ملف الإعدادات config.json غير موجود، سيتم استخدام الإعدادات الافتراضية.")
        return default_config
        
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # التأكد من وجود كافة المفاتيح المطلوبة
            for key, val in default_config.items():
                if key not in config:
                    config[key] = val
            return config
    except Exception as e:
        logging.error(f"خطأ في قراءة ملف الإعدادات: {e}. سيتم استخدام الإعدادات الافتراضية.")
        return default_config

def load_seen_projects():
    """تحميل قائمة المشاريع التي تم إرسال إشعارات لها سابقاً"""
    if not os.path.exists(SEEN_FILE):
        return []
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"خطأ في قراءة ملف المشاريع السابقة: {e}")
        return []

def save_seen_project(project_id):
    """حفظ مشروع جديد في قائمة المشاريع التي تم فحصها وإرسالها"""
    seen = load_seen_projects()
    if project_id not in seen:
        seen.append(project_id)
        # إبقاء الملف بحجم معقول (حفظ آخر 500 مشروع فقط)
        if len(seen) > 500:
            seen = seen[-500:]
        try:
            with open(SEEN_FILE, "w", encoding="utf-8") as f:
                json.dump(seen, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"خطأ في حفظ المشروع الجديد في القائمة: {e}")

def normalize_arabic(text):
    """تنظيف وتطبيع النصوص العربية لضمان مطابقة الكلمات المفتاحية بغض النظر عن طريقة الكتابة"""
    if not text:
        return ""
    text = text.lower().strip()
    # تطبيع الألف والهمزات
    text = re.sub(r"[أإآ]", "ا", text)
    # تطبيع التاء المربوطة والهاء
    text = re.sub(r"ة\b", "ه", text)
    # تطبيع الياء والألف المقصورة
    text = re.sub(r"[ى]", "ي", text)
    # إزالة التشكيل (الحركات)
    text = re.sub(r"[\u064B-\u0652]", "", text)
    return text

def matches_keywords(title, brief, keywords):
    """التحقق من وجود أي من الكلمات المفتاحية في عنوان أو وصف المشروع"""
    title_norm = normalize_arabic(title)
    brief_norm = normalize_arabic(brief)
    
    for kw in keywords:
        kw_norm = normalize_arabic(kw)
        if kw_norm in title_norm or kw_norm in brief_norm:
            logging.info(f"مطابقة الكلمة المفتاحية: '{kw}' في مشروع: '{title}'")
            return True
    return False

def play_sound(sound_path):
    """تشغيل صوت التنبيه"""
    if not os.path.exists(sound_path):
        # محاولة البحث عن بديل إذا لم يجد الملف الافتراضي
        fallback_paths = [
            "/usr/share/sounds/freedesktop/stereo/complete.oga",
            "/usr/share/sounds/freedesktop/stereo/bell.oga",
            "/usr/share/sounds/gnome/default/alerts/glass.ogg",
            "/usr/share/sounds/ubuntu/stereo/system-ready.ogg"
        ]
        found = False
        for path in fallback_paths:
            if os.path.exists(path):
                sound_path = path
                found = True
                break
        if not found:
            logging.warning("لم يتم العثور على أي ملف صوتي مناسب على النظام.")
            return

    try:
        # محاولة التشغيل باستخدام paplay كخيار أول
        subprocess.run(["paplay", sound_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        try:
            # محاولة التشغيل باستخدام canberra-gtk-play كبديل
            subprocess.run(["canberra-gtk-play", "--file", sound_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logging.error(f"فشل تشغيل الصوت: {e}")

def send_desktop_notification(title, brief, time_text, url, sound_enabled, sound_path):
    """إرسال إشعار سطح المكتب وتشغيل الصوت التنبيهي"""
    logging.info(f"إرسال إشعار بمشروع جديد: {title}")
    
    # تنسيق نص الإشعار باستخدام وسم HTML المدعوم في Linux
    # نضع رابط المشروع في الإشعار ليكون قابلاً للنقر
    body = f"⏱️ {time_text}\n\n{brief}\n\n🔗 اضغط هنا لفتح المشروع:\n{url}"
    
    try:
        # استدعاء notify-send
        subprocess.run([
            "notify-send",
            "-i", "preferences-desktop-notification",
            "-u", "normal",
            "-t", "15000",  # عرض الإشعار لمدة 15 ثانية
            f"🎁 مشروع مستقل جديد: {title}",
            body
        ], check=True)
    except Exception as e:
        logging.error(f"خطأ في إرسال إشعار سطح المكتب: {e}")
        
    # تشغيل الصوت التنبيهي إذا كان مفعلاً
    if sound_enabled:
        play_sound(sound_path)

def monitor_mostaql():
    """الدالة الرئيسية لمراقبة وفحص موقع مستقل"""
    config = load_config()
    seen_projects = load_seen_projects()
    
    url = "https://mostaql.com/projects/design"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
    }
    
    logging.info("بدء جلب المشاريع من موقع مستقل...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            logging.error(f"فشل جلب الصفحة، رمز الاستجابة: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.content, "html.parser")
        project_rows = soup.find_all("tr", class_="project-row")
        
        if not project_rows:
            logging.warning("لم يتم العثور على أي مشاريع في الصفحة. قد يكون هناك تعديل في هيكل الموقع البرمجي.")
            return
            
        logging.info(f"تم العثور على {len(project_rows)} مشروع في صفحة التصميم. بدء الفحص...")
        
        # نفحص المشاريع بترتيب عكسي (من الأقدم للأحدث في الصفحة لكي تصل الإشعارات بالترتيب الزمني الصحيح)
        newly_found_matching_projects = []
        
        for row in reversed(project_rows):
            try:
                # استخراج رابط وعنوان المشروع
                title_elem = row.find("h2", class_="mrg--bt-reset")
                if not title_elem:
                    continue
                a_tag = title_elem.find("a")
                if not a_tag or not a_tag.get("href"):
                    continue
                    
                title = a_tag.text.strip()
                link = a_tag["href"]
                
                # استخراج معرف المشروع ID من الرابط
                id_match = re.search(r"/project/(\d+)", link)
                if not id_match:
                    continue
                project_id = id_match.group(1)
                
                # استخراج الوصف المختصر للمشروع
                brief_elem = row.find("p", class_="project__brief")
                brief = brief_elem.text.strip() if brief_elem else ""
                
                # استخراج وقت النشر
                time_elem = row.find("time")
                time_text = time_elem.text.strip() if time_elem else "منذ قليل"
                
                # التحقق إذا كان المشروع جديداً ومطابقاً للكلمات المفتاحية
                if project_id not in seen_projects:
                    if matches_keywords(title, brief, config["keywords"]):
                        newly_found_matching_projects.append({
                            "id": project_id,
                            "title": title,
                            "brief": brief,
                            "time_text": time_text,
                            "link": link
                        })
                    else:
                        # لحمايتها من التكرار حتى لو لم تطابق الكلمات المفتاحية
                        save_seen_project(project_id)
            except Exception as row_error:
                logging.error(f"خطأ أثناء فحص أحد المشاريع: {row_error}")
                
        # إرسال الإشعارات وحفظ المشاريع الجديدة التي تمت مطابقتها
        for proj in newly_found_matching_projects:
            send_desktop_notification(
                title=proj["title"],
                brief=proj["brief"],
                time_text=proj["time_text"],
                url=proj["link"],
                sound_enabled=config["enable_sound"],
                sound_path=config["sound_file"]
            )
            save_seen_project(proj["id"])
            # فاصل زمني بسيط بين الإشعارات لمنع تكدسها
            time.sleep(1)
            
    except requests.exceptions.RequestException as net_error:
        logging.error(f"خطأ في الاتصال بالشبكة: {net_error}")
    except Exception as e:
        logging.error(f"حدث خطأ غير متوقع أثناء الفحص: {e}")

def main():
    logging.info("بدء تشغيل برنامج Mostaql Monitor بنجاح.")
    
    # فحص أولي فوري عند التشغيل
    monitor_mostaql()
    
    while True:
        config = load_config()
        interval = config.get("check_interval_seconds", 120)
        # التأكد من ألا تكون المدة قصيرة جداً لتفادي الحظر
        if interval < 30:
            interval = 30
            
        logging.info(f"الانتظار لمدة {interval} ثانية للفحص التالي...")
        time.sleep(interval)
        monitor_mostaql()

if __name__ == "__main__":
    main()
