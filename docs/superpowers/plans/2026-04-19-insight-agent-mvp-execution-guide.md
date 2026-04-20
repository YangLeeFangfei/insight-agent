# Insight Agent MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 2-3 周内交付一个可演示的 Insight Agent MVP，覆盖“自然语言查询 -> 多源采集 -> SQLite 入库 -> 情绪/声量/主题分析 -> 图表化报告输出”的核心闭环。

**Architecture:** 采用“受约束的 Agent 编排 + 结构化分析流水线”。第一阶段先把 CLI 和 HTML/Markdown 报告跑通，保证数据、分析、证据链稳定；第三周再补 Streamlit 工作台、演示体验和风险兜底。

**Tech Stack:** Python 3.11、Click、SQLite、Pydantic、Jinja2、Plotly、Streamlit、httpx、BeautifulSoup4、feedparser、OpenAI API 或 Claude API。

---

## 0. 先说结论

这份 PRD 的范围，**2 周能做出可演示 MVP，3 周能做出作品集级 Demo**。

推荐你采用下面的切法：

- **第 1 周：打通基础链路**
  - 项目初始化
  - 查询解析
  - 多源采集
  - SQLite 入库
  - 数据去重与标准化
- **第 2 周：做分析与报告**
  - 模板化 SQL 分析
  - 趋势检测规则
  - 图表生成
  - Markdown/HTML 报告
  - CLI 体验与错误处理
- **第 3 周：做展示与可信度**
  - Streamlit 工作台
  - Trace 日志
  - 证据面板
  - Demo 数据与演示脚本
  - 打磨作品集展示

如果时间只够 14 天，优先保留：

- CLI
- SQLite
- 3 类来源采集
- 情绪/声量/主题分析
- HTML 报告
- 证据引用

如果时间是 21 天，再补：

- Streamlit
- PDF 导出
- 更完整的趋势提醒
- Agent trace 可视化

---

## 1. 你真正要做的 MVP 范围

基于 PRD，我建议你把 MVP 定死为下面这 8 件事，别再扩：

1. 用户能输入一句自然语言，例如“比较 Kimi、ChatGPT、Gemini 最近 30 天的市场情绪和热点主题”
2. 系统能解析出公司、时间范围、分析类型
3. 系统能从 3 类来源采集数据：
   - 新闻资讯
   - 官方公告/博客
   - 行业内容
4. 数据能统一入 SQLite
5. 系统能输出 3 类基础分析：
   - 声量趋势
   - 情绪分布
   - 主题频率
6. 报告里必须有图表
7. 报告里必须有证据引用
8. 用户至少能通过 CLI 完成一次完整分析

这些内容做完，你的 PRD 核心闭环就成立了。

下面这些先不做：

- 飞书/Slack 推送
- 多用户协作
- 自动定时任务
- 开放 API
- 社交媒体实时抓取
- 很复杂的 Plan-and-Solve
- 高级 RAG
- 向量数据库

---

## 2. 推荐交付策略

### 方案 A：14 天压缩版

适合目标是“先做出能跑、能讲、能演示的作品集项目”。

**交付结果：**

- CLI 可用
- SQLite 可用
- 3 类来源可采集
- 支持 2-5 家竞品对比
- 输出 HTML 报告
- 有图表和证据

**砍掉或弱化：**

- Streamlit 只做只读展示，甚至不做
- PDF 导出延后
- 动态 SQL 先只做 very limited 版本
- 趋势检测先做规则版，不做复杂 Agent reflection

### 方案 B：21 天稳妥版

适合目标是“除了能跑，还想让面试官一眼看出产品和工程完整度”。

**额外交付：**

- Streamlit 工作台
- 证据卡片 UI
- Trace 日志查看
- 失败兜底提示
- Demo 场景脚本
- 更漂亮的作品集展示

**推荐：** 如果这是你作品集项目，优先按 21 天计划做，但前 14 天必须先保住 CLI 闭环。

---

## 3. 建议技术选型

为了在 2-3 周内稳定交付，不要追求“最先进”，要追求“最少坑”。

### 3.1 模型层

二选一即可：

- `OpenAI API`
- `Claude API`

建议策略：

- 查询解析、主题提取、情绪分类、报告摘要都走同一个模型
- 全部使用结构化 JSON 输出
- 给每一步加缓存，避免重复花钱

### 3.2 数据采集层

建议这样配：

