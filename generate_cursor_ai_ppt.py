from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.util import Inches, Pt


SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

BG = RGBColor(11, 16, 32)
PANEL = RGBColor(18, 28, 56)
PANEL_ALT = RGBColor(22, 35, 70)
TEXT = RGBColor(238, 242, 255)
MUTED = RGBColor(184, 193, 230)
ACCENT = RGBColor(110, 168, 254)
ACCENT_2 = RGBColor(126, 240, 194)
WARNING = RGBColor(255, 215, 110)
DANGER = RGBColor(255, 138, 138)


def set_bg(slide, color=BG):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_header(slide, tag, page):
    tag_box = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(0.45),
        Inches(0.28),
        Inches(2.2),
        Inches(0.4),
    )
    tag_box.fill.solid()
    tag_box.fill.fore_color.rgb = PANEL_ALT
    tag_box.line.color.rgb = ACCENT
    text_frame = tag_box.text_frame
    text_frame.clear()
    p = text_frame.paragraphs[0]
    r = p.add_run()
    r.text = tag
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = TEXT

    page_box = slide.shapes.add_textbox(Inches(12.25), Inches(0.28), Inches(0.6), Inches(0.3))
    tf = page_box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    r = p.add_run()
    r.text = page
    r.font.size = Pt(12)
    r.font.color.rgb = MUTED


def add_footer(slide, left, right):
    line = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(0.45),
        Inches(7.0),
        Inches(12.4),
        Inches(0.02),
    )
    line.fill.solid()
    line.fill.fore_color.rgb = PANEL_ALT
    line.line.fill.background()

    left_box = slide.shapes.add_textbox(Inches(0.45), Inches(7.05), Inches(8.5), Inches(0.28))
    tf = left_box.text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = left
    r.font.size = Pt(11)
    r.font.color.rgb = MUTED

    right_box = slide.shapes.add_textbox(Inches(11.2), Inches(7.05), Inches(1.7), Inches(0.28))
    tf = right_box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    r = p.add_run()
    r.text = right
    r.font.size = Pt(11)
    r.font.color.rgb = TEXT
    r.font.bold = True


def add_title(slide, title, subtitle=None):
    box = slide.shapes.add_textbox(Inches(0.65), Inches(0.92), Inches(11.8), Inches(1.4))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    r.font.size = Pt(26)
    r.font.bold = True
    r.font.color.rgb = TEXT
    if subtitle:
      p2 = tf.add_paragraph()
      p2.space_before = Pt(8)
      r2 = p2.add_run()
      r2.text = subtitle
      r2.font.size = Pt(14)
      r2.font.bold = True
      r2.font.color.rgb = ACCENT_2


def add_text_panel(slide, x, y, w, h, title, body_lines, accent=ACCENT):
    panel = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, y, w, h)
    panel.fill.solid()
    panel.fill.fore_color.rgb = PANEL
    panel.line.color.rgb = accent

    title_box = slide.shapes.add_textbox(x + Inches(0.18), y + Inches(0.16), w - Inches(0.36), Inches(0.32))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = accent

    body_box = slide.shapes.add_textbox(x + Inches(0.18), y + Inches(0.52), w - Inches(0.36), h - Inches(0.66))
    tf = body_box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    for idx, line in enumerate(body_lines):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.level = 0
        p.bullet = True
        p.space_after = Pt(5)
        r = p.add_run()
        r.text = line
        r.font.size = Pt(17)
        r.font.color.rgb = MUTED


def add_quote(slide, text, x=Inches(0.65), y=Inches(5.65), w=Inches(12.0), h=Inches(1.0)):
    panel = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, y, w, h)
    panel.fill.solid()
    panel.fill.fore_color.rgb = PANEL_ALT
    panel.line.color.rgb = ACCENT
    box = slide.shapes.add_textbox(x + Inches(0.22), y + Inches(0.14), w - Inches(0.44), h - Inches(0.28))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.size = Pt(18)
    r.font.color.rgb = TEXT
    r.font.bold = True


