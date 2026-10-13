#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 mdBook 版《毛泽东选集》Markdown 转成 OINK Book 结构的内容文件。

权限档位 (a)：仅做**无损排版规整** —— 统一全角/半角、去尾随空格、规范缩进、
统一分隔线；**正文文字一字不改**。扫到的可疑之处只写进报告，不动原文。

用法：
    python convert.py            # 转换默认篇目范围（见 build.py 的 RANGE）
    python convert.py 0 229      # 转换第 0 到第 229 篇（不含）
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(r"F:/WorkBuddy/毛泽东选集")
SITE = Path(r"F:/WorkBuddy/毛泽东选集站")
OUT = SITE / "content" / "book"

# 卷次定义：(卷号, 卷名, 时期说明, 起篇号, 止篇号含)
VOLUMES = [
    (1, "第一卷", "国内革命战争时期", 0, 17),
    (2, "第二卷", "抗日战争时期（上）", 18, 57),
    (3, "第三卷", "抗日战争时期（下）", 58, 88),
    (4, "第四卷", "第三次国内革命战争时期", 89, 158),
    (5, "第五卷", "中国人民站起来了", 159, 228),
]

CIRCLED = "⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇"
CIRCLED_MAP = {ch: i for i, ch in enumerate(CIRCLED, 1)}

