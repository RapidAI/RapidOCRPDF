# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.come
import os
import re
import sys

import setuptools


def extract_version(message: str) -> str:
    pattern = r'\d+\.(?:\d+\.)*\d+'
    matched_versions = re.findall(pattern, message)
    if matched_versions:
        return matched_versions[0]
    return ''


# 首先判断传入的列表长度，如果大于2，则说明有其他参数
# 否则，version是指定的tag值
if len(sys.argv) > 2:
    version = extract_version(''.join(sys.argv[2:]))
else:
    version = '1.0.0'
sys.argv = sys.argv[:2]

package_name = 'rapid_ocr_pdf'

os.system(f"""echo "version = '{version}'" >> {package_name}/__init__.py""")

setuptools.setup(
    name=package_name,
    version=version,
    platforms='Any',
    description='Tools of extracting PDF content based RapidOCR',
    author='SWHL',
    author_email='liekkaskono@163.com',
    install_requires=['opencv_python>=4.4.0.46',
                      'numpy>=1.19.5',
                      'filetype',
                      'pymupdf'],
    include_package_data=True,
    packages=[package_name],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.7,<=3.10',
    entry_points={
        'console_scripts': [f'{package_name}={package_name}.{package_name}:main'],
    }
)