def add_title_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "内部分享 / AI 编程实践", "01")

    title_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.15), Inches(7.8), Inches(2.0))
    tf = title_box.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "Cursor 场景下的 AI 编程最佳实践"
    r1.font.size = Pt(18)
    r1.font.bold = True
    r1.font.color.rgb = ACCENT_2

    p2 = tf.add_paragraph()
    p2.space_before = Pt(14)
    r2 = p2.add_run()
    r2.text = "把 AI 从“补全工具”升级为\n可协作的研发搭档"
    r2.font.size = Pt(28)
    r2.font.bold = True
    r2.font.color.rgb = TEXT

    p3 = tf.add_paragraph()
    p3.space_before = Pt(14)
    r3 = p3.add_run()
    r3.text = (
        "目标：帮助团队形成一套能稳定产出、可控风险、可复制推广的 AI 编程工作方式，"
        "而不是只停留在“偶尔让 AI 帮我写点代码”。"
    )
    r3.font.size = Pt(16)
    r3.font.color.rgb = MUTED

    pills = [
        "需求澄清",
        "代码探索",
        "实现与重构",
        "测试与 Review",
        "团队规范",
    ]
    x = 0.75
    for pill in pills:
        width = 1.35 if len(pill) <= 4 else 1.75
        shape = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
            Inches(x),
            Inches(4.65),
            Inches(width),
            Inches(0.42),
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = PANEL_ALT
        shape.line.color.rgb = ACCENT_2
        tf = shape.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = pill
        r.font.size = Pt(12)
        r.font.color.rgb = TEXT
        x += width + 0.18

    quote = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(8.75),
        Inches(1.45),
        Inches(3.75),
        Inches(3.0),
    )
    quote.fill.solid()
    quote.fill.fore_color.rgb = PANEL_ALT
    quote.line.color.rgb = ACCENT
    tf = slide.shapes.add_textbox(Inches(9.0), Inches(1.7), Inches(3.25), Inches(2.5)).text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = (
        "好的 AI 编程结果，通常不是来自“更会问一句话”，\n"
        "而是来自更好的上下文、拆解、约束与验证。"
    )
    r.font.size = Pt(18)
    r.font.bold = True
    r.font.color.rgb = TEXT

    add_footer(slide, "建议时长：30-40 分钟", "1 / 15")


def add_four_metrics_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "为什么值得系统化使用", "02")
    add_title(slide, "AI 编程的价值，不只是“写得更快”")

    cards = [
        ("1", "降低启动成本", "新任务、新语言、新模块更容易起步。"),
        ("2", "扩大个体能力边界", "一个人可以兼顾实现、测试、文档、脚本。"),
        ("3", "提升交付吞吐", "尤其适合样板代码、重构、批量修改、测试补齐。"),
        ("4", "倒逼工程规范", "上下文清晰、测试充分、结构良好的仓库更容易被 AI 利用。"),
    ]
    x_positions = [0.65, 3.8, 6.95, 10.1]
    for (num, title, desc), x in zip(cards, x_positions):
        panel = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
            Inches(x),
            Inches(2.0),
            Inches(2.45),
            Inches(2.55),
        )
        panel.fill.solid()
        panel.fill.fore_color.rgb = PANEL
        panel.line.color.rgb = ACCENT if num in {"1", "3"} else ACCENT_2

        tf = slide.shapes.add_textbox(Inches(x + 0.18), Inches(2.2), Inches(2.1), Inches(2.1)).text_frame
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = num
        r1.font.size = Pt(36)
        r1.font.bold = True
        r1.font.color.rgb = ACCENT
        p2 = tf.add_paragraph()
        p2.space_before = Pt(6)
        r2 = p2.add_run()
        r2.text = title
        r2.font.size = Pt(15)
        r2.font.bold = True
        r2.font.color.rgb = TEXT
        p3 = tf.add_paragraph()
        p3.space_before = Pt(6)
        r3 = p3.add_run()
        r3.text = desc
        r3.font.size = Pt(13)
        r3.font.color.rgb = MUTED

    add_quote(
        slide,
        "核心判断：AI 最适合解决“信息量大、模式重复、需要快速试错”的研发活动；"
        "最不适合“关键业务决策、隐式规则很多、验收标准不明确”的任务。",
    )
    add_footer(slide, "关键结论：AI 不是替代工程能力，而是放大工程能力", "2 / 15")


