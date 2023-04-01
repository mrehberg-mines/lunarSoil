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

def getDataTables(df_samples):

    tableCols = ['SiO2',
                 'TiO2', 
                 'Al2O3',
                 'FeO',
                 'MnO',
                 'MgO',
                 'CaO',
                 'Na2O',
                 'K2O',
                 'P2O5',
                 'S']
    
    df_samples = df_samples.reindex(columns = df_samples.columns.tolist() + tableCols).fillna('')
    for row in range(len(df_samples)):
        pageNum = int(df_samples['numPages'][row])
        pdfFile = df_samples['compendiumUrl'][row]
        if pageNum > 1:
            for page in range(1, pageNum+1):
                try:
                    tables = camelot.read_pdf(pdfFile, pages = str(page), table_regions=['0,300,800,500'])
                    table = tables[0].df
                    if 'SiO2' in table:
                        #then do cool stuff
                        
                        #and stop looking for pages
                        break
                except:
                    continue    









if __name__=="__main__":
    cwd = os.path.dirname(os.path.realpath(__file__)).replace('src','')
    df_samples = pd.read_csv(cwd+r'outputs\out_prepare.csv')
