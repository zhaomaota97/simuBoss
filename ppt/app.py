import json
import copy
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ============================================================
# 常量
# ============================================================
TEMPLATE = "破局审计内卷·共拓万亿蓝海.pptx"
CONTENT  = "content.json"
OUTPUT   = "财咖售前方案.pptx"

# 模板中各类Slide的原始索引（0-based）
IDX = {
    "cover":       0,   # 0_封面_1
    "toc":         1,   # 2_目录_2_装饰
    "text":        2,   # 2_正文_纯文字部分
    "module":      7,   # MODULE章节封面（Slide 8）
    "three_cols":  5,   # 三列卡片（Slide 6）
    "steps":      15,   # STEP流程（Slide 16）
    "numbered":   17,   # 编号列表（Slide 18）
    "four_grid":   9,   # 四象限（Slide 10）
    "ending":     28,   # 结尾页-商务
}

# ============================================================
# 工具函数
# ============================================================

def load_content(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def copy_slide(prs, src_index):
    """深拷贝指定索引的Slide，正确处理背景色和图片关系引用"""
    src_slide = prs.slides[src_index]
    layout = src_slide.slide_layout
    new_slide = prs.slides.add_slide(layout)

    # ① 复制背景 <p:bg>
    P_NS = 'http://schemas.openxmlformats.org/presentationml/2006/main'
    src_cSld = src_slide._element.find(f'{{{P_NS}}}cSld')
    new_cSld = new_slide._element.find(f'{{{P_NS}}}cSld')
    if src_cSld is not None and new_cSld is not None:
        src_bg = src_cSld.find(f'{{{P_NS}}}bg')
        if src_bg is not None:
            # 删除新Slide已有的bg（如果有）
            old_bg = new_cSld.find(f'{{{P_NS}}}bg')
            if old_bg is not None:
                new_cSld.remove(old_bg)
            # 插入到cSld的第一个位置
            new_cSld.insert(0, copy.deepcopy(src_bg))

    # ② 清空新Slide的shape树
    sp_tree = new_slide.shapes._spTree
    for child in list(sp_tree):
        sp_tree.remove(child)

    # ③ 复制所有shape，同时修复图片关系引用
    R_EMBED = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
    R_LINK  = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}link'

    for child in src_slide.shapes._spTree:
        new_child = copy.deepcopy(child)
        for elem in new_child.iter():
            for attr in (R_EMBED, R_LINK):
                old_rId = elem.get(attr)
                if old_rId and old_rId in src_slide.part.rels:
                    rel = src_slide.part.rels[old_rId]
                    new_rId = new_slide.part.relate_to(
                        rel.target_part, rel.reltype
                    )
                    elem.set(attr, new_rId)
        sp_tree.append(new_child)

    return new_slide

def set_shape_text(slide, name, text):
    """按shape name修改文字（DEFAULT布局用）"""
    for shape in slide.shapes:
        if shape.name == name and shape.has_text_frame:
            tf = shape.text_frame
            # 保留原有格式，只替换文字
            for para in tf.paragraphs:
                for run in para.runs:
                    run.text = ""
            if tf.paragraphs[0].runs:
                tf.paragraphs[0].runs[0].text = text
            else:
                tf.paragraphs[0].text = text
            return True
    return False


def set_placeholder(slide, idx, text):
    """按placeholder idx修改文字"""
    for shape in slide.shapes:
        if shape.is_placeholder and shape.placeholder_format.idx == idx:
            tf = shape.text_frame
            if tf.paragraphs[0].runs:
                tf.paragraphs[0].runs[0].text = text
                for p in tf.paragraphs[1:]:
                    p._p.getparent().remove(p._p)
            else:
                tf.paragraphs[0].text = text
            return True
    return False


def set_textbox(slide, name, text):
    """按name修改文本框（封面副标题用）"""
    for shape in slide.shapes:
        if shape.name == name and shape.has_text_frame:
            tf = shape.text_frame
            if tf.paragraphs[0].runs:
                tf.paragraphs[0].runs[0].text = text
            else:
                tf.paragraphs[0].text = text
            return True
    return False


def delete_original_slides(prs, count):
    """删除前count张原始模板Slide"""
    slide_id_list = prs.slides._sldIdLst
    for _ in range(count):
        sldId = slide_id_list[0]
        rId = sldId.get(
            '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
        )
        prs.part.drop_rel(rId)
        slide_id_list.remove(sldId)


# ============================================================
# 各类型Slide构建函数
# ============================================================

def build_cover(prs, data):
    slide = copy_slide(prs, IDX["cover"])
    set_placeholder(slide, 0, data["title"])
    set_textbox(slide, "文本框 2", data["subtitle"])
    return slide


def build_module(prs, data):
    """章节过渡页：复用MODULE封面布局"""
    slide = copy_slide(prs, IDX["module"])
    set_shape_text(slide, "Text 2", data["module_no"])
    set_shape_text(slide, "Text 3", data["module_name"])
    set_shape_text(slide, "Text 5", data["subtitle"])
    set_shape_text(slide, "Text 8", data["tagline"])
    return slide


def build_three_cols(prs, data):
    """三列卡片页：复用THE CHALLENGES布局"""
    slide = copy_slide(prs, IDX["three_cols"])
    set_shape_text(slide, "Text 0", data["tag"])
    set_shape_text(slide, "Text 1", data["title"])

    cols = data["cols"]
    # 第一列
    set_shape_text(slide, "Text 6",  cols[0]["heading"])
    set_shape_text(slide, "Text 7",  cols[0]["body"])
    set_shape_text(slide, "Text 10", cols[0]["quote"])
    # 第二列
    set_shape_text(slide, "Text 14", cols[1]["heading"])
    set_shape_text(slide, "Text 15", cols[1]["body"])
    set_shape_text(slide, "Text 18", cols[1]["quote"])
    # 第三列
    set_shape_text(slide, "Text 22", cols[2]["heading"])
    set_shape_text(slide, "Text 23", cols[2]["body"])
    set_shape_text(slide, "Text 26", cols[2]["quote"])

    set_shape_text(slide, "Text 30", data["footer"])
    return slide


