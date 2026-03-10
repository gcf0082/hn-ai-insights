#!/usr/bin/env python3
"""
测试关键词匹配配置
"""

import sys
import json
from pathlib import Path

# 导入匹配器
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
import importlib.util
spec = importlib.util.spec_from_file_location("hn_fetch", Path(__file__).parent / 'scripts' / 'hn-fetch.py')
hn_fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hn_fetch)
KeywordMatcher = hn_fetch.KeywordMatcher

def test_matcher():
    """测试匹配器"""
    config_path = Path(__file__).parent / 'config' / 'match-config.yaml'
    matcher = KeywordMatcher(config_path)
    
    # 测试用例
    test_cases = [
        # (标题，期望匹配)
        ("OpenAI releases GPT-5", True),
        ("I built an AI agent for coding", True),
        ("Machine Learning basics", True),
        ("LLM inference optimization", True),
        ("Claude 3.5 performance", True),
        ("My cat is cute", False),
        ("Agent framework for LLM apps", True),
        ("Local LLM running on MacBook", True),
        ("Hugging Face new model", True),
        ("The agent went to the store", False),  # agent 无 AI 上下文
    ]
    
    print("🧪 测试关键词匹配\n")
    print(f"配置文件：{config_path}\n")
    print(f"已加载 {len(matcher.ai_keywords)} 个关键词规则")
    print(f"已加载 {len(matcher.ai_domains)} 个域名规则")
    print(f"已加载 {len(matcher.special_rules)} 个特殊规则\n")
    
    passed = 0
    failed = 0
    
    for title, expected in test_cases:
        result = matcher.match(title)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} '{title}'")
        print(f"   期望：{expected}, 实际：{result}")
        
        if result != expected:
            match_info = matcher.get_match_info(title)
            print(f"   匹配详情：{json.dumps(match_info, ensure_ascii=False, indent=2)}")
        print()
    
    print(f"\n📊 结果：{passed} 通过，{failed} 失败")
    
    # 显示配置统计
    print("\n📋 配置统计:")
    mode_counts = {}
    for kw in matcher.ai_keywords:
        mode = kw.get('mode', 'icontains')
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
    
    for mode, count in sorted(mode_counts.items()):
        print(f"   {mode}: {count} 个")

if __name__ == '__main__':
    test_matcher()
