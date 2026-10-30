# Docker 学习文档计划

## 目标
在 docker/ 交付详细中文 Docker 学习文档 docker.md 和可离线阅读的 docker.html，包含原创示意图、前后端与 AI 实践、官方参考资料。

## 阶段
1. 资料与结构核对 — complete
2. 编写正文与完整案例 — complete
3. 绘制示意图并生成 HTML — complete
4. 内容、案例与页面验证 — complete

## 决策
- 面向具备前后端基础的 Docker 初学者，以 Linux 容器为主，解释 macOS/Windows 差异。
- HTML 从 Markdown 同源生成，图片内嵌；Markdown 引用 assets 中的图片。
- 本任务是已授权的学习资料创作，直接完成可审阅结果；无需设计审批。
- 不安装或更改 Docker 服务，不拉取大型模型；环境允许时只做必要验证。

## Next Step
已完成，向用户交付 HTML、Markdown 和案例文件。

## Errors Encountered
- 内置 web 工具两种调用均返回服务级 HTTP 404；改用 HTTPS 直接读取官方文档。

- 系统 Python 3.8 的旧 pip 安装依赖失败，改用应用提供的现代 Python 运行时。

- 页面检查脚本误将数字开头的合法 HTML id 当作未转义 CSS 选择器；改用 getElementById 定位。文档锚点本身无需修改。

- 图片检查在 lazy-loaded 图像完成解码前断言，复现证实等待后 8 图均加载正常；改为等待图片 complete 与 naturalWidth。