def build_steps(prs, data):
    """三步流程页：复用PRACTICAL TOOL 02布局"""
    slide = copy_slide(prs, IDX["steps"])
    set_shape_text(slide, "Text 0", data["tag"])
    set_shape_text(slide, "Text 1", data["title"])
    set_shape_text(slide, "Text 3", data["intro"])

    steps = data["steps"]
    # STEP 01
    set_shape_text(slide, "Text 5",  steps[0]["step"].split()[0])  # "STEP"
    set_shape_text(slide, "Text 6",  steps[0]["step"].split()[1])  # "01"
    set_shape_text(slide, "Text 8",  steps[0]["phase"])
    set_shape_text(slide, "Text 10", steps[0]["action"])
    set_shape_text(slide, "Text 13", steps[0]["detail_a"])
    set_shape_text(slide, "Text 16", steps[0]["detail_b"])
    # STEP 02
    set_shape_text(slide, "Text 18", steps[1]["step"].split()[0])
    set_shape_text(slide, "Text 19", steps[1]["step"].split()[1])
    set_shape_text(slide, "Text 21", steps[1]["phase"])
    set_shape_text(slide, "Text 23", steps[1]["action"])
    set_shape_text(slide, "Text 26", steps[1]["detail_a"])
    set_shape_text(slide, "Text 29", steps[1]["detail_b"])
    # STEP 03
    set_shape_text(slide, "Text 31", steps[2]["step"].split()[0])
    set_shape_text(slide, "Text 32", steps[2]["step"].split()[1])
    set_shape_text(slide, "Text 34", steps[2]["phase"])
    set_shape_text(slide, "Text 36", steps[2]["action"])
    set_shape_text(slide, "Text 39", steps[2]["detail_a"])
    set_shape_text(slide, "Text 42", steps[2]["detail_b"])

    set_shape_text(slide, "Text 46", data["footer"])
    return slide


def build_numbered_list(prs, data):
    """编号列表页：复用LESSONS LEARNED布局"""
    slide = copy_slide(prs, IDX["numbered"])
    set_shape_text(slide, "Text 0", data["tag"])
    set_shape_text(slide, "Text 1", data["title"])
    set_shape_text(slide, "Text 3", data["intro"])

    items = data["items"]
    offsets = [(6, 7, 8), (11, 12, 13), (16, 17, 18)]
    for i, item in enumerate(items[:3]):
        no_idx, heading_idx, body_idx = offsets[i]
        set_shape_text(slide, f"Text {no_idx}",      item["no"])
        set_shape_text(slide, f"Text {heading_idx}", item["heading"])
        set_shape_text(slide, f"Text {body_idx}",    item["body"])

    set_shape_text(slide, "Text 29", data["footer"])
    return slide


def build_four_grid(prs, data):
    """四象限页：复用UNDERLYING LOGIC布局"""
    slide = copy_slide(prs, IDX["four_grid"])
    set_shape_text(slide, "Text 0", data["tag"])
    set_shape_text(slide, "Text 1", data["title"])

    items = data["items"]
    # 左上
    set_shape_text(slide, "Text 6",  items[0]["heading"])
    set_shape_text(slide, "Text 7",  items[0]["body"])
    set_shape_text(slide, "Text 10", items[0]["quote"])
    # 右上
    set_shape_text(slide, "Text 14", items[1]["heading"])
    set_shape_text(slide, "Text 15", items[1]["body"])
    set_shape_text(slide, "Text 18", items[1]["quote"])
    # 左下
    set_shape_text(slide, "Text 22", items[2]["heading"])
    set_shape_text(slide, "Text 23", items[2]["body"])
    set_shape_text(slide, "Text 26", items[2]["quote"])
    # 右下
    set_shape_text(slide, "Text 30", items[3]["heading"])
    set_shape_text(slide, "Text 31", items[3]["body"])
    set_shape_text(slide, "Text 34", items[3]["quote"])

    set_shape_text(slide, "Text 38", data["footer"])
    return slide


def build_ending(prs, data):
    slide = copy_slide(prs, IDX["ending"])
    set_placeholder(slide, 10, data["name"])
    return slide


# ============================================================
# 路由分发
# ============================================================

BUILDERS = {
    "module":        build_module,
    "three_cols":    build_three_cols,
    "steps":         build_steps,
    "numbered_list": build_numbered_list,
    "four_grid":     build_four_grid,
}


def generate(template_path, content_path, output_path):
    prs = Presentation(template_path)
    original_count = len(prs.slides)
    data = load_content(content_path)

    # 封面
    build_cover(prs, data["cover"])

    # 内容页
    for slide_data in data["slides"]:
        t = slide_data["type"]
        if t in BUILDERS:
            BUILDERS[t](prs, slide_data)
        else:
            print(f"⚠️  未知类型：{t}，已跳过")

    # 结尾
    build_ending(prs, data["ending"])

    # 删除原始模板页
    delete_original_slides(prs, original_count)

    prs.save(output_path)
    total = len(prs.slides)
    print(f"✅ 生成成功：{output_path}，共 {total} 页")


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    generate(TEMPLATE, CONTENT, OUTPUT)
