import copy
import json
from pathlib import Path

from pptx import Presentation


TEMPLATE = "破局审计内卷·共拓万亿蓝海.pptx"
CONTENT = "content.json"
OUTPUT = "财咖售前方案.pptx"

# 模板中各类 slide 的原始索引（0-based）
IDX = {
    "cover": 0,
    "toc": 1,
    "text": 2,
    "module": 7,
    "three_cols": 5,
    "steps": 15,
    "numbered": 17,
    "four_grid": 9,
    "ending": 28,
}


def load_content(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def copy_slide(prs, src_index):
    """深拷贝指定索引的 slide，并正确处理背景与图片关系。"""
    src_slide = prs.slides[src_index]
    layout = src_slide.slide_layout
    new_slide = prs.slides.add_slide(layout)

    p_ns = "http://schemas.openxmlformats.org/presentationml/2006/main"
    src_csld = src_slide._element.find(f"{{{p_ns}}}cSld")
    new_csld = new_slide._element.find(f"{{{p_ns}}}cSld")
    if src_csld is not None and new_csld is not None:
        src_bg = src_csld.find(f"{{{p_ns}}}bg")
        if src_bg is not None:
            old_bg = new_csld.find(f"{{{p_ns}}}bg")
            if old_bg is not None:
                new_csld.remove(old_bg)
            new_csld.insert(0, copy.deepcopy(src_bg))

    sp_tree = new_slide.shapes._spTree
    for child in list(sp_tree):
        sp_tree.remove(child)

    r_embed = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
    r_link = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}link"

    for child in src_slide.shapes._spTree:
        new_child = copy.deepcopy(child)
        for elem in new_child.iter():
            for attr in (r_embed, r_link):
                old_rid = elem.get(attr)
                if old_rid and old_rid in src_slide.part.rels:
                    rel = src_slide.part.rels[old_rid]
                    new_rid = new_slide.part.relate_to(rel.target_part, rel.reltype)
                    elem.set(attr, new_rid)
        sp_tree.append(new_child)

    return new_slide


def set_shape_text(slide, name, text):
    for shape in slide.shapes:
        if shape.name == name and shape.has_text_frame:
            tf = shape.text_frame
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
    slide_id_list = prs.slides._sldIdLst
    for _ in range(count):
        sld_id = slide_id_list[0]
        rid = sld_id.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        )
        prs.part.drop_rel(rid)
        slide_id_list.remove(sld_id)


def build_cover(prs, data):
    slide = copy_slide(prs, IDX["cover"])
    set_placeholder(slide, 0, data["title"])
    set_textbox(slide, "文本框 2", data["subtitle"])
    return slide


def build_module(prs, data):
    slide = copy_slide(prs, IDX["module"])
    set_shape_text(slide, "Text 2", data["module_no"])
    set_shape_text(slide, "Text 3", data["module_name"])
    set_shape_text(slide, "Text 5", data["subtitle"])
    set_shape_text(slide, "Text 8", data["tagline"])
    return slide


def build_three_cols(prs, data):
    slide = copy_slide(prs, IDX["three_cols"])
    set_shape_text(slide, "Text 0", data["tag"])
    set_shape_text(slide, "Text 1", data["title"])

    cols = data["cols"]
    set_shape_text(slide, "Text 6", cols[0]["heading"])
    set_shape_text(slide, "Text 7", cols[0]["body"])
    set_shape_text(slide, "Text 10", cols[0]["quote"])
    set_shape_text(slide, "Text 14", cols[1]["heading"])
    set_shape_text(slide, "Text 15", cols[1]["body"])
    set_shape_text(slide, "Text 18", cols[1]["quote"])
    set_shape_text(slide, "Text 22", cols[2]["heading"])
    set_shape_text(slide, "Text 23", cols[2]["body"])
    set_shape_text(slide, "Text 26", cols[2]["quote"])
    set_shape_text(slide, "Text 30", data["footer"])
    return slide


