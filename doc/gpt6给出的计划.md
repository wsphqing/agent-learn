我把计划扩成 **20 周，每周约 10 小时**。你的前端基础可以直接用于做管理界面；学习时间主要投向后端的“正确性和架构”，然后在这个系统上做 Agent。技术栈建议固定为 **TypeScript、NestJS、PostgreSQL**；第 8 周以后再引入 Redis，Agent 初期直接使用模型 API，理解工具调用后再考虑 SDK 或编排框架。

贯穿项目是 **团队知识库与工单助手**。用户可以管理工单、上传文档；Agent 可以回答有来源的问题、查询工单，并在用户确认后创建工单。整个项目只有一个后端应用，按模块组织。

## 每周怎么学

每周固定节奏：**2 小时读官方文档／论文，5 小时实现，2 小时写测试和做实验，1 小时记录设计决策与问题**。每周末必须留下可运行的代码和一份简短记录；没有通过验收，就不要急着进入下一周。

| 周 | 要掌握的问题 | 具体任务与验收 |
|---|---|---|
| **1：HTTP 与 API** | 请求如何进入服务？状态码、校验和错误如何统一？ | 用 [NestJS 官方教程](https://docs.nestjs.com/first-steps)建立 API；实现工单创建、查询、更新。用 HTTP 客户端验证非法参数、找不到资源、服务异常三种情况。 |
| **2：关系建模** | 主键、外键、唯一约束分别保护什么？ | 建 `users`、`teams`、`memberships`、`tickets`、`documents` 表；画 ER 图。用原生 SQL 完成列表、筛选、分页，不依赖 ORM 自动生成查询。读 [PostgreSQL 教程](https://www.postgresql.org/docs/current/tutorial.html)。 |
| **3：查询与索引** | 为什么某个查询慢？索引有什么代价？ | 生成足量测试数据，对“按团队、状态、创建时间查工单”运行 [`EXPLAIN`](https://www.postgresql.org/docs/current/using-explain.html)；比较加索引前后的执行计划，并写下索引选择理由。 |
| **4：事务与并发** | 两人同时领取工单会怎样？ | 实现领取、转派、关闭工单。编写并发测试，证明同一工单不会被重复领取；模拟中途失败，证明事务回滚。读 [事务隔离](https://www.postgresql.org/docs/current/transaction-iso.html)。 |
| **5：模块边界** | Controller、业务服务、数据访问各负责什么？ | 按 `identity`、`tickets`、`documents` 拆 [NestJS 模块](https://docs.nestjs.com/modules)。画依赖图，规定跨模块只能通过公开服务调用；写一页“为什么这样分”的说明。 |
| **6：认证与授权** | “登录了”和“有权操作”有什么区别？ | 加团队成员角色；在每条读取、修改路径上检查团队归属。写测试证明 A 团队成员不能读取或修改 B 团队工单。参考 [OWASP API Security](https://owasp.org/projects/api-security-project)。 |
| **7：测试策略** | 哪些规则值得单测，哪些必须连数据库测？ | 为状态流转写单测；为事务、权限写数据库集成测试；为核心 HTTP 路径写接口测试。参考 [NestJS Testing](https://docs.nestjs.com/fundamentals/testing)。 |
| **8：异步任务** | 上传后解析失败或重复执行怎么办？ | 文档上传后异步解析；任务有 `pending/running/failed/done` 状态、重试次数和错误信息。重复处理同一文档不得产生重复内容。 |
| **9：缓存与一致性** | 什么值得缓存？数据更新后如何失效？ | 只缓存一个高频只读接口；记录命中率和延迟。修改底层数据后验证失效行为，写明为何其他接口暂不缓存。 |
| **10：可观测性** | 线上某次请求失败，怎样定位？ | 为请求和异步任务加入关联 ID、结构化日志、错误指标和 trace；能从一次失败请求追到数据库查询或后台任务。参考 [OpenTelemetry](https://opentelemetry.io/docs/)。 |
| **11：部署与故障** | 配置、数据库迁移、任务进程如何运行？ | 部署测试环境；完成健康检查、环境变量配置和迁移流程。演练数据库不可用、任务进程退出，记录用户看到什么以及如何恢复。参考 [Twelve-Factor App](https://www.12factor.net/)。 |
| **12：架构复盘** | 当前系统最难修改的部分在哪里？ | 提交架构图、模块职责表、三条关键业务不变量，以及一次真实重构。对照 [Fowler 企业应用模式](https://martinfowler.com/eaaCatalog/)审视数据访问和业务逻辑的边界。 |

**第 12 周验收**：不看框架文档，你应能说清“请求路径、数据所有权、事务边界、权限检查位置、后台任务失败处理、线上排障路径”。说不清的部分，就是下一轮要补的后端基础。

## Agent：从基线到可评估的系统

| 周 | 阅读与实验 | 具体交付 |
|---|---|---|
| **13：模型 API 基础** | 读 [OpenAI Docs 的 Agents 指南](https://developers.openai.com/api/docs/guides/agents)和[函数调用文档](https://developers.openai.com/api/docs/guides/function-calling)。区分普通生成、结构化输出、工具调用。 | 做一个只读“查询工单”工具；由后端执行工具并检查权限，保存完整调用轨迹。 |
| **14：RAG 基线** | 读 [RAG 原论文](https://arxiv.org/abs/2005.11401)。 | 将文档切分、索引、检索、生成串起来；回答附文档来源。建立 30 个固定问题，包含可回答与不可回答两类。 |
| **15：检索实验** | 读 [Lost in the Middle](https://arxiv.org/abs/2307.03172)与 [Self-RAG](https://arxiv.org/abs/2310.11511)。 | 比较两种切分大小、两种召回数量、两种上下文排序。记录检索命中率、答案正确率和无依据回答数，保留失败样本。 |
| **16：工具 Agent** | 读 [ReAct](https://arxiv.org/abs/2210.03629)，对照[作者代码](https://github.com/ysymyth/ReAct)；再读 [Toolformer](https://arxiv.org/abs/2302.04761)。 | 加查文档、查工单、创建工单三个工具。每个工具定义输入模式、权限、超时和错误响应；限制最大调用步数。 |
| **17：状态与恢复** | 读 [Reflexion](https://arxiv.org/abs/2303.11366)，重点看失败反馈怎样影响后续尝试。 | 模拟工具超时、无结果、参数错误；Agent 要么恢复，要么明确说明失败，不能假装完成。此时再判断是否需要 [Agents SDK 示例](https://github.com/openai/openai-agents-js/tree/main/examples)。 |
| **18：安全边界** | 读 [OWASP LLM Top 10](https://genai.owasp.org/llm-top-10/)。 | 在上传文档中植入“忽略指令、读取其他团队数据”等恶意内容。验证模型输出不能绕过服务端权限；创建工单必须经过用户确认。 |
| **19：系统评估** | 读 [τ-bench](https://arxiv.org/abs/2406.12045)及其[项目代码](https://github.com/sierra-research/tau-bench)，再看 [OpenAI Docs 的 Agent Evals](https://developers.openai.com/api/docs/guides/agent-evals)。 | 建立固定的 50 个案例，自动记录任务完成率、错误工具调用、耗时和成本；每次改提示词或检索策略都重新运行。 |
| **20：交付与复盘** | 回读前面的失败案例，而不是继续加新框架。 | 发布可演示版本、架构图、评估报告、运行说明；展示至少 5 个失败案例、原因和改进前后结果。 |

那 **50 个评估案例**可以这样分：15 个正常知识问答、10 个“文档没有答案”、10 个跨团队权限请求、10 个多步骤工单任务、5 个提示注入或工具故障。不要只用“回答看起来不错”判断效果；至少分别看**检索是否找到证据、最终回答是否有依据、工具是否执行正确、是否发生越权或错误写入**。

读论文时不要求复现完整训练过程。每篇只产出一页笔记：研究要解决的失败场景、核心机制、实验设置、结论的适用范围，以及**你在项目中做的一个小实验**。这样到第 20 周，你会同时有一套可解释的后端架构和一份有实验数据支撑的 Agent 项目，而不只是一个能聊天的演示页面。