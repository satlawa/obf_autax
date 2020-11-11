'''
converts an image (numpy array) into text using ocr
'''
import cv2
import numpy as np
import pandas as pd
import pytesseract

from dataclasses import dataclass
from typing import List

class OCRData(object):

    def __init__(self, wo):

        self.wo = self.clean_wo(wo)

        self.bkl = 0
        self.uz = 0

        self.stoe = 0

        self.vtyp = ""

        self.bz1 = ""
        self.bz2 = ""
        self.bz3 = ""
        self.bz4 = ""
        self.bz5 = ""

        self.text1 = ""
        self.text2 = ""
        self.text3 = ""
        self.text4 = ""
        self.text5 = ""

        self.ma1_sch = ""
        self.ma1_ma = ""
        self.ma1_fl = ""
        self.ma1_drg = ""
        self.ma1_bew = ""
        self.ma1_ztp = ""
        self.ma1_sgr = ""
        self.ma1_ruk = ""
        self.ma1_text = ""

        self.ma2_sch = ""
        self.ma2_ma = ""
        self.ma2_fl = ""
        self.ma2_drg = ""
        self.ma2_bew = ""
        self.ma2_ztp = ""
        self.ma2_sgr = ""
        self.ma2_ruk = ""
        self.ma2_text = ""

        self.ma3_sch = ""
        self.ma3_ma = ""
        self.ma3_fl = ""
        self.ma3_drg = ""
        self.ma3_bew = ""
        self.ma3_ztp = ""
        self.ma3_sgr = ""
        self.ma3_ruk = ""
        self.ma3_text = ""

        self.vg = 0


    def set_bkl(self, bkl):
        '''
            sets the BKL (int) from a text string
            in:     bkl   (string)
        '''
        self.bkl = int(self.clean_digits(bkl))


    def set_uz(self, uz):
        '''
            sets the UZ (int) from a text string
            in:     uz   (string)
        '''
        self.uz = int(self.clean_digits(uz))


    def set_stoe(self, stoe):
        '''
            sets the STOE (int) from a text string
            in:     stoe   (string)
        '''
        self.stoe = int(self.clean_digits(stoe))


    def set_vtyp(self, vtyp):
        '''
            sets the V-Typ (int) from a text string
            in:     vtyp   (string)
        '''
        self.vtyp = self.clean_text(vtyp)


    def set_bz(self, bz_all):
        '''
            sets the BZ (parts bz1 to bz5) from a text string
            in:     text   (string)
        '''
        # split BZ into parts
        bz_all = bz_all.split()
        # limit the parts to 5 BZ
        bz_all = bz_all[:5]
        # loop over all parts
        for i, bz_part in enumerate(bz_all):
            # clean falsely classifid characters
            part = self.clean_errors_bz(bz_part)
            # set BZs
            if i == 0:
                self.bz1 = part
                #print('bz1 = ' + self.bz1)
            elif i == 1:
                self.bz2 = part
                #print('bz2 = ' + self.bz2)
            elif i == 2:
                self.bz3= part
                #print('bz3 = ' + self.bz3)
            elif i == 3:
                self.bz4 = part
                #print('bz4 = ' + self.bz4)
            elif i == 4:
                self.bz5 = part
                #print('bz5 = ' + self.bz5)


    def set_text(self, txts):
        # split lines
        txts = txts.splitlines()
        # loop over all lines
        for i, txt in enumerate(txts):
            # correct the beging of the lines
            txt = txt.replace('ST ', 'ST   ')
            txt = txt.replace('BE ', 'BE   ')
            txt = txt.replace('MA ', 'MA   ')

            if i == 0:
                self.text1 = txt
            elif i == 1:
                self.text2 = txt
            elif i == 2:
                self.text3= txt
            elif i == 3:
                self.text4 = txt
            elif i == 4:
                self.text5 = txt


    def set_ma(self, ma_all):
        # split lines
        ma_all = ma_all.splitlines()
        # remove false lines
        if '' in ma_all:
            ma_all.remove('')
        # enumerator
        enum = 0
        # loop over all lines
        for ma_text in ma_all:
            # remove spaces
            ma = ma_text.replace(" ", "")
            # check if the string is at least 3 chars long
            if len(ma) > 2:
                # if it's a Massnahme
                if (ma[0] in ['1', '2', '3', '4']) &\
                 (ma[1:3] in ['AD', 'AE', 'AF', 'AG', 'AS', 'BU', 'DE', 'DF', 'DP',\
                 'EG', 'FM', 'JF', 'JP', 'KE', 'KF', 'KH', 'LI', 'LL', 'NB', 'ND',\
                 'PA', 'PL', 'RM', 'SB', 'TR', 'UE', 'ZE', 'ZN', 'ZV']):
                    enum += 1

                    if enum == 1:
                        self.ma1_sch = ma[0]
                        self.ma1_ma = ma[1:3]
                        self.ma1_fl = ma[3:ma.find(',')+2]
                        self.ma1_drg = ma[-6:-5]
                        self.ma1_bew = ma[-5:-4]
                        self.ma1_ztp = ma[-4:-3]
                        self.ma1_sgr = ma[-3:-2]
                        self.ma1_ruk = ma[-2:]
                    elif enum == 2:
                        self.ma2_sch = ma[0]
                        self.ma2_ma = ma[1:3]
                        self.ma2_fl = ma[3:ma.find(',')+2]
                        self.ma2_drg = ma[-6:-5]
                        self.ma2_bew = ma[-5:-4]
                        self.ma2_ztp = ma[-4:-3]
                        self.ma2_sgr = ma[-3:-2]
                        self.ma2_ruk = ma[-2:]
                    elif enum == 3:
                        self.ma3_sch = ma[0]
                        self.ma3_ma = ma[1:3]
                        self.ma3_fl = ma[3:ma.find(',')+2]
                        self.ma3_drg = ma[-6:-5]
                        self.ma3_bew = ma[-5:-4]
                        self.ma3_ztp = ma[-4:-3]
                        self.ma3_sgr = ma[-3:-2]
                        self.ma3_ruk = ma[-2:]
                else:
                    if enum == 1:
                        self.ma1_text = ma_text
                    elif enum == 2:
                        self.ma2_text = ma_text
                    elif enum == 3:
                        self.ma3_text = ma_text


    def set_vg(self, vg):
        '''
            sets the Verbissgrad (int) from a text string
            in:     vtg   (string)
        '''
        self.vg = self.clean_digits(vg)


    def clean_errors_bz(self, text):
        '''
            cuts the desired part [cut_boundries] out of the image [self.img]
            in:     text   (string)
            out:    text   (string)
        '''
        # eliminate spaces
        text = text.replace(" ", "")
        # replace falsely classified letters with digits
        digit = self.clean_digits(text[0])
        # replace falsely classified digits with letters
        ba = self.clean_text(text[1:])
        # correct the structure
        text = digit + ' ' + ba

        return text


    def clean_digits(self, text):

        if 'I' in text:
            text = text.replace('I','1')
        if 'l' in text:
            text = text.replace('l','1')
        if 't' in text:
            text = text.replace('t','1')
        if '|' in text:
            text = text.replace('|','1')
        if 'O' in text:
            text = text.replace('O','0')
        if 'S' in text:
            text = text.replace('S','5')
        if 'B' in text:
            text = text.replace('B','8')

        return text


    def clean_text(self, text):

        if '1' in text:
            text = text.replace('1','I')
        if '|' in text:
            text = text.replace('|','I')
        if '0' in text:
            text = text.replace('0','O')
        if '5' in text:
            text = text.replace('5','S')
        if '8' in text:
            text = text.replace('8','B')

        return text


    def clean_wo(self, text):
        text = text.replace(" ", "")

        if text[3] == '1':
            text = text[:3] + 'I' + text[4:]
        elif text[3] == '|':
            text = text[:3] + 'I' + text[4:]
        elif text[3] == '0':
            text = text[:3] + 'O' + text[4:]
        if text[4] == 'I':
            text = text[:4] + '1'
        elif text[4] == 'l':
            text = text[:4] + '1'
        elif text[4] == 't':
            text = text[:4] + '1'
        elif text[4] == 'O':
            text = text[:4] + '0'

        return(text)


