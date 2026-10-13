# 毛泽东选集 · 阅读站

《毛泽东选集》第一至五卷全文的静态阅读站，凡 **229 篇**。

用 [Hugo](https://gohugo.io/) 与 [OINK](https://github.com/pgsty/oink) 主题构建，
**不需要 Node.js、npm 或任何前端工具链** —— 依赖只有 Hugo Extended 一个二进制。

## 特点

- **原文一字未改**。只做无损排版规整：统一全角/半角标点、去除行尾空白、规范段落缩进。
- **原书注释照录**。正文中的注号（⑴、⑵……）可点击，直达篇末对应注释；注释区宽屏两栏疏排。
- **五卷点线目录**。卷首页按纸本目录排法生成：篇名靠左、纪年靠右、中间点线引导。
- **档案风版式**。宣纸暖白底、深墨字、绛红点睛；正文首行缩进两字、两端对齐。
- **字体本地交付**。三份子集化 woff2 随站分发（合计约 2 MB），无外部 CDN，可离线构建与阅读。
- **面向机器可读**。每页输出同级 `.md`，站点输出 `llms.txt`，另可整书打印。

## 本地构建

需要 **Hugo Extended 0.160.1 或更新**（`hugo version` 中须出现 `extended`）。
无需 Go：主题已随仓库交付在 `themes/oink/`。

```bash
hugo server
```

打开 <http://localhost:1313/>。

生产构建（警告即失败，与 CI 同口径）：

```bash
hugo --cleanDestinationDir --gc --minify --environment production \
  --printPathWarnings --panicOnWarning
```

产物在 `public/`，可直接托管到 GitHub Pages、Cloudflare Pages、Nginx 或任何静态服务器。

## 目录结构

```text
content/
  _index.md              首页
  book/
    _index.md            书根：五卷目录与「关于本站」
    volume-1/_index.md   第一卷：全卷篇目（点线目录）
    volume-1/000-*.md    单篇正文（含题解、注释、出处）
    ...
    volume-5/
data/home/zh.yaml        首页各区块的数据
assets/css/maoxuan.css   站点视觉层：字体声明与 OINK paper 预设的覆写
layouts/_partials/       两处覆写：hooks/head-end.html 与 page-title.html
tools/convert.py         语料转换器：源 Markdown → Hugo 内容文件
tools/转换报告.md         转换中发现的结构问题清单（只记录，不改原文）
static/fonts/            子集化中文字体与 OFL 授权原文
themes/oink/             OINK v1.2.0（Apache-2.0）
```

## 重新生成内容

`tools/convert.py` 把来源语料（`NNN-篇名.md`）转成上表的内容结构：

```bash
python tools/convert.py 0 229     # 转换第 000–228 篇
```

它会一并生成书根与五个卷首页的目录，并把「正文一字未改、只记录不修改」的结构异常
写进 `tools/转换报告.md`。

## 数据来源与权利

- **文本来源**：[weiyinfu/MaoZeDongAnthology](https://github.com/weiyinfu/MaoZeDongAnthology)
  的公开整理版本，原据人民出版社《毛泽东选集》第一至五卷排录。
  正文与注释的著作权利归原出版者所有。
- **本站性质**：非官方公益阅读版，仅供学习研究之用。如涉权利问题，请联系删除。
- **代码部分**：本站的配置、样式、模板与转换脚本（`hugo.yaml`、`assets/`、`layouts/`、
  `tools/`、`data/`）以 MIT 授权发布，见 `LICENSE`。
- **主题**：`themes/oink/` 是 [OINK](https://github.com/pgsty/oink) v1.2.0，
  以 Apache-2.0 授权分发，其 `LICENSE`、`NOTICE` 与 `VENDOR.json` 均原样保留。
- **字体**：思源宋体（Noto Serif SC）与霞鹜文楷 Lite，均为 SIL OFL 1.1，
  授权原文见 `static/fonts/`。
