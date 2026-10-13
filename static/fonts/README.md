# 毛泽东选集站 · 本地托管中文字体（自子集化 woff2）

本站正文使用**本地托管的开源中文字体子集**，不依赖任何第三方 CDN。
所有字体均按「《毛泽东选集》229 篇正文 + 站点 UI/标点」字符表子集化，**三份 woff2 合计 ≈ 1.99 MiB（2,089,580 字节），满足 ≤ 3.5 MB 硬约束**。

---

## 1. 产物清单

| 文件 | 用途 | 字节数 | 说明 |
|---|---|---:|---|
| `maoxuan-serif-400.woff2` | 正文（思源宋体 Regular） | 647,596 | wght=400 静态实例后子集 |
| `maoxuan-serif-600.woff2` | 标题/加粗（思源宋体 SemiBold） | 656,292 | wght=600 静态实例后子集 |
| `maoxuan-kai-400.woff2` | 卷名/引文点缀（霞鹜文楷 Lite） | 785,692 | Regular 子集 |
| `OFL-NotoSerifSC.txt` | 思源宋体授权原文 | 4,350 | SIL OFL 1.1 |
| `OFL-LXGWWenKai.txt` | 霞鹜文楷授权原文 | 5,176 | SIL OFL 1.1 |
| **合计（三份 woff2）** | | **2,089,580** | **≈ 1.99 MiB，≤ 3.5 MB ✅** |

---

## 2. 字符表

- 字符表文件：`F:/WorkBuddy/_tmp/fontchars.txt`（UTF-8，每行一个字符，码点升序）
- 生成方式：遍历 `F:/WorkBuddy/毛泽东选集/` 下全部 **229** 个形如 `NNN-标题.md` 的正文文件，提取全文所有字符，与需求给定的站点 UI/标点/数字/字母固定字符集合**合并去重**（排除 `\r`/`\n`），并补入普通空格 `U+0020`。
- **唯一码点数：3450**（最小 `U+0020`，最大 `U+FF3B`，全部落在 BMP 内）

三份字体对上述 3450 个码点均为 **100% 完整覆盖（3450 / 3450，无缺失）**，已通过 `fontTools` 读取 `cmap` 逐一比对验证。

---

## 3. 字体来源与原始体积

### 3.1 思源宋体（Noto Serif SC，可变字体）

- **来源 URL**：`https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifsc/NotoSerifSC%5Bwght%5D.ttf`
- 仓库：`google/fonts`（分支 `main`），字体为 **Noto Serif SC 可变字体**，`wght` 轴范围覆盖 200–900
- **原始体积：25,125,512 字节（≈ 23.96 MiB）**
- 授权：SIL Open Font License 1.1（见 `OFL-NotoSerifSC.txt`）

> 选用该可变字体并在本地实例化出 400/600 两个静态字重，避免额外下载两份静态字体；思路与需求文档一致。

### 3.2 霞鹜文楷 Lite（LXGW WenKai Lite）

- **来源 URL**：`https://raw.githubusercontent.com/lxgw/LxgwWenKai-Lite/main/fonts/TTF/LXGWWenKaiLite-Regular.ttf`
- 仓库：`lxgw/LxgwWenKai-Lite`（分支 `main`）
- **原始体积：13,949,472 字节（≈ 13.30 MiB）**
- 字形表结构：`glyf`（TrueType 轮廓，非 CFF），故未使用 `--desubroutinize`
- 授权：SIL Open Font License 1.1（见 `OFL-LXGWWenKai.txt`，含作者额外许可，允许为网页字体交付而子集化/转换为 WOFF/WOFF2）

---

## 4. 子集化流程与命令

工具链：系统 Python 3.9 + `fonttools 4.60.2` + `brotli 1.2.0`
（`C:/Users/V0yager/AppData/Local/Programs/Python/Python39/`）

### 步骤 1：将 Noto Serif SC 可变字体实例化为静态字重

```bash
python -m fontTools.varLib.instancer NotoSerifSC[wght].ttf wght=400 -o NotoSerifSC-400.ttf
python -m fontTools.varLib.instancer NotoSerifSC[wght].ttf wght=600 -o NotoSerifSC-600.ttf
```

（脚本实现：`F:/WorkBuddy/_tmp/instance_noto.py`，使用 `fontTools.varLib.instancer.instantiateVariableFont`）

### 步骤 2：按字符表子集化为 woff2

```bash
# 思源宋体 Regular
pyftsubset NotoSerifSC-400.ttf \
  --text-file=fontchars.txt --flavor=woff2 \
  --layout-features='*' --no-hinting --drop-tables+=DSIG \
  --output-file=maoxuan-serif-400.woff2

# 思源宋体 SemiBold
pyftsubset NotoSerifSC-600.ttf \
  --text-file=fontchars.txt --flavor=woff2 \
  --layout-features='*' --no-hinting --drop-tables+=DSIG \
  --output-file=maoxuan-serif-600.woff2

# 霞鹜文楷 Lite Regular
pyftsubset LXGWWenKaiLite-Regular.ttf \
  --text-file=fontchars.txt --flavor=woff2 \
  --layout-features='*' --no-hinting --drop-tables+=DSIG \
  --output-file=maoxuan-kai-400.woff2
```

---

## 5. 体积汇总

| 字体 | 原始体积 | 子集后 woff2 | 压缩比 | 子集内字符数 |
|---|---:|---:|---:|---:|
| 思源宋体 Regular | 25,125,512 B（可变） | 647,596 B | 2.6% | 3450 |
| 思源宋体 SemiBold | 同上（同源实例化） | 656,292 B | — | 3450 |
| 霞鹜文楷 Lite Regular | 13,949,472 B | 785,692 B | 5.6% | 3450 |
| **三份合计** | — | **2,089,580 B ≈ 1.99 MiB** | — | — |

> 注：思源宋体 400 与 600 源自同一份可变字体分别实例化，故「原始体积」按同一源文件计。

---

## 6. `@font-face` CSS

```css
/* 思源宋体 Regular —— 正文 */
@font-face {
  font-family: "Maoxuan Serif";
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/maoxuan-serif-400.woff2') format('woff2');
}

/* 思源宋体 SemiBold —— 标题 / 加粗 */
@font-face {
  font-family: "Maoxuan Serif";
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('/fonts/maoxuan-serif-600.woff2') format('woff2');
}

/* 霞鹜文楷 Lite Regular —— 卷名 / 引文点缀 */
@font-face {
  font-family: "Maoxuan Kai";
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/maoxuan-kai-400.woff2') format('woff2');
}
```

> 站点为根路径部署，URL 使用绝对路径 `/fonts/...`（与子路径无关）。

---

## 7. 授权与合规说明

- 两款字体均为 **SIL Open Font License 1.1**，允许自由使用、修改、再分发与网页嵌入；授权原文已随附（`OFL-NotoSerifSC.txt`、`OFL-LXGWWenKai.txt`）。
- **保留字体名（RFN）**：思源宋体的 RFN 为 `Noto`；本站 CSS 家族名改用 `Maoxuan Serif` / `Maoxuan Kai`，未使用 RFN，符合 OFL 对「修改版本」的命名要求。
- 霞鹜文楷的 OFL 附加许可明确允许**为网页字体交付而子集化并转换为 WOFF/WOFF2**（前提是不作为可安装桌面字体再分发）；本站仅作网页子集交付，符合该附加许可。
- 所有字体文件均**本地托管**于 `static/fonts/`，不引入外部 CDN 请求。
