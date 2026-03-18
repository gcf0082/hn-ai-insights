#!/usr/bin/env python3
"""
HN AI 文章抓取脚本 - 最终版
"""

import re
import sys
import json
import subprocess

# AI 相关关键词
AI_KEYWORDS = [
    'AI', 'artificial intelligence', 'machine learning', 'ML', 'deep learning',
    'neural network', 'LLM', 'large language model', 'transformer',
    'GPT', 'Claude', 'Anthropic', 'OpenAI', 'Mistral', 'Gemini',
    'stable diffusion', 'diffusion model', 'generative AI', 'gen AI',
    'agent', 'autonomous', 'prompt', 'embedding', 'fine-tuning',
    'inference', 'training', 'model', 'AI safety', 'alignment',
    'RAG', 'retrieval', 'vector database', 'embeddings',
    'Unsloth', 'forge', 'coding agent', 'AI coding', 'Copilot',
    'meta-prompting', 'context engineering'
]

def fetch_hn_page(page=1):
    """使用 curl 抓取 HN 页面"""
    url = f'https://news.ycombinator.com/?p={page}' if page > 1 else 'https://news.ycombinator.com/'
    
    result = subprocess.run(
        ['curl', '-s', '-A', 'Mozilla/5.0', url],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    return result.stdout

def parse_hn_stories(html):
    """解析 HN 故事"""
    stories = []
    
    # 找到所有故事起始位置
    story_matches = list(re.finditer(r'<tr\s+class="athing\s+submission"\s+id="(\d+)">', html))
    
    for i, match in enumerate(story_matches):
        story_id = match.group(1)
        start_pos = match.end()
        
        # 查找标题
        title_match = re.search(r'<span\s+class="titleline">\s*<a\s+href="([^"]+)"[^>]*>(.+?)</a>', html[start_pos:start_pos+600])
        if not title_match:
            continue
        
        url = title_match.group(1)
        title = re.sub(r'&#x27;', "'", title_match.group(2))
        title = re.sub(r'<[^>]+>', '', title).strip()
        
        # 查找来源
        source_match = re.search(r'<span\s+class="sitestr">([^<]+)</span>', html[start_pos:start_pos+600])
        source = source_match.group(1).strip() if source_match else ''
        
        # 在剩余 HTML 中查找分数 - 扩大搜索范围
        remaining = html[start_pos:]
        
        # 查找分数 - 使用更宽松的正则
        score_match = re.search(r'<span\s+class="score"[^>]*>(\d+)\s+points', remaining)
        score = int(score_match.group(1)) if score_match else 0
        
        # 查找评论数
        comments_match = re.search(r'(\d+)\s+comments?', remaining[:800])
        comments = int(comments_match.group(1)) if comments_match else 0
        
        stories.append({
            'id': story_id,
            'title': title,
            'url': url,
            'source': source,
            'score': score,
            'comments': comments,
            'hn_url': f'https://news.ycombinator.com/item?id={story_id}'
        })
    
    return stories

def is_ai_related(title, source=''):
    """判断是否 AI 相关"""
    text = f"{title} {source}".lower()
    
    for keyword in AI_KEYWORDS:
        if keyword.lower() in text:
            return True
    
    return False

def main():
    """主函数"""
    print("🕷️ 开始抓取 Hacker News...")
    
    all_stories = []
    pages_to_fetch = 3
    
    for page in range(1, pages_to_fetch + 1):
        print(f"   抓取第 {page} 页...")
        try:
            html = fetch_hn_page(page)
            stories = parse_hn_stories(html)
            all_stories.extend(stories)
            print(f"   找到 {len(stories)} 篇文章")
        except Exception as e:
            print(f"   抓取第 {page} 页失败：{e}")
    
    print(f"\n📊 共抓取 {len(all_stories)} 篇文章")
    
    # 筛选 AI 相关文章
    ai_stories_all = [s for s in all_stories if is_ai_related(s['title'], s['source'])]
    print(f"\n🤖 AI 相关文章：{len(ai_stories_all)} 篇")
    
    # 显示前 10 篇 AI 文章
    print("\n所有 AI 相关文章:")
    for s in ai_stories_all[:15]:
        print(f"   [{s['score']}分] {s['title'][:50]}... (ID: {s['id']})")
    
    # 过滤分数>=30
    high_score_stories = [s for s in ai_stories_all if s['score'] >= 30]
    low_score_count = len(ai_stories_all) - len(high_score_stories)
    print(f"\n🔥 分数>=30: {len(high_score_stories)} 篇 (过滤 {low_score_count} 篇低分)")
    
    # 按分数排序
    high_score_stories.sort(key=lambda x: x['score'], reverse=True)
    
    # 输出结果
    print(f"\n📋 高分 AI 文章列表:")
    for i, story in enumerate(high_score_stories, 1):
        title_short = story['title'][:50] + '...' if len(story['title']) > 50 else story['title']
        print(f"  {i}. [{story['score']}分] {title_short} (ID: {story['id']})")
    
    # 保存为 JSON
    output = {
        'total_fetched': len(all_stories),
        'ai_related': len(ai_stories_all),
        'filtered_low_score': low_score_count,
        'high_score_ai': len(high_score_stories),
        'stories': high_score_stories
    }
    
    output_file = '/root/hacknews/.state/hn-raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已保存到 {output_file}")

if __name__ == '__main__':
    main()