def build_steps(prs, data):
    slide = copy_slide(prs, IDX["steps"])
    set_shape_text(slide, "Text 0", data["tag"])
    set_shape_text(slide, "Text 1", data["title"])
    set_shape_text(slide, "Text 3", data["intro"])

    steps = data["steps"]
    set_shape_text(slide, "Text 5", steps[0]["step"].split()[0])
    set_shape_text(slide, "Text 6", steps[0]["step"].split()[1])
    set_shape_text(slide, "Text 8", steps[0]["phase"])
    set_shape_text(slide, "Text 10", steps[0]["action"])
    set_shape_text(slide, "Text 13", steps[0]["detail_a"])
    set_shape_text(slide, "Text 16", steps[0]["detail_b"])

    set_shape_text(slide, "Text 18", steps[1]["step"].split()[0])
    set_shape_text(slide, "Text 19", steps[1]["step"].split()[1])
    set_shape_text(slide, "Text 21", steps[1]["phase"])
    set_shape_text(slide, "Text 23", steps[1]["action"])
    set_shape_text(slide, "Text 26", steps[1]["detail_a"])
    set_shape_text(slide, "Text 29", steps[1]["detail_b"])

    set_shape_text(slide, "Text 31", steps[2]["step"].split()[0])
    set_shape_text(slide, "Text 32", steps[2]["step"].split()[1])
    set_shape_text(slide, "Text 34", steps[2]["phase"])
    set_shape_text(slide, "Text 36", steps[2]["action"])
    set_shape_text(slide, "Text 39", steps[2]["detail_a"])
    set_shape_text(slide, "Text 42", steps[2]["detail_b"])

    set_shape_text(slide, "Text 46", data["footer"])
    return slide


def build_numbered_list(prs, data):
    slide = copy_slide(prs, IDX["numbered"])
    set_shape_text(slide, "Text 0", data["tag"])
    set_shape_text(slide, "Text 1", data["title"])
    set_shape_text(slide, "Text 3", data["intro"])

    items = data["items"]
    offsets = [(6, 7, 8), (11, 12, 13), (16, 17, 18)]
    for i, item in enumerate(items[:3]):
        no_idx, heading_idx, body_idx = offsets[i]
        set_shape_text(slide, f"Text {no_idx}", item["no"])
        set_shape_text(slide, f"Text {heading_idx}", item["heading"])
        set_shape_text(slide, f"Text {body_idx}", item["body"])

    set_shape_text(slide, "Text 29", data["footer"])
    return slide


def build_four_grid(prs, data):
    slide = copy_slide(prs, IDX["four_grid"])
    set_shape_text(slide, "Text 0", data["tag"])
    set_shape_text(slide, "Text 1", data["title"])

    items = data["items"]
    set_shape_text(slide, "Text 6", items[0]["heading"])
    set_shape_text(slide, "Text 7", items[0]["body"])
    set_shape_text(slide, "Text 10", items[0]["quote"])
    set_shape_text(slide, "Text 14", items[1]["heading"])
    set_shape_text(slide, "Text 15", items[1]["body"])
    set_shape_text(slide, "Text 18", items[1]["quote"])
    set_shape_text(slide, "Text 22", items[2]["heading"])
    set_shape_text(slide, "Text 23", items[2]["body"])
    set_shape_text(slide, "Text 26", items[2]["quote"])
    set_shape_text(slide, "Text 30", items[3]["heading"])
    set_shape_text(slide, "Text 31", items[3]["body"])
    set_shape_text(slide, "Text 34", items[3]["quote"])
    set_shape_text(slide, "Text 38", data["footer"])
    return slide


def build_ending(prs, data):
    slide = copy_slide(prs, IDX["ending"])
    set_placeholder(slide, 10, data["name"])
    return slide


BUILDERS = {
    "module": build_module,
    "three_cols": build_three_cols,
    "steps": build_steps,
    "numbered_list": build_numbered_list,
    "four_grid": build_four_grid,
}


def generate(template_path, content_data, output_path):
    """直接接受 JSON 对象并生成 PPT。"""
    prs = Presentation(str(template_path))
    original_count = len(prs.slides)
    data = content_data

    build_cover(prs, data["cover"])

    for slide_data in data["slides"]:
        slide_type = slide_data["type"]
        if slide_type in BUILDERS:
            BUILDERS[slide_type](prs, slide_data)
        else:
            print(f"⚠️ 未知类型：{slide_type}，已跳过")

    build_ending(prs, data["ending"])
    delete_original_slides(prs, original_count)

    prs.save(str(output_path))
    total = len(prs.slides)
    print(f"✅ 生成成功：{output_path}，共 {total} 页")
    return str(output_path)


def generate_from_file(template_path, content_path, output_path):
    """兼容原有用法：从 content.json 读取后生成 PPT。"""
    return generate(template_path, load_content(content_path), output_path)


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    generate_from_file(base_dir / TEMPLATE, base_dir / CONTENT, base_dir / OUTPUT)
