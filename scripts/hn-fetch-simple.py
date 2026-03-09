#!/usr/bin/env python3
"""
HN AI 文章抓取脚本 - 简单版本
使用正则表达式解析 HN HTML
"""

import re
import sys
import json
import urllib.request

def fetch_hn_pages(num_pages=3):
    """抓取多页 HN"""
    all_html = ""
    for page in range(1, num_pages + 1):
        url = f'https://news.ycombinator.com/?p={page}' if page > 1 else 'https://news.ycombinator.com/'
        print(f"抓取第 {page} 页...", file=sys.stderr)
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                all_html += response.read().decode('utf-8')
        except Exception as e:
            print(f"抓取失败：{e}", file=sys.stderr)
    return all_html

def parse_articles(html):
    """解析文章"""
    articles = []
    
    # 匹配文章块
    pattern = r'<tr class="athing submission" id="(\d+)">.*?<a href="([^"]*)">(.*?)</a>.*?<span class="score"[^>]*>(\d+) points?</span>.*?<a href="item\?id=\d+">(\d+)\s*comments?</a>'
    
    for match in re.finditer(pattern, html, re.DOTALL):
        article_id = match.group(1)
        url = match.group(2)
        title = re.sub(r'&#x27;', "'", match.group(3))
        title = re.sub(r'&amp;', '&', title)
        title = re.sub(r'\s+', ' ', title).strip()
        points = int(match.group(4))
        comments = int(match.group(5))
        
        articles.append({
            'id': article_id,
            'title': title,
            'url': url if url.startswith('http') else f'https://news.ycombinator.com/{url}',
            'points': points,
            'comments': comments
        })
    
    # 也匹配没有外部链接的 Show HN 文章
    pattern2 = r'<tr class="athing submission" id="(\d+)">.*?<a href="item\?id=\d+">(Launch HN:|Show HN:)?\s*(.*?)</a>.*?<span class="score"[^>]*>(\d+) points?</span>'
    
    for match in re.finditer(pattern2, html, re.DOTALL):
        article_id = match.group(1)
        prefix = match.group(2) or ''
        title = re.sub(r'&#x27;', "'", match.group(3))
        title = re.sub(r'&amp;', '&', title)
        title = re.sub(r'\s+', ' ', title).strip()
        points = int(match.group(4))
        
        # 检查是否已存在
        if not any(a['id'] == article_id for a in articles):
            articles.append({
                'id': article_id,
                'title': f"{prefix} {title}".strip(),
                'url': f'https://news.ycombinator.com/item?id={article_id}',
                'points': points,
                'comments': 0
            })
    
    return articles

def is_ai_related(title, url=''):
    """判断文章是否与 AI 相关"""
    text = f"{title} {url}".lower()
    
    ai_keywords = [
        'ai ', ' ai.', ' ai,', '(ai)', ' ai"',
        'artificial intelligence',
        'machine learning', ' ml ', ' ml.',
        'deep learning',
        'neural network', 'neural networks',
        'llm', 'llms',
        'gpt-', 'gpt ', 'gpt4', 'gpt5',
        'claude', 'anthropic',
        'openai',
        'chatbot', 'chat bot',
        'agent', 'agents',
        'transformer',
        'diffusion',
        'inference',
        'fine-tuning', 'finetuning',
        'prompt', 'prompting',
        'generative',
        'copilot',
        'model weights',
        'training data',
        'ai act',
        'ai safety',
        'ai ethics',
        'ai regulation',
        'smart glasses',
        'voice ai',
        'text-to-speech',
        'speech recognition',
        'computer vision',
        'autonomous',
        'reinforcement learning',
    ]
    
    for keyword in ai_keywords:
        if keyword in text:
            return True
    
    return False

def main():
    num_pages = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    
    html = fetch_hn_pages(num_pages)
    articles = parse_articles(html)
    
    print(f"总文章数：{len(articles)}", file=sys.stderr)
    
    # 过滤 AI 相关文章
    ai_articles = [a for a in articles if is_ai_related(a['title'], a.get('url', ''))]
    
    print(f"AI 相关文章：{len(ai_articles)}", file=sys.stderr)
    
    # 输出 JSON
    print(json.dumps(ai_articles, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
