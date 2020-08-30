'''
******************************************************************************************
Filter age per Waldort

input --> tab separated file (.xls) raw data from SAP
output --> comma seperated file (.csv) table with age of the forest stands (Waldorte)
******************************************************************************************
'''

import os
import numpy as np
import pandas as pd
import multiprocessing as mp

class OBFEkl(object):

    def __init__(self, input_path_height, input_path_age, input_path_ekl):

        self.height_data = pd.read_csv(input_path_height, sep=',', error_bad_lines=False) # encoding = "ISO-8859-1"
        self.alter_data = pd.read_csv(input_path_age, sep=',', error_bad_lines=False)
        self.et_data = np.genfromtxt(input_path_ekl, delimiter=',')
        self.mass_data = pd.DataFrame(columns=['wo', 'v', 'area'])

        self.ba_list = [[1,"fi"],[6,"ta"],[7,"la"],[9,"bu"]]


    def set_im_vor(self, path):
        # set bimass data from image matching
        self.mass_data = pd.read_csv(path, sep=',', error_bad_lines=False)


    def set_ba(self, ba_list):
        self.ba_list = ba_list


    def get_ba(self):
        return self.ba_list


    def print_et(self):
        print([["FI_hoch", 1], ["FI_bayer", 2], ["FI_bruck", 3], ["FI_weit", 4], ["TA_wuet", 5],\
        ["TA_nwd", 6], ["LA", 7], ["KI", 8], ["BU", 9], ["DG", 10],\
        ["EI", 11], ["SK", 14], ["KW", 15], ["HB", 16], ["ER", 17], ["BI", 18], ["SP", 19],\
        ["RO", 20], ["HP", 21], ["ES", 22], ["LA_sTirol", 29], ["KI_sTirol", 30]])


    def main(self, output_path = ""):

        self.alter_data.drop(['Best.-Schicht.2', 'Nutzungsnummer',
           'Maßnahmenart', 'Massnahme geplant', 'Massnahmengruppe',
           'Angriffsfläche', 'Nutzung LH', 'Nutzung NH', 'Nutzungssumme',
           'Nutzdringlichkeit', 'Bewpfl.', 'Zeitpunkt', 'Rückungsart',
           'Schlägerungsart', 'Repr. Fläche Schicht', 'Maßnahme', 'Geschäftsfeld',
           'Bezeichnung', 'Pflanzen Ist', 'Baumarten Ist', 'Repr. Fläche Baumart',
           'Flächenanteil'], axis=1, inplace=True)

        self.alter_data['age'] = self.alter_data['Schichtalter']

        # get all wo
        wos = self.alter_data['WO'].unique()
        # make column oh
        self.alter_data['oh'] = 0
        self.alter_data['mass'] = 0
        self.alter_data['area'] = 0

        # merge data: age + height
        # get list of wo in height dataset
        height_wo = self.height_data['wo'].unique()

        for wo in wos:
            if wo in height_wo:
                wo_height = self.height_data[self.height_data['wo'] == wo]
                if not self.mass_data.empty:
                    wo_mass = self.mass_data[self.mass_data['wo'] == wo]

                # if WO has one Polygon
                if wo_height.shape[0] == 1:
                    # set oh and area
                    self.alter_data.loc[self.alter_data['WO'] == wo, 'oh'] = wo_height.iloc[0, 1]
                    self.alter_data.loc[self.alter_data['WO'] == wo, 'area'] = wo_height.iloc[0, 2]
                    if not self.mass_data.empty:
                        self.alter_data.loc[self.alter_data['WO'] == wo, 'mass'] = wo_mass.iloc[0, 1]

                # if WO has multiple Polygons
                else:
                    # set oh and area
                    self.alter_data.loc[self.alter_data['WO'] == wo, 'oh'] = self.wavg(wo_height, 'oh', 'area')
                    self.alter_data.loc[self.alter_data['WO'] == wo, 'area'] = wo_height.iloc[:, 2].sum()
                    if not self.mass_data.empty:
                        self.alter_data.loc[self.alter_data['WO'] == wo, 'mass'] = self.wavg(wo_mass, 'v', 'area')

        self.alter_data.loc[self.alter_data['oh'] < 1, 'age'] = 6

