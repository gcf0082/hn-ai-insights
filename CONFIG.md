# HN AI 匹配配置指南

## 📁 文件结构

```
hn-scripts/
├── config/
│   └── match-config.yaml    # 匹配配置文件
├── scripts/
│   └── hn-fetch.py          # 抓取脚本（支持配置化）
└── test-match.py            # 测试工具
```

## 🔧 匹配模式

支持 5 种匹配模式：

| 模式 | 说明 | 示例 | 匹配 | 不匹配 |
|------|------|------|------|--------|
| `exact` | 精确匹配（区分大小写） | `pattern: "AI"` | "AI" | "ai", "My AI" |
| `icontains` | 包含匹配（不区分大小写） | `pattern: "machine learning"` | "Machine Learning basics" | - |
| `word` | 单词匹配（区分大小写） | `pattern: "llm"` | "the llm is" | "llms", "allm" |
| `iword` | 单词匹配（不区分大小写） | `pattern: "agent"` | "An Agent app" | "agents", "agentive" |
| `regex` | 正则表达式 | `pattern: "gpt-[345]"` | "GPT-4", "gpt-3" | "gpt-2" |

## 📝 配置示例

### 基础配置

```yaml
ai_keywords:
  # 不区分大小写的包含匹配
  - pattern: "artificial intelligence"
    mode: icontains
  
  # 单词匹配（避免误匹配）
  - pattern: "llm"
    mode: iword
  
  # 正则表达式（匹配版本号）
  - pattern: "gpt-[345]"
    mode: regex
```

### 特殊规则（需要上下文）

```yaml
special_rules:
  # agent 只有在 AI 上下文中才匹配
  - keyword: "agent"
    require_context: ["ai", "llm", "model", "autonomous", "coding"]
    mode: iword
```

这样 "The agent went to the store" 不会匹配，但 "AI agent for coding" 会匹配。

### 域名匹配

```yaml
ai_domains:
  - "anthropic.com"
  - "openai.com"
  - "huggingface.co"
```

来源域名包含这些字符串的文章会自动匹配。

### 全局配置

```yaml
config:
  min_points: 30      # 最小分数过滤
  max_pages: 5        # 最大抓取页数
  enable_special_rules: true  # 启用特殊规则
  match_mode: any     # any=任一匹配，all=全部匹配
```

##  测试配置

运行测试脚本验证匹配逻辑：

```bash
cd /root/.openclaw/workspace/hn-scripts
python3 test-match.py
```

## 🚀 使用方式

### 默认（使用默认配置路径）

```bash
python3 scripts/hn-fetch.py --min-points 30
```

### 指定配置文件

```bash
python3 scripts/hn-fetch.py --config /path/to/config.yaml --min-points 30
```

### 调试模式（输出匹配详情）

```bash
python3 scripts/hn-fetch.py --min-points 30 --debug
```

## 📊 配置统计

查看当前配置的关键词分布：

```bash
python3 test-match.py
```

输出示例：
```
已加载 123 个关键词规则
已加载 27 个域名规则
已加载 2 个特殊规则

配置统计:
   icontains: 95 个
   iword: 25 个
   regex: 3 个
```

## 💡 最佳实践

1. **通用术语用 `icontains`** - 如 "machine learning", "deep learning"
2. **短词用 `iword`** - 如 "llm", "gpt", "agi" 避免误匹配
3. **版本号用 `regex`** - 如 "gpt-[345]", "llama[23]"
4. **多义词用特殊规则** - 如 "agent" 需要 AI 上下文
5. **定期更新配置** - 根据实际抓取效果调整关键词

## 🔄 更新配置后

修改 `match-config.yaml` 后无需重启，下次抓取自动生效。

定时任务会在下次运行时使用最新配置。
