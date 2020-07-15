'''
converts an image (numpy array) into text using ocr
'''
import numpy as np
import pandas as pd

from OCRPage import OCRPage

class OCRPharse(object):

    def __init__(self, page):
        # input: object of OCRPage
        self.page = page
        self.dic_ma = {'MA':0}
        self.row_info = []

    def set_mass_struc(self, dic_ma, dic_wp={'MA':0}):
        # exp: {'S':0, 'MA':1, 'FL':0, 'LH':1, 'NH':1, 'SUM':0, 'DR':1, 'BH':1, 'ZP':1, 'SG':1, 'RU':1}
        self.dic_ma = dic_ma
        self.dic_wp = dic_wp


    def get_abt(self):
        abt = self.page.get_text_abt()
        # clean errors
        abt = self.clean_errors_abt(abt)

        return(abt)

    def get_text(self):
        # get text
        txt = ocr.get_text('text')
        # split lines
        txt = txt.splitlines()
        #replace common mistakes
        txt[1].replace('El', 'EI')
        txt[1].replace('Kl', 'KI')
        txt[1].replace('Zl', 'ZI')

        return(txt)

    def get_mass(self):
        z = []
        ma = self.page.get_text('mass')

        if ma:
            data = self.split_lines(ma)
            print(data)

            for idx, typ in enumerate(self.row_info):
                print(idx, typ)
                if typ == 'nutz':

                    # get coordinates of characters
                    rec_fil,rows_pos = self.page.get_char_positions()

                    # filter only nutzungs row
                    rec_fil_fil = rec_fil[np.where((rec_fil[:,1] <= rows_pos[idx]*1.05) & (rec_fil[:,1] >= rows_pos[idx]*0.95))]
                    data_nutz = data[idx]

                    distances, idx_comma = self.get_dist_char(data, self.dic_ma, rec_fil_fil, rows_pos[idx], self.row_info)

                    z.append(self.from_string(data[idx], self.dic_ma, distances[0], idx_comma, typ))

                elif (typ == 'text') & (idx != 0):
                    z[-1]['Text'] = data[idx]

            return(z)

################################################################################
# mass helper functions
    def split_lines(self, ma):
        '''
        ma massnahme in text format
        dic_ma has to be set
        '''

        # check if dic_ma is set
        if self.dic_ma['MA'] > 0:
            ma = ma.splitlines()


            self.row_info = []
            for i in range(len(ma)):
                ma_typ = ma[i][self.dic_ma['S']:self.dic_ma['S']+2]
                print(ma_typ)
                if ('1' in ma_typ) | ('I' in ma_typ) | ('1' in ma_typ):
                    ma[i] = ma[i][:self.dic_ma['S']] + 'LI' + ma[i][self.dic_ma['S']+2:]
                    print('change', ma[i])

                if ma[i][self.dic_ma['S']:self.dic_ma['S']+2] in ["DE", "DF", "RM", "LI", "AD", "KH"]:
                    ma[i] = ma[i].replace(" ", "")
                    ma[i] = ma[i].replace(",", "")
                    ma[i] = ma[i].replace("O", "")
                    self.row_info.append("nutz")
                elif ma[i][self.dic_ma['S']:self.dic_ma['S']+2] in ["DP", "JP", "KE", "KF"]:
                    ma[i] = ma[i].replace(" ", "")
                    ma[i] = ma[i].replace(",", "")
                    ma[i] = ma[i].replace("O", "")
                    self.row_info.append("wp")
                else:
                    ma[i] = ma[i].replace("Bl", "BI")
                    ma[i] = ma[i].replace("El", "EI")
                    ma[i] = ma[i].replace("Kl", "KI")
                    ma[i] = ma[i].replace("Ll", "LI")
                    ma[i] = ma[i].replace("Zl", "ZI")
                    self.row_info.append("text")
        else:
