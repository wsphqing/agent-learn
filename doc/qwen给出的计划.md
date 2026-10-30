

好的，既然不限语言，先给一个语言策略结论，再上详细计划。

## 语言策略（先定这个，后面不用纠结）

| 语言 | 定位 | 理由 |
|---|---|---|
| **Python** | 主力（学习/研究/原型） | agent 生态中心：所有论文实现、Hugging Face、评估框架、LangGraph 首发都在 Python。不学它你看不了 70% 的一手资料 |
| **TypeScript/JS** | 产品工程主力 | 你做 agent 产品时 TS 是最佳选择：Vercel AI SDK 生态最成熟，流式 UX、前端集成天然顺滑 |
| **Go** | 可选，按工作需求 | 适合高并发 agent 网关、MCP server、流式代理这类基础设施；不急着学 |
| **Java** | 可选，仅当公司栈是 Java | Spring AI / LangChain4j 可用但生态最薄；除非工作需要否则不投入 |

**结论：Python + TS 双修，Go/Java 按需。** 下面的计划里标注了每个练习用哪门语言。

**总时长：15 周，每周 10–15 小时。** 时间不够走文末的"6 周压缩版"。

---

## 第 0 周：环境搭建（半天就够）

- Python 3.12 + `uv`（包管理，比 pip 快）、Node 20+、Docker、Git
- 申请 1–2 个 API key（OpenAI 或 DeepSeek/Moonshot 等国产，便宜量大），再装 Ollama 跑个本地小模型
- 验收：Python 和 JS 各写一个"调通 API 并打印回复"的脚本

---

## 阶段 1：LLM 基础（第 1–2 周）

**第 1 周 —— API 与核心概念**
- 读：Anthropic《Building Effective Agents》（**读两遍**，这是整个方向的地图）
- 概念：token / context window / temperature / top_p / system prompt / few-shot
- 练习：
  - 🐍 Python：openai SDK 实现流式输出（`stream=True`）
  - 🟨 JS：用原生 `fetch` 手写 SSE 解析实现同样效果（不用 SDK，理解协议）
  - 实验：同一 prompt 用 temperature 0 / 0.7 / 1 各跑 5 次，观察稳定性差异
- 验收：能解释 token 和字符的区别；能给一段文档估算 token 数和单次调用成本

**第 2 周 —— 模型原理（够用即可）**
- 看：Karpathy《Intro to LLMs》（1 小时视频）+ 3Blue1Brown《But what is a GPT?》
- 读：Attention Is All You Need（理解级，不用推公式）；数学好可以跟 Karpathy《Let's build GPT from scratch》
- 练习：
  - Ollama 本地跑 qwen 7B，对比 API 大模型的回答差异（理解"模型规模"的实际影响）
  - 🐍 用 tiktoken 给一篇长文档精确计 token，算分页策略
- 验收：能解释"context window 为什么是 agent 记忆的核心瓶颈"

---

## 阶段 2：Prompt 工程 + 工具调用（第 3–4 周）

**第 3 周 —— Prompt 工程**
- 读：Anthropic 官方 Prompt Engineering Guide + OpenAI Prompting Guide
- 技术：zero/few-shot、CoT、JSON schema 结构化输出、输出格式约束
- 练习：
  - 做一个"电商评论摘要器"，prompt 迭代至少 5 版，**每版记录改动和效果**（这就是 prompt 工程的真实工作方式）
  - 用 API 原生 JSON mode 输出结构化数据，统计 100 次调用成功率
- 验收：能列出 5 种以上 prompt 技术并各给一个例子；结构化输出成功率 > 99%

**第 4 周 —— Function Calling（agent 的真正起点）**
- 读：**ReAct 论文（Yao et al. 2022）**——重点对比"模型自发用文本调工具" vs "API 原生 tool calling"
- 练习：
  - 🐍 写一个"旅行规划助手"：工具 = 查天气 / 查机票 / 算预算（数据 mock 即可）
  - 同一任务分别用 ① 手写作文 ReAct（我给你的模板）② 原生 tool calling 跑，记录成功率和格式错误率
  - 处理边界情况：模型想调一个不存在的工具、连续调同一工具
