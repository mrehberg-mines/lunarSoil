# This file will accomplish the following objectives
# 1. Index all the lunar samples IDs from https://www.lpi.usra.edu/lunar/samples/#catalogues, 
# 2. Index the sample ID pdf files https://www.lpi.usra.edu/lunar/samples/atlas/compendium/15682.pdf
# 3. Count the number of pages in each PDF
# 4. Merge metadata from https://curator.jsc.nasa.gov/rest/lunarapi/samples/sampledetails/60010

import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import PyPDF2
import io
import requests
global headers, cwd
headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}

import os 


def getAllSampleIDs():
    catalog_url = cwd+'Lunar Samples.html'
    dfs = pd.read_html(catalog_url)
    sampleIDs=pd.Series()
    for df in dfs:
        temp_series = pd.Series(df.fillna('').replace(' ', '').astype(str).to_numpy().flatten())
        temp_series = temp_series.str.replace('\.0$','')
        sampleIDs = pd.concat([sampleIDs, temp_series])
    sampleIDs = sampleIDs.drop_duplicates(keep='first').reset_index(drop=True)
    sampleIDs = sampleIDs[sampleIDs.apply(len) > 1]
    return sampleIDs


def listPDFfiles(sampleIDs):
    base_url = r'https://www.lpi.usra.edu/lunar/samples/atlas/compendium/'
    df_samples = pd.DataFrame(sampleIDs, columns=['id'])
    df_samples['compendiumUrl'] = base_url + df_samples['id'] + '.pdf'
    return df_samples


# def downloadPDF(df_samples):
#     import urllib.request
#     urllib.request.urlretrieve(url, "filename.pdf")
#     return 


def getPageCount(df_samples):
    df_samples['numPages'] = 0
    for row in range(len(df_samples)):
        try:
            file_path = df_samples['compendiumUrl'][row]
            response = requests.get(url=file_path, headers=headers, timeout=120)
            on_fly_mem_obj = io.BytesIO(response.content)
            pdfReader = PyPDF2.PdfFileReader(on_fly_mem_obj, strict=False)
            totalPages = pdfReader.numPages
            df_samples.loc[row, 'numPages'] = totalPages
        except:
            continue
    return df_samples


def combineAPIdata(df_samples):
    df_samples['curatorApiUrl'] = r'https://curator.jsc.nasa.gov/rest/lunarapi/samples/sampledetails/' + df_samples['id']
    api_cols = ['GENERIC',
                 'SAMPLEID',
                 'MISSION',
                 'STATION',
                 'LANDMARK',
                 'BAGNUMBER',
                 'ORIGINALWEIGHT',
                 'SAMPLETYPE',
                 'SAMPLESUBTYPE',
                 'PRISTINITY',
                 'PRISTINITYDATE',
                 'HASTHINSECTION',
                 'HASDISPLAYSAMPLE',
                 'DISPLAYSAMPLENUMBER',
                 'GENERICDESCRIPTION']
    df_samples = df_samples.reindex(columns = df_samples.columns.tolist() + api_cols).fillna('')
    
    bad_api = []
    for row in range(len(df_samples)):
        try:
            r = requests.get(df_samples['curatorApiUrl'][row])
            temp = pd.DataFrame(r.json())
            for col in temp.columns:
                df_samples.loc[row, col] = temp[col][0]
        except:
            #bad_api.append(df_samples['id'][row])
            continue
        
    return df_samples


if __name__=="__main__":
    cwd = os.path.dirname(os.path.realpath(__file__)).replace('src','')
    sampleIDs = getAllSampleIDs()
    df_samples = listPDFfiles(sampleIDs)
    df_samples = getPageCount(df_samples)
    df_samples = combineAPIdata(df_samples)
    df_samples.to_csv(cwd+r'outputs\out_prepare.csv')