def add_two_by_two_roles_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "Cursor 的定位", "03")
    add_title(slide, "在 Cursor 里，建议把 AI 当成 4 类角色使用")
    roles = [
        ("1. 探索员", "快速扫描代码库、定位入口、解释调用链、总结模块职责。"),
        ("2. 实现助手", "按明确边界完成函数、组件、接口、迁移脚本、测试代码。"),
        ("3. 评审员", "对 diff 做风险扫描，找潜在 bug、回归点、边界条件、缺失测试。"),
        ("4. 教练", "解释陌生代码、给出重构思路、比较方案、补齐知识盲区。"),
    ]
    positions = [
        (0.65, 2.0), (6.65, 2.0),
        (0.65, 4.0), (6.65, 4.0),
    ]
    for (title, desc), (x, y) in zip(roles, positions):
        add_text_panel(slide, Inches(x), Inches(y), Inches(5.3), Inches(1.45), title, [desc], ACCENT_2 if x > 1 else ACCENT)
    add_quote(
        slide,
        "最低效的方式：把 Cursor 当“更高级的自动补全”。更高效的方式："
        "让它参与需求理解、方案拆解、实现、验证和复盘的完整链路。",
        y=Inches(5.95),
        h=Inches(0.82),
    )
    add_footer(slide, "角色切换越清晰，产出越稳定", "3 / 15")


def add_principles_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "最佳实践总原则", "04")
    add_title(slide, "先给原则，再谈技巧")
    principles = [
        ("原则 1", "先对齐任务，再开始写", "明确目标、范围、约束、验收标准。"),
        ("原则 2", "优先给上下文，不要只给指令", "让 AI 看到正确文件、接口、报错和已有模式。"),
        ("原则 3", "任务拆小，快速验证", "减少大段自动生成后难以审查和回滚的风险。"),
        ("原则 4", "让 AI 解释自己的修改", "要求列出改动点、影响面、未覆盖风险。"),
        ("原则 5", "人负责验收和决策", "AI 可以生成，但不拥有上线决策权。"),
        ("原则 6", "把高质量提示词沉淀成团队资产", "让最佳实践可复制、可推广。"),
    ]
    positions = [
        (0.65, 2.0), (4.45, 2.0), (8.25, 2.0),
        (0.65, 4.1), (4.45, 4.1), (8.25, 4.1),
    ]
    for (tag, title, desc), (x, y) in zip(principles, positions):
        panel = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
            Inches(x),
            Inches(y),
            Inches(3.45),
            Inches(1.7),
        )
        panel.fill.solid()
        panel.fill.fore_color.rgb = PANEL
        panel.line.color.rgb = ACCENT
        tf = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.12), Inches(3.1), Inches(1.4)).text_frame
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = tag
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = ACCENT_2
        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)
        r2 = p2.add_run()
        r2.text = title
        r2.font.size = Pt(14)
        r2.font.bold = True
        r2.font.color.rgb = TEXT
        p3 = tf.add_paragraph()
        p3.space_before = Pt(4)
        r3 = p3.add_run()
        r3.text = desc
        r3.font.size = Pt(12)
        r3.font.color.rgb = MUTED
    add_footer(slide, "经验：AI 编程的上限，常常取决于人的任务设计能力", "4 / 15")


def add_flow_slide(prs, tag, page, title, steps, prompt_text, footer_left, footer_right):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, tag, page)
    add_title(slide, title)
    x_positions = [0.65, 3.1, 5.55, 8.0, 10.45]
    for idx, ((step_title, desc), x) in enumerate(zip(steps, x_positions)):
        panel = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
            Inches(x),
            Inches(2.0),
            Inches(2.05),
            Inches(1.55),
        )
        panel.fill.solid()
        panel.fill.fore_color.rgb = PANEL_ALT
        panel.line.color.rgb = ACCENT
        tf = slide.shapes.add_textbox(Inches(x + 0.15), Inches(2.12), Inches(1.75), Inches(1.2)).text_frame
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = step_title
        r1.font.size = Pt(14)
        r1.font.bold = True
        r1.font.color.rgb = TEXT
        p2 = tf.add_paragraph()
        p2.space_before = Pt(6)
        r2 = p2.add_run()
        r2.text = desc
        r2.font.size = Pt(12)
        r2.font.color.rgb = MUTED
        if idx < len(steps) - 1:
            arrow_box = slide.shapes.add_textbox(Inches(x + 2.07), Inches(2.55), Inches(0.28), Inches(0.3))
            p = arrow_box.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = "→"
            r.font.size = Pt(20)
            r.font.bold = True
            r.font.color.rgb = ACCENT

    prompt_panel = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(0.65),
        Inches(4.05),
        Inches(12.0),
        Inches(2.25),
    )
    prompt_panel.fill.solid()
    prompt_panel.fill.fore_color.rgb = RGBColor(7, 12, 24)
    prompt_panel.line.color.rgb = ACCENT
    tf = slide.shapes.add_textbox(Inches(0.88), Inches(4.24), Inches(11.55), Inches(1.9)).text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = prompt_text
    r.font.name = "Courier New"
    r.font.size = Pt(13)
    r.font.color.rgb = TEXT
    add_footer(slide, footer_left, footer_right)