- `news`：GNews 或 NewsAPI
- `announcement`：公司官网新闻页 / Blog RSS / Press 页面
- `industry`：Tavily 或 SerpAPI + 域名白名单

原因：

- 这套组合最容易在短时间跑通
- 你能解释“受限数据源”这件事，和 PRD 完全一致

### 3.3 数据层

只用 SQLite，不要一开始就上 Postgres。

建议表：

- `articles`
- `article_topics`
- `analysis_runs`
- `trace_logs`

### 3.4 后端组织

使用普通 Python 包结构，不上 LangChain，不上重框架。

### 3.5 展示层

- 第一优先：HTML 报告
- 第二优先：Streamlit Dashboard

原因：

- HTML 报告最容易交付、最适合作品集截图
- Streamlit 可以在第三周补，增加“工作台感”

---

## 4. 推荐目录结构

从 0 开始就按这个结构建，后面不容易乱：

```text
insight-agent/
├─ .env
├─ .gitignore
├─ README.md
├─ requirements.txt
├─ pyproject.toml
├─ data/
│  ├─ raw/
│  ├─ reports/
│  └─ insight.db
├─ src/
│  └─ insight_agent/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ cli.py
│     ├─ models/
│     │  ├─ query.py
│     │  ├─ article.py
│     │  └─ report.py
│     ├─ agent/
│     │  ├─ loop.py
│     │  ├─ planner.py
│     │  └─ trace.py
│     ├─ collectors/
│     │  ├─ base.py
│     │  ├─ news.py
│     │  ├─ announcement.py
│     │  └─ industry.py
│     ├─ normalize/
│     │  ├─ cleaner.py
│     │  ├─ dedupe.py
│     │  └─ enricher.py
│     ├─ db/
│     │  ├─ schema.sql
│     │  ├─ repository.py
│     │  └─ queries.py
│     ├─ analysis/
│     │  ├─ templates.py
│     │  ├─ engine.py
│     │  ├─ trends.py
│     │  └─ sql_guard.py
│     ├─ reporting/
│     │  ├─ charts.py
│     │  ├─ builder.py
│     │  ├─ templates/
│     │  │  └─ report.html.j2
│     │  └─ exporter.py
│     └─ ui/
│        └─ app.py
└─ tests/
   ├─ test_query_parser.py
   ├─ test_collectors.py
   ├─ test_analysis_engine.py
   ├─ test_trends.py
   └─ test_report_builder.py
```

---

## 5. 21 天稳妥版计划

## 第 1 周：打通数据闭环

### Day 1

- 初始化仓库
- 建立目录结构
- 配置虚拟环境
- 安装依赖
- 配置 `.env`
- 写 README

**完成标志：**

- `python -m insight_agent.cli --help` 能运行

### Day 2

- 设计 SQLite schema
- 创建建表脚本
- 完成 repository 层
- 跑通插入、查询、去重

**完成标志：**

- 能把一条 article 写入数据库并查出来

### Day 3

- 做 Query Parser
- 支持解析：
  - 公司列表
  - 时间范围
  - 分析维度
  - 输出类型

**完成标志：**

- 输入自然语言后能返回结构化 JSON

### Day 4

- 做 `news collector`
- 跑通新闻采集
- 保存 raw response
- 落库前做字段标准化

**完成标志：**

- 能按公司名抓到新闻并写入 SQLite

### Day 5

- 做 `announcement collector`
- 优先接 RSS / 官网新闻页
- 落库并和 news 数据统一结构

**完成标志：**

- 能抓到至少 2 家公司的官方内容

### Day 6

- 做 `industry collector`
- 用 Tavily/SerpAPI + 白名单域名
- 统一标准化

**完成标志：**

- 三类来源都能进库

### Day 7

- 做清洗、去重、主题/情绪 enrichment
- 情绪分类先支持 positive / neutral / negative
- 主题提取先返回 1-5 个标签

**完成标志：**

- 同一条近似内容不会重复入库
- 每条文章都有 sentiment 和 topics

## 第 2 周：打通分析与报告

### Day 8

- 实现模板化 SQL
- 支持：
  - 声量统计
  - 情绪分布
  - 主题频率

**完成标志：**

- 能根据公司和时间范围输出标准分析结果

### Day 9

- 实现趋势检测
- 定义阈值：
  - 最小样本量
  - 环比增长阈值
  - 情绪变化阈值

**完成标志：**

- 至少能识别“声量增长明显”的趋势

### Day 10

