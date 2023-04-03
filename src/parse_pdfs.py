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
    outputs = df_samples.copy()
    for sampleID in raw.keys():
        #raw key
        df = raw[sampleID].copy()
        df['mineralVals'] = [[] for _ in range(len(df))]
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
        outputs = pd.merge(outputs, df, on='id', how='left')
    return outputs
    

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
    outputs = parseDF(raw, df_samples)
    outputs.to_csv(cwd + r'ouputs\final_out.csv')