def add_compare_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "工作流 2", "06")
    add_title(slide, "优先让 AI “读代码”，再让 AI “写代码”")
    add_text_panel(
        slide,
        Inches(0.65),
        Inches(2.0),
        Inches(5.7),
        Inches(3.15),
        "推荐做法",
        [
            "先让 Cursor 总结模块职责、入口函数、关键数据流。",
            "要求引用具体文件和函数，而不是泛泛解释。",
            "让 AI 用现有代码风格完成实现，而不是凭空创造新模式。",
            "要求它说明为什么选这个修改点而不是别处。",
        ],
        ACCENT_2,
    )
    add_text_panel(
        slide,
        Inches(6.95),
        Inches(2.0),
        Inches(5.7),
        Inches(3.15),
        "常见问题",
        [
            "没有给上下文，AI 按通用经验瞎猜。",
            "一次贴太多无关文件，核心信息被稀释。",
            "没要求它引用证据，回答听起来合理但脱离仓库实际。",
            "直接让它重构大片代码，最后人无法 Review。",
        ],
        DANGER,
    )
    add_quote(slide, "一个非常有效的习惯：先问“仓库里现在是怎么做的”，再问“这次我应该怎么改”。")
    add_footer(slide, "正确上下文 > 华丽提示词", "6 / 15")


def add_small_steps_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "工作流 3", "07")
    add_title(slide, "用“小步快跑”替代“一次生成一大坨”")
    add_text_panel(slide, Inches(0.65), Inches(2.0), Inches(3.75), Inches(1.6), "步骤 A", ["先让 AI 只做方案和影响分析，确认改动边界。"])
    add_text_panel(slide, Inches(4.8), Inches(2.0), Inches(3.75), Inches(1.6), "步骤 B", ["一次只改一个文件或一个子问题，方便人类 Review。"], ACCENT_2)
    add_text_panel(slide, Inches(8.95), Inches(2.0), Inches(3.7), Inches(1.6), "步骤 C", ["每轮修改后立刻跑测试、lint、编译或关键路径验证。"], WARNING)

    headers = ["场景", "不推荐", "更推荐"]
    rows = [
        ("功能开发", "“把整个需求都实现了”", "“先补接口层，再补 service，再补测试”"),
        ("Bug 修复", "“帮我修掉这个问题”", "“先定位根因，再给最小修复 diff”"),
        ("重构", "一次性批量重写", "“分批迁移，每批可回滚、有测试覆盖”"),
    ]
    widths = [1.8, 4.25, 5.75]
    x_offsets = [0.65, 2.7, 7.2]
    y = 4.0
    for h, w, x in zip(headers, widths, x_offsets):
        box = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.55))
        box.fill.solid()
        box.fill.fore_color.rgb = PANEL_ALT
        box.line.color.rgb = ACCENT
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = TEXT
    for idx, row in enumerate(rows):
        y_row = y + 0.68 + idx * 0.68
        for text, w, x in zip(row, widths, x_offsets):
            box = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y_row), Inches(w), Inches(0.56))
            box.fill.solid()
            box.fill.fore_color.rgb = PANEL
            box.line.color.rgb = PANEL_ALT
            tf = box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = text
            r.font.size = Pt(11)
            r.font.color.rgb = MUTED
    add_footer(slide, "AI 越强，越要控制改动粒度", "7 / 15")


