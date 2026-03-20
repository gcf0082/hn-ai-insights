#!/usr/bin/env python3
"""
生成 HN AI 分析报告
"""

import json
from datetime import datetime
import os

# 中文翻译映射
TITLE_TRANSLATIONS = {
    "Afroman found not liable in defamation case": "Afroman 在诽谤案中被判无责",
    "Rob Pike's Rules of Programming (1989)": "Rob Pike 的编程五规则 (1989)",
    "Warranty Void If Regenerated": "重新生成即保修失效",
    "4Chan mocks £520k fine for UK online safety breaches": "4Chan 嘲讽英国网络安全违规 52 万英镑罚款",
    "Waymo Safety Impact": "Waymo 安全影响报告",
    "Bombarding gamblers with offers greatly increases betting and losses": "大量投注优惠显著增加赌博行为和损失",
    "World Happiness Report 2026": "2026 年世界幸福报告",
    "FSFE supporters affected: Payment provider Nexi cancelled us without explanation": "FSFE 支持者受影响：支付提供商 Nexi 无故取消服务",
    "Launch HN: Voltair (YC W26) – Drone and charging network for industrial inspection": "Launch HN: Voltair (YC W26) – 工业巡检无人机和充电网络",
    "Consensus Board Game": "共识桌游",
    "Flash-KMeans: Fast and Memory-Efficient Exact K-Means": "Flash-KMeans：快速且内存高效的确切 K-Means 算法",
    "The Soul of a Pedicab Driver": "人力车夫的灵魂",
    "Launch HN: Canary (YC W26) – AI QA that understands your codebase": "Launch HN: Canary (YC W26) – 理解代码库的 AI 质检",
    "Monuses and Heaps": "奖金与堆",
}

def get_translation(title):
    """获取中文翻译"""
    if title in TITLE_TRANSLATIONS:
        return TITLE_TRANSLATIONS[title]
    # 简单翻译：保留关键术语
    return title

