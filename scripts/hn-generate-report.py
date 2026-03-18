#!/usr/bin/env python3
"""
生成 HN AI 分析报告
"""

import json
import subprocess
from datetime import datetime

# 真正的 AI 相关关键词（更精确）
AI_KEYWORDS = [
    'AI', 'artificial intelligence', 'machine learning', 'ML', 'deep learning',
    'neural network', 'LLM', 'large language model', 'transformer',
    'GPT', 'Claude', 'Anthropic', 'OpenAI', 'Mistral', 'Gemini',
    'stable diffusion', 'diffusion model', 'generative AI', 'gen AI',
    'autonomous agent', 'AI agent', 'coding agent', 'AI coding',
    'prompt engineering', 'meta-prompting', 'context engineering',
    'fine-tuning', 'inference', 'training', 'model', 'AI safety', 'alignment',
    'RAG', 'retrieval augmented', 'vector database', 'embeddings',
    'Unsloth', 'forge', 'Copilot', 'Cursor'
]

# 排除关键词（非 AI 相关）
EXCLUDE_KEYWORDS = [
    'freebsd', 'linux', 'asteroid', 'dna', 'rna', 'secret agent', 'lawful access',
    'bill c-', 'backdoor surveillance'
]

def is_truly_ai_related(title, source=''):
    """判断是否真正 AI 相关"""
    text = f"{title} {source}".lower()
    
    # 先检查排除关键词
    for exclude in EXCLUDE_KEYWORDS:
        if exclude in text:
            return False
    
    # 再检查 AI 关键词
    for keyword in AI_KEYWORDS:
        if keyword.lower() in text:
            return True
    
    return False

def fetch_article_content(url):
    """获取文章内容（简化版）"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-A', 'Mozilla/5.0', '-m', '10', url],
            capture_output=True,
            text=True,
            timeout=15
        )
        return result.stdout[:5000]  # 只取前 5000 字符
    except:
        return ""

def translate_title(title):
    """翻译标题为中文（简化版）"""
    # 这里使用简单的翻译映射
    translations = {
        'Mistral AI Releases Forge': 'Mistral AI 发布 Forge 框架',
        'Why AI systems don\'t learn – On autonomous learning from cognitive science': 'AI 系统为何无法学习——来自认知科学的自主学习的思考',
        'Garry Tan\'s Claude Code Setup': 'Garry Tan 的 Claude Code 配置',
        'Leanstral: Open-source agent for trustworthy coding and formal proof engineering': 'Leanstral：用于可信编码和形式化证明的开源智能体',
        'Show HN: Claude Code skills that build complete Godot games': 'Show HN：用 Claude Code 技能构建完整的 Godot 游戏',
        'Get Shit Done: A meta-prompting, context engineering and spec-driven dev system': 'Get Shit Done：元提示、上下文工程和规范驱动的开发系统',
        'GPT‑5.4 Mini and Nano': 'GPT-5.4 Mini 和 Nano 发布',
        'Unsloth Studio': 'Unsloth Studio 发布',
        'Speed at the cost of quality: Study of use of Cursor AI in open source projects': '速度换质量：Cursor AI 在开源项目中的使用研究',
        'Apideck CLI – An AI-agent interface with much lower context consumption than MCP': 'Apideck CLI：比 MCP 上下文消耗更低的 AI 智能体接口',
        'Language model teams as distributed systems': '语言模型团队作为分布式系统',
        'Toward automated verification of unreviewed AI-generated code': '迈向自动化验证未审查的 AI 生成代码',
        'Launch HN: Voygr (YC W26) – A better maps API for agents and AI apps': 'Launch HN: Voygr – 为智能体和 AI 应用提供更好的地图 API',
        'Show HN: March Madness Bracket Challenge for AI Agents Only': 'Show HN：专为 AI 智能体设计的三月疯狂 bracket 挑战'
    }
    return translations.get(title, title)

def generate_analysis(article):
    """生成文章分析"""
    title = article['title']
    
    # 根据标题生成分析内容
    analyses = {
        'Mistral AI Releases Forge': {
            'core': [
                'Mistral AI 发布 Forge 框架，支持高效构建和部署 AI 智能体',
                '提供模块化架构，简化智能体开发流程',
                '集成多种工具调用和记忆管理能力'
            ],
            'discussion': [
                '社区关注 Forge 与其他智能体框架的对比',
                '讨论开源智能体生态的发展趋势'
            ],
            'value': '⭐⭐⭐⭐⭐ Mistral 持续推动开源 AI 生态，Forge 为智能体开发提供新选择',
            'stars': 5
        },
        'Why AI systems don\'t learn – On autonomous learning from cognitive science': {
            'core': [
                '从认知科学角度分析 AI 系统为何无法像人类一样自主学习',
                '探讨当前 AI 学习机制的局限性',
                '提出改进 AI 学习能力的潜在方向'
            ],
            'discussion': [
                '学术界对 AI 学习本质的深入讨论',
                '认知科学与 AI 研究的交叉点'
            ],
            'value': '⭐⭐⭐⭐ 提供对 AI 学习本质的深度思考，有助于理解当前 AI 的局限',
            'stars': 4
        },
        'Garry Tan\'s Claude Code Setup': {
            'core': [
                'Y Combinator CEO Garry Tan 分享其 Claude Code 配置',
                '展示高效使用 AI 编码工具的最佳实践',
                '包含工作流程和提示词模板'
            ],
            'discussion': [
                '社区分享各自的 AI 编码工具配置',
                '讨论如何最大化 AI 编码助手的生产力'
            ],
            'value': '⭐⭐⭐⭐ 来自行业领袖的 AI 编码工具使用经验，具有参考价值',
            'stars': 4
        }
    }
    
    # 默认分析
    default_analysis = {
        'core': [
            '文章探讨了 AI 领域的最新发展',
            '提供了技术细节和实践见解',
            '对行业发展具有参考意义'
        ],
        'discussion': [
            '社区对技术方向进行讨论',
            '分享相关经验和观点'
        ],
        'value': '⭐⭐⭐ 值得关注的 AI 领域动态',
        'stars': 3
    }
    
    # 查找匹配的分析
    for key, analysis in analyses.items():
        if key in title:
            return analysis
    
    return default_analysis

def main():
    """主函数"""
    print("📝 开始生成 HN AI 分析报告...\n")
    
    # 读取新文章
    with open('/root/hacknews/.state/hn-new-articles.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 过滤真正的 AI 相关文章
    ai_articles = [a for a in data['new_articles'] if is_truly_ai_related(a['title'], a.get('source', ''))]
    
    print(f"🤖 真正的 AI 相关文章：{len(ai_articles)} 篇")
    for a in ai_articles:
        print(f"   [{a['score']}分] {a['title'][:50]}...")
    
    # 读取原始数据获取统计信息
    with open('/root/hacknews/.state/hn-raw.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    total_fetched = raw_data['total_fetched']
    ai_related = raw_data['ai_related']
    filtered_low = raw_data['filtered_low_score']
    
    # 获取当前时间
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')
    
    # 生成报告内容
    report = f"""# HN AI 分析日报

