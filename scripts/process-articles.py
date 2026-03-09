#!/usr/bin/env python3
"""
处理 HN AI 文章：过滤低分、检查数据库、选择 10 篇深度分析
"""

import json
import subprocess
import sys

# 从标准输入读取文章列表
articles = json.load(sys.stdin)

# 过滤分数>=30 的文章
high_score_articles = [a for a in articles if a['points'] >= 30]

print(f"📊 原始文章：{len(articles)} 篇", file=sys.stderr)
print(f"📊 分数>=30: {len(high_score_articles)} 篇", file=sys.stderr)

# 检查数据库状态
analyzed_ids = set()
new_articles = []
skipped_articles = []

for article in high_score_articles:
    article_id = article['id']
    try:
        result = subprocess.run(
            ['python3', '/root/.openclaw/workspace/scripts/hn-db.py', 'check', article_id],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            # 已分析过
            skipped_articles.append(article)
            analyzed_ids.add(article_id)
            print(f"  ⏭️  已分析：[{article_id}] {article['title'][:50]}...", file=sys.stderr)
        else:
            # 未分析过
            new_articles.append(article)
            print(f"  ✅ 未分析：[{article_id}] {article['title'][:50]}...", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠️  检查失败 [{article_id}]: {e}", file=sys.stderr)
        new_articles.append(article)

print(f"\n📊 已分析过：{len(skipped_articles)} 篇", file=sys.stderr)
print(f"📊 未分析过：{len(new_articles)} 篇", file=sys.stderr)

# 按分数排序，选择前 10 篇进行深度分析
new_articles.sort(key=lambda x: x['points'], reverse=True)
selected = new_articles[:10]

print(f"\n🎯 选择深度分析的 10 篇文章:", file=sys.stderr)
for i, article in enumerate(selected, 1):
    print(f"  {i}. [{article['id']}] {article['title'][:60]}... ({article['points']}分)", file=sys.stderr)

# 输出结果
result = {
    'total': len(articles),
    'high_score': len(high_score_articles),
    'skipped': len(skipped_articles),
    'new': len(new_articles),
    'selected': selected,
    'skipped_articles': skipped_articles,
    'all_high_score': high_score_articles
}

print(json.dumps(result, ensure_ascii=False, indent=2))