# TODO implement error
            pass

        return(ma)


    def get_comma(self, rec):
        rec.view('i8,i8,i8,i8').sort(order=['f0'], axis=0)
        idx = np.where((rec[:,3] < rec_max_hight/2.8) & (rec[:,3] > rec_max_hight/3.2))
        return idx[0]


    def get_dist_char(self, data, dic_ma, rec, rows_pos, info):
        '''
        get distances between characters
        dic_ma = {'S':0, 'MA':1, 'FL':1, 'LH':1, 'NH':1, 'SUM':0, 'DR':1, 'BH':0, 'ZP':1, 'SG':1, 'RU':1}
        string = 'DF13,8700023435'
        '''
        distances = []
        ### get info about structure
        len_1 = dic_ma['S'] + dic_ma['MA']*2
        len_2 = dic_ma['DR'] + dic_ma['BH'] + dic_ma['ZP'] + dic_ma['SG'] + dic_ma['RU']*2

        #for i, line in enumerate(data):
            # filter only nutzungs row
            #if info[i] == 'nutz':
                #rec = rec_fil[np.where(rec_fil[:,1] == rows_pos[i])]

        # sort
        rec.view('i8,i8,i8,i8').sort(order=['f0'], axis=0)

        rec_max_hight = rec[:,3].max()

        # get comma
        idx_comma = np.where((rec[:,3] < rec_max_hight/2.8) & (rec[:,3] > rec_max_hight/3.2))[0] - len_1 - 1

        rec = rec[np.where(rec[:,3] > rec_max_hight/2)]

        # filter just relevant
        rec = rec[len_1:-len_2]

        width_m = np.median(rec[:,2,])
        pos_x = rec[:,0,].copy()
        dist = pos_x[1:] - (pos_x[:-1]+int(width_m))

        thresh = self.otsu(dist)

        thisdict = {"dist": dist, "thresh": thresh}
        distances.append(thisdict)

        return distances, idx_comma


    def pharse_string(self, string, dist, thresh_val, idx_comma):
        '''
        pharse string into usable variables based on the distance between the characters
        input:  string = '13,87000'
                dist = np.array([ 5, 17, 19,  7,  6, 20])
        output: mass = ['13,8', '700', '0']
        '''
        # list of variables
        mass = []
        # if comma is detected swich to 1
        comma = 0
        # temporary helper variable
        save = string[0]
        # loop over char in string
        for i, char in enumerate(string[1:]):
            # if char is comma -> add char and reuse dist on ith position
            if i in idx_comma:
                save = save + ',' + char
                dist[i] = 0
                comma += 1
            # check if current dist is bigger than threshold -> add to list of variables
            else:
                if dist[i] <= thresh_val:
                    save = save + char
                else:
                    mass.append(save)
                    save = char
        # add last variable
        mass.append(save)

        return mass


    def from_string(self, ma_as_str, dic_ma, distances, idx_comma, typ):
        # TYP
        # first 2 -> Maßnahme
        # last 6 -> Nutzcode

        dic_ = {'S':0, 'MA':0, 'FL':0, 'LH':0, 'NH':0, 'SUM':0, 'DR':0, 'BH':0, 'ZP':0, 'SG':0, 'RU':0}

        #len_tech = dic_ma['DR'] + dic_ma['BH'] + dic_ma['ZP'] + dic_ma['SG'] + dic_ma['RU']*2

        # set Schicht (S)
        if dic_ma['S']:
            dic_['S'] = ma_as_str[:dic_ma['S']]

        # set Maßnahme (MA)
        if dic_ma['MA']:
            dic_['MA'] = ma_as_str[dic_ma['S']:dic_ma['S']+2]

        pos = 0

        if typ == 'nutz':
            # set Rückung (RU)
            if dic_ma['RU']:
                pos = -2
                dic_['RU'] = ma_as_str[pos:]

            # set Schlägerung (SG), Zeitpunkt (ZP), Behörde (BH), Dringlichkeit (DR)
            for i in ['SG', 'ZP', 'BH', 'DR']:
                if dic_ma[i]:
                    pos -= 1
                    dic_[i] = ma_as_str[pos:pos+1]

            #print(ma_as_str[dic_ma['S']+2:pos])
            #print(distances["dist"])

            # pharse FL - LH - NH string
            data_ma = self.pharse_string(ma_as_str[dic_ma['S']+2:pos], distances["dist"], distances["thresh"],idx_comma)
            print(data_ma)

            # set Fläche (FL), Laubholz (LH), Nadelholz (NH), Summe (SUM)
            cur = 0
            for typ in ['FL', 'LH', 'NH', 'SUM']:
                if dic_ma[typ]:
                    dic_[typ] = data_ma[cur]
                    cur += 1

# TODO implement flaähe for wp
        elif typ == 'wp':
            for i in ['ZP', 'BH', 'DR']:
                if dic_ma[i]:
                    pos -= 1
                    dic_[i] = ma_as_str[pos:pos+1]


        return dic_


################################################################################


    def clean_errors_abt(self, text):
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


    def otsu(self, gray):
        '''
            otsu algorithm for finding the best threshold value
        '''
        pixel_number = gray.shape[0]
        mean_weigth = 1.0/pixel_number
        his, bins = np.histogram(gray, np.array(range(0, np.max(gray)+1)))
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
