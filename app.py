# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import gradio as gr
from gradio_pdf import PDF

from rapidocr_pdf import RapidOCRPDF

pdf_extracter = RapidOCRPDF()


def get_result():
    pass


with gr.Blocks(
    title="RapidOCR 📄 PDF", css="custom_css", theme=gr.themes.Soft()
) as demo:
    gr.Markdown(
        "<h1 style='text-align: center;'><a href='https://github.com/RapidAI/RapidOCRPDF' style='text-decoration: none;'>RapidOCR 📄 PDF</a></h1>"
    )
    gr.HTML(
        """
        <div style="display: flex; justify-content: center; gap: 10px;">
            <a href=""><img src="https://img.shields.io/badge/Python->=3.6-aff.svg"></a>
            <a href=""><img src="https://img.shields.io/badge/OS-Linux%2C%20Win%2C%20Mac-pink.svg"></a>
            <a href="https://pypi.org/project/rapidocr-pdf/"><img alt="PyPI" src="https://img.shields.io/pypi/v/rapidocr-pdf"></a>
            <a href="https://pepy.tech/project/rapidocr-pdf"><img src="https://static.pepy.tech/personalized-badge/rapidocr-pdf?period=total&units=abbreviation&left_color=grey&right_color=blue&left_text=Downloads"></a>
            <a href="https://semver.org/"><img alt="SemVer2.0" src="https://img.shields.io/badge/SemVer-2.0-brightgreen"></a>
            <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
            <a href="https://choosealicense.com/licenses/apache-2.0/"><img alt="GitHub" src="https://img.shields.io/github/license/RapidAI/RapidOCRPDF"></a>
        </div>
    """
    )

    PDF(label="Upload a PDF", interactive=True)
    btn = gr.Button("Run")


if __name__ == "__main__":
    demo.launch()