- 实现 SQL guard
- 只允许 `SELECT`
- 做失败回退逻辑

**完成标志：**

- 非法 SQL 无法执行

### Day 11

- 生成 Plotly 图表
- 输出：
  - 情绪对比图
  - 声量趋势图
  - 主题 Top N 图

**完成标志：**

- 图表能嵌入 HTML 报告

### Day 12

- 完成报告构建器
- 结构至少包含：
  - Executive Summary
  - Key Findings
  - Charts
  - Evidence
  - Risks / Uncertainty

**完成标志：**

- 能导出一份 HTML 报告

### Day 13

- 做 CLI 命令
- 至少支持：
  - `insight search`
  - `insight compare`
  - `insight trends`
  - `insight report`

**完成标志：**

- 用户只靠 CLI 能完整跑通一次分析

### Day 14

- 加 trace 日志
- 加基础错误提示
- 修正端到端问题
- 准备第一版 demo 数据

**完成标志：**

- 2 周 MVP 闭环可演示

## 第 3 周：做作品集级展示

### Day 15

- 搭 Streamlit 首页
- 输入 query
- 显示分析结果列表

### Day 16

- 做图表面板
- 做证据面板

### Day 17

- 做运行历史和 trace 展示
- 显示失败原因和数据缺口

### Day 18

- 加导出按钮
- 补 PDF 或下载 HTML

### Day 19

- 打磨 UI 和说明文案
- 准备截图、录屏、作品集案例页

### Day 20

- 全链路回归测试
- 修复展示 bug

### Day 21

- 彩排 demo
- 输出最终 README
- 准备面试讲解稿

---

## 6. 14 天压缩版计划

如果你只能用 2 周，就按这个顺序砍：

1. 保留 CLI，砍复杂 UI
2. 保留 HTML，砍 PDF
3. 保留模板 SQL，弱化动态 SQL
4. 保留规则趋势检测，砍复杂智能发现
5. 保留 3 个核心图表，砍 fancy 交互

14 天版里，Day 15-21 的内容全部后移。

---

## 7. 保姆级教程：从 0 开始一步步做

下面这部分按“你今天开始动手”的方式写。

## Step 1：创建项目

在你的工作目录执行：

```bash
mkdir insight-agent
cd insight-agent
git init
python3 -m venv .venv
source .venv/bin/activate
```

安装依赖：

```bash
pip install --upgrade pip
pip install click pydantic python-dotenv httpx beautifulsoup4 feedparser jinja2 plotly streamlit pytest ruff
pip freeze > requirements.txt
```

创建目录：

```bash
mkdir -p data/raw data/reports
mkdir -p src/insight_agent/{models,agent,collectors,normalize,db,analysis,reporting/templates,ui}
mkdir -p tests
touch src/insight_agent/__init__.py
```

创建 `.gitignore`：

```gitignore
.venv/
__pycache__/
.env
data/insight.db
data/raw/
data/reports/
.pytest_cache/
```

## Step 2：写最小可运行 CLI

先做一个空壳，确保项目能跑。

新建 `src/insight_agent/cli.py`：

```python
import click


@click.group()
def cli() -> None:
    """Insight Agent CLI."""


@cli.command()
@click.argument("query")
def search(query: str) -> None:
    click.echo(f"search query: {query}")


if __name__ == "__main__":
    cli()
```

运行：

```bash
PYTHONPATH=src python -m insight_agent.cli search "compare ChatGPT and Gemini"
```

看到输出说明最小壳子成功。

## Step 3：把数据库先搭好

新建 `src/insight_agent/db/schema.sql`：

```sql
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    content TEXT,
    sentiment TEXT,
    published_date TEXT,
    collected_at TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS article_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    FOREIGN KEY(article_id) REFERENCES articles(id)
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,
    companies TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trace_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    step_name TEXT NOT NULL,
    status TEXT NOT NULL,
    detail TEXT,
    created_at TEXT NOT NULL
);
```

再建 `src/insight_agent/db/repository.py`：

```python
from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path("data/insight.db")


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    schema = Path("src/insight_agent/db/schema.sql").read_text()
    with get_conn() as conn:
        conn.executescript(schema)
```

然后执行一次：

```bash
PYTHONPATH=src python -c "from insight_agent.db.repository import init_db; init_db(); print('db ready')"
```

## Step 4：实现查询解析器

目标不是一步做到很聪明，而是先做到“稳定提取”。

