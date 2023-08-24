## RapidOCRPDF
<p>
    <a href=""><img src="https://img.shields.io/badge/Python->=3.6,<3.12-aff.svg"></a>
    <a href=""><img src="https://img.shields.io/badge/OS-Linux%2C%20Win%2C%20Mac-pink.svg"></a>
    <a href="https://pypi.org/project/rapidocr-pdf/"><img alt="PyPI" src="https://img.shields.io/pypi/v/rapidocr-pdf"></a>
    <a href="https://pepy.tech/project/rapidocr-pdf"><img src="https://static.pepy.tech/personalized-badge/rapidocr-pdf?period=total&units=abbreviation&left_color=grey&right_color=blue&left_text=Downloads"></a>
</p>

- Relying on [RapidOCR](https://github.com/RapidAI/RapidOCR), quickly extract text from PDF, including scanned PDF and encrypted PDF.
- Layout restore is not included for now.


### 1. Install package by pypi.
   ```bash
   # base rapidocr_onnxruntime
   pip install rapidocr_pdf[onnxruntime]

   # base rapidocr_openvino
   pip install rapidocr_pdf[openvino]
   ```

### 2. Use
- Run by script.
    ```python
    from rapidocr_pdf import PDFExtracter

    pdf_extracter = PDFExtracter()

    pdf_path = 'tests/test_files/direct_and_image.pdf'
    texts = pdf_extracter(pdf_path)
    print(texts)
    ```
- Run by command line.
    ```bash
    $ rapidocr_pdf -h
    usage: rapidocr_pdf [-h] [-path FILE_PATH]

    options:
    -h, --help            show this help message and exit
    -path FILE_PATH, --file_path FILE_PATH
                            File path, PDF or images

    $ rapidocr_pdf -path tests/test_files/direct_and_image.pdf
    ```
### 3. Ouput format.
   - **Input**：`Union[str, Path, bytes]`
   - **Output**：`List` \[**Page num**, **Page content** + **score**\], ：
       ```python
       [
           ['0', '达大学拉斯维加斯分校）的一次中文评测中获得最', '0.8969868'],
           ['1', 'ABCNet: Real-time Scene Text Spotting with Adaptive Bezier-Curve Network∗\nYuliang Liu‡†', '0.8969868'],
       ]
       ```