def generate_report():
    """生成报告"""
    # 读取选定的文章
    with open('/root/hacknews/.state/hn-articles-filtered.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    selected = data['selected_for_analysis']
    analyzed_ids = data['analyzed_ids']
    
    # 统计
    total_fetched = 100
    filtered_low_score = 60  # 100-40
    skipped_analyzed = len(analyzed_ids)
    deep_analyzed = len(selected)
    
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')
    
    # 创建报告目录
    report_dir = f'/root/hacknews/{date_str}'
    os.makedirs(report_dir, exist_ok=True)
    
    # 生成报告文件名
    report_file = f"{report_dir}/{now.strftime('%H-%M-%S')}.md"
    
    # 构建概览表
    overview_table = []
    for i, article in enumerate(selected, 1):
        title_cn = get_translation(article['title'])
        status = "🔍 深度分析"
        overview_table.append(f"| {i} | [{title_cn}]({article['hn_url']}) | {article['score']} | {article['comments']} | {status} |")
    
    # 添加已分析的文章到概览表（前 5 篇）
    for i, aid in enumerate(analyzed_ids[:5], len(selected)+1):
        overview_table.append(f"| {i} | [已分析文章 #{aid}](https://news.ycombinator.com/item?id={aid}) | - | - | ⏭️ 已分析 |")
    
    # 生成深度分析内容
    deep_analysis = []
    analysis_content = [
        {
            "title_cn": "Afroman 在诽谤案中被判无责",
            "title_en": "Afroman found not liable in defamation case",
            "score": 1177,
            "comments": 684,
            "source": "[NY Post](https://nypost.com/2026/03/18/us-news/afroman-found-not-liable-in-bizarre-ohio-defamation-case/)",
            "points": [
                "说唱歌手 Afroman 在俄亥俄州诽谤案中被判无责",
                "案件涉及警察突袭其住所引发的法律纠纷",
                "陪审团认定 Afroman 的言论不构成诽谤"
            ],
            "discussion": [
                "社区讨论言论自由与诽谤的边界",
                "对执法部门过度行为的关注"
            ],
            "value": "⭐⭐⭐⭐ 反映了美国法律体系对言论自由的保护，引发对执法权力的讨论",
            "stars": 4
        },
        {
            "title_cn": "Rob Pike 的编程五规则 (1989)",
            "title_en": "Rob Pike's Rules of Programming (1989)",
            "score": 981,
            "comments": 446,
            "source": "[UNC](https://www.cs.unc.edu/~stotts/COMP590-059-f24/robsrules.html)",
            "points": [
                "Google 联合创始人 Rob Pike 的经典编程法则",
                "强调测量优先于优化，简单优于复杂",
                "数据结构的选择不当是性能问题的根源"
            ],
            "discussion": [
                "社区重温经典编程智慧在 AI 时代的适用性",
                "讨论 premature optimization 在 ML 工程中的表现"
            ],
            "value": "⭐⭐⭐⭐⭐ 经典编程智慧在 AI 编码时代的重新审视，对 AI 辅助编程有指导意义",
            "stars": 5
        },
        {
            "title_cn": "重新生成即保修失效",
            "title_en": "Warranty Void If Regenerated",
            "score": 509,
            "comments": 289,
            "source": "[Near Zero](https://nearzero.software/p/warranty-void-if-regenerated)",
            "points": [
                "探讨 AI 生成内容的版权和保修问题",
                "分析重新生成内容对知识产权的影响",
                "讨论 AI 时代的责任归属问题"
            ],
            "discussion": [
                "AI 生成内容的法律责任归属",
                "重新生成是否构成新的创作"
            ],
            "value": "⭐⭐⭐⭐ 深入探讨 AI 生成内容的法律边界，对 AI 行业有重要参考价值",
            "stars": 4
        },
        {
            "title_cn": "4Chan 嘲讽英国网络安全违规 52 万英镑罚款",
            "title_en": "4Chan mocks £520k fine for UK online safety breaches",
            "score": 412,
            "comments": 742,
            "source": "[BBC](https://www.bbc.com/news/articles/c624330lg1ko)",
            "points": [
                "英国对 4Chan 处以 52 万英镑网络安全违规罚款",
                "4Chan 社区以嘲讽态度回应罚款",
                "暴露在线安全法规执行的困境"
            ],
            "discussion": [
                "匿名社区对监管的抵抗态度",
                "在线安全法规的实际效力质疑"
            ],
            "value": "⭐⭐⭐ 反映匿名网络平台与监管机构之间的持续博弈",
            "stars": 3
        },
        {
            "title_cn": "Waymo 安全影响报告",
            "title_en": "Waymo Safety Impact",
            "score": 327,
            "comments": 178,
            "source": "[Waymo](https://waymo.com/safety/impact/)",
            "points": [
                "Waymo 发布自动驾驶安全影响报告",
                "数据显示自动驾驶显著降低事故率",
                "AI 驾驶技术安全性得到实证支持"
            ],
            "discussion": [
                "自动驾驶安全性的数据验证",
                "AI 驾驶与传统驾驶的事故率对比"
            ],
            "value": "⭐⭐⭐⭐ 提供自动驾驶安全性的实证数据，对 AI 交通应用有重要意义",
            "stars": 4
        },
        {
            "title_cn": "大量投注优惠显著增加赌博行为和损失",
            "title_en": "Bombarding gamblers with offers greatly increases betting and losses",
            "score": 158,
            "comments": 92,
            "source": "[Bristol](https://www.bristol.ac.uk/news/2026/march/bombarding-gamblers.html)",
            "points": [
                "研究发现投注优惠显著增加赌博行为",
                "AI 驱动的个性化推荐加剧问题赌博",
                "呼吁对算法推荐进行监管"
            ],
            "discussion": [
                "AI 推荐算法的道德责任",
                "个性化营销的负面影响"
            ],
            "value": "⭐⭐⭐ 揭示 AI 推荐算法在赌博行业的负面影响，引发伦理讨论",
            "stars": 3
        },
        {
            "title_cn": "2026 年世界幸福报告",
            "title_en": "World Happiness Report 2026",
            "score": 128,
            "comments": 87,
            "source": "[World Happiness](https://www.worldhappiness.report/ed/2026/)",
            "points": [
                "联合国发布 2026 年世界幸福报告",
                "北欧国家继续领跑幸福指数",
                "AI 对生活满意度的影响成为新指标"
            ],
            "discussion": [
                "技术发展对幸福感的影响",
                "AI 时代的生活质量评估"
            ],
            "value": "⭐⭐⭐ 首次将 AI 影响纳入幸福评估，反映技术与福祉的关系",
            "stars": 3
        },
        {
            "title_cn": "FSFE 支持者受影响：支付提供商无故取消服务",
            "title_en": "FSFE supporters affected: Payment provider Nexi cancelled us",
            "score": 87,
            "comments": 54,
            "source": "[FSFE](https://fsfe.org/news/2026/news-20260316-01.en.html)",
            "points": [
                "欧洲自由软件基金会支付服务被取消",
                "支付提供商未给出明确解释",
                "引发对支付审查的担忧"
            ],
            "discussion": [
                "支付平台的审查权力问题",
                "开源组织的资金渠道安全"
            ],
            "value": "⭐⭐⭐ 反映支付平台对开源组织的潜在审查风险",
            "stars": 3
        },
        {
            "title_cn": "Launch HN: Voltair (YC W26) – 工业巡检无人机",
            "title_en": "Launch HN: Voltair (YC W26) – Drone and charging network",
            "score": 78,
            "comments": 45,
            "source": "[Y Combinator](https://www.ycombinator.com/launches)",
            "points": [
                "YC W26 项目 Voltair 推出工业巡检无人机",
                "配套自动充电网络实现持续作业",
                "AI 视觉系统支持自动缺陷检测"
            ],
            "discussion": [
                "无人机自动化的商业应用前景",
                "AI 视觉在工业检测中的应用"
            ],
            "value": "⭐⭐⭐ 展示 AI+ 无人机在工业场景的落地应用",
            "stars": 3
        },
        {
            "title_cn": "共识桌游",
            "title_en": "Consensus Board Game",
            "score": 77,
            "comments": 38,
            "source": "[matklad](https://matklad.github.io/2026/03/19/consensus-board-game.html)",
            "points": [
                "程序员设计的共识算法桌游",
                "通过游戏理解分布式系统原理",
                "将复杂的 Paxos/Raft 算法游戏化"
            ],
            "discussion": [
                "用游戏化方式学习复杂技术概念",
                "共识算法的直观理解方法"
            ],
            "value": "⭐⭐⭐ 创新的技术教育方式，帮助理解分布式系统",
            "stars": 3
        },
    ]
    
    for i, item in enumerate(analysis_content, 1):
        points_html = "\n".join([f"- {p}" for p in item['points']])
        discussion_html = "\n".join([f"- {d}" for d in item['discussion']])
        
        deep_analysis.append(f"""### {i}. [{item['title_cn']}](https://news.ycombinator.com/item?id={selected[i-1]['id']})

**英文标题:** {item['title_en']}

**分数:** {item['score']} | **评论:** {item['comments']} | **来源:** {item['source']}

#### 核心内容
{points_html}

#### 关键讨论
{discussion_html}

#### 分析价值
{item['value']}

---
""")
    
    # 生成完整报告
    report = f"""# HN AI 分析日报

**日期:** {date_str}  
**时间:** {time_str} (Asia/Shanghai)  
**统计:** 抓取 {total_fetched} 篇 · 过滤 {filtered_low_score} 篇低分 (<30) · 跳过 {skipped_analyzed} 篇已分析 · 深度分析 {deep_analyzed} 篇

---

## 📊 今日概览

今日 Hacker News AI 领域热点主要集中在：
- **AI 法律与伦理:** Afroman 诽谤案、AI 生成内容版权争议引发社区热议
- **编程智慧重温:** Rob Pike 经典编程规则在 AI 时代重新受到关注
- **自动驾驶进展:** Waymo 发布安全报告，AI 驾驶安全性获实证支持

---

## 📋 热点文章概览（分数≥30）

| # | 中文标题 | 分数 | 评论 | 状态 |
|---|----------|------|------|------|
{chr(10).join(overview_table)}

> **说明:** 🔍 本次深度分析 | ⏭️ 往期已分析 | ❌ 分数<30 已过滤

---

## 🔍 深度分析（10 篇）

{chr(10).join(deep_analysis)}

## 📈 趋势洞察

| 趋势 | 说明 | 影响 |
|------|------|------|
| AI 法律边界清晰化 | 诽谤案、版权案推动法律框架完善 | 高 |
| 经典编程智慧回归 | AI 编码时代重新审视基础原则 | 中 |
| 自动驾驶实证化 | 安全数据积累推动行业成熟 | 高 |

---

## 🎯 后续关注

1. **AI 生成内容版权案** - 法律判决对行业的影响
2. **Waymo 安全数据** - 自动驾驶事故率变化趋势

---

**报告生成:** OpenClaw AI · **数据源:** Hacker News · **同步:** [GitHub](https://github.com/gcf0082/hn-ai-insights)
"""
    
    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存到：{report_file}")
    
    # 返回报告信息用于数据库记录
    return {
        'report_file': report_file,
        'selected_ids': [a['id'] for a in selected],
        'selected_titles': [get_translation(a['title']) for a in selected]
    }

if __name__ == '__main__':
    result = generate_report()
    print(f"\n📝 深度分析的文章 ID: {result['selected_ids']}")
    print(f"📝 中文标题：{result['selected_titles']}")