#################################################################################


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
        if not(self.vtyp in ["A", "AH", "AHD", "AL", "AM", "B", "BH", "BR", "BS", "BW", "C", "CP", "CS", "E", "EHR", "EWV", "FW", "GE", "HA", "HD", "HM", "HS", "HU", "HW", "K", "KB", "KV", "KW", "LS", "MV", "OPV", "PF", "PH", "PK", "PM", "S", "SBS", "SF", "SH", "SI", "SK", "SL", "SN", "SR", "SS", "SSO", "SW", "TH", "THD", "VGR", "W", "WE", "WG", "WS", "WW"]):
            self.vtyp = 0
            error = True
        if not(self.wtyp in ["AU", "EI", "ED", "SK", "WK", "DG", "BU", "LNF", "LNK", "FITA", "FI", "FILA", "ZI", "LAZI", "SW"]):
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
class BAZiel:
    part: int = 0
    ba: str = ""
    error: bool = False

    def check_attr(self):
        if (self.part < 0) | (self.part > 10):
            self.part = 0
            self.error = True
        if not(self.ba in ["FI", "TA", "LA", "KI", "SK", "ZI", "PM", "DG", "KW", "SF", "FO", "TH", "FB", "AC", "AG", "AZ", "EB", "FZ", "GK", "HT", "JL", "CJ", "KK", "KO", "AN", "AB", "CH", "PU", "SN", "BU", "EI", "HB", "AH", "SA", "FA", "EA", "ES", "UL", "QP", "QR", "EZ", "RE", "FE", "ER", "GE", "AV", "KB", "TK", "WO", "SG", "NU", "JN", "LI", "LS", "LW", "BI", "PO", "AS", "WP", "SP", "HP", "WD", "SW", "EK", "RK", "EE", "EL", "ME", "RO", "TB", "GB", "ST", "SL"]):
            self.ba = ""
            self.error = True

    @classmethod
    def from_string(cls, bz_all):
        print(bz_all)
        part = int(bz_all[:-2])
        print(part)
        ba = bz_all[-2:]
        print(ba)
        return cls(part, ba)


