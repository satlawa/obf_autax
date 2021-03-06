'''
converts an image (numpy array) into text using ocr
'''
import cv2
import numpy as np
import pandas as pd
import pytesseract

from OCRData import OCRData
from OCRVision import OCRVision

class OCRPharse3(object):

    def __init__(self):

        self.wo_data = []
        self.bz = []
        self.text = []
        self.ma =[]


    def pharse_page(self, img):
        # create vision object
        ocr = OCRVision(img)

        wo = ocr.get_text('abt')
        print(wo)

        # use computer vison agorithms for ocr (filter red color)
        ocr.convert()
        # if page has an id (Waldort)
        if wo != "":
            # create data object with id (Waldort)
            data = OCRData(wo)

            # BKL
            txt = ocr.get_text('bkl')
            if txt != "":
                data.set_bkl(txt)
            # UZ
            txt = ocr.get_text('uz')
            if txt != "":
                data.set_uz(txt)
            # STOE
            txt = ocr.get_text('stoe')
            if txt != "":
                data.set_stoe(txt)
            # V-Typ
            txt = ocr.get_text('vtyp')
            if txt != "":
                data.set_vtyp(txt)
            # Verbissgrad
            txt = ocr.get_text('vg')
            if txt != "":
                data.set_vg(txt)
            # text
            txt = ocr.get_text('text')
            if txt != "":
                data.set_text(txt)
            # BZ
            txt = ocr.get_text('bz')
            if txt != "":
                data.set_bz(txt)
            # MA
            txt = ocr.get_text('mass')
            if txt != "":
                data.set_ma(txt)

            self.wo_data.append([data.wo, data.bkl, data.uz, data.stoe, data.vtyp, data.vg])
            self.text.append([data.wo, data.text1, data.text2, data.text3, data.text4, data.text5])
            self.bz.append([data.wo, data.bz1, data.bz2, data.bz3, data.bz4, data.bz5])
            self.ma.append([data.wo, data.ma1_sch, data.ma1_ma, data.ma1_fl, data.ma1_drg,\
            data.ma1_bew, data.ma1_ztp, data.ma1_sgr, data.ma1_ruk, data.ma1_text,\
            data.ma2_sch, data.ma2_ma, data.ma2_fl, data.ma2_drg,\
            data.ma2_bew, data.ma2_ztp, data.ma2_sgr, data.ma2_ruk, data.ma2_text,\
            data.ma3_sch, data.ma3_ma, data.ma3_fl, data.ma3_drg,\
            data.ma3_bew, data.ma3_ztp, data.ma3_sgr, data.ma3_ruk, data.ma3_text])
