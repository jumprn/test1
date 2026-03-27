from __future__ import annotations

import math
from dataclasses import dataclass
from html import escape
from pathlib import Path


@dataclass(frozen=True)
class MemberStat:
    name: str
    ai_lines: int
    total_lines: int
    ratio_percent: float


DATA = [
    MemberStat("李建科", 21, 21, 100.00),
    MemberStat("朱庆辉", 11, 11, 100.00),
    MemberStat("陈航", 356, 391, 91.05),
    MemberStat("肖恒", 287, 460, 62.39),
    MemberStat("焦露清", 2419, 4976, 48.61),
    MemberStat("林志成", 223, 539, 41.37),
    MemberStat("陈龙", 2917, 17706, 16.47),
    MemberStat("丁永成", 66, 430, 15.35),
    MemberStat("袁帆", 1052, 9336, 11.27),
    MemberStat("雷加伟", 1038, 26878, 3.86),
    MemberStat("赵毅", 23, 669, 3.44),
    MemberStat("梁正勇", 10, 324, 3.09),
    MemberStat("王学文", 631, 710260, 0.09),
    MemberStat("许佳行", 11, 28718, 0.04),
    MemberStat("方伟", 0, 8681, 0.00),
    MemberStat("敬江涛", 0, 50, 0.00),
    MemberStat("刘晓恒", 0, 11972, 0.00),
    MemberStat("孙泓翔", 0, 61708, 0.00),
    MemberStat("唐武斌", 0, 2337, 0.00),
    MemberStat("席宏文", 0, 10, 0.00),
    MemberStat("邢佳佳", 0, 8969, 0.00),
    MemberStat("徐枫", 0, 5217, 0.00),
    MemberStat("张思源", 0, 22, 0.00),
    MemberStat("张长英", 0, 790, 0.00),
    MemberStat("章建森", 0, 8096, 0.00),
    MemberStat("周文彬", 0, 58401, 0.00),
]

TITLE = "成员 AI 编码覆盖率与提交行数对比"
SUBTITLE = "说明：柱状图采用断轴显示（0-30,000 与 50,000-710,260），因为 30,000-50,000 区间无数据，可在保证准确性的同时提升可读性。"

BG = "#FFFFFF"
TEXT = "#1F2937"
SUBTEXT = "#6B7280"
GRID = "#E5E7EB"
ROW_BG = "#F8FAFC"
AI_BAR = "#3B82F6"
TOTAL_BAR = "#F87171"
RATIO_LINE = "#65A30D"
RATIO_DOT = "#84CC16"
AXIS = "#94A3B8"


def fmt_int(value: int) -> str:
    return f"{value:,}"


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def validate_data() -> None:
    for stat in DATA:
        if stat.total_lines == 0:
            expected = 0.0
        else:
            expected = round(stat.ai_lines / stat.total_lines * 100, 2)
        if not math.isclose(expected, stat.ratio_percent, abs_tol=0.01):
            raise ValueError(
                f"Ratio mismatch for {stat.name}: "
                f"expected {expected:.2f}%, got {stat.ratio_percent:.2f}%"
            )


def svg_text(x: float, y: float, text: str, **attrs: str) -> str:
    merged = {"x": f"{x:.2f}", "y": f"{y:.2f}"}
    merged.update(attrs)
    attr_text = " ".join(f'{svg_attr_name(k)}="{escape(v)}"' for k, v in merged.items())
    return f"<text {attr_text}>{escape(text)}</text>"


def svg_line(x1: float, y1: float, x2: float, y2: float, **attrs: str) -> str:
    merged = {
        "x1": f"{x1:.2f}",
        "y1": f"{y1:.2f}",
        "x2": f"{x2:.2f}",
        "y2": f"{y2:.2f}",
    }
    merged.update(attrs)
    attr_text = " ".join(f'{svg_attr_name(k)}="{escape(v)}"' for k, v in merged.items())
    return f"<line {attr_text} />"


