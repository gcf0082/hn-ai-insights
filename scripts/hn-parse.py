#!/usr/bin/env python3
"""
HN AI 文章解析脚本 - 从 HTML 文件中提取 AI 相关文章
"""

import re
import json
import sys
from html import unescape

AI_KEYWORDS = [
    ' ai ', ' ai,', ' ai.', ' ai?', '(ai)', '[ai]',
    'artificial intelligence',
    'machine learning', ' ml ', ' ml,',
    'deep learning',
    'neural network', 'neural networks',
    'llm', 'llms',
    'gpt-', 'gpt4', 'gpt5', 'gpt-4', 'gpt-5',
    'claude', 'anthropic', 'openai',
    'agent', 'agents',
    'transformer',
    'diffusion model',
    'inference',
    'fine-tun',
    'embedding',
    'vector api',
    'pytorch', 'tensorflow',
    'hugging face', 'huggingface',
    'copilot',
    'automated pr', 'ai-generated',
    'generative',
    'information extraction',
    'visual perception', 'brain data',
]

AI_DOMAINS = [
    'anthropic.com', 'openai.com', 'deepmind.com', 
    'huggingface.co', 'grith.ai', 'fastino-ai',
    'alibaba.github.io', 'jido.run', 'tensorspy.com'
]

def parse_html_file(filepath):
    """解析 HTML 文件提取文章"""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    articles = []
    
    # 查找所有文章条目
    # 匹配格式：<tr class="athing submission" id="XXXXX">
    athing_pattern = r'<tr class="athing submission" id="(\d+)">'
    
    for match in re.finditer(athing_pattern, html):
        article_id = match.group(1)
        start_pos = match.end()
        
        # 在后续内容中查找该文章的详细信息
        # 查找标题和链接
        title_match = re.search(
            r'<span class="titleline"><a href="([^"]+)">(.*?)</a>',
            html[start_pos:start_pos+500]
        )
        
        if not title_match:
            continue
            
        source_url = title_match.group(1)
        title = unescape(title_match.group(2).strip())
        
        # 查找分数
        score_match = re.search(
            rf'<span class="score"[^>]*id="score_{article_id}">(\d+) points</span>',
            html
        )
        points = int(score_match.group(1)) if score_match else 0
        
        # 查找评论数
        comments_match = re.search(
            rf'<a href="item\?id={article_id}">(\d+)\s*comments</a>',
            html
        )
        comments = int(comments_match.group(1)) if comments_match else 0
        
        # 查找域名
        domain_match = re.search(
            r'<span class="sitestr">([^<]+)</span>',
            html[start_pos:start_pos+500]
        )
        domain = domain_match.group(1) if domain_match else ""
        
        articles.append({
            'id': article_id,
            'title': title,
            'source_url': source_url,
            'domain': domain,
            'points': points,
            'comments': comments,
            'hn_url': f'https://news.ycombinator.com/item?id={article_id}'
        })
    
    return articles

def is_ai_related(article):
    """判断文章是否与 AI 相关"""
    text = (article['title'] + ' ' + article['domain']).lower()
    
    # 检查关键词
    for keyword in AI_KEYWORDS:
        if keyword in text:
            return True
    
    # 检查 AI 相关域名
    for domain in AI_DOMAINS:
        if domain in article['domain'].lower():
            return True
    
    return False

def main():
    all_articles = []
    
    # 解析所有 HTML 文件
    for page in range(1, 4):
        filepath = f'/tmp/hn{page}.html'
        try:
            articles = parse_html_file(filepath)
            all_articles.extend(articles)
            print(f"第 {page} 页：{len(articles)} 篇文章", file=sys.stderr)
        except Exception as e:
            print(f"解析第 {page} 页失败：{e}", file=sys.stderr)
    
    print(f"总共抓取 {len(all_articles)} 篇文章", file=sys.stderr)
    
    # 过滤 AI 相关文章
    ai_articles = [a for a in all_articles if is_ai_related(a)]
    print(f"AI 相关文章：{len(ai_articles)} 篇", file=sys.stderr)
    
    # 过滤分数>=30 的文章
    high_score_articles = [a for a in ai_articles if a['points'] >= 30]
    print(f"分数>=30 的文章：{len(high_score_articles)} 篇", file=sys.stderr)
    
    # 按分数排序
    high_score_articles.sort(key=lambda x: x['points'], reverse=True)
    
    # 输出 JSON 格式
    print(json.dumps(high_score_articles, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