def add_prompt_templates_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "Prompt 模板", "09")
    add_title(slide, "3 个最常用、最值得团队复用的 Prompt 模板")
    add_text_panel(slide, Inches(0.65), Inches(2.0), Inches(3.8), Inches(2.45), "模板 1：代码探索", [
        "请阅读相关文件，告诉我入口、调用链、关键数据结构、改动建议，并引用具体文件位置。"
    ])
    add_text_panel(slide, Inches(4.75), Inches(2.0), Inches(3.8), Inches(2.45), "模板 2：最小改动实现", [
        "基于现有风格完成最小改动，不额外引入新框架，修改后总结影响面并列出验证步骤。"
    ], ACCENT_2)
    add_text_panel(slide, Inches(8.85), Inches(2.0), Inches(3.8), Inches(2.45), "模板 3：Review / 风险扫描", [
        "请站在 reviewer 视角检查这次 diff，优先找 bug、回归风险、缺失测试，不要只总结改了什么。"
    ], WARNING)
    add_quote(
        slide,
        "模板设计建议：固定 5 个槽位——目标 / 上下文 / 约束 / 输出格式 / 验收标准。"
        "这样每个人都能把 AI 用法标准化，不依赖“某个高手会问”。",
        y=Inches(5.2),
        h=Inches(1.15),
    )
    add_footer(slide, "提示词不是玄学，模板化后就是团队方法论", "9 / 15")


def add_context_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "上下文管理", "10")
    add_title(slide, "在 Cursor 中，真正拉开差距的是上下文管理")
    add_text_panel(slide, Inches(0.65), Inches(2.0), Inches(5.8), Inches(3.3), "高质量上下文应该包含", [
        "当前目标和背景：为什么要改。",
        "相关文件与错误信息：而不是只贴结论。",
        "已有实现模式：类似模块、历史方案、命名规范。",
        "边界和禁区：哪些地方不能改、不能破坏什么。",
        "验证标准：测试、运行、页面、日志、性能。",
    ], ACCENT_2)
    add_text_panel(slide, Inches(6.85), Inches(2.0), Inches(5.8), Inches(3.3), "实操建议", [
        "长对话中及时重置上下文，避免历史噪音污染当前任务。",
        "复杂任务把分析、实现、Review 分成多个对话阶段。",
        "发现 AI 偏题时，先补上下文或缩小任务。",
        "对关键结论要求引用代码证据和文件位置。",
    ])
    add_footer(slide, "一个经验：越复杂的需求，越要像写需求文档一样写给 AI", "10 / 15")


def add_review_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "Review 与风险控制", "11")
    add_title(slide, "把 AI 用在 Review，通常是投入产出比最高的环节")
    add_text_panel(slide, Inches(0.65), Inches(2.0), Inches(3.8), Inches(1.55), "检查 bug", [
        "空指针、未处理异常、并发问题、状态遗漏、边界条件漏掉。"
    ], DANGER)
    add_text_panel(slide, Inches(4.75), Inches(2.0), Inches(3.8), Inches(1.55), "检查回归", [
        "公共接口是否变更、老逻辑是否被破坏、兼容性是否受影响。"
    ], WARNING)
    add_text_panel(slide, Inches(8.85), Inches(2.0), Inches(3.8), Inches(1.55), "检查测试", [
        "关键路径是否覆盖、失败场景是否覆盖、断言是否足够严格。"
    ], ACCENT_2)
    review_text = (
        "Review 提示词建议：\n\n"
        "“请用 code review 的方式审查这次改动：\n"
        "- 优先指出可能的 bug、风险和行为变化；\n"
        "- 标注影响文件或逻辑点；\n"
        "- 判断是否缺失测试；\n"
        "- 如果没有明显问题，也请说明仍然存在的测试盲区。\n\n"
        "不要只复述改动内容。”"
    )
    prompt_panel = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
        Inches(0.65),
        Inches(4.0),
        Inches(12.0),
        Inches(2.0),
    )
    prompt_panel.fill.solid()
    prompt_panel.fill.fore_color.rgb = RGBColor(7, 12, 24)
    prompt_panel.line.color.rgb = ACCENT
    tf = slide.shapes.add_textbox(Inches(0.88), Inches(4.18), Inches(11.55), Inches(1.65)).text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = review_text
    r.font.size = Pt(13)
    r.font.color.rgb = TEXT
    add_footer(slide, "优秀团队不是“少写错”，而是“更快发现错”", "11 / 15")