def svg_rect(x: float, y: float, width: float, height: float, **attrs: str) -> str:
    merged = {
        "x": f"{x:.2f}",
        "y": f"{y:.2f}",
        "width": f"{max(width, 0):.2f}",
        "height": f"{max(height, 0):.2f}",
    }
    merged.update(attrs)
    attr_text = " ".join(f'{svg_attr_name(k)}="{escape(v)}"' for k, v in merged.items())
    return f"<rect {attr_text} />"


def svg_circle(cx: float, cy: float, r: float, **attrs: str) -> str:
    merged = {"cx": f"{cx:.2f}", "cy": f"{cy:.2f}", "r": f"{r:.2f}"}
    merged.update(attrs)
    attr_text = " ".join(f'{svg_attr_name(k)}="{escape(v)}"' for k, v in merged.items())
    return f"<circle {attr_text} />"


def svg_path(d: str, **attrs: str) -> str:
    merged = {"d": d}
    merged.update(attrs)
    attr_text = " ".join(f'{svg_attr_name(k)}="{escape(v)}"' for k, v in merged.items())
    return f"<path {attr_text} />"


def svg_attr_name(name: str) -> str:
    if name.endswith("_"):
        name = name[:-1]
    return name.replace("_", "-")


def build_chart() -> str:
    validate_data()

    width = 1820
    left_margin = 210
    right_margin = 360
    top_margin = 130
    bottom_margin = 130
    row_gap = 32
    plot_height = row_gap * len(DATA)
    height = top_margin + plot_height + bottom_margin

    plot_x0 = left_margin
    plot_x1 = width - right_margin
    plot_width = plot_x1 - plot_x0
    plot_y0 = top_margin
    plot_y1 = top_margin + plot_height

    left_segment_width = 680
    gap_width = 36
    right_segment_width = plot_width - left_segment_width - gap_width
    left_segment_end = plot_x0 + left_segment_width
    right_segment_start = left_segment_end + gap_width

    count_low_max = 30000
    count_high_min = 50000
    count_max = max(item.total_lines for item in DATA)

    def count_to_x(value: int) -> float:
        if value <= 0:
            return plot_x0
        if value <= count_low_max:
            return plot_x0 + left_segment_width * (value / count_low_max)
        if value < count_high_min:
            return left_segment_end + gap_width * (
                (value - count_low_max) / (count_high_min - count_low_max)
            )
        return right_segment_start + right_segment_width * (
            (value - count_high_min) / (count_max - count_high_min)
        )

    def ratio_to_x(value: float) -> float:
        return plot_x0 + plot_width * (value / 100.0)

    def y_center(index: int) -> float:
        return plot_y0 + index * row_gap + row_gap / 2

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(TITLE)}">'
    )
    parts.append(
        "<style>"
        "text{font-family:'Noto Sans CJK SC','Microsoft YaHei','PingFang SC','Heiti SC',sans-serif;}"
        ".title{font-size:28px;font-weight:700;fill:#111827;}"
        ".subtitle{font-size:14px;fill:#6B7280;}"
        ".axis-label{font-size:14px;font-weight:600;fill:#475569;}"
        ".axis-tick{font-size:12px;fill:#64748B;}"
        ".name{font-size:14px;fill:#111827;}"
        ".value-ai{font-size:11px;fill:#2563EB;}"
        ".value-total{font-size:11px;fill:#B91C1C;}"
        ".value-ratio{font-size:11px;font-weight:600;fill:#4D7C0F;}"
        ".legend-title{font-size:14px;font-weight:700;fill:#111827;}"
        ".legend-text{font-size:13px;fill:#334155;}"
        "</style>"
    )
    parts.append(svg_rect(0, 0, width, height, fill=BG))

    parts.append(svg_text(plot_x0, 48, TITLE, class_="title"))
    parts.append(svg_text(plot_x0, 75, SUBTITLE, class_="subtitle"))

    for index, stat in enumerate(DATA):
        if index % 2 == 0:
            parts.append(
                svg_rect(
                    plot_x0 - 15,
                    plot_y0 + index * row_gap,
                    plot_width + 30,
                    row_gap,
                    fill=ROW_BG,
                )
            )

    axis_bottom_y = plot_y1 + 8
    axis_top_y = plot_y0 - 8

    parts.append(svg_line(plot_x0, axis_bottom_y, left_segment_end, axis_bottom_y, stroke=AXIS, stroke_width="1.5"))
    parts.append(svg_line(right_segment_start, axis_bottom_y, plot_x1, axis_bottom_y, stroke=AXIS, stroke_width="1.5"))
    parts.append(svg_line(plot_x0, axis_top_y, plot_x1, axis_top_y, stroke=AXIS, stroke_width="1.5"))

    left_ticks = [0, 5000, 10000, 20000, 30000]
    right_ticks = [50000, 100000, 300000, 500000, count_max]
    pct_ticks = list(range(0, 101, 10))

    for tick in left_ticks:
        x = plot_x0 + left_segment_width * (tick / count_low_max)
        parts.append(svg_line(x, plot_y0, x, plot_y1, stroke=GRID, stroke_width="1"))
        parts.append(svg_line(x, axis_bottom_y, x, axis_bottom_y + 7, stroke=AXIS, stroke_width="1"))
        parts.append(svg_text(x, axis_bottom_y + 24, fmt_int(tick), class_="axis-tick", text_anchor="middle"))

    for tick in right_ticks:
        x = right_segment_start + right_segment_width * ((tick - count_high_min) / (count_max - count_high_min))
        parts.append(svg_line(x, plot_y0, x, plot_y1, stroke=GRID, stroke_width="1"))
        parts.append(svg_line(x, axis_bottom_y, x, axis_bottom_y + 7, stroke=AXIS, stroke_width="1"))
        parts.append(svg_text(x, axis_bottom_y + 24, fmt_int(tick), class_="axis-tick", text_anchor="middle"))

    for tick in pct_ticks:
        x = ratio_to_x(tick)
        parts.append(svg_line(x, axis_top_y - 7, x, axis_top_y, stroke=AXIS, stroke_width="1"))
        parts.append(svg_text(x, axis_top_y - 12, f"{tick}%", class_="axis-tick", text_anchor="middle"))

    for marker_x in (left_segment_end - 8, left_segment_end + 8):
        parts.append(svg_line(marker_x, axis_bottom_y - 8, marker_x + 6, axis_bottom_y + 8, stroke=SUBTEXT, stroke_width="2"))
    for marker_x in (right_segment_start - 14, right_segment_start + 2):
        parts.append(svg_line(marker_x, axis_bottom_y - 8, marker_x + 6, axis_bottom_y + 8, stroke=SUBTEXT, stroke_width="2"))

    parts.append(svg_text(plot_x0, plot_y0 - 42, "AI 代码覆盖率（上方横轴）", class_="axis-label"))
    parts.append(svg_text(plot_x0, axis_bottom_y + 52, "代码行数（下方断轴）", class_="axis-label"))

    line_points: list[tuple[float, float, float]] = []

    for index, stat in enumerate(DATA):
        yc = y_center(index)
        name_x = plot_x0 - 22
        parts.append(svg_text(name_x, yc + 5, stat.name, class_="name", text_anchor="end"))

        ai_y = yc - 9
        total_y = yc + 1
        bar_h = 8

        total_end = count_to_x(stat.total_lines)
        ai_end = count_to_x(stat.ai_lines)

        if stat.total_lines <= count_low_max:
            parts.append(svg_rect(plot_x0, total_y, total_end - plot_x0, bar_h, rx="3", fill=TOTAL_BAR, opacity="0.88"))
        elif stat.total_lines < count_high_min:
            parts.append(svg_rect(plot_x0, total_y, left_segment_width, bar_h, rx="3", fill=TOTAL_BAR, opacity="0.88"))
        else:
            parts.append(svg_rect(plot_x0, total_y, left_segment_width, bar_h, rx="3", fill=TOTAL_BAR, opacity="0.88"))
            parts.append(svg_rect(right_segment_start, total_y, total_end - right_segment_start, bar_h, rx="3", fill=TOTAL_BAR, opacity="0.88"))

        if stat.ai_lines <= count_low_max:
            parts.append(svg_rect(plot_x0, ai_y, ai_end - plot_x0, bar_h, rx="3", fill=AI_BAR, opacity="0.92"))
        elif stat.ai_lines < count_high_min:
            parts.append(svg_rect(plot_x0, ai_y, left_segment_width, bar_h, rx="3", fill=AI_BAR, opacity="0.92"))
        else:
            parts.append(svg_rect(plot_x0, ai_y, left_segment_width, bar_h, rx="3", fill=AI_BAR, opacity="0.92"))
            parts.append(svg_rect(right_segment_start, ai_y, ai_end - right_segment_start, bar_h, rx="3", fill=AI_BAR, opacity="0.92"))

        total_label_x = min(total_end + 8, plot_x1 - 6)
        total_anchor = "start" if total_end < plot_x1 - 90 else "end"
        if total_anchor == "end":
            total_label_x = plot_x1 - 6
        parts.append(
            svg_text(
                total_label_x,
                total_y + bar_h - 0.5,
                fmt_int(stat.total_lines),
                class_="value-total",
                text_anchor=total_anchor,
            )
        )

        ai_label_x = min(ai_end + 8, plot_x1 - 6)
        ai_anchor = "start" if ai_end < plot_x1 - 90 else "end"
        if ai_anchor == "end":
            ai_label_x = plot_x1 - 6
        parts.append(
            svg_text(
                ai_label_x,
                ai_y + bar_h - 0.5,
                fmt_int(stat.ai_lines),
                class_="value-ai",
                text_anchor=ai_anchor,
            )
        )

        line_points.append((ratio_to_x(stat.ratio_percent), yc, stat.ratio_percent))

    path_d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y, _ in line_points)
    parts.append(svg_path(path_d, fill="none", stroke="#FFFFFF", stroke_width="6", stroke_linejoin="round", stroke_linecap="round", opacity="0.7"))
    parts.append(svg_path(path_d, fill="none", stroke=RATIO_LINE, stroke_width="3.5", stroke_linejoin="round", stroke_linecap="round"))

    for x, y, ratio in line_points:
        parts.append(svg_circle(x, y, 4.5, fill=RATIO_DOT, stroke="#FFFFFF", stroke_width="1.5"))
        label_anchor = "start"
        label_x = x + 8
        if ratio >= 92:
            label_anchor = "end"
            label_x = x - 8
        parts.append(svg_text(label_x, y - 10, fmt_pct(ratio), class_="value-ratio", text_anchor=label_anchor))

    legend_x = plot_x1 + 55
    legend_y = plot_y1 - 120
    parts.append(svg_rect(legend_x - 20, legend_y - 30, 250, 110, rx="12", fill="#FFFFFF", stroke=GRID, stroke_width="1.2"))
    parts.append(svg_text(legend_x, legend_y - 4, "图例", class_="legend-title"))

    parts.append(svg_rect(legend_x, legend_y + 16, 28, 10, rx="3", fill=AI_BAR, opacity="0.92"))
    parts.append(svg_text(legend_x + 40, legend_y + 25, "AI 代码行数", class_="legend-text"))

    parts.append(svg_rect(legend_x, legend_y + 44, 28, 10, rx="3", fill=TOTAL_BAR, opacity="0.88"))
    parts.append(svg_text(legend_x + 40, legend_y + 53, "总提交行数", class_="legend-text"))

    parts.append(svg_line(legend_x, legend_y + 74, legend_x + 28, legend_y + 74, stroke=RATIO_LINE, stroke_width="3.5"))
    parts.append(svg_circle(legend_x + 14, legend_y + 74, 4.5, fill=RATIO_DOT, stroke="#FFFFFF", stroke_width="1.5"))
    parts.append(svg_text(legend_x + 40, legend_y + 79, "AI 代码覆盖率", class_="legend-text"))

    parts.append(svg_text(plot_x1 - 2, height - 26, "数据来源：图1原始表格逐行转录，共 26 名成员", class_="subtitle", text_anchor="end"))
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "ai_code_usage_chart.svg"
    output_path.write_text(build_chart(), encoding="utf-8")
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
