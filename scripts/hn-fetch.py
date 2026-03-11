#!/usr/bin/env python3
"""
HN AI 文章抓取和识别脚本
"""

import requests
import re
import json
import sys
from html.parser import HTMLParser

class HNParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.articles = []
        self.current_article = {}
        self.in_title = False
        self.in_score = False
        self.in_age = False
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'tr' and 'class' in attrs_dict and 'athing' in attrs_dict['class']:
            self.current_article = {}
            if 'id' in attrs_dict:
                self.current_article['id'] = attrs_dict['id']
        
        elif tag == 'a' and 'class' in attrs_dict and 'titleline' in attrs_dict.get('class', ''):
            self.in_title = True
            self.current_article['title'] = ''
            if 'href' in attrs_dict and attrs_dict['href'].startswith('http'):
                self.current_article['source_url'] = attrs_dict['href']
        
        elif tag == 'a' and self.in_title and 'href' in attrs_dict:
            self.current_article['hn_url'] = attrs_dict['href']
            
        elif tag == 'span' and 'class' in attrs_dict and attrs_dict['class'] == 'score':
            self.in_score = True
            self.current_article['score_text'] = ''
            
        elif tag == 'span' and 'class' in attrs_dict and 'age' in attrs_dict.get('class', ''):
            self.in_age = True
            
        elif tag == 'a' and self.in_age and 'href' in attrs_dict and 'item?id=' in attrs_dict['href']:
            # 提取评论数
            parent = self.get_starttag_text()
            
        elif tag == 'span' and 'class' in attrs_dict and 'subline' in attrs_dict.get('class', ''):
            # 解析 subtext 行获取评论数
            pass
    
    def handle_endtag(self, tag):
        if tag == 'a' and self.in_title:
            self.in_title = False
        elif tag == 'span' and self.in_score:
            self.in_score = False
            # 解析分数
            if 'score_text' in self.current_article:
                match = re.search(r'(\d+)', self.current_article['score_text'])
                if match:
                    self.current_article['points'] = int(match.group(1))
                else:
                    self.current_article['points'] = 0
        elif tag == 'span' and self.in_age:
            self.in_age = False
        elif tag == 'tr' and 'class' in self.current_article:
            pass
    
    def handle_data(self, data):
        if self.in_title:
            self.current_article['title'] += data
        elif self.in_score:
            self.current_article['score_text'] += data
        elif self.current_article and 'id' in self.current_article:
            # 尝试从 subtext 中提取评论数
            if 'comments' not in self.current_article:
                match = re.search(r'(\d+)\s*comments?', data)
                if match:
                    self.current_article['comments'] = int(match.group(1))
                elif '0 comments' in data.lower() or data.strip() == 'discuss':
                    self.current_article['comments'] = 0
    
    def feed_article(self, html):
        self.feed(html)
        return self.articles

