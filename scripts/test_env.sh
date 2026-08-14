#!/bin/sh
# 作用：加载项目固定版本的Python、Java、Node.js和Appium命令环境。

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

export JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
export APPIUM_HOME="$PROJECT_ROOT/.appium"
export PATH="$PROJECT_ROOT/.venv/bin:$PROJECT_ROOT/node_modules/.bin:/opt/homebrew/opt/openjdk@21/bin:/opt/homebrew/opt/node@22/bin:$PATH"
export PYTHONNOUSERSITE=1

if [ "$#" -eq 0 ]; then
    echo "用法: ./scripts/test_env.sh <命令> [参数...]"
    echo "示例: ./scripts/test_env.sh python --version"
    exit 1
fi

cd "$PROJECT_ROOT" || exit 1
exec "$@"