def add_team_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "团队治理", "12")
    add_title(slide, "如果要规模化落地，需要建立 4 个团队机制")
    items = [
        ("机制 1：提示词模板库", "沉淀探索、实现、测试、Review、文档等常用模板。"),
        ("机制 2：AI 使用边界", "明确哪些代码、数据、密钥、客户信息不能放进上下文。"),
        ("机制 3：验收标准", "AI 生成代码必须过测试、lint、编译、Review，不得跳过工程门禁。"),
        ("机制 4：案例复盘", "定期复盘高价值用例和失败案例，让方法论持续进化。"),
    ]
    positions = [(0.65, 2.0), (6.65, 2.0), (0.65, 4.0), (6.65, 4.0)]
    for (title, desc), (x, y) in zip(items, positions):
        add_text_panel(slide, Inches(x), Inches(y), Inches(5.3), Inches(1.45), title, [desc], ACCENT_2 if y > 3 else ACCENT)
    add_quote(slide, "团队采用 AI 编程，不是“装个工具”就结束了，而是一次研发工作流升级。", y=Inches(5.9), h=Inches(0.82))
    add_footer(slide, "规模化效果 = 工具能力 × 工程规范 × 团队习惯", "12 / 15")


def add_mistakes_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "常见误区", "13")
    add_title(slide, "最容易让团队“用了 AI 但没得到收益”的 6 个误区")
    items = [
        "把 AI 当搜索引擎，问泛问题，不给仓库上下文。",
        "一次性让 AI 改太多，导致 Review 和回滚成本过高。",
        "只看它能不能生成，不看生成后是否可验证、可维护。",
        "把 AI 输出直接当事实，不要求引用仓库证据。",
        "没有沉淀复用模板，每个人都从零摸索。",
        "忽略安全边界，把不该暴露的信息交给 AI 上下文。",
    ]
    positions = [
        (0.65, 2.0), (4.45, 2.0), (8.25, 2.0),
        (0.65, 4.0), (4.45, 4.0), (8.25, 4.0),
    ]
    for idx, (text, (x, y)) in enumerate(zip(items, positions), start=1):
        panel = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
            Inches(x),
            Inches(y),
            Inches(3.45),
            Inches(1.45),
        )
        panel.fill.solid()
        panel.fill.fore_color.rgb = PANEL
        panel.line.color.rgb = DANGER
        tf = slide.shapes.add_textbox(Inches(x + 0.14), Inches(y + 0.12), Inches(3.1), Inches(1.18)).text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = f"误区 {idx}"
        r1.font.size = Pt(12)
        r1.font.bold = True
        r1.font.color.rgb = WARNING
        p2 = tf.add_paragraph()
        p2.space_before = Pt(5)
        r2 = p2.add_run()
        r2.text = text
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = MUTED
    add_footer(slide, "结论：AI 编程失败，通常不是因为模型不够强，而是流程设计不到位", "13 / 15")


def add_demo_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "建议现场 Demo", "14")
    add_title(slide, "分享时，推荐演示 1 个完整闭环")
    steps = [
        ("Step 1", "给出一个真实需求或 bug。"),
        ("Step 2", "先让 Cursor 分析代码与定位影响点。"),
        ("Step 3", "再让它提出最小改动方案。"),
        ("Step 4", "分步实现，并跑验证命令。"),
        ("Step 5", "最后让 AI 站在 reviewer 视角复查。"),
    ]
    x_positions = [0.65, 3.1, 5.55, 8.0, 10.45]
    for idx, ((step_title, desc), x) in enumerate(zip(steps, x_positions)):
        add_text_panel(slide, Inches(x), Inches(2.1), Inches(2.05), Inches(1.65), step_title, [desc], ACCENT_2 if idx % 2 else ACCENT)
        if idx < len(steps) - 1:
            arrow = slide.shapes.add_textbox(Inches(x + 2.07), Inches(2.72), Inches(0.26), Inches(0.3))
            p = arrow.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = "→"
            r.font.size = Pt(20)
            r.font.bold = True
            r.font.color.rgb = ACCENT
    add_quote(
        slide,
        "不要演示“AI 一次写了很多代码”，而要演示“AI 如何帮助你更快做出正确决策、减少试错、补齐验证”。"
        "这才最容易让团队认同。",
        y=Inches(4.65),
        h=Inches(1.2),
    )
    add_footer(slide, "最佳 demo：一个真实小任务胜过十个空泛技巧", "14 / 15")


