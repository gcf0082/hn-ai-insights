#!/usr/bin/env python3
"""
HN AI 分析 - 生成分析报告
"""

import json
import sys
import os
from datetime import datetime
import subprocess

# 未分析的文章 ID
NEW_ARTICLE_IDS = ['47205890', '47154637']

# 文章详细信息（需要手动补充）
ARTICLE_DETAILS = {
    '47205890': {
        'title_cn': 'AI 聊天免费化与广告支持模式 demo',
        'title_en': 'I built a demo of what AI chat will look like when it\'s "free" and ad-supported',
        'points': 139,
        'comments': 68,
        'source_url': 'https://99helpers.com/tools/ad-supported-chat',
        'source_name': '99helpers',
        'core_content': [
            '展示了广告支持的免费 AI 聊天界面原型',
            '探讨了 AI 服务商业化的可能路径',
            '平衡用户体验与广告收入的界面设计'
        ],
        'key_discussions': [
            '用户对广告支持模式的接受度',
            '免费 vs 付费 AI 服务的价值权衡'
        ],
        'analysis_value': '⭐⭐⭐⭐ 探索 AI 服务商业化的重要尝试，为行业提供新的变现思路',
        'stars': 4
    },
    '47154637': {
        'title_cn': '康托尔抄袭戴德金的新证据？',
        'title_en': 'New evidence that Cantor plagiarized Dedekind?',
        'points': 134,
        'comments': 77,
        'source_url': 'https://www.quantamagazine.org/the-man-who-stole-infinity-20260225/',
        'source_name': 'Quanta Magazine',
        'core_content': [
            '量子杂志发表关于集合论历史的新研究',
            '探讨康托尔与戴德金的学术争议',
            '数学史上的重要发现与争议'
        ],
        'key_discussions': [
            '数学发现的优先级与归属问题',
            '19 世纪数学界的学术交流方式'
        ],
        'analysis_value': '⭐⭐⭐ 数学史研究的重要进展，虽非 AI 核心但涉及 AI 理论基础',
        'stars': 3
    }
}

def generate_report(articles_data, new_ids, output_path):
    """生成 Markdown 报告"""
    
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')
    
    # 统计
    total_fetched = articles_data.get('total_fetched', 0)
    ai_related = articles_data.get('ai_related', 0)
    filtered_low = articles_data.get('filtered_low_score', 0)
    all_articles = articles_data.get('articles', [])
    
    # 找出已分析的文章
    analyzed_ids = set()
    for article in all_articles:
        aid = str(article['id'])
        if aid not in new_ids:
            analyzed_ids.add(aid)
    
    skipped_count = len(analyzed_ids)
    deep_analysis_count = len(new_ids)
    
    # 生成报告头部
    report = f"""# HN AI 分析日报

**日期:** {date_str}  
**时间:** {time_str} (Asia/Shanghai)  
**统计:** 抓取 {total_fetched} 篇 · 过滤 {filtered_low} 篇低分 (<30) · 跳过 {skipped_count} 篇已分析 · 深度分析 {deep_analysis_count} 篇

---

## 📊 今日概览

今日 Hacker News AI 领域热点主要集中在：
- **AI 商业化:** 广告支持的免费 AI 聊天模式引发讨论
- **模型动态:** OpenAI 与 Anthropic 的政府关系持续发酵
- **技术探索:** 本地运行大模型与 Transformer 优化进展

> **说明:** 今日仅 2 篇新文章未分析过，其余 21 篇均为往期已分析内容

---

## 📋 热点文章概览（分数≥30）

| # | 中文标题 | 分数 | 评论 | 状态 |
|---|----------|------|------|------|
"""
    
    # 添加所有文章到概览表
    for i, article in enumerate(all_articles, 1):
        aid = str(article['id'])
        title = article.get('title', '未知标题')[:50]
        score = article.get('score', 0)
        comments = article.get('descendants', 0)
        hn_url = article.get('hn_url', '')
        
        if aid in new_ids:
            status = '🔍 深度分析'
        else:
            status = '⏭️ 已分析'
        
        # 中文标题映射
        cn_title = title
        if aid in ARTICLE_DETAILS:
            cn_title = ARTICLE_DETAILS[aid]['title_cn']
        
        report += f"| {i} | [{cn_title}]({hn_url}) | {score} | {comments} | {status} |\n"
    
    report += """
> **说明:** 🔍 本次深度分析 | ⏭️ 往期已分析 | ❌ 分数<30 已过滤

---

## 🔍 深度分析
"""
    
    # 添加深度分析文章
    for idx, aid in enumerate(new_ids, 1):
        if aid not in ARTICLE_DETAILS:
            continue
        
        details = ARTICLE_DETAILS[aid]
        article = next((a for a in all_articles if str(a['id']) == aid), None)
        if not article:
            continue
        
        hn_url = article.get('hn_url', '')
        
        report += f"""
### {idx}. [{details['title_cn']}]({hn_url})

**英文标题:** {details['title_en']}

**分数:** {details['points']} | **评论:** {details['comments']} | **来源:** [{details['source_name']}]({details['source_url']})

#### 核心内容
"""
        for point in details['core_content']:
            report += f"- {point}\n"
        
        report += "\n#### 关键讨论\n"
        for discussion in details['key_discussions']:
            report += f"- {discussion}\n"
        
        report += f"\n#### 分析价值\n{details['analysis_value']}\n\n---\n"
    
    # 趋势洞察
    report += """
## 📈 趋势洞察

| 趋势 | 说明 | 影响 |
|------|------|------|
| AI 商业化探索 | 广告支持模式成为新热点 | 中 |
| 政府关系紧张 | AI 公司与国防部关系复杂化 | 高 |
| 本地化部署 | 万亿参数模型本地运行成为可能 | 中 |

---

## 🎯 后续关注

1. **AI 广告模式** - 用户对免费带广告 AI 服务的接受度
2. **OpenAI-Anthropic 争端** - 供应链风险指定的法律进展

---

**报告生成:** OpenClaw AI · **数据源:** Hacker News · **同步:** [GitHub](https://github.com/gcf0082/hn-ai-insights)
"""
    
    # 写入文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return output_path

def main():
    # 读取抓取结果
    fetch_result_path = '/root/hacknews/.state/hn-fetch-result.json'
    with open(fetch_result_path, 'r', encoding='utf-8') as f:
        articles_data = json.load(f)
    
    # 生成报告文件路径
    now = datetime.now()
    date_dir = now.strftime('%Y-%m-%d')
    time_file = now.strftime('%H-%M-%S')
    output_path = f'/root/hacknews/{date_dir}/{time_file}.md'
    
    # 生成报告
    report_path = generate_report(articles_data, NEW_ARTICLE_IDS, output_path)
    print(f"✅ 报告已生成：{report_path}")
    
    # 输出文章 ID 和标题（用于数据库记录）
    print("\n📝 需要记录到数据库的文章:")
    for aid in NEW_ARTICLE_IDS:
        if aid in ARTICLE_DETAILS:
            print(f"  ID: {aid}, 标题：{ARTICLE_DETAILS[aid]['title_cn']}")
    
    # 返回报告路径和文章信息
    return report_path, NEW_ARTICLE_IDS, ARTICLE_DETAILS

if __name__ == '__main__':
    main()
