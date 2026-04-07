from pathlib import Path
import argparse
import pymupdf as fitz


class PDFImageExtractionAgent:
    """
    从 PDF 中提取高分辨率图片：
    1. 优先提取 PDF 中的原始嵌入图片
    2. 若某页完全没有图片对象，可选择将整页按高 DPI 渲染导出
    3. 支持指定页码处理
    """

    def __init__(self, pdf_path, output_dir="output_images", dpi=300,
                 render_full_page_if_needed=False, pages=None):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.dpi = dpi
        self.render_full_page_if_needed = render_full_page_if_needed
        self.pages = pages  # 例如 [1, 3, 5]，表示处理第1、3、5页（人类习惯页码）

        self.doc = None
        self.total_pages = 0
        self.extracted_count = 0
        self.rendered_count = 0
        self.seen_xrefs = set()

    def analyze_task(self):
        print("【Agent】开始分析任务...")

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"找不到 PDF 文件：{self.pdf_path}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"【Agent】输出目录已准备：{self.output_dir}")

    def open_pdf(self):
        print("【Agent】正在打开 PDF 文件...")
        try:
            self.doc = fitz.open(self.pdf_path)
            self.total_pages = len(self.doc)
            print(f"【Agent】PDF 打开成功，共 {self.total_pages} 页。")
        except Exception as e:
            raise RuntimeError(f"无法打开 PDF 文件，错误信息：{e}")

    def get_target_page_indices(self):
        """返回实际要处理的页索引（从0开始）"""
        if not self.pages:
            return list(range(self.total_pages))

        page_indices = []
        for p in self.pages:
            if 1 <= p <= self.total_pages:
                page_indices.append(p - 1)
            else:
                print(f"【Agent】警告：页码 {p} 超出范围，已跳过。")
        return page_indices

    def extract_images_from_page(self, page, page_index):
        """
        返回：
            has_any_image: 本页是否存在图片对象
            found_new_image: 是否提取到了新图片
        """
        image_list = page.get_images(full=True)

        if not image_list:
            return False, False

        found_new_image = False

        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]

            # 跳过重复图片
            if xref in self.seen_xrefs:
                continue
            self.seen_xrefs.add(xref)

            try:
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                filename = f"page_{page_index + 1}_img_{img_index}.{image_ext}"
                save_path = self.output_dir / filename

                with open(save_path, "wb") as f:
                    f.write(image_bytes)

                self.extracted_count += 1
                found_new_image = True
                print(f"【Agent】已提取原始图片：{save_path}")

            except Exception as e:
                print(f"【Agent】提取第 {page_index + 1} 页第 {img_index} 张图片失败：{e}")

        return True, found_new_image

    def render_page_as_image(self, page, page_index):
        """
        将整页按高 DPI 渲染为 PNG
        """
        zoom = self.dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        try:
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            filename = f"page_{page_index + 1}_render_{self.dpi}dpi.png"
            save_path = self.output_dir / filename
            pix.save(save_path)

            self.rendered_count += 1
            print(f"【Agent】该页无图片对象，已高分辨率渲染整页：{save_path}")
        except Exception as e:
            print(f"【Agent】渲染第 {page_index + 1} 页失败：{e}")

    def execute(self):
        print("【Agent】开始执行图片提取任务...")
        target_indices = self.get_target_page_indices()

        for page_index in target_indices:
            page = self.doc[page_index]
            print(f"\n【Agent】正在处理第 {page_index + 1}/{self.total_pages} 页...")

            has_any_image, extracted_new = self.extract_images_from_page(page, page_index)

            # 只有本页根本没有图片对象，才整页渲染
            if (not has_any_image) and self.render_full_page_if_needed:
                self.render_page_as_image(page, page_index)

    def summarize(self):
        print("\n========== 任务完成 ==========")
        print(f"PDF 文件：{self.pdf_path}")
        print(f"总页数：{self.total_pages}")
        print(f"提取的原始图片数量：{self.extracted_count}")
        print(f"高分辨率渲染页数：{self.rendered_count}")
        print(f"输出目录：{self.output_dir.resolve()}")
        print("================================")

    def run(self):
        self.analyze_task()
        self.open_pdf()
        self.execute()
        self.summarize()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从 PDF 中提取嵌入图片或按需渲染整页")
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument("-o", "--output_dir", default="pdf_output_images", help="输出目录")
    parser.add_argument("--dpi", type=int, default=300, help="整页渲染 DPI")
    parser.add_argument("--render-page", action="store_true", help="若某页无图片对象，则渲染整页")
    parser.add_argument("--pages", nargs="*", type=int, help="指定处理页码，例如 --pages 1 3 5")

    args = parser.parse_args()

    agent = PDFImageExtractionAgent(
        pdf_path=args.pdf_path,
        output_dir=args.output_dir,
        dpi=args.dpi,
        render_full_page_if_needed=args.render_page,
        pages=args.pages
    )
    agent.run()