新建 `src/insight_agent/models/query.py`：

```python
from pydantic import BaseModel


class QuerySpec(BaseModel):
    raw_query: str
    companies: list[str]
    time_range: str
    metrics: list[str]
    output_format: str = "html"
```

新建 `src/insight_agent/agent/planner.py`：

```python
from insight_agent.models.query import QuerySpec


def parse_query(raw_query: str) -> QuerySpec:
    lowered = raw_query.lower()
    metrics = []
    if "emotion" in lowered or "sentiment" in lowered or "情绪" in raw_query:
        metrics.append("sentiment")
    if "trend" in lowered or "趋势" in raw_query or "声量" in raw_query:
        metrics.append("volume")
    if "topic" in lowered or "主题" in raw_query:
        metrics.append("topics")

    companies = []
    for name in ["ChatGPT", "Gemini", "Kimi", "Claude", "Perplexity"]:
        if name.lower() in lowered:
            companies.append(name)

    if "30" in raw_query:
        time_range = "30d"
    elif "7" in raw_query:
        time_range = "7d"
    else:
        time_range = "30d"

    if not metrics:
        metrics = ["sentiment", "volume", "topics"]

    return QuerySpec(
        raw_query=raw_query,
        companies=companies,
        time_range=time_range,
        metrics=metrics,
    )
```

先别追求完美，后面再接 LLM 做增强解析。

## Step 5：先打通一个数据源，再扩成三个

不要三个一起做。顺序是：

1. `news`
2. `announcement`
3. `industry`

先定义统一数据模型 `src/insight_agent/models/article.py`：

```python
from pydantic import BaseModel


class Article(BaseModel):
    company: str
    title: str
    source_name: str
    source_type: str
    content: str
    published_date: str
    url: str
    sentiment: str | None = None
    topics: list[str] = []
```

然后定义 `collectors/base.py`：

```python
from insight_agent.models.article import Article


class BaseCollector:
    source_type: str

    def collect(self, company: str, days: int) -> list[Article]:
        raise NotImplementedError
```

你每实现一个 collector，都统一返回 `list[Article]`，后面整个系统会轻松很多。

## Step 6：做标准化和去重

这一步非常关键，因为没有干净数据，后面的图表和分析都不可信。

至少做这些规则：

- 标题去空格
- URL 规范化
- 内容为空时过滤
- 相同 URL 不重复插入
- 相似标题可做弱去重

先做简单版就够：

- 数据库层用 `url UNIQUE`
- 入库前按标题做一次 `lower().strip()`

## Step 7：做主题和情绪 enrichment

这一步可以先用 LLM，一次返回结构化 JSON：

```json
{
  "sentiment": "positive",
  "topics": ["AI search", "product launch", "enterprise"]
}
```

注意：

- 只让模型做分类和标签提取
- 不让模型自由写长结论
- 原文证据必须来自数据库，不来自模型编造

## Step 8：实现分析 SQL

先只做模板 SQL，别急着上动态 SQL。

你至少要准备 3 类查询：

### 声量统计

```sql
SELECT company, published_date, COUNT(*) AS article_count
FROM articles
WHERE published_date BETWEEN ? AND ?
GROUP BY company, published_date
ORDER BY published_date ASC;
```

### 情绪分布

```sql
SELECT company, sentiment, COUNT(*) AS count
FROM articles
WHERE published_date BETWEEN ? AND ?
GROUP BY company, sentiment;
```

### 主题频率

```sql
SELECT a.company, t.topic, COUNT(*) AS count
FROM article_topics t
JOIN articles a ON a.id = t.article_id
WHERE a.published_date BETWEEN ? AND ?
GROUP BY a.company, t.topic
ORDER BY count DESC;
```

这三个 SQL 跑通，MVP 的分析部分就成立了。

## Step 9：做趋势检测

别一开始做复杂 AI 判断，先做规则。

最简单版本：

- 最近 7 天 vs 前 7 天
- 如果声量增长超过 50%
- 且样本数 >= 5
- 就提示“可能存在上升趋势”

再加一个情绪波动规则：

- 负面占比提升超过 20%
- 则标记“潜在风险”

这就已经能讲得很完整。

## Step 10：做报告生成器

建议报告结构固定，不要让模型自由发挥：

1. 执行摘要
2. 对比概览
3. 图表展示
4. 趋势发现
5. 关键证据
6. 风险与不确定性

你可以让 LLM 只负责：

- 把结构化分析结果总结成 5-8 句摘要

