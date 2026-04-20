# Insight Agent Final Design

**Date:** 2026-04-20

**Goal:** 基于 PRD 与近期 Anthropic / OpenAI / Cursor / Claude Code 架构分析文章，完成一版适合作品集与可实现 MVP 的最终系统设计。

## 1. 设计结论

Insight Agent 不应被设计成一个“无边界自由探索的通用研究代理”，而应被设计成一个：

- **workflow-first**
- **agent-assisted**
- **evidence-backed**
- **human-reviewable**

的竞品情报分析工作台。

换句话说：

- **工作流负责稳定性**
- **Agent 负责弹性编排**
- **数据库负责事实与证据**
- **报告层负责解释与呈现**

这不是一个“让模型自己上网搜一圈然后生成结论”的系统，而是一个“在受控边界内，让模型协调信息采集、数据分析和证据绑定”的系统。

---

## 2. 从外部设计里借什么，不借什么

### 2.1 Anthropic：借“工作流优先”，不借“过度自治”

来自 Anthropic《Building effective agents》的核心启发：

- 成功的 agent 系统通常建立在 **simple, composable patterns** 上，而不是复杂框架之上。
- 应明确区分 **workflow** 和 **agent**：
  - workflow：预定义代码路径
  - agent：模型在边界内自主选择过程与工具

Insight Agent 的落地方式：

- **主链路用 workflow 固化**
  - query parsing
  - source collection
  - normalization
  - storage
  - analysis
  - report generation
- **Agent 只负责有限编排**
  - 调整搜索顺序
  - 选择优先数据源
  - 触发补充分析
  - 组织报告结构

不采用的部分：

- 不做“无限循环的开放式自主研究”
- 不让 Agent 直接主导所有事实判断

### 2.2 Anthropic / Cursor：借“上下文按需加载”，不借“把所有信息塞进 prompt”

来自 Anthropic《Effective context engineering for AI agents》和 Cursor《Dynamic context discovery》的共同启发：

- 上下文是稀缺资源
- 最好的上下文不是越多越好，而是 **最小且高信号**
- 大量数据应使用 **just-in-time / dynamic context discovery**
- 长工具输出不应直接灌入 prompt，而应转成文件、句柄或可再读取对象

Insight Agent 的落地方式：

- 初始 prompt 只放：
  - 用户问题
  - 解析后的任务卡
  - 数据源范围
  - 允许工具清单
  - 当前 run 的关键状态摘要
- 原文、长网页、raw 抓取结果、SQL 大结果集：
  - 不直接放入上下文
  - 先写数据库或本地 artifact
  - 模型只拿 `article_id`、`source_id`、`run_id`、`snippet_id`
- 需要时按需再取：
  - 某篇文章全文
  - 某个来源的最近 10 条
  - 某次 SQL 查询结果样本

不采用的部分：

- 不做“把所有抓回来的文本都喂给模型总结”
- 不让模型直接消费超长原始搜索结果

### 2.3 Anthropic：借“有边界的多代理”，不借“默认上 swarm”

来自 Anthropic《How we built our multi-agent research system》的启发：

- 多代理适合复杂研究任务
- 推荐 **orchestrator-worker**
- 并行化显著提升速度
- 但只有当任务可自然拆分时才值得使用

Insight Agent 的落地方式：

- 默认单 orchestrator，不默认多代理
- 只有以下场景启用 worker：
  - 竞品数量 >= 4
  - 同时需要多维分析（情绪 + 主题 + 趋势 + 风险）
  - 数据源跨多个类型且跨度较大
- worker 职责只限于：
  - 某个来源采集
  - 某个竞品维度分析
  - 某段时间窗口比对
- worker 返回：
  - structured findings
  - evidence ids
  - source quality flags
- worker **不返回完整长上下文**

不采用的部分：

- 不做从 MVP 开始就依赖多代理
- 不做无上限并行

### 2.4 OpenAI：借“harness 才是关键”，不借“把复杂性都堆给模型”

来自 OpenAI《Harness engineering》《Unrolling the Codex agent loop》《Unlocking the Codex harness》的启发：

- 真正的复杂度在 harness，不在一段 prompt
- agent loop 是核心，但只是系统的一部分
- 用户 / Agent 交互不是简单 request/response，而是持续的事件流
- 计划、文档、环境、验证、恢复机制都是一等公民

