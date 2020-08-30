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

class SAPAge(object):

    def __init__(self, input_path):
        self.input_path = input_path

    def main(self, output_path = ""):
        # load data
        data = pd.read_csv(self.input_path, sep='\t', encoding = "ISO-8859-1", decimal=',', error_bad_lines=False)
        # filter data
        data.drop(data[data['Debitor']!=220442].index, axis=0, inplace=True)
        data.drop(data[data['WE-Typ']=='NG'].index, axis=0, inplace=True)
        data.drop(['Merkmalausprägung', 'AuswKatTyp', 'Teiloperats-ID', 'Forstbetrieb',
       'Debitor', 'TO-Bezeichnung', 'Status', 'Beg. Laufzeit', 'Ende Laufzeit',
       'Operat-ID', 'vorgeschl. Hiebssatz', 'Verantwortlicher',
       'Erfassungsstatus', 'Migriert?', 'GUID', 'Debitor.1', 'Bearbeitungsblock', 'fr. Schälschade',
       'Verbissgrad', 'SchutzwaldProjNr', 'Schlussgrad', 'Stabilität',
       'VJ Bedingung', 'VJ Situation', 'Erreichbark. des BZ', 'GUID.1', 'GUID.2', 'Forstbetrieb.2', 'Teiloperats-ID.2',
       'Forstrevier.1', 'Abteilung.1', 'Unterabteil..1', 'Teilfl..1',
       'Selektiver Verbiss', 'Erfassungsstatus.1', 'Storno', 'Angelegt von',
        'Erfassungsstatus.2', 'Storno.1', 'GUID.3', 'GUID.4',
       'Forstbetrieb.3', 'Teiloperats-ID.3', 'Forstrevier.2', 'Abteilung.2',
       'Unterabteil..2', 'Teilfl..2', 'Erfassungsstatus.3', 'Storno.2', 'GUID.5', 'GUID.6',
       'Forstbetrieb.4', 'Teiloperats-ID.4', 'Forstrevier.3', 'Abteilung.3',
       'Unterabteil..3', 'Teilfl..3', 'Debitor.2', 'Debitor.3',
       'Angelegt am', 'Uhrzeit', 'Geändert von', 'Geändert am', 'Uhrzeit.1', 'Erfassungsstatus.4', 'Storno.3',
       'Nutztext', 'Alter der 1. Schicht', 'TAX: Altersklasse', 'Produktionskategorie', 'Geschäftsjahr',
       'Abmaßbeleg', 'Ertragstafelnummer', 'Ertragstafelbezeich',
       'Anmerkung', 'Zeile1', 'Zeile2', 'Zeile3', 'Zeile4', 'Zeile5', 'Zeile6',
       'Zeile7', 'Zeile8', 'Bestockungsziel'], axis=1, inplace=True)

        data_fil = data[(data['Best.-Schicht'] != 0) & (data['Best.-Schicht.1'] == 0) & (data['Best.-Schicht.2'] == 0)].copy()
        data_fil['WO'] = data_fil['Forstrevier'].astype(int).astype(str) + data_fil['Abteilung'].astype(int).astype(str) + data_fil['Unterabteil.'] + data_fil['Teilfl.'].astype(int).astype(str)

        data_alter = data_fil[(data_fil['Best.-Schicht'] == 1)].copy()
        data_ext = data_fil[data_fil['Best.-Schicht'] > 1].copy()
        wos = data_ext['WO'].unique()

        for wo in wos:
           temp = data_fil[data_fil['WO'] == wo]
           idx = temp['S-Best.grad'].idxmax(axis=1)

        if temp.loc[idx, 'Best.-Schicht'] != 1:
            idx_alter = data_alter[data_alter['WO'] == wo].index.values[0]
            data_alter.loc[idx_alter, ['Schichtalter']] = temp.loc[idx, ['Schichtalter']].values[0]
            data_alter.loc[idx_alter, ['Best.-Schicht']] = temp.loc[idx, ['Best.-Schicht']].values[0]
            data_alter.loc[idx_alter, ['S-Best.grad']] = temp.loc[idx, ['S-Best.grad']].values[0]

        if not output_path == "":
            # write to csv
            data_alter.to_csv(output_path, index=False)

        return data_alter
