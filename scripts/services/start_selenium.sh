#!/bin/sh
# 作用：提供start selenium相关的Shell启动命令。

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
SELENIUM_PORT=${SELENIUM_PORT:-4444}

mkdir -p /tmp/automation-test-downloads
exec "$PROJECT_ROOT/scripts/test_env.sh" \
    /opt/homebrew/opt/selenium-server/bin/selenium-server standalone --port "$SELENIUM_PORT"
