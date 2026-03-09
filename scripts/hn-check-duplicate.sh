#!/bin/bash
# HN AI 分析去重检查脚本
# 用法：./hn-check-duplicate.sh "文章 ID 列表（空格分隔）"
# 返回：0=有新文章，1=全部重复

set -e

STATE_FILE="/root/hacknews/.state/analyzed-articles.json"
NEW_IDS="$1"

if [ -z "$NEW_IDS" ]; then
    echo "Error: No article IDs provided"
    echo "Usage: $0 \"id1 id2 id3\""
    exit 1
fi

# 如果状态文件不存在，说明全是新文章
if [ ! -f "$STATE_FILE" ]; then
    echo "STATE_FILE_NOT_FOUND - 所有文章都是新的"
    exit 0
fi

# 检查每个 ID 是否已存在
DUPLICATE_COUNT=0
NEW_COUNT=0

for id in $NEW_IDS; do
    if grep -q "\"$id\"" "$STATE_FILE"; then
        DUPLICATE_COUNT=$((DUPLICATE_COUNT + 1))
    else
        NEW_COUNT=$((NEW_COUNT + 1))
    fi
done

echo "检查完成：$NEW_COUNT 篇新文章，$DUPLICATE_COUNT 篇重复"

if [ $NEW_COUNT -eq 0 ]; then
    echo "ALL_DUPLICATES - 没有新文章需要分析"
    exit 1
fi

exit 0
