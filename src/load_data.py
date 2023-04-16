# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 21:00:34 2023

@author: HelloWorld
"""

import ast
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import io
import requests
global cwd
import os 
import pickle
import glob
import matplotlib.pyplot as plt

def to_list(df, col):
    df[col] = df[col].str.strip("[]").str.replace("'",'').str.replace(' ','').str.split(',')
    return df


def getMetal(df, col):
    keep_cols = ['id', 'MISSION', 'SAMPLETYPE', 'SAMPLESUBTYPE', col]
    temp = df.copy()
    temp = temp[keep_cols]
    temp = to_list(temp, col)
    temp = temp.explode(col)
    temp[col] = pd.to_numeric(temp[col], errors='raise')
    temp = temp[temp[col] > 0].reset_index(drop=True)
    plotMetals(temp, col)
    return temp

def plotMetals(metal, col):
    fig, ax = plt.subplots(figsize=(10,6))
    filterby = 'SAMPLETYPE'
    missions = metal[filterby].unique()
    for mission in missions:
        if type(mission) == str:
            metal_temp = metal[metal[filterby]==mission]
            ax.plot(metal_temp[col], 'o', label=mission)
        
    # if ylim!=None:
    ax.set_ylim([0,100])
    # if xlim!=None:
    #     ax.set_xlim(xlim)
    ax.legend(loc='upper right')
    ax.set_xlabel('Number of Apollo Characterization Results')
    ax.set_ylabel(f'Mass Percent {col}')
    ax.set_title(col)
    return

if __name__=="__main__":
    cwd = os.path.dirname(os.path.realpath(__file__)).replace('src','')
    df = pd.read_csv(cwd+r'outputs\final_out.csv')
    al = getMetal(df, 'Al2O3')
    fe = getMetal(df, 'FeO')
    ti = getMetal(df, 'TiO2')
    si = getMetal(df, 'SiO2')

    