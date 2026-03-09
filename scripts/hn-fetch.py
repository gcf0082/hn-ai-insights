#!/usr/bin/env python3
"""
HN AI 文章抓取和分析脚本 - 配置化版本
支持从 YAML 配置文件读取匹配规则
"""

import requests
import re
import json
import sys
import yaml
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

# 默认配置路径（脚本所在目录的父目录下的 config 文件夹）
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / 'config' / 'match-config.yaml'

class KeywordMatcher:
    """关键词匹配器 - 支持多种匹配模式"""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config = self._load_config()
        self.ai_keywords = self.config.get('ai_keywords', [])
        self.ai_domains = self.config.get('ai_domains', [])
        self.special_rules = self.config.get('special_rules', [])
        self.global_config = self.config.get('config', {})
        
        # 预编译正则表达式
        self._compiled_patterns = []
        self._compile_patterns()
    
    def _load_config(self):
        """加载 YAML 配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"警告：配置文件未找到 {self.config_path}，使用默认配置", file=sys.stderr)
            return self._get_default_config()
        except Exception as e:
            print(f"错误：加载配置文件失败：{e}", file=sys.stderr)
            return self._get_default_config()
    
    def _get_default_config(self):
        """返回默认配置（向后兼容）"""
        return {
            'ai_keywords': [],
            'ai_domains': [],
            'special_rules': [],
            'config': {'min_points': 30, 'max_pages': 5}
        }
    
    def _compile_patterns(self):
        """预编译正则表达式"""
        for kw in self.ai_keywords:
            pattern = kw.get('pattern', '')
            mode = kw.get('mode', 'icontains')
            
            try:
                if mode == 'exact':
                    # 精确匹配
                    compiled = re.compile(re.escape(pattern))
                elif mode == 'icontains':
                    # 包含匹配（不区分大小写）
                    compiled = re.compile(re.escape(pattern), re.IGNORECASE)
                elif mode == 'word':
                    # 单词匹配
                    compiled = re.compile(r'\b' + re.escape(pattern) + r'\b')
                elif mode == 'iword':
                    # 单词匹配（不区分大小写）
                    compiled = re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
                elif mode == 'regex':
                    # 正则表达式
                    compiled = re.compile(pattern, re.IGNORECASE)
                else:
                    # 默认：包含匹配
                    compiled = re.compile(re.escape(pattern), re.IGNORECASE)
                
                self._compiled_patterns.append({
                    'pattern': compiled,
                    'mode': mode,
                    'original': pattern
                })
            except re.error as e:
                print(f"警告：正则表达式编译失败 '{pattern}': {e}", file=sys.stderr)
    
    def match(self, text, source=''):
        """
        判断文本是否匹配 AI 关键词
        
        Args:
            text: 要匹配的文本（通常是标题）
            source: 来源域名（可选）
        
        Returns:
            bool: 是否匹配
        """
        full_text = f" {text} {source} "
        
        # 1. 检查关键词匹配
        for item in self._compiled_patterns:
            if item['pattern'].search(full_text):
                # 检查是否有特殊规则
                original = item['original']
                special_rule = self._find_special_rule(original)
                
                if special_rule and special_rule.get('require_context'):
                    # 需要上下文验证
                    context_keywords = special_rule['require_context']
                    for ctx in context_keywords:
                        if ctx.lower() in full_text.lower():
                            return True
                    # 上下文不匹配，继续检查其他关键词
                    continue
                else:
                    return True
        
        # 2. 检查域名匹配
        for domain in self.ai_domains:
            if domain.lower() in source.lower():
                return True
        
        return False
    
    def _find_special_rule(self, keyword):
        """查找特殊规则"""
        for rule in self.special_rules:
            if rule.get('keyword', '').lower() == keyword.lower():
                return rule
        return None
    
    def get_match_info(self, text, source=''):
        """
        获取匹配详情（用于调试）
        
        Returns:
            dict: 匹配的关键词和模式
        """
        full_text = f" {text} {source} "
        matches = []
        
        for item in self._compiled_patterns:
            if item['pattern'].search(full_text):
                matches.append({
                    'keyword': item['original'],
                    'mode': item['mode']
                })
        
        # 检查域名
        for domain in self.ai_domains:
            if domain.lower() in source.lower():
                matches.append({
                    'keyword': domain,
                    'mode': 'domain'
                })
        
        return {
            'matched': len(matches) > 0,
            'matches': matches,
            'text': text,
            'source': source
        }


def fetch_hn_page(page=1):
    """抓取 HN 页面"""
    url = f"https://news.ycombinator.com/?p={page}" if page > 1 else "https://news.ycombinator.com/"
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }, timeout=10)
    return response.text


def parse_hn_stories(html):
    """解析 HN 故事列表"""
    soup = BeautifulSoup(html, 'html.parser')
    stories = []
    
    for tr in soup.find_all('tr', class_='athing'):
        story = {
            'id': '',
            'rank': None,
            'title': '',
            'url': '',
            'source': '',
            'source_url': '',
            'points': 0,
            'comments': 0,
            'time_ago': '',
            'user': ''
        }
        
        # 获取 ID
        story_id = tr.get('id', '')
        if story_id:
            story['id'] = story_id
        
        # 排名
        rank_td = tr.find('td', class_='rank')
        if rank_td:
            story['rank'] = int(rank_td.text.strip().rstrip('.'))
        
        # 标题和链接
        title_span = tr.find('span', class_='titleline')
        if title_span:
            link = title_span.find('a')
            if link:
                story['title'] = link.text.strip()
                story['url'] = link.get('href', '')
            
            # 来源
            sitebit = title_span.find('span', class_='sitebit')
            if sitebit:
                site_link = sitebit.find('a')
                if site_link:
                    sitestr = site_link.find('span', class_='sitestr')
                    story['source'] = sitestr.text if sitestr else ''
                    story['source_url'] = site_link.get('href', '')
        
        # 获取 subtext（分数、评论等）
        next_tr = tr.find_next_sibling('tr')
        if next_tr and 'subtext' in str(next_tr.get('class', [])):
            subtext = next_tr.find('span', class_='subline')
            if subtext:
                # 分数
                score = subtext.find('span', class_='score')
                if score:
                    points_text = score.text.strip()
                    match = re.search(r'(\d+)', points_text)
                    if match:
                        story['points'] = int(match.group(1))
                
                # 评论数
                comments_links = subtext.find_all('a')
                for link in comments_links:
                    if 'comment' in link.text:
                        match = re.search(r'(\d+)', link.text)
                        if match:
                            story['comments'] = int(match.group(1))
                        break
                
                # 时间
                age = subtext.find('span', class_='age')
                if age:
                    story['time_ago'] = age.text.strip()
                
                # 用户
                user = subtext.find('a', class_='hnuser')
                if user:
                    story['user'] = user.text.strip()
        
        if story['id'] and story['title']:
            stories.append(story)
    
    return stories


def fetch_ai_stories(matcher, min_points=30, max_pages=5):
    """抓取 AI 相关文章"""
    all_stories = []
    ai_stories_all = []
    page = 1
    
    while page <= max_pages:
        print(f"抓取第 {page} 页...", file=sys.stderr)
        try:
            html = fetch_hn_page(page)
            stories = parse_hn_stories(html)
            
            if not stories:
                break
            
            # 检查 AI 相关文章
            for story in stories:
                if matcher.match(story['title'], story['source']):
                    ai_stories_all.append(story)
            
            all_stories.extend(stories)
            
            # 如果已经有足够多的高分文章，可以提前停止
            high_score = [s for s in ai_stories_all if s['points'] >= min_points]
            if len(high_score) >= 25:
                break
            
            page += 1
        except Exception as e:
            print(f"抓取第 {page} 页失败：{e}", file=sys.stderr)
            break
    
    # 过滤分数
    filtered = [s for s in ai_stories_all if s['points'] >= min_points]
    
    # 按分数排序
    filtered.sort(key=lambda x: x['points'], reverse=True)
    
    print(f"总共抓取 {len(all_stories)} 篇文章，识别 {len(ai_stories_all)} 篇 AI 相关，过滤后 {len(filtered)} 篇（分数>={min_points}）", file=sys.stderr)
    
    return filtered, len(ai_stories_all), len(all_stories)


def main():
    # 解析命令行参数
    config_path = None
    min_points = 30
    debug = False
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--config' and i + 1 < len(args):
            config_path = args[i + 1]
            i += 2
        elif args[i] == '--min-points' and i + 1 < len(args):
            min_points = int(args[i + 1])
            i += 2
        elif args[i] == '--debug':
            debug = True
            i += 1
        elif args[i].isdigit():
            min_points = int(args[i])
            i += 1
        else:
            i += 1
    
    # 初始化匹配器
    if config_path:
        matcher = KeywordMatcher(Path(config_path))
    else:
        matcher = KeywordMatcher()
    
    # 从配置读取最小分数（如果未指定）
    if min_points == 30:
        min_points = matcher.global_config.get('min_points', 30)
    
    max_pages = matcher.global_config.get('max_pages', 5)
    
    print(f"使用配置文件：{matcher.config_path}", file=sys.stderr)
    print(f"最小分数：{min_points}, 最大页数：{max_pages}", file=sys.stderr)
    
    # 抓取文章
    stories, ai_total, total = fetch_ai_stories(matcher, min_points=min_points, max_pages=max_pages)
    
    # 输出结果
    for story in stories:
        if debug:
            match_info = matcher.get_match_info(story['title'], story['source'])
            story['_match_info'] = match_info
        print(json.dumps(story, ensure_ascii=False))


if __name__ == '__main__':
    main()
