'''
converts an image (numpy array) into text using ocr
'''
import cv2
import numpy as np
import pandas as pd
import pytesseract

class OCRData(object):

    def __init__(self, wo):

        self.wo = wo
        self.stoe =
        self.mass =
        self.


    def cut_feature(self, img, feature):
        '''
            cuts the desired part [cut_boundries] out of the image [self.img]
            in:     cut_boundries   (array with boundries)
            out:
        '''
        # cut image
        cut = self.dic[feature]
        return (img[cut[0]:cut[1], cut[2]:cut[3]])
