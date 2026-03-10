#!/bin/bash
cd /var/www/projects/bakugo-web
source .venv/bin/activate

python manage.py runserver 0.0.0.0:8002 &>/tmp/server.log &
SERVER_PID=$!
sleep 3

URLS=(
  "/"
  "/routes/"
  "/routes/1/"
  "/routes/2/"
  "/stops/"
  "/stops/1/"
  "/stops/5/"
  "/planner/"
  "/map/"
  "/accounts/login/"
  "/accounts/register/"
)

ALL_OK=true
for url in "${URLS[@]}"; do
  code=$(wget -qO /dev/null --server-response "http://localhost:8002$url" 2>&1 | grep "HTTP/" | tail -1 | awk '{print $2}')
  if [ "$code" = "200" ] || [ "$code" = "301" ] || [ "$code" = "302" ]; then
    echo "OK $code $url"
  else
    echo "FAIL $code $url"
    ALL_OK=false
  fi
done

kill $SERVER_PID 2>/dev/null
sleep 1

echo ""
echo "Server errors in log:"
grep -c "Internal Server Error" /tmp/server.log 2>/dev/null || echo "0"

if $ALL_OK; then echo "ALL TESTS PASSED"; else echo "SOME TESTS FAILED"; fi
