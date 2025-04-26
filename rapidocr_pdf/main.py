# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import cv2
import fitz
import numpy as np
from rapidocr import RapidOCR

from .logger import Logger
from .utils import which_type


class RapidOCRPDF:
    def __init__(self, dpi=200, ocr_params: Optional[Dict] = None):
        self.dpi = dpi
        self.ocr_engine = RapidOCR(params=ocr_params)
        self.empty_list = []
        self.logger = Logger(logger_name=__name__).get_log()

    def __call__(
        self, content: Union[str, Path, bytes], force_ocr: bool = False
    ) -> List[List[Union[str, str, str]]]:
        try:
            file_type = which_type(content)
        except (FileExistsError, TypeError) as e:
            raise RapidOCRPDFError("The input content is empty.") from e

        if file_type != "pdf":
            raise RapidOCRPDFError("The file type is not PDF format.")

        try:
            pdf_data = self.load_pdf(content)
        except RapidOCRPDFError as e:
            self.logger.error(e)
            return self.empty_list

        txts_dict, need_ocr_idxs = self.extract_texts(pdf_data, force_ocr)

        ocr_res_dict = self.get_ocr_res_streaming(pdf_data, need_ocr_idxs)

        final_result = self.merge_direct_ocr(txts_dict, ocr_res_dict)
        return final_result

    @staticmethod
    def load_pdf(pdf_content: Union[str, Path, bytes]) -> bytes:
        if isinstance(pdf_content, (str, Path)):
            if not Path(pdf_content).exists():
                raise RapidOCRPDFError(f"{pdf_content} does not exist.")

            with open(pdf_content, "rb") as f:
                data = f.read()
            return data

        if isinstance(pdf_content, bytes):
            return pdf_content

        raise RapidOCRPDFError(f"{type(pdf_content)} is not in [str, Path, bytes].")

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

                preds = self.ocr_engine(img)
                if preds.txts is None:
                    continue

                avg_score = (
                    sum(preds.scores) / len(preds.scores) if preds.scores else 0.0
                )

                ocr_res[str(i)] = {
                    "text": "\n".join(preds.txts),
                    "avg_confidence": avg_score,
                }
        return ocr_res

    def merge_direct_ocr(self, txts_dict: Dict, ocr_res_dict: Dict) -> List[List[str]]:
        final_result = {}
        for page_idx, text in txts_dict.items():
            final_result[page_idx] = {"text": text, "avg_confidence": "N/A"}

        for page_idx, ocr_data in ocr_res_dict.items():
            final_result[page_idx] = {
                "text": ocr_data["text"],
                "avg_confidence": ocr_data["avg_confidence"],
            }

        final_result = dict(sorted(final_result.items(), key=lambda x: int(x[0])))
        return [[k, v["text"], v["avg_confidence"]] for k, v in final_result.items()]


class RapidOCRPDFError(Exception):
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

    pdf_extracter = RapidOCRPDF()

    try:
        result = pdf_extracter(args.file_path, args.force_ocr)
        print(result)
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
