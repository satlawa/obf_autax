'''
converts an image (numpy array) into text using ocr
'''
import cv2
import numpy as np
import pandas as pd
import pytesseract

from dataclasses import dataclass

class OCRData(object):

    def __init__(self, wo):

        self.wo = wo
        self.stoe = 0
        self.mass = 0
        self.text = 0
        self.nutz = 0


    def cut_feature(self, img, feature):
        '''
            cuts the desired part [cut_boundries] out of the image [self.img]
            in:     cut_boundries   (array with boundries)
            out:
        '''
        # cut image
        cut = self.dic[feature]
        return (img[cut[0]:cut[1], cut[2]:cut[3]])

@dataclass
class WOName:
    wo: str = ""

#    def check_attr(self):
#        if len(self.ma) != 2:
#            self.ma = ""

@dataclass
class WOAttr:
    bkl: int = 0
    uz: int = 0
    stoe: int = 0
    vtyp: str = ""
    wtyp: str = ""
    vg: int = 0
    fss: int = 0
    error: bool = False

    def check_attr(self):
        if (self.bkl < 0) | (self.bkl > 9999):
            self.bkl = 0
            error = True
        if (self.uz < 0) | (self.uz > 200):
            self.uz = 0
            error = True
        if not(self.stoe in [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 21, 22, 23, 25, 26, 27, 28, 31, 32, 33, 34, 35, 36, 37, 41, 42, 43, 44, 51, 52, 53, 54, 55, 56, 57, 58, 61, 62, 63, 64, 65, 66, 71, 72, 73, 74, 75, 76, 81, 82, 83, 84, 85, 86, 86, 87, 88, 89, 91, 92, 93, 94, 95, 96, 97, 98]):
            self.stoe = 0
            error = True
        if not(self.vtyp in [10,23,26,30,31,35,36,90]):
            self.vtyp = 0
            error = True
        if not(self.wtyp in [10,23,26,30,31,35,36,90]):
            self.wtyp = 0
            error = True
        if (self.vg < 0) | (self.vg > 5):
            self.vg = 0
            error = True
        if (self.fss < 0) | (self.fss > 1):
            self.fss = 0
            error = True


    #["FI", "TA", "LA", "KI", "SK", "ZI", "PM", "DG", "KW", "SF", "FO", "TH", "FB", "AC", "AG", "AZ", "EB", "FZ", "GK", "HT", "JL", "CJ", "KK", "KO", "AN", "AB", "CH", "PU", "SN", "BU", "EI", "HB", "AH", "SA", "FA", "EA", "ES", "UL", "QP", "QR", "EZ", "RE", "FE", "ER", "GE", "AV", "KB", "TK", "WO", "SG", "NU", "JN", "LI", "LS", "LW", "BI", "PO", "AS", "WP", "SP", "HP", "WD", "SW", "EK", "RK", "EE", "EL", "ME", "RO", "TB", "GB", "ST", "SL", "BL"]
    #[1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 21, 22, 23, 25, 26, 27, 28, 31, 32, 33, 34, 35, 36, 37, 41, 42, 43, 44, 51, 52, 53, 54, 55, 56, 57, 58, 61, 62, 63, 64, 65, 66, 71, 72, 73, 74, 75, 76, 81, 82, 83, 84, 85, 86, 86, 87, 88, 89, 91, 92, 93, 94, 95, 96, 97, 98]

@dataclass
class BZiel:
    line0: str = ""
    line1: str = ""
    line2: str = ""

    def check_attr(self):
        if (self.area < 0) | (self.area > 9999):
            self.area = 9010

@dataclass
class Text:
    line0: str = ""
    line1: str = ""
    line2: str = ""

    def check_attr(self):
        if (self.area < 0) | (self.area > 9999):
            self.area = 9010

@dataclass
class Nutz:
    ma: str = ""
    area: float = 0.0
    v_lh: float = 0.0
    v_nh: float = 0.0
    dring: int = 0
    behoerde: int = 0
    zeitp: int = 0
    schlaeg: int = 0
    rueck: int = 0
    text: str = ""
    error: bool = False

    def check_attr(self):
        self.check_ma()
        self.check_v()
        self.check_dring()
        self.check_behoerde()
        self.check_zeitp()
        self.check_schlaeg()
        self.check_rueck()
        self.check_for_error()

    def check_ma(self):
        if len(self.ma) != 2:
            self.ma = ""

    def check_v(self):
        if self.area < 0.0:
            self.area = 0.0
        if self.v_lh < 0.0:
            self.v_lh = 0.0
        if self.v_nh < 0.0:
            self.v_nh = 0.0

    def check_dring(self):
        if not(self.dring in [1,2,3,4,5]):
            self.dring = 0

    def check_behoerde(self):
        if not(self.behoerde in [1,2,3]):
            self.behoerde = 0

    def check_zeitp(self):
        if not(self.zeitp in [1,2,3]):
            self.zeitp = 0

    def check_schlaeg(self):
        if not(self.schlaeg in [1,2,3,4,5,6]):
            self.schlaeg = 0

    def check_rueck(self):
        if not(self.rueck in [10,23,26,30,31,35,36,90]):
            self.rueck = 0

    def check_for_error(self):
        if (self.ma == "") | (self.dring == 0)  | (self.behoerde == 0) | (self.zeitp == 0) | \
        (self.schlaeg == 0) | (self.rueck == 0):
            self.error = True
        else:
            self.error = False