- 验收：能说清两种机制的区别；知道生产环境为什么优先原生 tool calling

---

## 阶段 3：Agent 核心模式（第 5–6 周）⭐ 最重要

**第 5 周 —— ReAct 深水区**
- 练习：
  - 跑通 ReAct 模板（🐍 和 🟨 各一份，体会两种语言生态的差异）
  - 读 **Reflexion 论文**（自我反思）
  - 给模板加"自我检查"：每次执行工具后问模型"这一步真的推进了解决方案吗？"，不行就换路线
  - 实现 Plan-and-Execute 模式（先出完整计划再执行），与 ReAct 在多步任务上对比（如"调研 3 家公司并写对比报告"）
- 验收：能说出两种模式各自的适用场景和成本差异；死循环被步数上限拦住

**第 6 周 —— Evaluator-Optimizer 与 workflow**
- 精读《Building Effective Agents》的 workflow 章节（prompt chaining / routing / parallelization / orchestrator-worker）
- 练习：
  - 写"代码审查 agent"：生成代码 → 评审员挑毛病 → 修复，最多 3 轮
  - **关键实验**：记录不同轮数下的质量 vs 成本曲线，找出"边际收益归零"的点
- 验收：能画出一张"什么任务该用什么 pattern"的决策表

---

## 阶段 4：RAG（第 7–8 周）

**第 7 周 —— 从零手写 RAG（不用任何框架）**
- 概念：chunking / embedding / 向量检索 / 混合检索（BM25 + 向量）
- 🐍 技术栈：sentence-transformers + chroma（本地轻量向量库）
- 练习：
  - 完整管线：文档加载 → 分块（~500 token，100 overlap）→ 向量化 → chroma 存储 → top-5 召回 → 生成
  - 语料用 10–20 份你自己的真实文档（公司制度、项目文档都行，效果感知更直接）
- 验收：能说出 RAG 三大失败模式（切分不当 / 召回失败 / 幻觉）及各自的解法

**第 8 周 —— RAG 进阶 + 第一次量化**
- 技术：rerank（bge-reranker）、元数据过滤、查询改写（multi-query）、HyDE
- 练习：
  - **建评估集**：20 个问题 + 标准答案，用 LLM-as-judge 打分
  - A/B 对比：加 rerank 前后、查询改写前后，记录 recall@5 和回答准确率变化
- 验收：你的 RAG 系统有一张带数字的效果表（这是和"demo 型 RAG"的本质区别）

---

## 阶段 5：记忆与状态（第 9 周）

- 读：**MemGPT 论文**（Letta，agent 分层记忆的开山之作）
- 概念：短期记忆（滑动窗口 / 对话摘要）、长期记忆（向量 + KV 混合）
- 练习：
  - 给聊天 agent 加长期记忆：自动抽取用户偏好存起来，新会话自动召回（手写，别直接用 mem0，先理解原理）
  - 状态持久化：agent 跑到一半存 checkpoint（JSON），崩溃后从断点恢复
- 验收：跨会话 agent 记得你的偏好；中断恢复正常工作

---

## 阶段 6：多 Agent + MCP（第 10–11 周）

**第 10 周 —— 多 agent**
- 读：AutoGen 论文 + **Anthropic《How we built our multi-agent research system》博客**（实战经验，必读）
- 练习：
  - 🐍 手写或 LangGraph 实现"研究团队"：orchestrator + 3 个子 agent（检索 / 综合 / 批判）
  - 任务：给一个研究问题，产出带引用和"批判性结论"的报告
- 验收：**能论证多 agent 何时真的优于单 agent**（多数任务单 agent 就够，多 agent 是成本放大器——这是最常见的认知陷阱）

