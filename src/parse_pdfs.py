# This file will take the output from prepare_data and:
# 1. Try to parse Table 1 data for each PDF
# -- The top left corner of each page will be searched to see if there is data for the top 12 minerals
# -- Trace minerals, due to parsing difficulties, will not be included at this time
# -- Only the first set of sample data will be kept at this time
# The output will either be a df or a dictionary of all lunar samples. 
# The stretch goal is to get that dictionary into a python library that can be pip'd. 
# The underlying processing and data should never have to be ran by an outsider since the pdfs are constant

import camelot
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import io
import requests
global cwd
import os 
import pickle
import glob

def getDataTables(df_samples):
    raw = dict()
    i=0
    for row in range(750, len(df_samples)):
        i+=1
        pageNum = int(df_samples['numPages'][row])
        pdfFile = df_samples['compendiumUrl'][row]
        sampleID = str(df_samples['id'][row])
        if pageNum > 1:
            stop_searching = False
            for page in range(1, pageNum+1):
                try:
                    tables = camelot.read_pdf(pdfFile, pages = str(page), table_areas=['60,750,300,70'], flavor='stream')
                    table_df = tables[0].df
                    if table_df.iloc[0].str.contains('Table 1').sum() > 0:
                        print(i)
                        raw.update({sampleID : table_df})
                        stop_searching = True
                        #and stop looking for pages
                        break
                except:
                    print('error' + sampleID)
                    continue    
            # try the other side of the page
            if stop_searching == False:
                for page in range(1, pageNum+1):
                    try:
                        tables = camelot.read_pdf(pdfFile, pages = str(page), table_areas=['300,750,600,70'], flavor='stream')
                        table_df = tables[0].df
                        if table_df.iloc[0].str.contains('Table 1').sum() > 0:
                            print(i+'_op')
                            raw.update({sampleID : table_df})
                            #and stop looking for pages
                            break
                    except:
                        print('error' + sampleID)
                        continue  
    return raw


def loadPickles():
    pickles = glob.glob(cwd+'outputs\*.pickle')
    raw = dict()
    for pick in pickles:
        with (open(pick, "rb")) as openfile:
            raw.update(pickle.load(openfile))
    return raw


def parseDF(raw, df_samples):
    outputs = pd.DataFrame()
    i=0
    for sampleID in raw.keys():
        #raw key
        df = raw[sampleID].copy()
        df['mineralVals'] = [[] for _ in range(len(df))]
        try:
            for col in df.columns:
                if df[col].str.contains('SiO2').sum() > 0:
                    #this is the column with the mineral names
                    mineralCol = col
                    df[col] = df[col].str.replace(' %','')
                    df['mineralName'] = df[col]
                elif col != 'mineralVals':
                    dig_col = str(col)+'_dig'
                    df[dig_col] = df[col].str.findall(r'(\d+\.*\d*)').fillna('')
                    df['mineralVals'] = df['mineralVals'] + df[dig_col]
            df = df[['mineralName', 'mineralVals']]
            df = df.T
            df.columns = df.iloc[0]
            df = df[1:]
            df['id'] = sampleID
            keep_cols = ['SiO2', 'TiO2', 'Al2O3', 'FeO', 'MnO', 'MgO',
                   'CaO', 'Na2O', 'K2O', 'P2O5', 'S', 'sum', 'Sc ppm', 'Cr', 'Co', 'Cu',
                   'Zn', 'Ga', 'Ge ppb', 'As', 'Se', 'Rb', 'Sr', '', '', 'Nb', 'Mo', 'Ru',
                   'Rh', 'Pd ppb', 'Ag ppb', 'Cd ppb', 'In ppb', 'Sn ppb', 'Sb ppb',
                   'Te ppb', 'Cs ppm', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Sm', 'Eu', 'Gd',
                   'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W ppb', 'Re ppb',
                   'Os ppb', 'Ir ppb', 'Pt ppb', 'Au ppb', 'Th ppm', 'U ppm', 'id']
            temp = pd.DataFrame()
            for col in keep_cols:
                if col in df.columns and len(col)>0:
                    temp[col] = df[col]
                else:
                    temp[col] = ''
            outputs = pd.concat([outputs, temp])
            print(i)
            i+=1
        except: 
            i+=1
            print(sampleID)
    total = pd.merge(df_samples, outputs, on='id', how='left')
    return total
    

if __name__=="__main__":
    cwd = os.path.dirname(os.path.realpath(__file__)).replace('src','')
    df_samples = pd.read_csv(cwd+r'outputs\out_prepare.csv')
    pullData = False
    if pullData:
        raw = getDataTables(df_samples)
        #save raw data as a backstop
        with open(r'C:\Users\HelloWorld\Documents\_git_code\lunarSoil\outputs\raw_data_750_1000.pickle', 'wb') as f:
            pickle.dump(raw, f)
    raw = loadPickles()
    total = parseDF(raw, df_samples)
    total.to_csv(cwd + r'outputs\final_out.csv')