def add_summary_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide)
    add_header(slide, "落地建议", "15")
    add_title(slide, "结论与落地建议")
    add_text_panel(slide, Inches(0.65), Inches(2.0), Inches(5.8), Inches(2.6), "今天希望带走的 3 个观点", [
        "AI 编程的关键不是“写得快”，而是“更快得到正确结果”。",
        "Cursor 最好的用法，是把 AI 放进完整研发链路，而不是只做补全。",
        "团队收益来自模板、流程、验证和复盘，而不是个人技巧。",
    ], ACCENT_2)
    add_text_panel(slide, Inches(6.85), Inches(2.0), Inches(5.8), Inches(2.6), "建议下一步行动", [
        "挑 2-3 个真实场景做试点：Bug 修复、测试补齐、批量重构。",
        "沉淀一套团队 Prompt 模板与安全边界。",
        "每周复盘“最好用”和“最翻车”的案例。",
    ], ACCENT)
    add_quote(slide, "Q&A：我们不是在学习一个新工具，而是在学习一种新的研发协作方式。", y=Inches(5.4), h=Inches(0.95))
    add_footer(slide, "谢谢 / 可按公司案例继续替换内容", "15 / 15")


def build_presentation():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    add_title_slide(prs)
    add_four_metrics_slide(prs)
    add_two_by_two_roles_slide(prs)
    add_principles_slide(prs)
    add_flow_slide(
        prs,
        "工作流 1",
        "05",
        "从模糊需求到可执行任务",
        [
            ("目标", "我要解决什么业务问题？"),
            ("范围", "改哪些模块？不改哪些模块？"),
            ("约束", "语言、接口、兼容性、性能要求。"),
            ("验收", "测试、日志、页面、接口返回标准。"),
            ("行动", "先分析，再提方案，再实现。"),
        ],
        "建议先这样问 Cursor：\n\n"
        "“你先不要写代码。请基于当前仓库帮我完成 3 件事：\n"
        "1. 找出和这个需求最相关的文件与调用链；\n"
        "2. 给出最小改动方案；\n"
        "3. 列出可能影响的测试点和风险点。\n\n"
        "需求目标：...\n改动范围：...\n不要改动：...\n验收标准：...”",
        "先分析再实现，能显著减少“写出来但不对”的返工",
        "5 / 15",
    )
    add_compare_slide(prs)
    add_small_steps_slide(prs)
    add_flow_slide(
        prs,
        "工作流 4",
        "08",
        "让 AI 先写“验证方式”，再写实现",
        [
            ("验证", "先设计测试或验证清单。"),
            ("覆盖", "正常路径、边界、异常、回归。"),
            ("定位", "确认现有代码为什么失败。"),
            ("方案", "给出最小修复方案。"),
            ("落地", "修复后补齐测试。"),
        ],
        "可复用提示词：\n\n"
        "“请先不要修改生产代码，先基于当前实现补充或设计测试用例：\n"
        "- 正常路径\n- 边界条件\n- 异常分支\n- 回归风险\n\n"
        "然后告诉我：\n1. 现有代码为什么会失败；\n2. 最小修复方案是什么；\n3. 修复后需要补哪些测试。”",
        "如果你不知道怎么验证，通常也不该让 AI 直接开始写",
        "8 / 15",
    )
    add_prompt_templates_slide(prs)
    add_context_slide(prs)
    add_review_slide(prs)
    add_team_slide(prs)
    add_mistakes_slide(prs)
    add_demo_slide(prs)
    add_summary_slide(prs)
    return prs


if __name__ == "__main__":
    presentation = build_presentation()
    output_path = "cursor-ai-best-practices.pptx"
    presentation.save(output_path)
    print(f"Generated {output_path}")
