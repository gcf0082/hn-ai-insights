#!/bin/bash
# HN AI 分析结果自动同步到 GitHub
# 用法：./sync-to-github.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR"
HACKNEWS_DIR="/root/hacknews"

echo "🔄 开始同步 HN 分析结果到 GitHub..."
echo "   仓库目录：$REPO_DIR"
echo "   数据目录：$HACKNEWS_DIR"

cd "$REPO_DIR"

# 获取最新日期目录
LATEST_DATE=$(ls -1 "$HACKNEWS_DIR" | sort -r | head -1)
if [ -z "$LATEST_DATE" ]; then
    echo "❌ 未找到报告目录"
    exit 1
fi

echo "📅 最新报告日期：$LATEST_DATE"

# 复制今日报告到仓库
TARGET_DIR="$REPO_DIR/datas/reports/$LATEST_DATE"
mkdir -p "$TARGET_DIR"

# 复制所有今日报告
cp "$HACKNEWS_DIR/$LATEST_DATE"/*.md "$TARGET_DIR/" 2>/dev/null || true

# 检查是否有新文件
NEW_FILES=$(ls -1 "$TARGET_DIR"/*.md 2>/dev/null | wc -l)
if [ "$NEW_FILES" -eq 0 ]; then
    echo "⚠️ 没有报告文件"
    exit 0
fi

echo "📄 已复制 $NEW_FILES 篇报告"

# 更新 reports.json
echo "📝 更新 reports.json..."
python3 "$REPO_DIR/update-reports-index.py"

# Git 提交
echo "📦 提交到 Git..."
cd "$REPO_DIR"

# 配置 git 用户
git config user.name "HN AI Bot"
git config user.email "hn-ai-bot@local"

# 添加并检查是否有变化
git add "datas/reports/$LATEST_DATE/" reports.json
CHANGED=$(git status --porcelain | wc -l)

if [ "$CHANGED" -eq 0 ]; then
    echo "✅ 没有新变化，跳过提交"
    exit 0
fi

# 提交
git commit -m "Add HN AI analysis reports $LATEST_DATE (auto-sync)"

# 推送
echo "🚀 推送到 GitHub..."
git pull --rebase --strategy-option=theirs 2>/dev/null || true
git push origin main

echo "✅ 同步完成！"
echo "   GitHub: https://github.com/gcf0082/hn-ai-insights"
echo "   Pages: https://gcf0082.github.io/hn-ai-insights/"
