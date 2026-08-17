#!/bin/sh
# 作用：兼容旧命令，转发到统一测试入口。

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)

if [ "${INCLUDE_FAILURE_DEMO:-0}" = "1" ]; then
    set -- --include-failure-demo "$@"
fi

if [ -n "${REPORT_PORT:-}" ]; then
    set -- --port "$REPORT_PORT" "$@"
fi

exec "$PROJECT_ROOT/scripts/runners/run_test_suite.sh" --demo saucedemo "$@"
