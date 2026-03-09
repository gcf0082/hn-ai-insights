#!/usr/bin/env python3
"""
Fetch AI-related articles from Hacker News
"""

import requests
import json
import re
import sys

# AI 相关关键词
AI_KEYWORDS = [
    'ai', 'artificial intelligence', 'llm', 'language model', 'machine learning',
    'deep learning', 'neural network', 'transformer', 'gpt', 'claude', 'anthropic',
    'openai', 'gemini', 'mistral', 'llama', 'diffusion', 'stable diffusion',
    'midjourney', 'copilot', 'coding agent', 'ai agent', 'agentic', 'rag',
    'embedding', 'vector', 'inference', 'fine-tuning', 'prompt', 'chatbot',
    'generative', 'foundation model', 'ai safety', 'alignment', 'agi'
]

def fetch_top_stories(limit=100):
    """获取热门故事列表"""
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()[:limit]
    return []

def fetch_item(item_id):
    """获取单个故事详情"""
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def is_ai_related(item):
    """判断文章是否与 AI 相关"""
    if not item:
        return False
    
    title = (item.get('title', '') or '').lower()
    text = (item.get('text', '') or '').lower()
    url = (item.get('url', '') or '').lower()
    
    # 检查标题、文本和 URL 是否包含 AI 关键词
    for keyword in AI_KEYWORDS:
        if keyword in title or keyword in text or keyword in url:
            return True
    
    return False

def main():
    print("🔍 正在获取 Hacker News 热门故事...", file=sys.stderr)
    top_stories = fetch_top_stories(200)
    
    ai_articles = []
    
    print(f"📊 共获取 {len(top_stories)} 篇热门故事，开始筛选 AI 相关文章...", file=sys.stderr)
    
    for i, story_id in enumerate(top_stories):
        item = fetch_item(story_id)
        if item and is_ai_related(item):
            points = item.get('score', 0)
            comments = item.get('descendants', 0)
            ai_articles.append({
                'id': str(story_id),
                'title': item.get('title', ''),
                'url': item.get('url', f'https://news.ycombinator.com/item?id={story_id}'),
                'hn_url': f'https://news.ycombinator.com/item?id={story_id}',
                'points': points,
                'comments': comments,
                'by': item.get('by', ''),
                'time': item.get('time', 0)
            })
            print(f"  ✅ [{story_id}] {item.get('title', '')[:60]}... ({points}分)", file=sys.stderr)
        
        if len(ai_articles) >= 30:
            break
    
    print(f"\n📈 共找到 {len(ai_articles)} 篇 AI 相关文章", file=sys.stderr)
    
    # 输出 JSON
    print(json.dumps(ai_articles, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
