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

from .utils import import_package


class PDFExtracter:
    def __init__(self, dpi=200, **ocr_kwargs):
        self.dpi = dpi

        ocr_engine = import_package("rapidocr_onnxruntime")
        if ocr_engine is None:
            ocr_engine = import_package("rapidocr_openvino")

            if ocr_engine is None:
                ocr_engine = import_package("rapidocr_paddle")

                if ocr_engine is not None:
                    ocr_kwargs.update({
                        "det_use_cuda": True,
                        "cls_use_cuda": True,
                        "rec_use_cuda": True
                    })
                else:
                    raise ModuleNotFoundError(
                        "Can't find the rapidocr_onnxruntime/rapidocr_openvino/rapidocr_paddle package.\n Please pip install rapidocr_onnxruntime to run the code."
                    )

        self.text_sys = ocr_engine.RapidOCR(**ocr_kwargs)
        self.empty_list = []

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
            return self.empty_list

        txts_dict, need_ocr_idxs = self.extract_texts(pdf_data, force_ocr)

        ocr_res_dict = self.get_ocr_res_streaming(pdf_data, need_ocr_idxs)

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

                text = page.get_text("text", sort=True)
                if text:
                    texts[str(i)] = text
                else:
                    need_ocr_idxs.append(i)
        return texts, need_ocr_idxs

    def get_ocr_res_streaming(self, pdf_data: bytes, need_ocr_idxs: List) -> Dict:
        def convert_img(page):
            pix = page.get_pixmap(dpi=self.dpi)
            img = np.frombuffer(pix.samples, dtype=np.uint8)
            img = img.reshape([pix.h, pix.w, pix.n])
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return img

        ocr_res = {}
        with fitz.open(stream=pdf_data) as doc:
            for i in need_ocr_idxs:
                img = convert_img(doc[i])
                preds, _ = self.text_sys(img)
                if preds:
                    text = []
                    confidences = []
                    for pred in preds:
                        _, rec_res, confidence = pred
                        text.append(rec_res)
                        confidences.append(float(confidence))

                    avg_confidence = np.mean(confidences) if confidences else 0.0
                    ocr_res[str(i)] = {
                        "text": "\n".join(text),
                        "avg_confidence": avg_confidence
                    }
        return ocr_res

    def merge_direct_ocr(self, txts_dict: Dict, ocr_res_dict: Dict) -> List[List[str]]:
        final_result = {}
        for page_idx, text in txts_dict.items():
            final_result[page_idx] = {"text": text, "avg_confidence": "N/A"}

        for page_idx, ocr_data in ocr_res_dict.items():
            final_result[page_idx] = {
                "text": ocr_data["text"],
                "avg_confidence": ocr_data["avg_confidence"]
            }

        final_result = dict(sorted(final_result.items(), key=lambda x: int(x[0])))
        return [[k, v["text"], str(v["avg_confidence"])] for k, v in final_result.items()]

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

    try:
        result = pdf_extracter(args.file_path, args.force_ocr)
        print(result)
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
