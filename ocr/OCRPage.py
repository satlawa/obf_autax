'''
converts an image (numpy array) into text using ocr
'''
import cv2
import numpy as np
import pandas as pd
import pytesseract

class OCRPage(object):

    def __init__(self, img):

        self.img = img
        self.img_thresh = img[:,:,0]
        self.dic = {'abt':[100, 250, 3400, 4000], \
                    'mass':[2242, 3070, 120, 4055], \
                    'bz':[1540, 1745, 2270, 4050], \
                    'text':[1810, 2200, 120, 4055], \
                    'stoe':[400, 560, 1550, 1900], \
                    'vtyp':[400, 560, 1920, 2250], \
                    'wtyp':[400, 560, 2280, 2600], \
                    'vg':[400, 560, 3000, 3340], \
                    'fss':[400, 560, 3700, 4050], \
                    'bkl':[100, 370, 2090, 2350], \
                    'uz':[100, 370, 2350, 2640]}


    def cut_feature(self, img, feature):
        '''
            cuts the desired part [cut_boundries] out of the image [self.img]
            in:     cut_boundries   (array with boundries)
            out:
        '''
        # cut image
        cut = self.dic[feature]
        return (img[cut[0]:cut[1], cut[2]:cut[3]])


    def filter_red_color(self, img):
        '''
            * private *
            filter just red color
            in:     im          (RGB image)
            out:    output_img  (red filterd image)
        '''
        # convert to hsv
        img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        # lower mask (0-10)
        lower_red = np.array([0,50,50])
        upper_red = np.array([10,255,255])
        mask0 = cv2.inRange(img_hsv, lower_red, upper_red)
        # upper mask (170-180)
        lower_red = np.array([170,50,80])
        upper_red = np.array([180,255,255])
        mask1 = cv2.inRange(img_hsv, lower_red, upper_red)
        ## Merge the mask and crop the red regions
        mask = cv2.bitwise_or(mask0, mask1)
        croped = cv2.bitwise_and(img_hsv, img_hsv, mask=mask)

        return(croped)


    def thresh(self, img):
        # convert RGB to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # threshold
        ret, img_thr = cv2.threshold(img_gray, 90, 255, cv2.THRESH_BINARY_INV)

        return(img_thr)


    def ocr(self, img):
        # Adding custom options for ocr
        custom_config = r'--oem 3 --psm 6'
        # retreving text from threshholded image
        text = pytesseract.image_to_string(img, config=custom_config)

        return(text)


    def convert(self):
        img_filter = self.filter_red_color(self.img)
        self.img_thresh = self.thresh(img_filter)


    def get_text(self, feature):
        img_cut = self.cut_feature(self.img_thresh, feature)
        text = self.ocr(img_cut)

        return(text)
