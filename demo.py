# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from rapidocr_pdf import PDFExtracter

pdf_extracter = PDFExtracter()

pdf_path = 'tests/test_files/image.pdf'
texts = pdf_extracter(pdf_path)
print(texts)
