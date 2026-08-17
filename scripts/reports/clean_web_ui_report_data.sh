#!/bin/sh
# 作用：清理Chrome Web UI测试的Allure原始数据，避免新旧结果混合。

set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
REPORT_DATA_DIR="$PROJECT_ROOT/output/web_ui/chrome/report_data"
REPORT_OUTPUT_DIR="$PROJECT_ROOT/output/web_ui/chrome/report"

if [ "$#" -gt 1 ] || { [ "$#" -eq 1 ] && [ "$1" != "--all" ]; }; then
    echo "用法: $0 [--all]"
    exit 2
fi

rm -rf "$REPORT_DATA_DIR"
mkdir -p "$REPORT_DATA_DIR"

if [ "$#" -eq 1 ]; then
    rm -rf "$REPORT_OUTPUT_DIR"
    mkdir -p "$REPORT_OUTPUT_DIR"
fi

echo "已清理Allure原始数据: $REPORT_DATA_DIR"
if [ "$#" -eq 1 ]; then
    echo "已清理历史HTML报告: $REPORT_OUTPUT_DIR"
fi
