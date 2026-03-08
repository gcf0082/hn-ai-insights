# HN AI 分析技能

## 任务说明

定时分析 Hacker News 上关于 AI 的最新文章，**自动去重**，保存到指定目录并发送摘要给用户。

## 🚨 去重机制（重要）

**每次运行必须执行去重检查，避免重复分析相同文章！**

### 去重流程

1. **读取状态文件** `/root/hacknews/.state/analyzed-articles.json`
2. **提取已分析的文章 ID 和标题**
3. **抓取 HN 后对比过滤** — 跳过已分析过的文章
4. **只分析新文章** — 如果全部重复，输出"今日无新文章"并跳过保存
5. **更新状态文件** — 将新分析的文章 ID/标题添加到状态文件

### 状态文件格式

```json
{
  "lastUpdated": "2026-02-28T12:30:00+08:00",
  "analyzedArticleIds": ["47186677", "47178371", "47181211"],
  "analyzedTitles": [
    "I am directing the Department of War to designate Anthropic a Supply-Chain Risk",
    "Get free Claude max 20x for open-source maintainers"
  ]
}
```

### 去重匹配规则

- **优先匹配 item ID**（HN 链接中的 `?id=XXXXX`）
- **备用匹配标题**（模糊匹配，忽略大小写和标点）
- **保留最近 500 篇** — 状态文件超过 500 条时，移除最早的记录

### 报告中标注去重信息

在报告开头注明：
```markdown
**本次分析:** 5 篇新文章 | **跳过:** 12 篇已分析文章
```

## 输出要求

### 1. 文件保存路径
- **根目录:** `/root/hacknews/`
- **日期子目录:** `/root/hacknews/YYYY-MM-DD/`
- **时间戳文件:** `/root/hacknews/YYYY-MM-DD/HH-MM-SS.md`

示例：`/root/hacknews/2026-02-28/12-30-00.md`

### 2. 必须包含文章链接
每篇文章必须包含原始 URL 链接，格式：
```markdown
[文章标题](https://news.ycombinator.com/item?id=XXXXX)
```

或同时包含来源链接：
```markdown
### 1. [文章标题](https://news.ycombinator.com/item?id=XXXXX)
**来源:** [TechCrunch](https://techcrunch.com/...)
```

### 3. Markdown 格式模板
```markdown
# HN AI Daily Analysis - YYYY-MM-DD HH:MM

**抓取时间:** YYYY-MM-DD HH:MM (Asia/Shanghai)  
**来源:** Hacker News (news.ycombinator.com)  
**分析文章数:** N 篇

---

## 📊 今日 AI 相关文章概览

| 排名 | 文章标题 | 热度 (points) | 评论数 | 链接 |
|------|----------|---------------|--------|------|
| 1 | [标题](URL) | XXX | XXX | [🔗](URL) |

---

## 🔍 深度分析

### 1. [文章标题](文章 URL)

**热度:** XXX points | **评论:** XXX 条  
**来源:** [来源名称](来源 URL)

#### 核心内容
- 要点 1
- 要点 2

#### 价值点
1. **标签:** 描述
2. **标签:** 描述

#### 社区讨论焦点
- 讨论点 1
- 讨论点 2

---
```

## 保存方法

### 1. 保存分析报告

使用提供的脚本保存分析结果：

```bash
/root/.openclaw/workspace/scripts/hn-save-analysis.sh "完整的 markdown 内容"
```

或者直接使用 shell 命令：

```bash
DATE_DIR=$(date +%Y-%m-%d)
TIME_FILE=$(date +%H-%M-%S)
mkdir -p /root/hacknews/${DATE_DIR}
cat > /root/hacknews/${DATE_DIR}/${TIME_FILE}.md << 'EOF'
你的 markdown 内容
EOF
```

### 2. 更新状态文件（去重关键）

分析完成后，**必须**更新状态文件记录新分析的文章：

```bash
# 添加新文章 ID 到状态文件
NEW_IDS="47186677 47178371 47181211"
NEW_TITLES="文章标题 1|文章标题 2|文章标题 3"

# 使用 Node.js 脚本更新（推荐）
node /root/.openclaw/workspace/scripts/update-hn-state.js "$NEW_IDS" "$NEW_TITLES"
```

### 3. 检查是否有新文章

```bash
# 检查状态文件
cat /root/hacknews/.state/analyzed-articles.json | jq '.analyzedArticleIds'
```

## 抓取 HN 文章

使用 browser 工具或 web_fetch 抓取 Hacker News：

```
https://news.ycombinator.com/
```

识别 AI 相关关键词：
- AI, Artificial Intelligence, Machine Learning, LLM, GPT, Claude, Anthropic, OpenAI
- Neural Network, Deep Learning, NLP, Computer Vision
- AGI, AI Safety, AI Regulation

## 定时任务配置

当前配置 4 个时间点（Asia/Shanghai 时区）：
- **早晨:** 07:20 (`20 7 * * *`)
- **中午:** 12:30 (`30 12 * * *`)
- **傍晚:** 18:30 (`30 18 * * *`)
- **晚上:** 21:20 (`20 21 * * *`)

## 注意事项

1. **必须带链接** - 每篇文章都要有可点击的 URL
2. **独立文件** - 每次运行创建新文件，不要追加到已有文件
3. **目录自动创建** - 使用 `mkdir -p` 确保日期目录存在
4. **时间戳命名** - 使用 HH-MM-SS 格式，便于区分同一天的多次分析
5. **控制文章数量** - 选择 3-5 篇最有价值的文章深度分析
6. **必须去重** - 每次运行前检查状态文件，跳过已分析文章
7. **更新状态** - 分析完成后必须更新状态文件记录新文章 ID

## 完整示例

```bash
# 1. 检查重复
/root/.openclaw/workspace/scripts/hn-check-duplicate.sh "47186677 47199999"

# 2. 保存分析报告
/root/.openclaw/workspace/scripts/hn-save-analysis.sh "# HN AI 分析..."

# 3. 更新状态文件
node /root/.openclaw/workspace/scripts/update-hn-state.js "47186677 47199999" "文章标题 1|文章标题 2"
```
