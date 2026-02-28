# HN AI Insights 🤖

Hacker News AI 技术洞察日报，每日自动更新。

## 🌐 在线浏览

访问 GitHub Pages: **https://gcf0082.github.io/hn-ai-insights/**

## 📊 内容说明

每日定时抓取 Hacker News，识别 AI 相关文章，进行深度分析：

- **抓取时间**: 每日 4 次（07:20, 12:30, 18:30, 21:20 北京时间）
- **分析内容**: 文章标题、热度、核心内容、价值点、社区讨论焦点
- **去重机制**: 自动跳过已分析过的文章

## 📁 目录结构

```
/
├── index.html          # 主页
├── styles.css          # 样式
├── app.js              # 前端逻辑
├── reports.json        # 报告索引
├── reports/            # 分析报告目录
│   ├── YYYY-MM-DD-HH-MM-SS.md
│   └── ...
└── README.md
```

## 🔄 自动更新

由 OpenClaw AI 定时任务自动推送更新：

1. 抓取 Hacker News
2. 分析 AI 相关文章
3. 生成 Markdown 报告
4. 同步到 GitHub Pages

## 📅 报告格式

每篇报告包含：

- 文章概览表格（热度、评论数、链接）
- 深度分析（核心内容、价值点、社区讨论）
- 原始链接（HN 讨论 + 来源网站）

## 🛠️ 技术栈

- **生成**: OpenClaw AI + Cron Jobs
- **托管**: GitHub Pages
- **前端**: 原生 HTML/CSS/JavaScript

---

由 [OpenClaw](https://openclaw.ai) 驱动 · [查看源码](https://github.com/gcf0082/hn-ai-insights)
