# -*- encoding: utf-8 -*-
# @Author:  SWHL
# @Contact: liekkaskono@163.com
import sys
import warnings
from typing import List

import setuptools
from get_pypi_latest_version import GetPyPiLatestVersion


def read_txt(txt_path: str) -> List:
    if not isinstance(txt_path, str):
        txt_path = str(txt_path)

    with open(txt_path, "r", encoding="utf-8") as f:
        data = list(map(lambda x: x.rstrip("\n"), f))
    return data


def get_readme():
    readme_path = "./docs/docs.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()
    return readme


MODULE_NAME = "rapidocr_pdf"
VERSION_NUM = "0.0.1"

obtainer = GetPyPiLatestVersion()
try:
    latest_version = obtainer(MODULE_NAME)
    if latest_version:
        VERSION_NUM = obtainer.version_add_one(latest_version)

    if len(sys.argv) > 2:
        match_str = " ".join(sys.argv[2:])
        matched_versions = obtainer.extract_version(match_str)
        if matched_versions:
            VERSION_NUM = matched_versions
except ValueError:
    warnings.warn(
        f"The package {MODULE_NAME} seems to be submitting for the first time."
    )

sys.argv = sys.argv[:2]

setuptools.setup(
    name=MODULE_NAME,
    version=VERSION_NUM,
    platforms="Any",
    description="Tools of extracting PDF content based on RapidOCR",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    author="SWHL",
    author_email="liekkaskono@163.com",
    url="https://github.com/RapidAI/RapidOCRPDF",
    license="Apache-2.0",
    packages=[MODULE_NAME],
    install_requires=read_txt("requirements.txt"),
    keywords=["rapidocr_pdf,rapidocr_onnxruntime,ocr,onnxruntime,openvino"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6,<3.12",
    entry_points={
        "console_scripts": [f"{MODULE_NAME}={MODULE_NAME}.main:main"],
    },
    extras_require={
        "onnxruntime": ["rapidocr_onnxruntime"],
        "openvino": ["rapidocr_openvino"],
    },
)
