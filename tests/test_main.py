# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import shlex
import sys
from pathlib import Path

cur_dir = Path(__file__).resolve().parent
root_dir = cur_dir.parent
sys.path.append(str(root_dir))

import pytest

from rapidocr_pdf import RapidOCRPDF, RapidOCRPDFError
from rapidocr_pdf.main import main

test_dir = cur_dir / "test_files"

pdf_path = test_dir / "direct_and_image.pdf"

extracter = RapidOCRPDF()


@pytest.mark.parametrize(
    "command, expected_output",
    [
        (
            f"{pdf_path} --page_num_list '1'",
            "Defending Ukraine: Early Lessons from the Cyber War",
        )
    ],
)
def test_cli(capsys, command, expected_output):
    main(shlex.split(command))
    output = capsys.readouterr().out.rstrip()
    assert output[0][1].split("\n")[0].strip() == expected_output


def test_page_num():
    pdf_path = test_dir / "direct_extract.pdf"
    result = extracter(pdf_path, page_num_list=[1])

    assert (
        result[0][1].split("\n")[0].strip()
        == "Defending Ukraine: Early Lessons from the Cyber War"
    )


def test_error_page_num():
    pdf_path = test_dir / "direct_extract.pdf"
    with pytest.raises(ValueError) as exc_info:
        result = extracter(pdf_path, page_num_list=[2])
    assert exc_info.type is ValueError


@pytest.mark.parametrize(
    "pdf_content, result1, result2",
    [
        (test_dir / "direct_extract.pdf", 4858, "      "),
        (test_dir / "image.pdf", 3478, "Kurbas"),
        (test_dir / "direct_and_image.pdf", 4848, "      "),
    ],
)
def test_different_pdf(pdf_content, result1, result2):
    result = extracter(pdf_content)
    assert len(result[0][1]) >= result1
    assert result[0][1][:6] == result2


def test_input_bytes():
    pdf_content = test_dir / "image.pdf"
    with open(pdf_content, "rb") as f:
        data = f.read()

    result = extracter(data)

    assert len(result[0][1]) > 0
    assert result[0][1][:6] == "Kurbas"


def test_force_ocr():
    pdf_content = test_dir / "image.pdf"
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
