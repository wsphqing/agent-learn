# React 学习文档生成工具

本目录包含 `react.md` / `react.html` 学习文档的生成与检查脚本，与 docker 知识点的工具链保持一致。

| 脚本 | 作用 |
| --- | --- |
| `make_figures.py` | 生成 `assets/` 下的 17 张原创 SVG 示意图（仅用 Python 标准库） |
| `render_figures.py` | 用 Chrome 无头模式把 SVG 渲染成同名 PNG，并输出缩略图联系页 |
| `build_document.py` | 从 `react.md` 生成内嵌配图的独立离线版 `react.html` |
| `check_document.py` | 对 `react.html` 做浏览器级 QA：章节链接、配图加载、代码复制、离线可用、移动端与打印样式 |

## 使用顺序

```bash
# 1. 生成示意图（需要 .work/venv，或系统 python3 安装 markdown + beautifulsoup4）
python3 tools/make_figures.py

# 2. 渲染 PNG（需要系统 python3，含 playwright + PIL，Chrome 位于默认路径）
python3 tools/render_figures.py

# 3. 从 Markdown 构建 HTML
python3 tools/build_document.py   # 用 .work/venv 中的 markdown/bs4

# 4. QA 检查
python3 tools/check_document.py   # 用系统 python3（playwright）
```

## 内容约定

- `react.md` 是唯一正文源；`react.html` 由它生成，不要手工编辑。
- 示意图编号对应章节：图 1～12 分别说明技术栈位置、组件树、JSX 编译、数据流、生命周期、虚拟 DOM、渲染流程、Hooks、Todo 实践、请求链路、路由、构建部署；图 13～17 深入实现原理：Fiber 架构、双缓存、Hooks 链表、合成事件、并发渲染与优先级调度。
- Markdown 引用 `assets/*.png`；HTML 内嵌对应 SVG（矢量、可放大），PNG 供 Markdown 与离线展示使用。
