# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
from rapidocr_pdf import RapidOCRPDF

pdf_extracter = RapidOCRPDF()

pdf_path = "tests/test_files/direct_extract.pdf"
texts = pdf_extracter(pdf_path, force_ocr=False, page_num_list=[1])
print(texts[0][1])
