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
        '''
            threshold filterd image
        '''
        # convert RGB to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # threshold
        ret, img_thr = cv2.threshold(img_gray, 90, 255, cv2.THRESH_BINARY_INV)

        return(img_thr)


    def ocr(self, img):
        '''
            apply tesseracts OCR to obtain text for the german language
        '''
        # Adding custom options for ocr
        custom_config = r'-l deu --oem 3 --psm 6'
        # retreving text from threshholded image
        text = pytesseract.image_to_string(img, config=custom_config)

        return(text)


    def convert(self): # public
        '''
            prepere image for applying OCR
        '''
        # filter red colour
        img_filter = self.filter_red_color(self.img)
        # threshhold
        self.img_thresh = self.thresh(img_filter)


    def get_text(self, feature): # public
        '''
            apply OCR on filterd and thresholded image
        '''
        # cut area with information from thresholded image
        img_cut = self.cut_feature(self.img_thresh, feature)
        # apply tesseracts OCR to obtain text
        text = self.ocr(img_cut)

        return(text)


    def get_spaces(self): # public
        '''
            get spaces between maßnahmen code
        '''
        # invert binary
        img = cv2.bitwise_not(self.img_thresh)
        # cut the mass
        img = self.cut_feature(img, "mass")
        # get boundries of detected characters
        rects = self.find_objects(img)
        # convert to numpy array
        rects = np.asarray(rects)

### TODO dont filter commas

        # filter noise (small points)
        rec_fil = rects[rects[:,3] > np.mean(rects[:,3])/2]
        # get amount of Nutzungsmaßnahmen
        rec_fil[:,1] = rec_fil[:,1] + rec_fil[:,3]
        # get unique row positions
        rows_pos = np.sort(np.unique(rec_fil[:,1]))

        spaces = []

        for i in range(0, rows_pos.size-1, 2):
            # filter only nutzungs row
            rec_fil_fil = rec_fil[np.where(rec_fil[:,1] == rows_pos[i])]
            # invert array on first column
            rec_fil_fil.view('i8,i8,i8,i8').sort(order=['f1'], axis=0)
            # position of char on x-axis -> column 0
            pos_x = rec_fil_fil[:,0,].copy()
            # median width > column 2
            width_m = np.median(rec_fil_fil[:,2,])
            # space (pixels) between characters
            diff = pos_x[1:] - (pos_x[:-1]+int(width_m))
            # use otsu algorithm to obtain the best threshold value
            thresh_val = self.otsu(diff)

            diff[np.where(diff < thresh_val)] = 0
            diff[np.where(diff >= thresh_val)] = 1

            spaces.append(diff)

### TODO add possibitity for 2 or more Maßnahmen and one without text

        ## search for commas
        # get Maßnahme
        mass = self.get_text("mass")
        mass = mass.splitlines()
    ### TODO
        # find commas
        idx_comma = mass[0].find(',')
        # change space to no space
        spaces[0][idx_comma-1] = 0
        # add no space, since comma is not recognised as char
        spaces[0] = np.insert(spaces[0],3,0)

        return(spaces)


    def find_objects(self, img):
        '''
            * private *
            find objects in image
            in:     self.img           (grayscale image)
            out:    rects           (coordinates of detected objects)
        '''
        # Find contours in the image
        im2, ctrs, hier = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Get rectangles contains each contour
        rects = [cv2.boundingRect(ctr) for ctr in ctrs]

        return(rects)


    def otsu(self, gray):
        '''
            otsu algorithm for finding the best threshold value
        '''
        pixel_number = gray.shape[0]
        mean_weigth = 1.0/pixel_number
        his, bins = np.histogram(gray, np.array(range(0, np.max(gray))))
        final_thresh = -1
        final_value = -1
        for t in bins[1:-1]: # This goes from 1 to 254 uint8 range (Pretty sure wont be those values)
            Wb = np.sum(his[:t]) * mean_weigth
            Wf = np.sum(his[t:]) * mean_weigth

            mub = np.mean(his[:t])
            muf = np.mean(his[t:])

            value = Wb * Wf * (mub - muf) ** 2

            if value > final_value:
                final_thresh = t
                final_value = value

        return(final_thresh)
