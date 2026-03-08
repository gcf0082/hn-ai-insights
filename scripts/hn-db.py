#!/usr/bin/env python3
"""
HN AI 分析 - SQLite 数据库管理
用于存储已深度分析的文章 ID，支持去重查询
"""

import sqlite3
import json
import sys
from datetime import datetime

DB_PATH = '/root/hacknews/.state/hn_analyzed.db'

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建已分析文章表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyzed_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT UNIQUE NOT NULL,
            title_cn TEXT NOT NULL,
            title_en TEXT,
            hn_url TEXT,
            source_url TEXT,
            points INTEGER,
            comments INTEGER,
            analyzed_at TEXT NOT NULL,
            report_file TEXT,
            analysis_time TEXT
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_id ON analyzed_articles(article_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analyzed_at ON analyzed_articles(analyzed_at)')
    
    conn.commit()
    conn.close()

def is_analyzed(article_id):
    """检查文章是否已分析过"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT article_id FROM analyzed_articles WHERE article_id = ?', (article_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result is not None

def add_analyzed(article_id, title_cn, title_en, hn_url, source_url, points, comments, report_file, analysis_time):
    """添加已分析的文章"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    analyzed_at = datetime.now().isoformat()
    
    try:
        cursor.execute('''
            INSERT INTO analyzed_articles 
            (article_id, title_cn, title_en, hn_url, source_url, points, comments, analyzed_at, report_file, analysis_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (article_id, title_cn, title_en, hn_url, source_url, points, comments, analyzed_at, report_file, analysis_time))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 文章已存在
        return False
    finally:
        conn.close()

def add_analyzed_batch(articles, report_file, analysis_time):
    """批量添加已分析的文章"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    analyzed_at = datetime.now().isoformat()
    added_count = 0
    
    for article in articles:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO analyzed_articles 
                (article_id, title_cn, title_en, hn_url, source_url, points, comments, analyzed_at, report_file, analysis_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article['id'],
                article['title_cn'],
                article['title_en'],
                article['hn_url'],
                article.get('source_url', ''),
                article.get('points', 0),
                article.get('comments', 0),
                analyzed_at,
                report_file,
                analysis_time
            ))
            if cursor.rowcount > 0:
                added_count += 1
        except Exception as e:
            print(f"添加文章失败 {article['id']}: {e}", file=sys.stderr)
    
    conn.commit()
    conn.close()
    return added_count

def get_analyzed_ids():
    """获取所有已分析的文章 ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT article_id FROM analyzed_articles')
    ids = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return ids

def get_analyzed_count():
    """获取已分析文章总数"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM analyzed_articles')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def get_recent_analyzed(limit=10):
    """获取最近分析的文章"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT article_id, title_cn, points, comments, analyzed_at 
        FROM analyzed_articles 
        ORDER BY analyzed_at DESC 
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'title_cn': row[1],
            'points': row[2],
            'comments': row[3],
            'analyzed_at': row[4]
        }
        for row in results
    ]

def export_to_json():
    """导出已分析文章 ID 到 JSON（兼容旧格式）"""
    ids = get_analyzed_ids()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT article_id, title_cn FROM analyzed_articles')
    titles = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    data = {
        'lastUpdated': datetime.now().isoformat(),
        'analyzedArticleIds': ids,
        'analyzedTitles': [titles.get(id, '') for id in ids]
    }
    
    json_path = '/root/hacknews/.state/analyzed-articles.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return data

# 命令行工具
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python hn-db.py <命令> [参数]")
        print("命令:")
        print("  init              - 初始化数据库")
        print("  check <id>        - 检查文章是否已分析")
        print("  add <id> <title>  - 添加已分析文章")
        print("  list [limit]      - 列出最近分析的文章")
        print("  count             - 显示已分析文章总数")
        print("  export            - 导出到 JSON 文件")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_db()
        print("✅ 数据库初始化完成")
    
    elif command == 'check':
        if len(sys.argv) < 3:
            print("错误：请提供文章 ID")
            sys.exit(1)
        article_id = sys.argv[2]
        if is_analyzed(article_id):
            print(f"✅ 文章 {article_id} 已分析过")
            sys.exit(0)
        else:
            print(f"⏭️  文章 {article_id} 未分析过")
            sys.exit(1)
    
    elif command == 'add':
        if len(sys.argv) < 4:
            print("错误：请提供文章 ID 和标题")
            sys.exit(1)
        article_id = sys.argv[2]
        title = sys.argv[3]
        if add_analyzed(article_id, title, title, f'https://news.ycombinator.com/item?id={article_id}', '', 0, 0, 'manual', 'manual'):
            print(f"✅ 已添加文章 {article_id}")
        else:
            print(f"⏭️  文章 {article_id} 已存在")
    
    elif command == 'list':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        articles = get_recent_analyzed(limit)
        print(f"最近分析的 {len(articles)} 篇文章:")
        for i, article in enumerate(articles, 1):
            print(f"  {i}. [{article['id']}] {article['title_cn']} (🔥{article['points']} 💬{article['comments']})")
    
    elif command == 'count':
        count = get_analyzed_count()
        print(f"已分析文章总数：{count}")
    
    elif command == 'export':
        data = export_to_json()
        print(f"✅ 已导出 {len(data['analyzedArticleIds'])} 篇文章到 JSON")
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)
