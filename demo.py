# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.come
from rapid_ocr_pdf import PDFExtracter


pdf_path = 'tests/test_files/1.jpg'

pdf_extracter = PDFExtracter()

texts = pdf_extracter(str(pdf_path))
print(texts)
