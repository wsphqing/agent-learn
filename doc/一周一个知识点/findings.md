# 核对记录

- 工作目录为空，无现有文档或 AGENTS.md 约束。
- 本机有 Python、Node、Docker CLI、Chrome 和 Playwright；Python 暂无 Markdown 转换器。
- 用户需要介绍、使用、原理、案例，HTML 与 Markdown 两版，带示意图。

- Docker CLI 28.5.2 / Compose v2.40.3；当前 orbstack daemon 不可连接，容器端到端实验需标为未执行。
- Docker 官方文档确认：Engine 29+ 全新安装默认 containerd image store / overlayfs snapshotter，升级安装可能沿用 overlay2。
- Compose secrets 使用文件挂载；BuildKit secrets 不应由 ARG/ENV 代替。
- 已获取多数 Docker/Ollama/OCI 官方来源；部分 HTTPS 连接失败，使用 curl 重试。

- 已确认 psycopg 3.2.10 官方 PyPI 版本存在；PostgreSQL 17 与 18 的数据目录差异、POSTGRES_USER 超级用户语义，以及 Nginx 变量 proxy_pass 解析行为均有官方来源支持。
- 文档覆盖 15 章、47 个代码块、31 个 Bash 块、8 张配图、3 个项目案例。
- HTML 已通过真实 Chrome 桌面/390px 窄屏、离线、复制、导航、图像放大与打印样式检查；无页面 JS 错误。
- 所有案例端到端运行输出为预期，不对未启动的 daemon 声称运行通过。