Insight Agent 的落地方式：

- 设计一个独立的 **Insight Harness**
- Harness 管理：
  - run lifecycle
  - tool routing
  - retries
  - stop conditions
  - trace events
  - approvals / review points
- 前端和 CLI 都不直接拼 prompt，而是通过 harness 发起任务

事件模型采用：

- `run.started`
- `run.plan_generated`
- `source.fetch.started`
- `source.fetch.completed`
- `analysis.started`
- `analysis.completed`
- `report.started`
- `report.completed`
- `run.partial_failed`
- `run.completed`

不采用的部分：

- 不把 agent loop 裸暴露成黑盒
- 不让 UI 直接绑模型 API

### 2.5 OpenAI 数据代理：借“工具少而清晰、权限透传、结果透明”

来自 OpenAI《Inside OpenAI’s in-house data agent》的启发：

- **Less is More**
- 工具过多且能力重叠会让 agent 困惑
- 权限应 pass-through，而不是 agent 自己拥有额外权限
- 必须提高透明度，让用户能检查假设、步骤和原始结果

Insight Agent 的落地方式：

- 工具数保持少且职责互斥
- 所有数据访问默认只读
- 动态 SQL 仅允许 `SELECT`
- 报告必须展示：
  - 假设
  - 数据缺口
  - 关键步骤
  - 证据链接

不采用的部分：

- 不做多个语义高度重叠的搜索工具
- 不给 agent 开放式 shell / 浏览器完全权限作为默认路径

### 2.6 Cursor：借“先出计划、再执行、给可验证产物”，不借“为炫技而自动化”

来自 Cursor《Expanding our long-running agents research preview》《Cursor agents can now control their own computers》的启发：

- 长任务应先 plan，再执行
- 代理不应只给 diff 或文字，应给 artifacts 让人复核
- 代理能力受环境能力限制

Insight Agent 的落地方式：

- 对中大任务，先生成 **Execution Plan Preview**
- 用户可确认：
  - 要分析哪些公司
  - 哪些数据源
  - 哪些分析维度
  - 时间范围
- 执行后必须产出 artifacts：
  - HTML 报告
  - 图表
  - 证据表
  - trace 日志

不采用的部分：

- MVP 不做 full computer-use
- MVP 不做 remote VM 作为默认执行方式

### 2.7 Claude Code 分析仓库：借“基础设施比模型逻辑更重要”

来自 `Dive-into-Claude-Code` 仓库的核心启发：

- 真正难的是 deterministic infrastructure
- 安全、权限、上下文管理、恢复机制往往占主要复杂度
- 子代理应通过 summary-return 避免主上下文爆炸

Insight Agent 的落地方式：

- 重心放在：
  - source boundary
  - data contracts
  - SQL safety
  - evidence binding
  - traceability
  - partial failure recovery
- 子任务只回传摘要和证据 id，不回传全文

---

## 3. 最终产品设计原则

最终采用 8 条原则：

1. **Evidence First**
   - 所有关键结论必须能映射到数据库中的真实记录。
2. **Workflow First**
   - 主链路优先 workflow，agent 只做受约束编排。
3. **Minimal Tool Surface**
   - 工具少、边界清晰、避免重叠。
4. **Just-in-Time Context**
   - 上下文按需拉取，不做全量注入。
5. **Read-Only by Default**
   - 默认只读采集与查询，危险能力不上线或需显式审批。
6. **Human Checkpoints**
   - 长任务和高风险任务设人工确认点。
7. **Artifacts over Assertions**
   - 输出图表、证据、trace，而不是只给一句结论。
8. **Graceful Degradation**
   - 局部失败不导致整体失败，系统返回已完成结果和不确定性提示。

---

## 4. 最终系统架构

## 4.1 总体分层

最终系统采用 6 层结构：

### A. Interaction Layer

负责用户输入与结果展示。

接口形态：

- CLI
- Streamlit Web UI
- 导出 HTML / Markdown / PDF

### B. Orchestration Layer

核心为 `Insight Harness`。

职责：

- query intake
- task planning
- tool selection
- run state management
- retries / stopping
- approval checkpoints
- event streaming

### C. Collection Layer

负责多源采集。

来源类型：

- News
- Announcement
- Industry

### D. Structuring Layer

负责标准化和入库。

