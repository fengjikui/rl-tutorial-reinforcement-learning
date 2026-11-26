"""把 main.pdf（强化学习和多模态教程，358 页）拆成「强化学习」和「多模态」两部分。

用法：
    python3 split_pdf.py main.pdf            # 默认输出到 ./，切点 p182/p183
    python3 split_pdf.py main.pdf --outdir out

依赖 pymupdf：python3 -m pip install pymupdf
"""

import argparse
import os

import pymupdf


def split(src_path, outdir, cut=182):
    src = pymupdf.open(src_path)
    toc = src.get_toc(simple=True)  # [[level, title, page(1-based)], ...]

    parts = [
        (1, cut, "强化学习部分_p1-%d.pdf" % cut, "第一部分：强化学习"),
        (cut + 1, src.page_count,
         "多模态视觉部分_p%d-%d.pdf" % (cut + 1, src.page_count), "第三部分：多模态"),
    ]

    for start, end, name, label in parts:
        doc = pymupdf.open()
        doc.insert_pdf(src, from_page=start - 1, to_page=end - 1)
        # 重建书签：只保留落在本段内的条目，页码平移为段内页码
        new_toc = [[lvl, title, page - start + 1]
                   for lvl, title, page in toc if start <= page <= end]
        if new_toc:
            doc.set_toc(new_toc)
        doc.set_metadata({
            "title": "强化学习和多模态教程 · %s（p%d-%d）" % (label, start, end),
            "author": src.metadata.get("author", ""),
            "subject": "%s 第 %d-%d 页" % (os.path.basename(src_path), start, end),
        })
        out = os.path.join(outdir, name)
        doc.save(out, garbage=4, deflate=True)
        doc.close()
        print("%s  页数 %d -> %s" % (name, end - start + 1, out))

    src.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="源 PDF 路径")
    ap.add_argument("--outdir", default=".", help="输出目录")
    ap.add_argument("--cut", type=int, default=182,
                    help="前一段的最后一页（默认 182：p183 起是「多模态」分部页）")
    args = ap.parse_args()
    split(args.pdf, args.outdir, args.cut)
