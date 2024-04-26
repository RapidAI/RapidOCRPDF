# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from rapidocr_pdf import PDFExtracter

pdf_extracter = PDFExtracter(print_verbose=True)

pdf_path = "tests/test_files/direct_and_image.pdf"
texts = pdf_extracter(pdf_path, force_ocr=False)
print(texts)
