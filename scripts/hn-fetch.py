#!/usr/bin/env python3
"""
HN AI 文章抓取脚本
抓取 Hacker News 首页，识别 AI 相关文章
"""

import re
import sys
import urllib.request
from html import unescape

# AI 相关关键词
AI_KEYWORDS = [
    'ai ', ' ai,', ' ai.', ' ai?',
    'artificial intelligence',
    'machine learning', 'ml ', ' ml,',
    'deep learning',
    'neural',
    'llm', 'llms',
    'gpt', 'claude', 'anthropic', 'openai',
    'agent', 'agents',
    'transformer',
    'diffusion',
    'inference',
    'fine-tun',
    'embedding',
    'vector',
    'pytorch', 'tensorflow',
    'hugging',
    'copilot',
    'automated', 'automation',
    'generative',
    'model', 'models',
]

def fetch_hn_page(page=1):
    """抓取 HN 页面"""
    url = f"https://news.ycombinator.com/?p={page}" if page > 1 else "https://news.ycombinator.com/"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"抓取失败：{e}", file=sys.stderr)
        return ""

def parse_articles(html):
    """解析 HTML 提取文章信息"""
    articles = []
    
    # 匹配文章条目
    pattern = r'<tr class="athing submission" id="(\d+)">.*?<a href="([^"]+)">(.*?)</a>.*?<span class="score"[^>]*>(\d+) points</span>.*?<a href="item\?id=\d+">(\d+)\s*comments</a>'
    
    for match in re.finditer(pattern, html, re.DOTALL):
        article_id = match.group(1)
        source_url = match.group(2)
        title = unescape(match.group(3))
        points = int(match.group(4))
        comments = int(match.group(5))
        
        # 提取域名
        domain_match = re.search(r'sitestr">([^<]+)</span>', match.group(0))
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
    ai_domains = ['anthropic.com', 'openai.com', 'deepmind.com', 'huggingface.co', 
                  'grith.ai', 'fastino-ai', 'alibaba.github.io/page-agent']
    for domain in ai_domains:
        if domain in article['domain'].lower():
            return True
    
    return False

def main():
    all_articles = []
    
    # 抓取前 3 页
    for page in range(1, 4):
        print(f"抓取第 {page} 页...", file=sys.stderr)
        html = fetch_hn_page(page)
        if html:
            articles = parse_articles(html)
            all_articles.extend(articles)
    
    print(f"总共抓取 {len(all_articles)} 篇文章", file=sys.stderr)
    
    # 过滤 AI 相关文章
    ai_articles = [a for a in all_articles if is_ai_related(a)]
    print(f"AI 相关文章：{len(ai_articles)} 篇", file=sys.stderr)
    
    # 输出 JSON 格式
    import json
    print(json.dumps(ai_articles, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