@dataclass
class BestZiel:
    bz: List[BAZiel]
    error: bool = False

    def check_attr(self):
        sum_parts = 0
        for b in self.bz:
            sum_parts += b.part
        if (sum_parts != 10):
            self.error = True

    @classmethod
    def from_string(cls, bz_alling):
        bz_as_list = bz_alling.split()
        bzs = []
        for bz_unit in bz_as_list:
            bz_BAZ = BAZiel.from_string(bz_unit)
            bz_BAZ.check_attr()
            bzs.append(bz_BAZ)
        return cls(bzs)


@dataclass
class Text:
    line0: str = ""
    line1: str = ""
    line2: str = ""

    @classmethod
    def from_string(cls, text_as_str):
        text_as_list = text_as_str.splitlines()
        for i in range(3-len(text_as_list)):
            text_as_list.append("")
        line0, line1, line2 = text_as_list
        text = cls(line0, line1, line2)
        return text


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

    @classmethod
    def from_string(cls, ma_as_str, spaces):

        ma = ma_str.splitlines()

        l = []
        ch = ""

        for i in range(len(ma[0])):

            if i == 0:
                ch = ma[0][i]
            elif i == len(ma[0])-1:
                l.append(ch + ma[0][i])
            elif spaces[0][i-1] == 0:
                ch = ch + ma[0][i]
            elif spaces[0][i-1] == 1:
                l.append(ch)
                ch = ma[0][i]
        l.append(ma[1])

        first_name, last_name = map(str, name_str.split(' '))
        student = cls(first_name, last_name)
        return student