def fetch_hn_page(page=1):
    """获取 HN 页面"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    url = f'https://news.ycombinator.com/?p={page}' if page > 1 else 'https://news.ycombinator.com/'
    response = requests.get(url, headers=headers, timeout=30)
    return response.text

def fetch_multiple_pages(max_pages=3):
    """获取多页内容"""
    all_html = ""
    for page in range(1, max_pages + 1):
        try:
            html = fetch_hn_page(page)
            all_html += html
            print(f"   已抓取第 {page} 页", file=sys.stderr)
        except Exception as e:
            print(f"   第 {page} 页抓取失败：{e}", file=sys.stderr)
            break
    return all_html

def is_ai_related(title, source_url=''):
    """判断文章是否与 AI 相关"""
    title_lower = title.lower()
    source_lower = source_url.lower()
    
    ai_keywords = [
        'ai ', ' ai,', ' ai.', ' ai!',
        'artificial intelligence',
        'machine learning', 'ml ', ' ml,',
        'deep learning',
        'neural network', 'neural networks',
        'llm', 'llms',
        'transformer', 'transformers',
        'gpt', 'claude', 'gemini', 'llama',
        'agent', 'agents', 'agentic',
        'inference', 'inference engine',
        'model', 'models',  # 需要结合上下文
        'training', 'trained',
        'fine-tuning', 'fine tuning',
        'prompt', 'prompting',
        'rag', 'retrieval-augmented',
        'embedding', 'embeddings',
        'diffusion', 'stable diffusion',
        'generative', 'generation',
        'nlp', 'natural language',
        'computer vision',
        'reinforcement learning',
        'autonomous', 'auto-',
        'hume.ai', 'openai', 'anthropic', 'meta ai',
        'bitnet', 'vllm', 'ollama',
        'gpu kernel', 'inference stack',
    ]
    
    # 检查标题
    for keyword in ai_keywords:
        if keyword in title_lower:
            return True
    
    # 检查来源
    ai_domains = [
        'hume.ai', 'openai.com', 'anthropic.com', 'ai.',
        'arxiv.org', 'paperswithcode.com',
        'huggingface', 'replicate',
    ]
    
    for domain in ai_domains:
        if domain in source_lower:
            return True
    
    return False

def parse_hn_html(html):
    """解析 HN HTML 提取文章"""
    articles = []
    
    # 提取所有 athing 行
    article_pattern = r'<tr class="athing[^"]*"[^>]*id="(\d+)">'
    article_ids = re.findall(article_pattern, html)
    
    for article_id in article_ids:
        # 查找对应的标题区域
        title_area_pattern = rf'id="{article_id}".*?<td class="title">(.*?)</td>'
        title_match = re.search(title_area_pattern, html, re.DOTALL)
        
        if not title_match:
            continue
            
        title_area = title_match.group(1)
        
        # 提取标题和链接
        title_link_pattern = r'<a href="([^"]+)">([^<]+)</a>'
        title_matches = re.findall(title_link_pattern, title_area)
        
        if not title_matches:
            continue
            
        # 第一个链接是文章链接
        source_url = title_matches[0][0]
        title = title_matches[0][1].strip()
        
        # 查找分数 (在 subtext 行)
        score_pattern = rf'id="{article_id}".*?<span class="score"[^>]*>(\d+) points</span>'
        score_match = re.search(score_pattern, html, re.DOTALL)
        points = int(score_match.group(1)) if score_match else 0
        
        # 查找评论数
        comments_pattern = rf'id="{article_id}".*?href="item\?id={article_id}">(\d+)\s*comments?</a>'
        comments_match = re.search(comments_pattern, html, re.DOTALL)
        comments = int(comments_match.group(1)) if comments_match else 0
        
        # 处理相对链接
        if source_url.startswith('item?'):
            source_url = f'https://news.ycombinator.com/{source_url}'
        elif not source_url.startswith('http'):
            source_url = f'https://news.ycombinator.com/{source_url}'
        
        articles.append({
            'id': article_id,
            'source_url': source_url,
            'title': title,
            'points': points,
            'comments': comments,
            'hn_url': f'https://news.ycombinator.com/item?id={article_id}'
        })
    
    return articles

def main():
    import os
    print("📰 抓取 Hacker News...", file=sys.stderr)
    
    try:
        html = fetch_multiple_pages(8)  # 抓取 8 页
    except Exception as e:
        print(f"❌ 抓取失败：{e}", file=sys.stderr)
        sys.exit(1)
    
    print("🔍 解析文章...", file=sys.stderr)
    articles = parse_hn_html(html)
    print(f"   共找到 {len(articles)} 篇文章", file=sys.stderr)
    
    # 筛选 AI 相关文章
    print("🤖 筛选 AI 相关文章...", file=sys.stderr)
    ai_articles = [a for a in articles if is_ai_related(a['title'], a.get('source_url', ''))]
    print(f"   找到 {len(ai_articles)} 篇 AI 相关文章", file=sys.stderr)
    
    # 过滤分数>=30 的
    print("📊 过滤分数>=30 的文章...", file=sys.stderr)
    high_score_articles = [a for a in ai_articles if a['points'] >= 30]
    low_score_count = len(ai_articles) - len(high_score_articles)
    print(f"   高分文章：{len(high_score_articles)} 篇 | 低分过滤：{low_score_count} 篇", file=sys.stderr)
    
    # 输出结果
    result = {
        'total_articles': len(articles),
        'ai_articles': len(ai_articles),
        'low_score_filtered': low_score_count,
        'high_score_articles': len(high_score_articles),
        'articles': sorted(high_score_articles, key=lambda x: x['points'], reverse=True)
    }
    
    # 输出 JSON 到 stdout
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return result

if __name__ == '__main__':
    main()