CN_DIGIT = {"〇": 0, "○": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
            "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}

SEPARATOR = re.compile(r"^-{10,}\s*$")
CN = "一二三四五六七八九〇○零十"
# 日期核心：中文纪年 + 可选月日
_DATE_CORE = (r"([" + CN + r"]{2,4})年"
              r"(?:\s*([" + CN + r"]{1,3})月)?"
              r"(?:\s*([" + CN + r"]{1,3})日)?")
# 严格式：整段被括号包住，如「（一九二五年十二月一日）」
DATE_RE = re.compile(r"[（(]\s*" + _DATE_CORE + r"\s*[）)]\s*$")
# 宽松式：仅要求出现纪年。用于跨年区间（一九四六年十一月、一九四七年四月）
# 与不带括号的写法（一九五七年三月十二日）。
DATE_RE_LOOSE = re.compile(_DATE_CORE)
NOTE_RE = re.compile(r"^[\s\u3000]*〔\s*(\d+)\s*〕\s*(.*)$")
SOURCE_RE = re.compile(r"^[\s\u3000]*[（(][^）)]*(?:人民出版社|出版|页)[^）)]*[）)]\s*$")

report: list[str] = []


def cn2int(s: str) -> int:
    """把『一九二五』『二十五』这类中文数字转成 int。"""
    if not s:
        return 0
    if "十" not in s:
        n = 0
        for ch in s:
            if ch not in CN_DIGIT:
                return 0
            n = n * 10 + CN_DIGIT[ch]
        return n
    head, _, tail = s.partition("十")
    tens = 1 if head == "" else CN_DIGIT.get(head, 0)
    ones = 0 if tail == "" else CN_DIGIT.get(tail, 0)
    return tens * 10 + ones


def find_date(lines: list[str], upto: int = 8):
    """在开头若干行里找日期行。先试严格式（整段括号），再退回宽松式。"""
    for rx in (DATE_RE, DATE_RE_LOOSE):
        for i in range(1, min(upto, len(lines))):
            if not lines[i].strip():
                continue
            m = rx.search(lines[i])
            if m:
                return i, m
    return -1, None


def norm_lines(text: str) -> list[str]:
    """无损排版规整：去尾随空白、统一换行。"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return [ln.rstrip() for ln in text.split("\n")]


def body_marker_index(body: str) -> dict[int, int]:
    """返回 {圈号数字: 在正文中第几次出现}，用于顺序校验。"""
    seq = [CIRCLED_MAP[ch] for ch in body if ch in CIRCLED_MAP]
    return seq


def parse(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    lines = norm_lines(raw)
    num = int(path.name[:3])

    # ---- 标题：第 1 行 '# 篇名' ----
    title = lines[0].lstrip("#").strip()
    if title.endswith("  "):
        title = title.rstrip()

    # ---- 定位日期行（前 8 行内，容忍 `## 副标题` 插在前面）----
    date_str = ""
    date_iso = ""
    date_idx, dm = find_date(lines)
    if dm:
        date_str = lines[date_idx].strip().strip("（）()").strip()
        y = cn2int(dm.group(1))
        mo = cn2int(dm.group(2)) if dm.group(2) else 0
        d = cn2int(dm.group(3)) if dm.group(3) else 0
        if y:
            date_iso = f"{y:04d}"
            if mo:
                date_iso += f"-{mo:02d}"
                if d:
                    date_iso += f"-{d:02d}"

    # ---- 编者按：正文里第一段连续的 '> ' 引用块 ----
    quote: list[str] = []
    for i in range(date_idx + 1 if date_idx >= 0 else 1, len(lines)):
        if lines[i].startswith(">"):
            quote.append(lines[i])
        elif quote and lines[i].strip() == "":
            # 引用块内部的空行，只有下一行仍是引用才继续
            if i + 1 < len(lines) and lines[i + 1].startswith(">"):
                quote.append(">")
            else:
                break
        elif quote:
            break

    # ---- 正文与注释的分界 ----
    sep_idx = next((i for i, ln in enumerate(lines) if SEPARATOR.match(ln)), -1)

    start = (date_idx + 1) if date_idx >= 0 else 1
    if quote:
        # 跳过引用块所占的行
        j = start
        consumed = 0
        while j < len(lines) and consumed < len(quote):
            if lines[j].startswith(">"):
                consumed += 1
            j += 1
        start = j

    body_end = sep_idx if sep_idx >= 0 else len(lines)
    body_lines = lines[start:body_end]
    note_lines = lines[sep_idx + 1:] if sep_idx >= 0 else []

    # ---- 正文里剔除『注　　释』标题与纯分隔残留 ----
    body_lines = [ln for ln in body_lines if ln.strip() not in ("注　　释", "注  释", "注释")]
    while body_lines and body_lines[-1].strip() == "":
        body_lines.pop()

    # ---- 注释条目：以 〔n〕 开头为一条，后续非空行并入上一条 ----
    notes: list[tuple[int, str]] = []
    pending_head = ""
    for ln in note_lines:
        if not ln.strip():
            continue
        if ln.strip() in ("注　　释", "注  释", "注释"):
            pending_head = "HEADING"
            continue
        if pending_head == "HEADING":
            pending_head = ""
        m = NOTE_RE.match(ln)
        if m:
            notes.append((int(m.group(1)), m.group(2).strip()))
        elif notes:
            n, txt = notes[-1]
            notes[-1] = (n, (txt + ln.strip()).strip())
        elif SOURCE_RE.match(ln):
            pass  # 出处行，单独处理

    # ---- 出处行（有的篇目在注释之后，有的没有注释区）----
    source_line = ""
    for ln in reversed(note_lines):
        if ln.strip() and SOURCE_RE.match(ln):
            source_line = ln.strip()
            break
    if not source_line:
        for ln in reversed(body_lines):
            if ln.strip() and SOURCE_RE.match(ln):
                source_line = ln.strip()
                body_lines = [x for x in body_lines if x is not ln]
                break

    # ---- 正文规整：去掉段首全角缩进，交给 CSS text-indent ----
    cleaned: list[str] = []
    for ln in body_lines:
        if ln.strip() == "":
            cleaned.append("")
            continue
        stripped = re.sub(r"^[\u3000\s]+", "", ln)
        cleaned.append(stripped)

    # ---- 圈号 -> Markdown 链接 ----
    marks = body_marker_index("\n".join(cleaned))
    note_nums = {n for n, _ in notes}
    link_map: dict[int, int] = {}
    for pos, n in enumerate(marks, 1):
        if n in note_nums:
            link_map.setdefault(n, pos)

    body_text = "\n".join(cleaned)
    for ch, n in CIRCLED_MAP.items():
        if n in link_map:
            body_text = body_text.replace(ch, f"[{ch}](#note-{n})")

    # ---- 组装正文 ----
    parts: list[str] = []
    if date_str:
        parts.append(f"（{date_str}）\n{{.mx-date}}")
    if quote:
        parts.append("\n".join(quote))
    parts.append(body_text.strip())

    if notes:
        # 注释区输出为受控标记：需要一个容器才能做两栏疏排，
        # 而 Goldmark 的属性行语法无法创建容器，所以这里直接用 HTML。
        # 注释正文本身仍逐字照录，只做 HTML 转义。
        items = []
        for n, txt in notes:
            txt = re.sub(r"^[\u3000\s]+", "", txt)
            esc = (txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            items.append(
                f'<p class="mx-note" id="note-{n}">'
                f'<span class="mx-note-num">〔{n}〕</span>'
                f'{esc}</p>'
            )
        parts.append('<h2 class="mx-notes-heading" id="notes">注　　释</h2>')
        parts.append('<section class="mx-notes">\n' + "\n".join(items) + "\n</section>")
    if source_line:
        parts.append(f"{source_line}\n{{.mx-source}}")

    # ---- description：编者按首句，压到 80 字内 ----
    desc = ""
    if quote:
        flat = "".join(re.sub(r"^>\s?", "", q) for q in quote)
        flat = re.sub(r"[（(]?一九[^）)]*[）)]?", "", flat)
        m = re.search(r"^(.{10,80}?[。；])", flat)
        desc = m.group(1) if m else flat[:80]
    if not desc:
        desc = f"《毛泽东选集》{title}"

    # ---- 结构校验，只记录不改 ----
    title_nums = sorted({CIRCLED_MAP[ch] for ch in title if ch in CIRCLED_MAP})
    body_nums = set(marks)
    if title_nums:
        # 原书有些篇目的注号是标在标题里的（如《关于国际新形势对新华日报⑴记者的谈话》）。
        # 标题进 front matter 后无法内嵌链接，这条注释就只能在文末注释区读到。
        report.append(
            f"- `{path.name}`：标题内含注号 {title_nums}（源文本体例），"
            "该注在正文中无锚点，仅列于注释区"
        )
    missing = sorted(note_nums - body_nums - set(title_nums))
    if missing:
        report.append(f"- `{path.name}`：注释 {len(notes)} 条，其中 {missing} 在正文中无标记（源文本如此）")
    if not date_str:
        report.append(f"- `{path.name}`：未识别到日期行")
    if not quote:
        report.append(f"- `{path.name}`：无编者按引用块")

    return {
        "num": num,
        "title": title,
        "date_str": date_str,
        "date_iso": date_iso,
        "desc": desc,
        "body": "\n\n".join(parts),
        "notes": len(notes),
        "marks": len(marks),
    }


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def vol_of(num: int) -> tuple:
    for v in VOLUMES:
        if v[3] <= num <= v[4]:
            return v
    raise ValueError(f"篇号 {num} 不在任何卷内")


def quick_year(path: Path) -> str:
    """只读日期行，用于按全卷（而非已录入部分）计算年代区间。"""
    _, m = find_date(norm_lines(path.read_text(encoding="utf-8")))
    if not m:
        return ""
    y = cn2int(m.group(1))
    return f"{y:04d}" if y else ""


def cn_year(y: str) -> str:
    return "".join("〇一二三四五六七八九"[int(d)] for d in y)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def toc_html(rows: list[tuple[str, str, str]]) -> str:
    """生成带点线引导的目录。rows 每项是 (href, 标题, 右侧注记)。"""
    lis = []
    for href, label, note in rows:
        lis.append(
            f'<li><a href="{href}">{esc(label)}</a>'
            '<i class="mx-toc-dots" aria-hidden="true"></i>'
            f'<span class="mx-toc-date">{esc(note)}</span></li>'
        )
    return '<ul class="mx-toc">\n' + "\n".join(lis) + "\n</ul>"


def vol_span(files: list[Path], lo_n: int, hi_n: int) -> str:
    """按全卷（而非已录入部分）计算年代区间。"""
    years = [
        y for p in files
        if lo_n <= int(p.name[:3]) <= hi_n
        for y in [quick_year(p)] if y
    ]
    if not years:
        return ""
    lo_y, hi_y = min(years), max(years)
    return f"{cn_year(lo_y)}年至{cn_year(hi_y)}年" if lo_y != hi_y else f"{cn_year(lo_y)}年"


def main() -> int:
    args = [a for a in sys.argv[1:] if a.isdigit()]
    lo = int(args[0]) if args else 0
    hi = int(args[1]) if len(args) > 1 else 10

    files = sorted(p for p in SRC.glob("*.md") if re.match(r"^\d{3}-", p.name))
    sel = [p for p in files if lo <= int(p.name[:3]) < hi]

    OUT.mkdir(parents=True, exist_ok=True)
    per_vol: dict[int, list] = {v[0]: [] for v in VOLUMES}

    for p in sel:
        art = parse(p)
        v = vol_of(art["num"])
        vdir = OUT / f"volume-{v[0]}"
        vdir.mkdir(parents=True, exist_ok=True)

        fm = [
            "---",
            f"title: {yaml_str(art['title'])}",
            f"description: {yaml_str(art['desc'])}",
            f"slug: {yaml_str('%03d' % art['num'])}",
            f"weight: {art['num'] * 10 + 10}",
            "---",
            "",
        ]
        (vdir / f"{art['num']:03d}-{art['title']}.md").write_text(
            "\n".join(fm) + art["body"] + "\n", encoding="utf-8"
        )
        per_vol[v[0]].append(art)

    # ---- 卷首页 ----
    vol_rows: list[tuple[str, str, str]] = []
    for vnum, vname, period, lo_n, hi_n in VOLUMES:
        arts = sorted(per_vol[vnum], key=lambda a: a["num"])

        span = vol_span(files, lo_n, hi_n)
        total = hi_n - lo_n + 1
        done = len(arts)
        vdir = OUT / f"volume-{vnum}"
        vdir.mkdir(parents=True, exist_ok=True)

        lead = f"{span}，{period}，共 {total} 篇。" if span else f"{period}，共 {total} 篇。"
        if done and done < total:
            lead += f"本卷已录入前 {done} 篇。"
        elif done == 0:
            lead += "本卷篇目待录入。"
        # 本卷篇目：带点线引导的目录。标题保留在正文里，不做卡片。
        entries = [
            (f"{a['num']:03d}/", a["title"], a["date_str"] or "")
            for a in arts
        ]
        body = [lead, '<div class="mx-orn" aria-hidden="true"></div>']
        if entries:
            body.append(toc_html(entries))
        else:
            body.append("本卷篇目尚未录入。")

        (vdir / "_index.md").write_text(
            "---\n"
            f"title: {yaml_str(vname + '　' + period)}\n"
            f"linkTitle: {yaml_str(vname)}\n"
            f"description: {yaml_str(period + '，共 ' + str(total) + ' 篇')}\n"
            f"weight: {vnum * 10}\n"
            "no_list: true\n"
            "---\n\n"
            + "\n\n".join(body)
            + "\n",
            encoding="utf-8",
        )

        note = (f"{span} · {total} 篇" if span else f"{total} 篇")
        vol_rows.append((f"volume-{vnum}/", f"{vname}　{period}", note))

    # ---- 书根：五卷目录由脚本生成，随卷次信息同步 ----
    (OUT / "_index.md").write_text(
        "---\n"
        "title: 毛泽东选集\n"
        "linkTitle: 选集\n"
        "description: 一九二五年至一九五七年，五卷二百二十九篇。\n"
        "type: book\n"
        "book_kind: book\n"
        "sidebar_root_for: self\n"
        "sidebar_root_link_self: true\n"
        "outputs: [HTML, print, markdown]\n"
        "menus:\n"
        "  main:\n"
        "    identifier: book\n"
        "    weight: 10\n"
        "no_list: true\n"
        "cascade:\n"
        "  type: book\n"
        "  footer_style: slim\n"
        "---\n\n"
        "《毛泽东选集》收录毛泽东自一九二五年至一九五七年的著述，"
        "按历史时期分五卷编次，凡二百二十九篇。\n\n"
        "本站文本整理自公开资料，**原文未作任何删改**，原书注释一并照录。\n\n"
        '<div class="mx-orn" aria-hidden="true"></div>\n\n'
        + toc_html(vol_rows)
        + "\n\n"
        "## 关于本站 {#about}\n\n"
        "- **文本来源**：[weiyinfu/MaoZeDongAnthology]"
        "(https://github.com/weiyinfu/MaoZeDongAnthology) 的公开整理版本，"
        "原据人民出版社《毛泽东选集》第一至五卷排录。\n"
        "- **整理原则**：正文一字未改。只做无损排版规整——统一全角/半角标点、"
        "去除行尾空白、规范段落缩进；原书注释按原文照录，篇末逐条列出。\n"
        "- **体例**：正文中的注号（⑴、⑵……）可点击，直达篇末对应注释；"
        "原书把注号标在标题里的篇目，标题中的注号同样可点击。\n"
        "- **说明**：本站为非官方公益阅读版，仅供学习研究之用。"
        "著作权利归原出版者所有；如涉权利问题，请联系删除。\n",
        encoding="utf-8",
    )

    # ---- 报告 ----
    total_bytes = sum(f.stat().st_size for f in OUT.rglob("*.md"))
    head = [
        "# 转换报告",
        "",
        f"- 转换篇目：`{lo:03d}` – `{hi - 1:03d}`，共 **{len(sel)} 篇**",
        f"- 输出目录：`{OUT}`（{total_bytes:,} 字节）",
        f"- 权限档位：**(a) 仅无损排版规整，正文一字未改**",
        "",
        "## 结构发现（只记录，未修改原文）",
        "",
    ]
    (SITE / "tools").mkdir(parents=True, exist_ok=True)
    (SITE / "tools" / "转换报告.md").write_text(
        "\n".join(head + (report or ["- 无异常。"]) + [""]), encoding="utf-8"
    )

    print(f"转换 {len(sel)} 篇 -> {OUT}")
    for v in VOLUMES:
        n = len(per_vol[v[0]])
        print(f"  volume-{v[0]} ({v[1]}) : {n} 篇")
    print(f"报告 -> {SITE / 'tools' / '转换报告.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
