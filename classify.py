# -*- coding: utf-8 -*-
"""
把 memes/ 里的表情包按标题关键词分类，移动进 memes_classified/<分类>/。

分类规则（按优先级）：
1. 用途类关键词：节日祝福 / 早安晚安 / 打工搬砖 / 恋爱情感 / 吃货
2. 角色/IP（标题括号或正文）：熊猫头 / 动漫IP / 影视剧综 / 动物萌宠
3. GIF 动图单列
4. 其余进「沙雕斗图」

产出：
- memes_classified/<分类>/*.jpg|gif
- memes_classified/分类明细.csv（file, title, category, source_list, 命中词）
- memes_classified/gallery.html（本地相册预览）
- 反悔可用 manifest 里的原路径移回去
"""
import csv
import html
import os
import re
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "memes")
DST = os.path.join(BASE, "memes_classified")

# (分类名, 关键词列表)  —— 顺序即优先级，先命中先得
RULES = [
    ("节日祝福", ["七夕", "新年", "春节", "中秋", "圣诞", "生日", "端午", "情人节",
                  "跨年", "元宵", "国庆", "元旦", "快乐"]),
    ("早安晚安", ["早安", "晚安", "早上好", "早啊", "早早早", "早点睡", "早睡",
                  "早起", "早醒", "午安", "催眠", "睡觉"]),
    ("打工搬砖", ["上班", "搬砖", "加班", "工资", "老板", "上学", "考试", "作业",
                  "面试", "辞职", "砖厂", "打工", "周一", "上班族", "摸鱼", "放假",
                  "写代码"]),
    ("怼人嘴臭", ["滚", "闭嘴", "妈的", "必死", "打死", "废物", "垃圾", "傻",
                  "臭", "给你脸", "挨", "别逼我", "干架", "撕", "骂", "嘴臭",
                  "一巴掌", "打死你", "啐", "呸"]),
    ("恋爱情感", ["女朋友", "男朋友", "对象", "表白", "撩", "心动", "爱你", "喜欢你",
                  "想你", "分手", "脱单", "单身", "相亲", "恋爱", "宝贝"]),
    ("情绪状态", ["大哭", "哭", "泪", "自闭", "难过", "崩溃", "无语", "尴尬",
                  "心累", "慌", "怕", "气到", "酸", "柠檬精", "emo", "丧"]),
    ("吃货", ["吃", "饭", "奶茶", "火锅", "烧烤", "零食", "减肥", "外卖", "干饭"]),
    ("熊猫头", ["熊猫头"]),
    ("动漫IP", ["派大星", "海绵宝宝", "杰尼龟", "皮卡丘", "宝可梦", "神奇宝贝",
                "哆啦", "小猪佩奇", "蜡笔小新", "柯南", "路飞", "海贼", "火影",
                "樱桃小丸子", "猫和老鼠", "tom", "jerry", "光头强", "熊出没",
                "哪吒", "千与千寻", "龙猫"]),
    ("影视剧综", ["武林外传", "甄嬛", "还珠", "西游记", "周星驰", "星爷", "成龙",
                  "吴京", "沈腾", "马丽", "王境泽", "金馆长", "蘑菇头", "发际线男孩",
                  "尔康", "紫薇", "容嬷嬷", "和珅", "纪晓岚", "亮剑", "李云龙",
                  "铁齿铜牙", "家有儿女", "刘星", "giao哥", "快手", "马保国",
                  "窃格瓦拉", "周立齐", "陈独秀", "鲁迅", "施瓦辛格", "施瓦星格"]),
    ("动物萌宠", ["猫", "狗", "鸭", "鸡", "鸟", "鱼", "兔", "猪", "熊", "老鼠",
                  "仓鼠", "柴犬", "柯基", "哈士奇", "鹦鹉", "企鹅", "狐狸", "马"]),
]
GIF_CAT = "动图GIF"
FALLBACK = "沙雕斗图"

def classify(title, fname):
    """返回 (分类, 命中词)"""
    t = title.lower()
    if fname.lower().endswith(".gif") and GIF_CAT != "":
        # GIF 也先过一遍规则，命中用途类就归用途，否则归动图
        for cat, kws in RULES:
            for k in kws:
                if k in t:
                    return cat, k
        return GIF_CAT, ""
    for cat, kws in RULES:
        for k in kws:
            if k in t:
                return cat, k
    return FALLBACK, ""

def find_file(fname):
    """文件可能还没搬（在 SRC），也可能上次运行已搬进某个分类目录"""
    p = os.path.join(SRC, fname)
    if os.path.exists(p):
        return p
    for cat in [c for c, _ in RULES] + [GIF_CAT, FALLBACK]:
        p = os.path.join(DST, cat, fname)
        if os.path.exists(p):
            return p
    return None

def main():
    with open(os.path.join(SRC, "index.csv"), newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    os.makedirs(DST, exist_ok=True)
    stats = {}
    detail = []
    for r in rows:
        fname, title, src_list = r["file"].strip(), r["title"].strip(), r["source_list"].strip()
        src_path = find_file(fname)
        if src_path is None:
            print("!! 缺文件", fname)
            continue
        cat, hit = classify(title, fname)
        cat_dir = os.path.join(DST, cat)
        os.makedirs(cat_dir, exist_ok=True)
        target = os.path.join(cat_dir, fname)
        if os.path.abspath(src_path) != os.path.abspath(target):
            shutil.move(src_path, target)
        stats[cat] = stats.get(cat, 0) + 1
        detail.append({"file": fname, "title": title, "category": cat,
                       "hit": hit, "source_list": src_list})

    # 分类明细
    with open(os.path.join(DST, "分类明细.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["file", "title", "category", "hit", "source_list"])
        w.writeheader()
        w.writerows(detail)

    # 相册 HTML
    cats_sorted = sorted(stats, key=lambda c: -stats[c])
    head = """<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<title>表情包分类相册</title><style>
body{font-family:"Microsoft YaHei",sans-serif;background:#111;color:#eee;margin:0;padding:24px}
h1{font-size:22px} .cat{margin:28px 0} .cat h2{font-size:17px;color:#7cc4ff;border-left:4px solid #7cc4ff;padding-left:10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.card{background:#1c1c1c;border-radius:8px;overflow:hidden}
.card img{width:100%;height:140px;object-fit:contain;background:#000;display:block}
.card p{font-size:12px;color:#bbb;margin:6px 8px;height:32px;overflow:hidden}
</style></head><body><h1>表情包分类相册（""" + str(len(detail)) + " 张）</h1>"
    parts = [head]
    for cat in cats_sorted:
        items = [d for d in detail if d["category"] == cat]
        parts.append('<div class="cat"><h2>%s（%d）</h2><div class="grid">' %
                     (html.escape(cat), len(items)))
        for d in items:
            parts.append(
                '<div class="card"><img loading="lazy" src="%s/%s" title="%s"><p>%s</p></div>'
                % (html.escape(cat), html.escape(d["file"]),
                   html.escape(d["title"]), html.escape(d["title"])))
        parts.append("</div></div>")
    parts.append("</body></html>")
    with open(os.path.join(DST, "gallery.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

    print("=== 分类结果 ===")
    for c in cats_sorted:
        print("%-8s %d 张" % (c, stats[c]))
    print("合计 %d 张 → memes_classified/" % len(detail))

if __name__ == "__main__":
    main()