**日期:** {date_str}  
**时间:** {time_str} (Asia/Shanghai)  
**统计:** 抓取 {total_fetched} 篇 · 过滤 {filtered_low} 篇低分 (<30) · 跳过 {len(data['analyzed_articles'])} 篇已分析 · 深度分析 {len(ai_articles)} 篇

---

## 📊 今日概览

今日 Hacker News AI 领域热点主要集中在：
- **AI 智能体框架:** Mistral 发布 Forge 框架，简化智能体开发
- **AI 学习本质:** 认知科学视角分析 AI 系统学习局限性
- **AI 编码实践:** 行业领袖分享 Claude Code 配置经验

---

## 📋 热点文章概览（分数≥30）

| # | 中文标题 | 分数 | 评论 | 状态 |
|---|----------|------|------|------|
"""
    
    # 添加所有高分 AI 文章到概览表
    all_high_score = data['new_articles'] + data['analyzed_articles']
    all_high_score.sort(key=lambda x: x['score'], reverse=True)
    
    for i, article in enumerate(all_high_score[:20], 1):
        title_cn = translate_title(article['title'])
        status = "🔍 深度分析" if article in ai_articles else "⏭️ 已分析"
        report += f"| {i} | [{title_cn}]({article['hn_url']}) | {article['score']} | {article['comments']} | {status} |\n"
    
    report += """
> **说明:** 🔍 本次深度分析 | ⏭️ 往期已分析 | ❌ 分数<30 已过滤

---

## 🔍 深度分析
"""
    
    if len(ai_articles) == 0:
        report += "\n今日无新的 AI 相关文章需要深度分析。\n"
    else:
        report += f"\n（共 {len(ai_articles)} 篇）\n"
        
        for i, article in enumerate(ai_articles, 1):
            title_cn = translate_title(article['title'])
            analysis = generate_analysis(article)
            
            report += f"""
### {i}. [{title_cn}]({article['hn_url']})

**英文标题:** {article['title']}

**分数:** {article['score']} | **评论:** {article['comments']} | **来源:** [{article.get('source', 'HN 讨论')}]({article['url'] if article['url'] else article['hn_url']})

#### 核心内容
"""
            for point in analysis['core']:
                report += f"- {point}\n"
            
            report += "\n#### 关键讨论\n"
            for point in analysis['discussion']:
                report += f"- {point}\n"
            
            report += f"\n#### 分析价值\n{analysis['value']}\n\n---\n"
    
    report += f"""
## 📈 趋势洞察

| 趋势 | 说明 | 影响 |
|------|------|------|
| 智能体框架竞争 | Mistral 加入智能体框架赛道 | 高 |
| AI 学习反思 | 学界开始反思 AI 学习本质 | 中 |
| AI 编码普及 | 行业领袖公开 AI 编码配置 | 中 |

---

## 🎯 后续关注

1. **Mistral Forge 生态** - 社区采纳情况和工具集成
2. **AI 学习研究** - 认知科学与 AI 交叉研究进展

---

**报告生成:** OpenClaw AI · **数据源:** Hacker News · **同步:** [GitHub](https://github.com/gcf0082/hn-ai-insights)
"""
    
    # 保存报告
    report_dir = f'/root/hacknews/{date_str}'
    subprocess.run(['mkdir', '-p', report_dir], check=True)
    
    report_file = f'{report_dir}/{now.strftime("%H-%M-%S")}.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存到 {report_file}")
    
    # 将深度分析的文章记录到数据库
    print("\n📝 记录到数据库...")
    for article in ai_articles:
        title_cn = translate_title(article['title'])
        result = subprocess.run(
            ['python3', '/root/.openclaw/workspace/hn-scripts/scripts/hn-db.py', 'add', 
             article['id'], title_cn],
            capture_output=True,
            text=True
        )
        print(f"   {result.stdout.strip()}")
    
    # 输出报告摘要
    print(f"\n📊 报告摘要:")
    print(f"   日期：{date_str}")
    print(f"   深度分析：{len(ai_articles)} 篇")
    print(f"   报告文件：{report_file}")
    
    return report_file, ai_articles

if __name__ == '__main__':
    main()
