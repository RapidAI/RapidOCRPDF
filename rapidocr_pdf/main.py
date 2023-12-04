# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import argparse
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Union

import cv2
import filetype
import fitz
import numpy as np

try:
    from rapidocr_onnxruntime import RapidOCR
except:
    warnings.warn(
        "Can't find the rapidocr_onnxruntime module,"
        "try to import the rapidocr_openvino"
    )
    from rapidocr_openvino import RapidOCR


class PDFExtracter:
    def __init__(self, dpi=200, **ocr_kwargs):
        self.dpi = dpi
        self.text_sys = RapidOCR(**ocr_kwargs)
        self.empyt_list = []

    def __call__(
        self,
        content: Union[str, Path, bytes],
        force_ocr: bool = False,
    ) -> List[List[Union[str, str, str]]]:
        try:
            file_type = self.which_type(content)
        except (FileExistsError, TypeError) as e:
            raise PDFExtracterError("The input content is empty.") from e

        if file_type != "pdf":
            raise PDFExtracterError("The file type is not PDF format.")

        try:
            pdf_data = self.load_pdf(content)
        except PDFExtracterError as e:
            warnings.warn(str(e))
            return self.empyt_list

        txts_dict, need_ocr_idxs = self.extract_texts(pdf_data, force_ocr)

        page_img_dict = self.read_pdf_with_image(pdf_data, need_ocr_idxs)
        ocr_res_dict = self.get_ocr_res(page_img_dict)

        final_result = self.merge_direct_ocr(txts_dict, ocr_res_dict)
        return final_result

    @staticmethod
    def load_pdf(pdf_content: Union[str, Path, bytes]) -> bytes:
        if isinstance(pdf_content, (str, Path)):
            if not Path(pdf_content).exists():
                raise PDFExtracterError(f"{pdf_content} does not exist.")

            with open(pdf_content, "rb") as f:
                data = f.read()
            return data

        if isinstance(pdf_content, bytes):
            return pdf_content

        raise PDFExtracterError(f"{type(pdf_content)} is not in [str, Path, bytes].")

    def extract_texts(self, pdf_data: bytes, force_ocr: bool) -> Tuple[Dict, List]:
        texts, need_ocr_idxs = {}, []
        with fitz.open(stream=pdf_data) as doc:
            for i, page in enumerate(doc):
                if force_ocr:
                    need_ocr_idxs.append(i)
                    continue

                text = page.get_text()
                if text:
                    texts[str(i)] = text
                else:
                    need_ocr_idxs.append(i)
        return texts, need_ocr_idxs

    def read_pdf_with_image(self, pdf_data: bytes, need_ocr_idxs: List) -> Dict:
        def convert_img(page):
            pix = page.get_pixmap(dpi=self.dpi)
            img = np.frombuffer(pix.samples, dtype=np.uint8)
            img = img.reshape([pix.h, pix.w, pix.n])
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return img

        with fitz.open(stream=pdf_data) as doc:
            page_img_dict = {k: convert_img(doc[k]) for k in need_ocr_idxs}
        return page_img_dict

    def get_ocr_res(self, page_img_dict: Dict) -> Dict:
        ocr_res = {}
        for k, v in page_img_dict.items():
            preds, _ = self.text_sys(v)
            if preds:
                _, rec_res, _ = list(zip(*preds))
                ocr_res[str(k)] = "\n".join(rec_res)
        return ocr_res

    def merge_direct_ocr(self, txts_dict, ocr_res_dict):
        final_result = {**txts_dict, **ocr_res_dict}
        final_result = dict(sorted(final_result.items(), key=lambda x: int(x[0])))
        final_result = [[k, v, "1.0"] for k, v in final_result.items()]
        return final_result

    @staticmethod
    def which_type(content: Union[bytes, str, Path]) -> str:
        if isinstance(content, (str, Path)) and not Path(content).exists():
            raise FileExistsError(f"{content} does not exist.")

        kind = filetype.guess(content)
        if kind is None:
            raise TypeError(f"The type of {content} does not support.")

        return kind.extension


class PDFExtracterError(Exception):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-path", "--file_path", type=str, help="File path, PDF or images"
    )
    parser.add_argument(
        "-f",
        "--force_ocr",
        action="store_true",
        default=False,
        help="Whether to use ocr for all pages.",
    )
    args = parser.parse_args()

    pdf_extracter = PDFExtracter()

    result = pdf_extracter(args.file_path)
    print(result)


if __name__ == "__main__":
    main()