**第 11 周 —— MCP（Model Context Protocol）**
- 读 MCP 规范 + 官方文档
- 练习：
  - 写一个 MCP server（暴露 2–3 个工具：文件搜索、查数据库等）
  - 分别用 Claude Desktop 和你自己的 agent 客户端接入
- 验收：能解释 MCP 解决的是 N 个 agent × M 个工具的集成爆炸问题；能独立写出一个 MCP server

---

## 阶段 7：评估体系（第 12 周）⭐ 最容易被跳过、最值钱

- 方法：LLM-as-judge（注意 judge 的自偏好偏差）、**轨迹评估**（不只对最终答案，对每一步工具调用打分）
- 指标：任务成功率 / 工具调用正确率 / 平均成本 / 延迟 / 幻觉率
- 工具：Langfuse（开源自部署）或 LangSmith
- 练习：
  - 给毕业项目写评估 harness：30 个真实问题，自动跑 + 自动打分
  - 对两个版本（不同 prompt / 不同模型）出对比报告
- 验收：你能用数字说"版本 B 在任务 X 上比 A 好 N%，成本低 M%"

---

## 阶段 8：生产化（第 13 周）

- 成本：prompt caching、模型路由（简单任务小模型 / 复杂任务大模型）
- 可靠性：重试、fallback、超时、断路器
- 安全：**prompt 注入防御**（任何外部输入——网页、文件、用户消息——都视为不可信）、输出校验、API key 只走服务端代理
- 流式 UX（🟨 Vercel AI SDK + React）：实时展示 agent 的思考/工具调用过程
- 练习：
  - Docker 化部署成 HTTP API，加限流、日志、全链路 trace
  - 压测 + 让它跑 24 小时无人值守
- 验收：每次 LLM 调用和工具调用都可追踪；有明确的成本上限

---

## 阶段 9：毕业项目（第 14–15 周）

三选一（选你工作最相关的）：

| 项目 | 考察点 |
|---|---|
| **客服 agent**：RAG 知识库 + 查订单工具 + 转人工兜底 | RAG、tool calling、评估 |
| **轻量 coding agent**：读仓库 → 理解 → 答问题 / 修简单 bug | ReAct、长上下文管理，可用 SWE-bench-lite 打分 |
| **研究助手**：multi-agent 调研管线（检索→精读→综合→批判） | 多 agent、编排、成本 |

**硬性交付**：
1. GitHub 仓库 + README（架构图 + 一键运行）
2. 评估报告（带数字的对比）
3. 一篇博客，讲**设计决策和权衡**（为什么选这个 pattern 不选那个）——这是面试和求职时最硬的东西

---

## 每日节奏（10–15 h/周）

- 周一/二：读材料、看视频（4h）
- 周三/四：动手写代码（6h）
- 周五：调试 + 写笔记/博客（3h）
- 周末：周复盘——本周验收标准过了没？不过就下周补，不推进

## 五个最贵的坑（提前打预防针）

1. **一上来就上 LangChain** —— 先徒手写出最小循环，框架才有意义
2. **不做评估就迭代** —— 无法度量的 agent 无法改进，你在盲飞
3. **不管成本** —— 10 步循环 = 10 倍 token，永远设步数上限和预算上限
4. **盲目多 agent** —— 先证明单 agent 做不到，再拆
5. **忽视 prompt 注入** —— agent 一旦能读网页/文件，外部内容就是攻击面

## 时间不够？6 周压缩版

第 1 周（LLM 基础 + prompt）→ 第 2 周（tool calling + ReAct 模板）→ 第 3 周（RAG 手写）→ 第 4 周（评估 harness）→ 第 5 周（生产化基础）→ 第 6 周（毕业项目）。砍掉多 agent、记忆、MCP 和论文精读——这些是"第二圈"再补的。

需要的话，下一步我可以把**任意一周**细化到天级任务清单（比如把"第 5 周 ReAct 深水区"拆成 5 天，每天 2 小时做什么、交付什么）。