## RapidOCRPDF
<p>
    <a href=""><img src="https://img.shields.io/badge/Python->=3.7,<=3.10-aff.svg"></a>
    <a href=""><img src="https://img.shields.io/badge/OS-Linux%2C%20Win%2C%20Mac-pink.svg"></a>
</p>


- 依托于RapidOCR仓库，快速提取PDF中文字，包括扫描版PDF、加密版PDF。

### 使用
1. 安装`rapid_ocr_pdf`库
   ```bash
    pip install rapid_ocr_pdf
   ```
2. 使用方式
    ```bash
    python demo.py
    ```
   - **输入**：`Union[str, Path, bytes]`
   - **输出**：`List` \[**页码**, **文本内容** + **置信度**\]， 具体参见下例：
       ```python
       [
           ['0', '达大学拉斯维加斯分校）的一次中文评测中获得最', '0.8969868'],
           ['1', 'ABCNet: Real-time Scene Text Spotting with Adaptive Bezier-Curve Network∗\nYuliang Liu‡†', '0.8969868'],
       ]
       ```
