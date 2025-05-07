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

from .utils.logger import Logger
from .utils.utils import error_log, which_type

logger = Logger(logger_name=__name__).get_log()


class RapidOCRPDF:
    def __init__(self, dpi=200, ocr_params: Optional[Dict] = None):
        self.dpi = dpi
        self.ocr_engine = RapidOCR(params=ocr_params)
        self.empty_list = []

    def __call__(
        self,
        content: Union[str, Path, bytes],
        force_ocr: bool = False,
        page_num_list: Optional[List[int]] = None,
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
            logger.error("%s\n%s", e, error_log())
            return self.empty_list

        txts_dict, need_ocr_idxs = self.extract_texts(
            pdf_data, force_ocr, page_num_list
        )

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

    def extract_texts(
        self, pdf_data: bytes, force_ocr: bool, page_num_list: Optional[List[int]]
    ) -> Tuple[Dict, List]:
        texts, need_ocr_idxs = {}, []
        with fitz.open(stream=pdf_data) as doc:
            page_num_list = self.get_page_num_range(page_num_list, doc.page_count)
            for i, page in enumerate(doc):
                if page_num_list is not None and i not in page_num_list:
                    continue

                if force_ocr:
                    need_ocr_idxs.append(i)
                    continue

                text = page.get_text("text", sort=True)
                if text:
                    texts[i] = text
                else:
                    need_ocr_idxs.append(i)
        return texts, need_ocr_idxs

    @staticmethod
    def get_page_num_range(
        page_num_list: Optional[List[int]], page_count: int
    ) -> Optional[List[int]]:
        if page_num_list is None:
            return None

        if max(page_num_list) >= page_count:
            raise RapidOCRPDFError(
                f"The max value of {page_num_list} is greater than total page nums: {page_count}"
            )

        # support negative number
        new_page_num = []
        for page_num in page_num_list:
            if page_num >= 0:
                new_page_num.append(page_num)

            if abs(page_num) > page_count:
                raise RapidOCRPDFError(
                    f"{page_num} is out of range [{-page_count}, {page_count - 1})"
                )

            positive_num = page_count + page_num
            new_page_num.append(positive_num)

        return new_page_num

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

                ocr_res[i] = {
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


def parse_args(arg_list: Optional[List[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path", type=str)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument(
        "-f",
        "--force_ocr",
        action="store_true",
        default=False,
        help="Whether to use ocr for all pages.",
    )
    parser.add_argument(
        "--page_num_list",
        type=int,
        nargs="*",
        default=None,
        help="Which pages will be extracted. e.g. 0 1 2. Note: the index of page num starts from 0.",
    )
    args = parser.parse_args(arg_list)
    return args


def main(arg_list: Optional[List[str]] = None):
    args = parse_args(arg_list)
    pdf_extracter = RapidOCRPDF(args.dpi)
    try:
        result = pdf_extracter(args.pdf_path, args.force_ocr, args.page_num_list)
        print(result)
    except Exception as e:
        logger.error("%s\n%s", e, error_log())


if __name__ == "__main__":
    main()
