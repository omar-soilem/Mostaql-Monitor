#!/bin/bash

# مسار المشروع
DIR="$(dirname "$(realpath "$0")")"

if [ "$1" = "start" ]; then
    cd "$DIR"
    nohup ./run.sh > /dev/null 2>&1 &
    echo "✅ تم تشغيل مراقبة مستقل في الخلفية."
elif [ "$1" = "stop" ]; then
    pkill -f mostaql_monitor.py
    echo "🛑 تم إيقاف مراقبة مستقل."
elif [ "$1" = "status" ]; then
    if pgrep -f mostaql_monitor.py > /dev/null; then
        echo "🟢 البرنامج يعمل حالياً."
    else
        echo "🔴 البرنامج متوقف."
    fi
elif [ "$1" = "logs" ]; then
    tail -f "$DIR/monitor.log"
else
    echo "مرحباً بك في أداة مراقبة مستقل!"
    echo "الاستخدام: mostaql [start|stop|status|logs]"
fi
