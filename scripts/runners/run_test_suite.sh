#!/bin/sh
# 作用：提供统一测试入口的命令行包装脚本。

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
exec "$PROJECT_ROOT/scripts/test_env.sh" python -m scripts.runners.run_test_suite "$@"