职责：

- 去重
- 清洗
- company resolution
- sentiment tagging
- topic extraction
- snippet extraction

### E. Analysis Layer

负责可复现分析。

职责：

- 模板 SQL 分析
- 趋势检测
- 受控动态 SQL
- cross-company comparison

### F. Reporting Layer

负责生成可复核产物。

职责：

- executive summary
- evidence cards
- charts
- uncertainty notes
- export

---

## 4.2 核心执行流

最终的主执行流为：

1. User Query
2. Query Parser
3. Execution Plan Preview
4. Source Collection
5. Normalization & Storage
6. Structured Analysis
7. Trend Detection
8. Evidence Binding
9. Report Synthesis
10. Artifact Export

只有第 3 步之后，才允许进入长耗时任务。

---

## 4.3 Agent 角色划分

### Lead Analyst Agent

唯一默认常驻 agent。

职责：

- 理解用户意图
- 生成任务卡
- 选择 workflow 路径
- 判断是否需要 worker
- 组织最终报告

不负责：

- 直接编造事实
- 自由扩展任务边界
- 绕过数据库和分析引擎给出结论

### Bounded Worker Agents

只在复杂任务触发。

类型：

- `SourceWorker`
- `CompanyWorker`
- `TrendWorker`

返回结构：

- `findings_summary`
- `evidence_ids`
- `source_quality_notes`
- `open_questions`

不返回：

- 冗长推理全文
- 原始巨量上下文

---

## 4.4 工具设计

最终工具清单建议收敛为：

1. `search_news(company, date_range)`
2. `search_announcements(company, date_range)`
3. `search_industry(company, date_range, domains)`
4. `fetch_article(url)`
5. `store_articles(records)`
6. `enrich_articles(article_ids)`
7. `run_template_analysis(template_name, params)`
8. `run_safe_sql(query, params)`
9. `detect_trends(scope)`
10. `build_chart(chart_type, dataset_id)`
11. `build_report(report_spec_id)`
12. `write_trace(run_id, event)`

设计要求：

- 每个工具单一职责
- 大结果集返回 `dataset_id` / `artifact_id`
- 不返回无上限原文
- 参数结构稳定、可验证

---

## 5. 数据设计

## 5.1 核心表

### articles

- `id`
- `company`
- `title`
- `source_name`
- `source_type`
- `content`
- `published_date`
- `collected_at`
- `url`
- `sentiment`

### article_topics

- `id`
- `article_id`
- `topic`

### evidence_snippets

- `id`
- `article_id`
- `snippet_text`
- `snippet_start`
- `snippet_end`
- `used_in_report`

### analysis_runs

- `id`
- `query_text`
- `plan_json`
- `status`
- `created_at`
- `completed_at`

### run_events

- `id`
- `run_id`
- `event_type`
- `payload_json`
- `created_at`

### artifacts

- `id`
- `run_id`
- `artifact_type`
- `path`
- `metadata_json`

---

## 5.2 为什么必须新增 evidence_snippets

PRD 里已经强调证据可追溯，但最终设计里我建议把它从“报告附带信息”提升成一个独立数据对象。

原因：

- 报告引用不应直接临时从全文截断
- 证据应可复用、可审计、可再次渲染
- snippet 是事实层和叙述层之间的稳定桥梁

这能显著提升“结论可追溯率”。

---

## 6. 上下文与记忆设计

## 6.1 运行时上下文

每个 run 只保留：

- 用户问题
- 解析后的任务卡
- 当前阶段摘要
- 待处理对象 id
- 最近关键失败与重试记录

不保留：

- 全量网页正文
- 大量重复日志
- 原始工具大返回

## 6.2 Compaction 机制

当 run 过长或上下文接近上限时：

1. 保留任务目标
2. 保留已完成阶段摘要
3. 保留尚未完成任务
4. 保留关键证据引用 id
5. 保留异常和回退状态

丢弃：

- 冗长中间解释
- 已处理完的大工具输出

## 6.3 Repository / Config as System of Record

借鉴 OpenAI harness 的思路：

- source registry
- SQL templates
- analysis thresholds
- report layout
- risk rules

都应放在 repo 中版本化，而不是藏在 prompt 或外部文档里。

---

## 7. 可信度与安全设计

## 7.1 可信度机制

每一条结论分成两类：

