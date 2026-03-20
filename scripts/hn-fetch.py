#!/usr/bin/env python3
"""
HN AI 文章抓取脚本
从 HN API 获取文章详情，识别 AI 相关文章
"""

import json
import urllib.request
import sys
from datetime import datetime

# AI 相关关键词
AI_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
    'neural', 'llm', 'language model', 'transformer', 'gpt', 'claude', 'anthropic',
    'openai', 'google ai', 'gemini', 'mistral', 'llama', 'meta ai',
    'agent', 'agents', 'autoresearch', 'coding agent', 'ai coding',
    'tts', 'text-to-speech', 'speech synthesis', 'voice ai',
    'computer vision', 'cv', 'image generation', 'diffusion', 'stable diffusion',
    'midjourney', 'dalle', 'sora', 'runway', 'ai video',
    'reinforcement learning', 'rl', 'rlhf', 'training', 'fine-tuning',
    'inference', 'model', 'huggingface', 'pytorch', 'tensorflow',
    'kmeans', 'clustering', 'embedding', 'vector', 'rag',
    'autonomous', 'automation', 'agi', 'alignment', 'safety',
    'cursor', 'copilot', 'github copilot', 'code completion',
    'arxiv', 'preprint', 'research paper', 'ai research'
]

def fetch_item(item_id):
    """获取文章详情"""
    try:
        url = f'https://hacker-news.firebaseio.com/v0/item/{item_id}.json'
        with urllib.request.urlopen(url, timeout=5) as response:
            return json.loads(response.read())
    except Exception as e:
        return None

def is_ai_related(title, url='', text=''):
    """判断文章是否与 AI 相关"""
    content = f"{title} {url} {text}".lower()
    for keyword in AI_KEYWORDS:
        if keyword in content:
            return True
    return False

def main():
    # 获取热门故事 ID
    print("📡 获取热门故事列表...")
    top_url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    with urllib.request.urlopen(top_url, timeout=10) as response:
        story_ids = json.loads(response.read())[:100]  # 前 100 篇
    
    print(f"📋 共获取 {len(story_ids)} 篇热门故事")
    
    ai_articles = []
    
    for i, item_id in enumerate(story_ids):
        item = fetch_item(item_id)
        if not item or item.get('type') != 'story':
            continue
        
        title = item.get('title', '')
        url = item.get('url', '')
        text = item.get('text', '')
        score = item.get('score', 0)
        descendants = item.get('descendants', 0)
        
        # 检查是否 AI 相关
        if is_ai_related(title, url, text):
            article = {
                'id': str(item_id),
                'title': title,
                'url': url,
                'hn_url': f'https://news.ycombinator.com/item?id={item_id}',
                'score': score,
                'comments': descendants,
                'time': item.get('time', 0),
                'by': item.get('by', '')
            }
            ai_articles.append(article)
            status = f"🔥{score}" if score >= 30 else f"·{score}"
            print(f"  [{len(ai_articles)}] {status} {title[:60]}...")
    
    print(f"\n✅ 共识别 {len(ai_articles)} 篇 AI 相关文章")
    
    # 输出为 JSON
    output = {
        'fetched_at': datetime.now().isoformat(),
        'total_fetched': len(story_ids),
        'ai_related': len(ai_articles),
        'articles': ai_articles
    }
    
    # 保存到文件
    output_file = '/root/hacknews/.state/hn-articles-raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"📄 已保存到 {output_file}")
    
    # 输出分数>=30 的文章
    high_score = [a for a in ai_articles if a['score'] >= 30]
    print(f"\n📊 分数>=30 的文章：{len(high_score)} 篇")
    for a in sorted(high_score, key=lambda x: -x['score']):
        print(f"  🔥{a['score']} [{a['id']}] {a['title'][:50]}")

if __name__ == '__main__':
    main()