################################################################################

        self.alter_data = self.alter_data[self.alter_data['oh'] > 0]

        for ba in self.ba_list:
            print(ba)
            self.ba = ba[0]
            # interpolate every instance for BU
            pool = mp.Pool(processes=mp.cpu_count())

            et_data_ba = pool.map(self.parallel_bon, np.arange(self.alter_data.shape[0]))
            #prtin(ba[0])
            #et_data_ba = alter_data.apply(lambda row: self.bon_new(ba[0], row['age'], row['oh']-2), axis=1)
            temp_ba = np.vstack(et_data_ba).astype(np.float)

            # create attributes
            self.alter_data[ba[1] + '_ekl'] = 0
            self.alter_data[ba[1] + '_g'] = 0
            self.alter_data[ba[1] + '_v'] = 0

            # fill data into new attributes
            self.alter_data.loc[:,[ba[1] + '_ekl', ba[1] + '_g', ba[1] + '_v']] = temp_ba

        if not output_path == "":
            # write to csv
            self.alter_data.to_csv(output_path, index=False)

        return self.alter_data


    def parallel_bon(self, iter):
        row = self.alter_data.iloc[iter]
        bon = self.bon_new(self.ba, row['age'], row['oh']-2)
        return(bon)


    def bon_new(self, et, alter, oh):

        ##############
        # bonitieren #
        ##############

        # values: FI    FI    FI    FI    TA    TA    LA    KI    BU    DG    EI    SK    KW   HB   ER   BI   SP   RO   HP   ES   LA   KI
        #        hoch  bayer bruck weit  wütt   NWD         Lit                           Stb                 PA        hPA       STi  STi
        #         1     2     3     4     5     6     7     8     9     10    11    14    15   16   17   18   19   20   21   22   29   30

        # values: et   ekl  alter   oh    mh    fz    G     V     dg    N     lfZ    GWL    dGZ    hDZ
        #         0     1     2     3     4     5     6     7     8     9     10     11     12     13

        if (alter < 11) | (oh < 10) | ((oh < 22) & (alter > 200)):
            et_data_oh = np.zeros(14)
        else:

            et_data = self.et_data.copy()

            try:
                # filter et
                x = np.where(et_data[:,0] == et)
                et_data_et = et_data[x]

                # get age of next 5 year intervall age
                temp_alter = int(alter/5)*5

                # filter 5 year intervall age (min)
                x = np.where(et_data_et[:,2] == temp_alter)
                et_data_alter_0 = et_data_et[x]

                # filter 5 year intervall age (max)
                x = np.where(et_data_et[:,2] == temp_alter + 5)
                et_data_alter_1 = et_data_et[x]

                # interpolate in alter
                et_data_alter_2 = et_data_alter_0 + ((alter - temp_alter)/(5)) * (et_data_alter_1 - et_data_alter_0)

                # filter et intervall oh (min)
                x = np.where(et_data_alter_2[:,3] < oh)
                y = np.max(x)
                #print(et_data_alter_2[-1,3], oh, et_data_alter_2[0,3].max())

                if et_data_alter_2[-1,3] >= oh:
                    # interpolate in oh
                    et_data_oh = et_data_alter_2[y] + ((oh - et_data_alter_2[y,3]) / (et_data_alter_2[y + 1,3] - et_data_alter_2[y,3])) * (et_data_alter_2[y+1] - et_data_alter_2[y])
                else:
                    # extrapolate in oh
                    et_data_oh = et_data_alter_2[-2] + ((oh - et_data_alter_2[-2,3]) / (et_data_alter_2[-1,3] - et_data_alter_2[-2,3])) * (et_data_alter_2[-1] - et_data_alter_2[-2])
            except:
                et_data_oh = np.zeros(14)

        return(et_data_oh[[1,6,7]])

    ## weight average (calc)
    def wavg(self, group, avg_name, weight_name):

        d = group[avg_name]
        w = group[weight_name]

        try:
            return (d*w).sum() / w.sum()
        except ZeroDivisionError:
            return 0