不要让它：

- 自己编造证据
- 自己算统计值

## Step 11：做 HTML 报告

用 Jinja2 模板输出就够了。

报告页里至少要有：

- 标题
- 查询条件
- 关键结论
- Plotly 图表
- evidence table

如果时间不够，HTML 足够交差，PDF 放到第三周。

## Step 12：串成 Agent 主流程

你的主流程可以非常简单：

```text
parse_query
-> collect data
-> normalize
-> enrich sentiment/topics
-> store in sqlite
-> run analysis sql
-> detect trends
-> build report
-> export html
```

所谓 ReAct，在 MVP 阶段不用做得太玄。

你只需要让 Agent 能：

- 决定先查哪些源
- 决定是否重试
- 决定最后生成哪种报告结构

同时加上：

- 最大迭代次数 = 10
- 超时就停
- 部分失败也返回已有结果

## Step 13：做 CLI 命令

建议第一版命令如下：

```bash
insight search "OpenAI recent announcements"
insight compare "Compare Kimi, ChatGPT, Gemini in the last 30 days"
insight trends "Who grew fastest in AI search in the last month?"
insight report "Compare Claude and Gemini sentiment in the last 14 days"
```

命令背后其实都可以调用同一个主 pipeline，只是输出重点不同。

## Step 14：第三周再补 Streamlit

如果前两周闭环已经跑通，第三周加一个工作台：

- 左边输入 query
- 中间显示 summary 和 charts
- 右边显示 evidence
- 底部显示 trace log

这样面试时会显得非常完整。

---

## 8. 每个阶段的验收标准

### 阶段 1 验收

- 能手动运行 CLI
- 能采集至少 3 类来源
- SQLite 中能看到结构化数据

### 阶段 2 验收

- 能输出情绪、声量、主题三个分析结果
- 能导出 HTML 报告
- 报告里每个关键结论都有证据引用

### 阶段 3 验收

- Streamlit 可演示
- 有错误提示
- 有 trace
- 有一套完整 demo 讲解路径

---

## 9. 你最容易踩的坑

### 坑 1：一开始就做很复杂的 Agent

别这样。先把 pipeline 写死，再让 Agent 只做轻量编排。

### 坑 2：一开始就接太多来源

你只需要 3 类来源，不需要 20 个网站。

### 坑 3：一开始就做动态 SQL

先做模板 SQL。动态 SQL 只作为补充，不是主路径。

### 坑 4：报告全靠模型自由生成

这会直接毁掉可信度。事实、统计、证据都必须来自数据库。

### 坑 5：太早做 UI

先保住 CLI + HTML 报告。它们才是 MVP 的骨架。

---

## 10. 时间不够时怎么砍

如果你在第 7 天之后发现进度落后，按这个顺序砍：

1. 砍 PDF
2. 砍高级 UI
3. 砍复杂趋势检测
4. 砍动态 SQL
5. 保留核心闭环

一定不要砍掉：

- SQLite 持久化
- 三类基础分析
- 报告证据引用
- CLI 跑通

---

## 11. 面试或作品集怎么讲

你最终讲述这项目时，重点不要放在“我用了 Agent”。

重点放在这 4 件事：

1. 我把竞品分析拆成了一个可控的结构化流水线
2. 我没有让 LLM 直接自由生成结论，而是把关键结论绑定到数据库证据
3. 我把动态能力限制在安全边界内，例如只读 SQL 和最大迭代次数
4. 我先用 MVP 验证核心闭环，再逐步补工作台和趋势能力

这会比单纯讲“AI 很智能”更像一个成熟 PM / Agent Engineer。

---

## 12. 开工顺序建议

如果你明天就开始做，严格按这个顺序：

1. 初始化项目
2. CLI 壳子
3. SQLite schema
4. 一个 collector 跑通
5. 三个 collector 跑通
6. 去重与 enrichment
7. 模板 SQL 分析
8. HTML 报告
9. 端到端跑通
10. 再补 Streamlit

别跳步骤。

---

## 13. 我对你的建议

这个项目最正确的做法不是“做大”，而是“做实”。

你这份 PRD 已经很像一个成熟的作品集方向了。真正决定成败的不是功能数量，而是你能不能把下面这句话做出来：

**“输入一句竞品分析需求，系统在受控边界内完成采集、分析、证据绑定和报告输出。”**

只要这句话对应的产品闭环是实的，这个项目就成立。
