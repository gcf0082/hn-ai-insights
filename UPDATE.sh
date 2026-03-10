#!/bin/bash
# HN AI 分析脚本更新脚本
# 使用方法：bash UPDATE.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 正在更新 HN AI 分析脚本..."
cd "$SCRIPT_DIR"

# 检查是否是 git 仓库
if [ ! -d ".git" ]; then
    echo "❌ 错误：这不是一个 git 仓库"
    exit 1
fi

# 拉取最新代码
git fetch origin
git reset --hard origin/main

echo "✅ 更新完成！"
echo ""
echo "📁 当前脚本位置：$SCRIPT_DIR"
echo "📊 GitHub: https://github.com/gcf0082/hn-ai-insights"
