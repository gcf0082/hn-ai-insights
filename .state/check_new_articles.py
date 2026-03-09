#!/usr/bin/env python3
"""检查新增 HN 文章是否已分析过"""
import subprocess
import sys

# 新增 AI 相关文章列表 (ID, 英文标题, 分数, 评论数, 来源 URL)
new_articles = [
    # 第 5 页
    ("47170174", "Launch HN: Cardboard (YC W26) – Agentic video editor", 129, 82, "https://www.usecardboard.com/"),
    ("47146487", "Can you reverse engineer our neural network?", 309, 197, "https://blog.janestreet.com/can-you-reverse-engineer-our-neural-network/"),
    ("47181471", "Show HN: Badge that shows how well your codebase fits in an LLM's context window", 84, 40, "https://github.com/qwibitai/nanoclaw/tree/main/repo-tokens"),
    ("47183527", "An AI agent coding skeptic tries AI agent coding, in excessive detail", 54, 8, "https://minimaxir.com/2026/02/ai-agent-coding/"),
    ("47169757", "What Claude Code chooses", 601, 227, "https://amplifying.ai/research/claude-code-picks"),
    ("47186677", "I am directing the Department of War to designate Anthropic a supply-chain risk", 1331, 1063, "https://twitter.com/secwar/status/2027507717469049070"),
    ("47181841", "ChatGPT Health fails to recognise medical emergencies – study", 209, 148, "https://www.theguardian.com/technology/2026/feb/26/chatgpt-health-fails-recognise-medical-emergencies"),
    ("47176239", "Parakeet.cpp – Parakeet ASR inference in pure C++ with Metal GPU acceleration", 110, 30, "https://github.com/Frikallo/parakeet.cpp"),
    ("47184744", "The Robotic Dexterity Deadlock", 84, 51, "https://www.origami-robotics.com/blog/dexterity-deadlocks.html"),
    # 第 6 页
    ("47194555", "Claude just jumped to #2 on the iOS App Store", 36, 2, "https://xcancel.com/search?f=tweets&q=2027614403693318348"),
    ("47190997", "How do I cancel my ChatGPT subscription?", 1024, 239, "https://help.openai.com/en/articles/7232927-how-do-i-cancel-my-chatgpt-subscription"),
    ("47167858", "Nano Banana 2: Google's latest AI image generation model", 600, 573, "https://blog.google/innovation-and-ai/technology/ai/nano-banana-2/"),
    ("47159833", "Steering interpretable language models with concept algebra", 76, 8, "https://www.guidelabs.ai/post/steerling-steering-8b/"),
]

print(f"检查 {len(new_articles)} 篇新增 AI 相关文章")
print("=" * 70)

analyzed = []
not_analyzed = []

for article_id, title, points, comments, source_url in new_articles:
    result = subprocess.run(
        ["python3", "/root/.openclaw/workspace/scripts/hn-db.py", "check", article_id],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        analyzed.append((article_id, title, points, comments, source_url))
        print(f"⏭️  [{article_id}] {title[:55]}... (🔥{points})")
    else:
        not_analyzed.append((article_id, title, points, comments, source_url))
        print(f"✅ [{article_id}] {title[:55]}... (🔥{points})")

print("=" * 70)
print(f"已分析：{len(analyzed)} 篇")
print(f"未分析：{len(not_analyzed)} 篇")

# 输出未分析的文章（按分数排序）
not_analyzed_sorted = sorted(not_analyzed, key=lambda x: x[2], reverse=True)
print("\n未分析的文章（按分数排序）:")
for i, (article_id, title, points, comments, source_url) in enumerate(not_analyzed_sorted, 1):
    print(f"{i}. [{article_id}] {title} (🔥{points} 💬{comments})")
