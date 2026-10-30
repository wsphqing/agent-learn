# 文档维护

`docker.md` 是正文源文件。修改后可以重新生成单文件 HTML：

```bash
# 从 docker/ 目录执行，建议使用自己的 Python 虚拟环境
python3 -m pip install -r tools/requirements.txt
python3 tools/build_document.py
```

生成器会将 `assets/` 中与 PNG 同名的 SVG 内嵌到 HTML；HTML 阅读不需要 Python、网络或任何额外安装。

`make_figures.py` 使用 Python 标准库生成 8 张 SVG。Markdown 使用同名 PNG，以兼容常见 Markdown 阅读器。修改 SVG 后需要重新导出同名 PNG（本次用 Chrome / Playwright 按 1.5 倍尺寸导出），再生成 HTML。

实践代码在 `examples/`。修改代码时需要同步更新 Markdown 中的对应代码块；交付版本已经核对一致。
