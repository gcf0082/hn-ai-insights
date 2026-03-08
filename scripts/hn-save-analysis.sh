#!/bin/bash
# HN AI 分析结果保存脚本
# 用法：./hn-save-analysis.sh "markdown 内容"
# 自动创建 /root/hacknews/YYYY-MM-DD/ 目录并保存为 HH-MM-SS.md

set -e

CONTENT="$1"

if [ -z "$CONTENT" ]; then
    echo "Error: No content provided"
    echo "Usage: $0 \"markdown content\""
    exit 1
fi

# 获取当前日期和时间
DATE_DIR=$(date +%Y-%m-%d)
TIME_FILE=$(date +%H-%M-%S)

# 创建目录
TARGET_DIR="/root/hacknews/${DATE_DIR}"
mkdir -p "${TARGET_DIR}"

# 保存文件
TARGET_FILE="${TARGET_DIR}/${TIME_FILE}.md"
echo "$CONTENT" > "${TARGET_FILE}"

echo "Saved to: ${TARGET_FILE}"