- **事实**
  - 可直接映射到 articles / snippets / SQL 统计
- **推断**
  - 由模型或规则在事实基础上归纳

报告中必须显式区分。

## 7.2 SQL 安全

动态 SQL 只允许：

- `SELECT`
- 白名单表
- 限制返回行数
- 超时控制

禁止：

- DDL
- DML
- 多语句
- 任意 schema 访问

## 7.3 Source 边界

MVP 明确来源白名单，不做开放式全网抓取。

原因：

- 降低噪音
- 保证结构稳定
- 更利于作品集叙述“受约束的 agent”

## 7.4 Human-in-the-loop

以下情况必须提示人工确认：

- 样本量过低
- 多来源结论冲突
- 动态 SQL 失败且需要改写
- 来源抓取严重不足
- 任务达到最大迭代

---

## 8. 最终用户体验设计

## 8.1 CLI

保留：

- `insight search`
- `insight compare`
- `insight trends`
- `insight report`

但统一走同一个 harness。

## 8.2 Web UI

工作台建议分 4 区：

1. Query 输入区
2. Plan / Progress 区
3. Charts & Findings 区
4. Evidence & Trace 区

这比只做一个聊天窗口更符合竞品分析工作流。

## 8.3 Plan Preview

在执行前给用户展示：

- 竞品对象
- 时间范围
- 分析维度
- 预计数据源
- 可能耗时
- 数据风险提示

这一步借鉴长任务代理的“先 plan 后 execution”。

## 8.4 Report 页面结构

最终建议固定为：

1. Executive Summary
2. Comparative Overview
3. Charts
4. Trend Signals
5. Evidence Cards
6. Risks & Uncertainty
7. Appendix / Sources

---

## 9. MVP 边界

最终的 MVP 范围维持收敛，不继续扩：

- 自然语言输入
- 3 类数据源
- SQLite 入库
- 情绪 / 声量 / 主题分析
- 趋势检测基础版
- HTML / Markdown 报告
- CLI
- 基础 Web UI
- trace 日志

MVP 不做：

- Slack / Feishu push
- 多租户协作
- 自动定时任务
- 插件市场
- 完整 computer use
- 大规模社交媒体实时抓取

---

## 10. 一句话架构总结

Insight Agent 的最终设计，不是“一个会自己到处搜的 AI”，而是：

**一个以结构化工作流为骨架、以受约束 Agent 为调度器、以 SQLite + SQL 分析为事实层、以证据绑定报告为输出层的竞品情报分析系统。**

这套设计取长补短后的核心判断是：

- 借 Anthropic 的“workflow vs agent”边界
- 借 OpenAI 的 harness / event / plan-first 思维
- 借 Cursor 的动态上下文与长任务体验
- 借 Claude Code 分析里的“基础设施复杂度大于模型逻辑”判断
- 最终落在一个更适合竞品情报而不是通用 coding agent 的系统形态上

---

## 11. 参考来源

- Anthropic, “Building effective agents”  
  https://www.anthropic.com/engineering/building-effective-agents
- Anthropic, “Effective context engineering for AI agents”  
  https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic, “How we built our multi-agent research system”  
  https://www.anthropic.com/engineering/multi-agent-research-system
- OpenAI, “Unrolling the Codex agent loop”  
  https://openai.com/index/unrolling-the-codex-agent-loop/
- OpenAI, “Harness engineering: leveraging Codex in an agent-first world”  
  https://openai.com/index/harness-engineering/
- OpenAI, “Unlocking the Codex harness: how we built the App Server”  
  https://openai.com/index/unlocking-the-codex-harness/
- OpenAI, “Inside OpenAI’s in-house data agent”  
  https://openai.com/index/inside-our-in-house-data-agent/
- OpenAI, “From model to agent: Equipping the Responses API with a computer environment”  
  https://openai.com/index/equip-responses-api-computer-environment/
- Cursor, “Dynamic context discovery”  
  https://cursor.com/blog/dynamic-context-discovery
- Cursor, “Expanding our long-running agents research preview”  
  https://cursor.com/blog/long-running-agents
- Cursor, “Cursor agents can now control their own computers”  
  https://cursor.com/blog/agent-computer-use
- VILA-Lab, “Dive into Claude Code”  
  https://github.com/VILA-Lab/Dive-into-Claude-Code
