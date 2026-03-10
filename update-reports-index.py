#!/usr/bin/env python3
"""
更新 reports.json - 从 Markdown 报告提取元数据
"""

import json
import re
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path(__file__).parent / 'datas' / 'reports'
REPORTS_JSON = Path(__file__).parent / 'reports.json'

def parse_markdown_report(filepath):
    """从 Markdown 报告提取元数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取日期和时间
    date_match = re.search(r'\*\*日期:\*\* (\d{4}-\d{2}-\d{2})', content)
    time_match = re.search(r'\*\*时间:\*\* (\d{2}:\d{2})', content)
    stats_match = re.search(r'\*\*统计:\*\* (.+?)(?:\n|$)', content)
    
    # 提取文章列表（从表格中）
    articles = []
    # 匹配表格行：| 1 | [标题](url) | 分数 | 评论 | 状态 |
    table_pattern = r'\|\s*\d+\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*🔍'
    for match in re.finditer(table_pattern, content):
        title_cn = match.group(1)
        url = match.group(2)
        points = int(match.group(3))
        comments = int(match.group(4))
        
        # 提取 HN ID
        hn_id_match = re.search(r'id=(\d+)', url)
        hn_id = hn_id_match.group(1) if hn_id_match else ''
        
        articles.append({
            'title': title_cn,
            'title_en': '',  # 需要从内容中提取
            'url': url,
            'hnUrl': url,
            'sourceUrl': url,
            'points': points,
            'comments': comments,
            'hnId': hn_id
        })
    
    # 提取深度分析部分的英文标题
    deep_analysis = re.findall(r'### \d+\. \[([^\]]+)\].*?\*\*英文标题:\*\* (.+?)\n', content, re.DOTALL)
    for i, (cn_title, en_title) in enumerate(deep_analysis):
        if i < len(articles):
            articles[i]['title_en'] = en_title.strip()
    
    # 生成摘要
    summary = f"HN AI 每日分析 - {date_match.group(1) if date_match else 'Unknown'}"
    if stats_match:
        summary += f" · {stats_match.group(1).strip()}"
    
    # 计算相对于仓库根目录的路径（包含 datas/reports/）
    # 路径结构：repo_root/datas/reports/YYYY-MM-DD/HH-MM-SS.md
    # filepath.parent = date_dir (e.g., 2026-03-10)
    # filepath.parent.parent = reports_dir (e.g., reports)
    # filepath.parent.parent.parent = datas_dir
    relative_path = 'datas/reports/' + filepath.parent.name + '/' + filepath.name
    
    return {
        'date': date_match.group(1) if date_match else filepath.parent.name,
        'time': time_match.group(1) if time_match else filepath.stem.split('-')[0] + ':' + filepath.stem.split('-')[1],
        'file': str(relative_path),
        'summary': summary,
        'articles': articles[:5]  # 只保留前 5 篇用于预览
    }

def scan_reports():
    """扫描所有报告"""
    reports = []
    
    if not REPORTS_DIR.exists():
        print(f"报告目录不存在：{REPORTS_DIR}")
        return reports
    
    # 遍历所有日期目录
    import re as re_module
    for date_dir in sorted(REPORTS_DIR.iterdir(), reverse=True):
        if not date_dir.is_dir() or not re_module.match(r'\d{4}-\d{2}-\d{2}', date_dir.name):
            continue
        
        # 遍历该日期的所有报告
        for md_file in sorted(date_dir.glob('*.md'), reverse=True):
            try:
                report = parse_markdown_report(md_file)
                reports.append(report)
                print(f"✅ 已处理：{md_file.name}")
            except Exception as e:
                print(f"❌ 处理失败 {md_file.name}: {e}")
    
    return reports

def main():
    print("🔍 扫描报告目录...")
    reports = scan_reports()
    
    if not reports:
        print("⚠️ 未找到任何报告")
        return
    
    # 去重（按文件路径）
    seen = set()
    unique_reports = []
    for r in reports:
        if r['file'] not in seen:
            seen.add(r['file'])
            unique_reports.append(r)
    
    # 按日期和时间排序（最新的在前）
    unique_reports.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)
    
    # 保存
    with open(REPORTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(unique_reports, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已更新 reports.json")
    print(f"   报告总数：{len(unique_reports)}")
    print(f"   最新报告：{unique_reports[0]['date']} {unique_reports[0]['time']}")
    print(f"   文件位置：{REPORTS_JSON}")

if __name__ == '__main__':
    main()
