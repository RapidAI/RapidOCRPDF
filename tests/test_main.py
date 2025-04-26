# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

import pytest

from rapidocr_pdf import RapidOCRPDF, RapidOCRPDFError

test_file_dir = Path(__file__).resolve().parent / "test_files"
extracter = RapidOCRPDF()


@pytest.mark.parametrize(
    "pdf_content, result1, result2",
    [
        (test_file_dir / "direct_extract.pdf", 3214, "Defend"),
        (test_file_dir / "image.pdf", 3400, "Kurbas"),
        (test_file_dir / "direct_and_image.pdf", 3710, "ABCNet"),
    ],
)
def test_different_pdf(pdf_content, result1, result2):
    result = extracter(pdf_content)
    assert len(result[0][1]) >= result1
    assert result[0][1][:6] == result2


def test_input_bytes():
    pdf_content = test_file_dir / "image.pdf"
    with open(pdf_content, "rb") as f:
        data = f.read()

    result = extracter(data)

    assert len(result[0][1]) > 0
    assert result[0][1][:6] == "Kurbas"


def test_force_ocr():
    pdf_content = test_file_dir / "image.pdf"
    with open(pdf_content, "rb") as f:
        data = f.read()

    result = extracter(data, force_ocr=True)
    assert len(result[0][1]) > 3400
    assert result[0][1][:6] == "Kurbas"


@pytest.mark.parametrize("content", [None, ""])
def test_corner_case(content):
    with pytest.raises(RapidOCRPDFError) as exc_info:
        extracter(content)
    assert exc_info.type is RapidOCRPDFError
