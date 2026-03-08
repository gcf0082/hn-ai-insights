# HN AI 分析脚本集合

这是用于分析 Hacker News 上 AI 相关文章的脚本集合，配合 OpenClaw 定时任务使用。

## 📁 目录结构

```
├── scripts/          # 核心脚本
│   ├── hn-fetch.py           # 抓取 HN 文章
│   ├── hn-parse.py           # 解析文章内容
│   ├── hn-parse2.py          # 解析器 v2
│   ├── hn-parse-all.py       # 批量解析
│   ├── hn-db.py              # SQLite 数据库管理（去重/记录）
│   ├── hn-generate-report.py # 生成分析报告
│   ├── hn-fetch-simple.py    # 简化版抓取器
│   ├── hn-check-duplicate.sh # 检查重复文章
│   └── hn-save-analysis.sh   # 保存分析并同步 GitHub
├── templates/        # 报告模板
│   └── hn-report-template.md
└── skills/           # OpenClaw 技能定义
    └── hn-ai-analysis/
        └── SKILL.md
```

## 🔧 使用方法

### 1. 抓取文章
```bash
python3 scripts/hn-fetch.py
```

### 2. 检查是否已分析
```bash
python3 scripts/hn-db.py check <文章 ID>
```

### 3. 记录已分析的文章
```bash
python3 scripts/hn-db.py add <文章 ID> <中文标题>
```

### 4. 生成报告
使用模板 `templates/hn-report-template.md` 生成标准化报告。

### 5. 同步到 GitHub
```bash
bash scripts/hn-save-analysis.sh
```

## ⏰ 定时任务

配置在 OpenClaw cron 中，每天运行 5 次：
- 早晨 7:20
- 中午 12:30
- 傍晚 18:30
- 晚上 21:20
- 凌晨 1:30

## 📊 输出

- 报告保存在：`/root/hacknews/YYYY-MM-DD/HH-MM-SS.md`
- GitHub Pages: https://gcf0082.github.io/hn-ai-insights/

## 📋 数据库

使用 SQLite 存储已分析的文章 ID，避免重复分析。
数据库位置：`/root/.openclaw/workspace/hn_analyzed.db`

## 📝 注意事项

1. 只分析分数 >= 30 的文章
2. 使用数据库去重，避免重复分析
3. 报告格式严格按照模板
4. 分析完成后自动同步到 GitHub
