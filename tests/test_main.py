# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import ast
import shlex
import sys
from pathlib import Path

cur_dir = Path(__file__).resolve().parent
root_dir = cur_dir.parent
sys.path.append(str(root_dir))

import fitz
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
            f"{pdf_path} --page_num_list 0",
            "ABCNet: Real-time Scene Text Spotting with Adaptive Bezier-Curve Network∗",
        )
    ],
)
def test_cli(capsys, command, expected_output):
    main(shlex.split(command))
    output = capsys.readouterr().out.rstrip()
    output = ast.literal_eval(output)
    assert output[0][1].split("\n")[0].strip() == expected_output


def test_negative_page_num():
    pdf_path = test_dir / "direct_and_image.pdf"
    result = extracter(pdf_path, page_num_list=[-1])

    assert result[0][1].split("\n")[0].strip() == "Microsoft"


def test_error_negative_page_num():
    pdf_path = test_dir / "direct_and_image.pdf"
    with pytest.raises(RapidOCRPDFError) as exc_info:
        result = extracter(pdf_path, page_num_list=[-3])
    assert exc_info.type is RapidOCRPDFError


def test_page_num():
    pdf_path = test_dir / "direct_extract.pdf"
    result = extracter(pdf_path, page_num_list=[0])

    assert (
        result[0][1].split("\n")[0].strip()
        == "Defending Ukraine: Early Lessons from the Cyber War"
    )


def test_error_page_num():
    pdf_path = test_dir / "direct_extract.pdf"
    with pytest.raises(RapidOCRPDFError) as exc_info:
        result = extracter(pdf_path, page_num_list=[1])
    assert exc_info.type is RapidOCRPDFError


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


# ---------------------------------------------------------------------------
# Tests for to_searchable_pdf
# ---------------------------------------------------------------------------


def test_to_searchable_pdf_returns_bytes():
    """to_searchable_pdf should return a non-empty bytes object."""
    pdf_content = test_dir / "image.pdf"
    result = extracter.to_searchable_pdf(pdf_content)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_to_searchable_pdf_text_layer():
    """The output PDF should contain a searchable text layer on OCR pages."""
    pdf_content = test_dir / "image.pdf"
    result = extracter.to_searchable_pdf(pdf_content)
    with fitz.open(stream=result) as doc:
        text = doc[0].get_text("text")
    assert len(text) > 0


def test_to_searchable_pdf_saves_file(tmp_path):
    """When output_path is given the file should be written to disk."""
    pdf_content = test_dir / "image.pdf"
    out = tmp_path / "searchable.pdf"
    extracter.to_searchable_pdf(pdf_content, output_path=out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_to_searchable_pdf_from_bytes():
    """to_searchable_pdf should accept raw PDF bytes as input."""
    pdf_content = test_dir / "image.pdf"
    with open(pdf_content, "rb") as f:
        data = f.read()
    result = extracter.to_searchable_pdf(data)
    assert isinstance(result, bytes)
    with fitz.open(stream=result) as doc:
        text = doc[0].get_text("text")
    assert len(text) > 0


def test_to_searchable_pdf_invalid_input():
    """to_searchable_pdf should raise RapidOCRPDFError for invalid input."""
    with pytest.raises(RapidOCRPDFError):
        extracter.to_searchable_pdf(None)


def test_cli_output_pdf(tmp_path):
    """--output_pdf flag should produce a valid searchable PDF file."""
    out = tmp_path / "out.pdf"
    cmd = f"{test_dir / 'image.pdf'} --output_pdf {out}"
    main(shlex.split(cmd))
    assert out.exists()
    assert out.stat().st_size > 0
    with fitz.open(str(out)) as doc:
        text = doc[0].get_text("text")
    assert len(text) > 0
