#!/usr/bin/env python3
"""检查 HN 文章是否已分析过 - 完整版"""
import subprocess
import sys
import json

# AI 相关文章列表 (ID, 英文标题, 分数, 评论数, 来源 URL)
articles = [
    # 第 1 页
    ("47202708", "Microgpt", 436, 81, "http://karpathy.github.io/2026/02/12/microgpt/"),
    ("47200420", "We do not think Anthropic should be designated as a supply chain risk", 426, 184, "https://twitter.com/OpenAI/status/2027846016423321831"),
    ("47201816", "Show HN: Xmloxide – an agent made rust replacement for libxml2", 49, 33, "https://github.com/jonwiggins/xmloxide"),
    ("47195371", "Addressing Antigravity Bans and Reinstating Access", 223, 181, "https://github.com/google-gemini/gemini-cli/discussions/20632"),
    ("47193064", "MCP server that reduces Claude Code context consumption by 98%", 304, 70, "https://mksg.lu/blog/context-mode"),
    ("47199781", "Qwen3.5 122B and 35B models offer Sonnet 4.5 performance on local computers", 295, 184, "https://venturebeat.com/technology/alibabas-new-open-source-qwen3-5-medium-models-offer-sonnet-4-5-performance"),
    ("47200828", "Building a Minimal Transformer for 10-digit Addition", 47, 7, "https://alexlitzenberger.com/blog/post.html?post=/building_a_minimal_transformer_for_10_digit_addition"),
    ("47199948", "Our Agreement with the Department of War", 255, 205, "https://openai.com/index/our-agreement-with-the-department-of-war"),
    ("47197505", "The whole thing was a scam", 706, 215, "https://garymarcus.substack.com/p/the-whole-thing-was-scam"),
    ("47182986", "747s and Coding Agents", 141, 62, "https://carlkolon.com/2026/02/27/engineering-747-coding-agents/"),
    ("47158834", "Deterministic Programming with LLMs", 36, 19, "https://www.mcherm.com/deterministic-programming-with-llms.html"),
    ("47202614", "Running a One Trillion-Parameter LLM Locally on AMD Ryzen AI Max+ Cluster", 49, 9, "https://www.amd.com/en/developer/resources/technical-articles/2026/how-to-run-a-one-trillion-parameter-llm-locally-an-amd.html"),
    ("47147597", "The Eternal Promise: A History of Attempts to Eliminate Programmers", 259, 173, "https://www.ivanturkovic.com/2026/01/22/history-software-simplification-cobol-ai-hype/"),
    # 第 2 页
    ("47192505", "Unsloth Dynamic 2.0 GGUFs", 215, 59, "https://unsloth.ai/docs/basics/unsloth-dynamic-2.0-ggufs"),
    ("47163167", "From Noise to Image – interactive guide to diffusion", 123, 16, "https://lighthousesoftware.co.uk/projects/from-noise-to-image/"),
    ("47189650", "OpenAI agrees with Dept. of War to deploy models in their classified network", 1352, 626, "https://twitter.com/sama/status/2027578652477821175"),
    ("47193476", "The Future of AI", 123, 98, "https://lucijagregov.com/2026/02/26/the-future-of-ai/"),
    ("47170030", "Smallest transformer that can add two 10-digit numbers", 230, 94, "https://github.com/anadim/AdderBoard"),
    ("47195317", "OpenAI fires an employee for prediction market insider trading", 274, 142, "https://www.wired.com/story/openai-fires-employee-insider-trading-polymarket-kalshi/"),
    ("47201882", "Pentagon chief blocks officers from Ivy League schools and top universities", 89, 32, "https://fortune.com/2026/02/28/pentagon-officer-education-ivy-league-schools-universities-partners-ai-space/"),
    ("47181944", "A Chinese official's use of ChatGPT revealed an intimidation operation", 247, 156, "https://www.cnn.com/2026/02/25/politics/chatgpt-china-intimidation-operation"),
    ("47194611", "Don't trust AI agents", 311, 177, "https://nanoclaw.dev/blog/nanoclaw-security-model"),
    ("47188697", "Statement on the comments from Secretary of War Pete Hegseth", 1133, 349, "https://www.anthropic.com/news/statement-comments-secretary-war"),
    ("47181801", "We gave terabytes of CI logs to an LLM", 217, 107, "https://www.mendral.com/blog/llms-are-good-at-sql"),
    ("47181211", "OpenAI raises $110B on $730B pre-money valuation", 555, 580, "https://techcrunch.com/2026/02/27/openai-raises-110b-in-one-of-the-largest-private-funding-rounds-in-history/"),
    # 第 3 页
    ("47197003", "Show HN: SQLite for Rivet Actors – one database per agent, tenant, or document", 39, 13, "https://github.com/rivet-dev/rivet"),
    ("47194847", "What AI coding costs you", 297, 177, "https://tomwojcik.com/posts/2026-02-15/finding-the-right-amount-of-ai/"),
    ("47182387", "Show HN: Claude-File-Recovery, recover files from your ~/.claude sessions", 94, 39, "https://github.com/hjtenklooster/claude-file-recovery"),
    ("47183940", "GitHub Copilot CLI downloads and executes malware", 55, 21, "https://www.promptarmor.com/resources/github-copilot-cli-downloads-and-executes-malware"),
    ("47195530", "Show HN: Decided to play god this morning, so I built an agent civilisation", 43, 31, "https://github.com/nocodemf/werld"),
    ("47193478", "OpenAI – How to delete your account", 1839, 345, "https://help.openai.com/en/articles/6378407-how-to-delete-your-account"),
    ("47178371", "Get free Claude max 20x for open-source maintainers", 557, 233, "https://claude.com/contact-sales/claude-for-oss"),
    ("47181316", "Building secure, scalable agent sandbox infrastructure", 75, 16, "https://browser-use.com/posts/two-ways-to-sandbox-agents"),
    # 第 4 页
    ("47201028", "Anthropic's Claude rises to No. 2 in the App Store following Pentagon dispute", 31, 2, "https://techcrunch.com/2026/02/28/anthropics-claude-rises-to-no-2-in-the-app-store-following-pentagon-dispute/"),
    ("47186031", "President Trump bans Anthropic from use in government systems", 317, 212, "https://www.npr.org/2026/02/27/nx-s1-5729118/trump-anthropic-pentagon-openai-ai-weapons-ban"),
    ("47149829", "Implementing a Z80 / ZX Spectrum emulator with Claude Code", 150, 71, "https://antirez.com/news/160"),
    ("47173121", "Statement from Dario Amodei on our discussions with the Department of War", 2902, 1558, "https://www.anthropic.com/news/statement-department-of-war"),
    ("47156925", "Google API keys weren't secrets, but then Gemini changed the rules", 1273, 304, "https://trufflesecurity.com/blog/google-api-keys-werent-secrets-but-then-gemini-changed-the-rules"),
]

print(f"共抓取 {len(articles)} 篇 AI 相关文章")
print("=" * 70)

analyzed = []
not_analyzed = []

for article_id, title, points, comments, source_url in articles:
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
print("=" * 70)

# 输出未分析的文章（按分数排序）
not_analyzed_sorted = sorted(not_analyzed, key=lambda x: x[2], reverse=True)
print("\n未分析的文章（按分数排序）:")
for i, (article_id, title, points, comments, source_url) in enumerate(not_analyzed_sorted, 1):
    print(f"{i}. [{article_id}] {title} (🔥{points} 💬{comments})")

# 保存结果到 JSON
data = {
    "total": len(articles),
    "analyzed_count": len(analyzed),
    "not_analyzed_count": len(not_analyzed),
    "analyzed": [{"id": a[0], "title": a[1], "points": a[2], "comments": a[3], "source": a[4]} for a in analyzed],
    "not_analyzed": [{"id": a[0], "title": a[1], "points": a[2], "comments": a[3], "source": a[4]} for a in not_analyzed_sorted]
}

with open("/root/hacknews/.state/articles_check_result.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n结果已保存到 /root/hacknews/.state/articles_check_result.json")
