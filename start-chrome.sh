#!/bin/bash
pkill -f chrome 2>/dev/null || true
google-chrome --remote-debugging-port=9222 --no-first-run --no-default-browser-check --user-data-dir=/tmp/chrome-debug &
sleep 3
