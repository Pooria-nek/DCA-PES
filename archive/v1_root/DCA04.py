# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 09:41:27 2021

@author: mrasoulzadeh
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import time
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from scipy.signal import find_peaks
from scipy.signal import argrelextrema
from scipy.optimize import curve_fit
from lmfit import Model
import matplotlib.dates as mdates
import statsmodels.formula.api as sm
import statsmodels.tsa.seasonal as sms
import peakutils
from scipy.optimize import fsolve
from scipy.integrate import quad
###############################################################################
#%% Reads csv files for water and oil production

def removeOutliers(df, fieldName,zScoreThreshhold):
    #remove outliers in oil production
    if df.empty:
        return df
    df=df.replace({np.nan:0})
    df=df[(np.abs(scipy.stats.zscore(df[fieldName])) < zScoreThreshhold)]
    #plotProductionData(df, 'Outliers removed')
    
    # replace 0 values with nan
    df=df.replace({0: np.nan})
    return df
def readDataFramefromcsvfile(filename):
    # #plt.figure(figsize=(20,10))
    df=pd.DataFrame(pd.read_csv(filename, thousands=','))
    df.columns = ["Date", "OilMonthlyVol","WaterMonthlyVol","OilPriceWTI"]
    df=df.replace({0: np.nan})

    # df['OilMonthlyVol']=df['OilMonthlyVol'].str.replace(',', '').astype(float)
    # df['WaterMonthlyVol']=df['WaterMonthlyVol'].str.replace(',', '').astype(float)
    # df['OilPriceWTI']=df['OilPriceWTI'].str.replace(',', '').astype(float)
    
    # remove $ sign in currency fields 
    df['OilPriceWTI'] = df['OilPriceWTI'].replace('[\$,]', '', regex=True).astype(float)

    df['Date']=df['Date'].astype('datetime64[ns]')
    # #plotProductionData(df, 'Original production data')
    
    
    # df=removeOutliers(df,'OilMonthlyVol',1.2)
    # df=removeOutliers(df,'WaterMonthlyVol',1.2)
    # plotProductionData(df, 'Original production data with daily outliers removed')

    df.index=df['Date']
    data_columns = ["OilMonthlyVol","WaterMonthlyVol"]
    df_rol= df[data_columns].rolling(window = 3, center = True).mean()
    # df=df_rol

    df=df.resample("MS").mean()    
    # df['Date']=df['Date'].astype('datetime64[ns]')
    df_rol=df_rol.reset_index()
    # #plotProductionData(df_rol, 'Original rolled data')

    df=df.reset_index()
    # #plotProductionData(df, 'Original monthly averaged production data')
    
    return df
def plotProductionData(df, plotTitle,dfPeaksW=None,dfPeaksO=None, lw=1,mrk='.'):
    # plt.figure(figsize=(20,10))
    plt.subplot(2,1,1)
    plt.plot(df['Date'],df['WaterMonthlyVol'], label = "Water"+plotTitle, linewidth=lw, marker=mrk)
    if (dfPeaksW is not None):
        plt.plot(dfPeaksW['Date'],dfPeaksW['WaterMonthlyVol'], label = "WaterPeaks",linestyle='None',  marker='o' )
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.gca().xaxis.set_major_formatter((mdates.DateFormatter('%y/%m')))
        
    plt.legend( loc='best', fontsize=15)
    plt.grid()
    plt.subplot(2,1,2)
    plt.plot(df['Date'],df['OilMonthlyVol'], label = "Oil"+plotTitle, linewidth=lw, marker=mrk )
    if (dfPeaksO is not None):
        plt.plot(dfPeaksO['Date'],dfPeaksO['OilMonthlyVol'], label = "OilPeaks",linestyle='None',  marker='o' , color='red')
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.gca().xaxis.set_major_formatter((mdates.DateFormatter('%y/%m')))
    plt.grid()
    plt.legend( loc='best', fontsize=15)
    plt.suptitle(plotTitle, fontsize=15)
    
    # plt.show()
    return 
# dfOriginal=readDataFramefromcsvfile('WagnerRecordedData2018-2020.csv')
# dfOriginal=readDataFramefromcsvfile('WagnerUnitTotal.csv') # dailyXXXX
# dfOriginal=readDataFramefromcsvfile('BarnettShaleDenton.csv')
# dfOriginal=readDataFramefromcsvfile('BarnetteShaleTarrant.csv')
# dfOriginal=readDataFramefromcsvfile('BarnettShaleJohnson.csv')#XXX
# dfOriginal=readDataFramefromcsvfile('HuntsvilleShale.csv')

#------------------------------------------------------------------------------
#%% Removes outliers and fills missing data with interpolation
def removeMinima(df, fieldName, factor):
    if df.empty:
        return df    
    if df[fieldName].isnull().all():
        return df
    A = -df[fieldName].diff()
    threshholdDiff = (A[A > 0]).median(skipna=True)
    M = -df[fieldName]
    # M=pd.concat([pd.Series([0]), M])
    indices = find_peaks(M,  prominence=threshholdDiff*factor)[0]
    df.loc[indices, fieldName] = np.nan
    return df


def fillMissingDates(df,dateCol):
    if df.empty:
        return df
    # add missing dates
    if (df[dateCol].loc[2]-df[dateCol].loc[1]).days>10:
        freqm='MS'
    else:
        freqm='D'
    r = pd.date_range(start=df[dateCol].min(), end=df[dateCol].max(), freq =freqm)
    df=df.set_index(dateCol).reindex(r).fillna(np.nan).rename_axis(dateCol).reset_index()   
    df=df.interpolate(method='linear')
    # df["WATER_LEVEL"]=df["WATER_LEVEL"].interpolate(method='cubic')
    # df["WATER_LEVEL"]=df["WATER_LEVEL"].interpolate(method='linear',limit_direction='backward' , limit=4 )    
    return df


#               # plt.figure(figsize=(20,10))
#               df=removeMinima(dfOriginal, 'WaterMonthlyVol',1.2)
#               df=removeMinima(df, 'OilMonthlyVol',1.2)
#               # #plotProductionData(df, 'Data Minima Removed')
#               # #plt.show()
#               df=fillMissingDates(df)
#               df=removeOutliers(df,'OilMonthlyVol',3.5)
#               # #plotProductionData(df, 'Removed outliers')
#               # #plt.show()
#------------------------------------------------------------------------------
#%% Finds peaks of data
def findPeaks0(df, fieldName, factor):
    if df[fieldName].isnull().all():
        return []
    A=abs(df[fieldName]).diff()
    A=(df[fieldName])
    A=A-A.shift(1)
    # threshholdDiff=(A[A>0]).median(skipna=True)
    # threshholdDiff=(A[A>0]).quantile(0.5, interpolation='linear')
    # threshholdDiff=(A[A>0]).quantile(0.5, interpolation='linear')
    heightthreshholdDiff=(A[A>0]).quantile(0.75, interpolation='linear')
    
    M=df[fieldName]
    M=pd.concat([pd.Series([0]), M])    
    indices = find_peaks(M,  prominence=heightthreshholdDiff*factor,
                         distance=6)[0]
    # indices = find_peaks(df[fieldName],  threshold=threshholdDiff*factor)[0]
    return indices-1

                    # plt.figure(figsize=(20,10))
                    # indices=findPeaks(df, 'WaterMonthlyVol',1.0)
                    # dfPeaksW=df.iloc[indices,:]
                    # indices=findPeaks(df, 'OilMonthlyVol',1.0)
                    # dfPeaksO=df.iloc[indices,:]
                    # plotProductionData(df, 'Data Peaks', dfPeaksW, dfPeaksO)

#------------------------------------------------------------------------------
#%%
# import tkinter as tk
# import tkinter.filedialog as fd

# root = tk.Tk()
# filez = fd.askopenfilenames(parent=root, title='Choose a file')
filez=['BarnettShaleJohnson.csv','WagnerRecordedData2018-2020.csv','WagnerUnitTotal.csv','BarnettShaleDenton.csv',
       'BarnetteShaleTarrant.csv','BarnettShaleJohnson.csv','HuntsvilleShale.csv']
#%%
def findPeaks(df, fieldName, factor):
    if df[fieldName].isnull().all():
        return []
    M=df[fieldName]
    M=pd.concat([pd.Series([0]), M])    
    M=M.to_numpy()    
    ### IMPORTANT ### order should be define by user
    indices = argrelextrema(M, np.greater, order=6)  # np.greater for maxima
    indices=np.asarray(indices)-1
    indices=indices.flatten()

    return indices

def Duong(t, q1,q_inf=0, a=0.1, m=0.1):
    global t0
    # q1 is the initial qi
    t1=t**(-m)*np.exp( (a/(1-m))*(t**(1-m)-1)  )
    A=  q1*t1+q_inf
    return A

def Duongqa(t,q1,q_inf, a, m,qa):
    global t0
    # q1 is the initial qi
    t1=t**(-m)*np.exp( (a/(1-m))*(t**(1-m)-1)  )
    A=  q1*t1+q_inf-qa
    return A

def NpDuong( q1,q_inf, a, m,qa,r=0):
    guess=20
    ta=fsolve(Duongqa, guess, args=(q1,q_inf, a, m,qa))
    Np=quad(Duong, 0, ta, args=(q1,q_inf, a, m))+q1
    return Np[0]-Np[1]



def Arps(t, qi, b=1e-1, Di=0.1):
    # global t0
    # t=t-t0
    if (b<=1e-1):
        A=qi *np.exp(-Di*t)
    else:
        A=    qi / ((1+b*Di*t)**(1/b))
    return A

def taArps(t, qi, b, Di, qa,r=0):
    # global t0
    # t=t-t0
    if (b<=1e-1):
        ta=np.log(qi/(qa-r))/Di
    else:
        ta=1/b/Di*((qi/(qa-r))**b-1)
    return ta

def NpArps(t, qi, b, Di, qa,r=0):
    ta=taArps(t, qi, b, Di, qa)
    if (b<=1e-1):
        Np=(qi-qa)/Di+r*ta
    else:
        Np=qi/((1-b)*Di)*(1-(qa/qi)**(1-b))+r*ta
    return Np

def makeDataFrame (startDate,columns, numberOfMonths):
    index = pd.date_range(startDate, periods=numberOfMonths, freq='MS')
    df = pd.DataFrame(index=index, columns=columns)
    df=df.reset_index()
    # df.columns = ["Date", "OilMonthlyVol","WaterMonthlyVol","OilPriceWTI"]
    # df = df.fillna(0)
    return df



def fitArpsModel(df,indices,mjd,numberOfMonths):
    df=df.dropna()
   # indices=findPeaks(df, df.columns[1],1.0)
    qis=np.array(df.iloc[:,1])

    # Fit Duong model
    # pars = decay_model.make_params(b=1e-1, Di=0.01,t0=mjd)
    qi=qis[indices[mjd] ]
    if mjd==len(indices)-1:
            x = df.index[(indices[mjd]):len(df)]
    else:
            x = df.index[(indices[mjd]):(indices[mjd+1]-3)]

    t0=indices[mjd]
    y_sim = df.iloc[x,1]
    popt, pcov=curve_fit(Arps, x-t0, y_sim,bounds=(0, [qi,5,20]),max_nfev=10000)
                                              # (t, qi, b=1e-1, Di=0.1)
    qi=popt[0]
    b=popt[1]
    Di=popt[2]
    x=np.array(range(indices[mjd],indices[mjd]+numberOfMonths))
    yy=Arps(x-t0, qi,b,Di)
    dfFitO=makeDataFrame (df[df.columns[0]].loc[indices[mjd]], df.columns[1:],numberOfMonths)
    dfFitO[df.columns[1]]=yy
    dfFitO.columns=df.columns
  
    return dfFitO, x,t0, qi,b,Di
    
def fitDuongModel(df,indices,mjd,numberOfMonths):
    df=df.dropna()
    #indices=findPeaks(df, df.columns[1],1.0)
    qis=np.array(df.iloc[:,1])

    # Fit Duong model
    # pars = decay_model.make_params(b=1e-1, Di=0.01,t0=mjd)
    qi=qis[indices[mjd] ]
    if mjd==len(indices)-1:
            x = df.index[(indices[mjd]):len(df)]
    else:
            x = df.index[(indices[mjd]):(indices[mjd+1]-3)]
    t0=indices[mjd]-0.01
    y_sim = df.iloc[x,1]
    #def Duong(t, q1,q_inf, a, m, t00):
    popt, pcov=curve_fit(Duong, x-t0, y_sim,bounds=([0,0, -10, -10], [qi,qi, 10, 5]),max_nfev=10000)
                                      # (t, q1,q_inf, a, m)
    q1=popt[0]
    q_inf=popt[1]
    a=popt[2]
    m=popt[3]
    x=np.array(range(indices[mjd],indices[mjd]+numberOfMonths))
    yy=Duong(x-t0, q1,q_inf, a, m)
    dfFitO=makeDataFrame (df[df.columns[0]].loc[indices[mjd]], df.columns[1:],numberOfMonths)
    dfFitO[df.columns[1]]=yy
    dfFitO.columns=df.columns     
 

    return dfFitO,x,t0, q1,q_inf, a, m

    
def MonteCarloSimulationArpes(dfFitted, x,t0, qi,b,Di,numberOfMonths,qa,yy,triangularLeft,triangularRight,normalSTD,DistRadioButton):
    iteration = 1000
    if DistRadioButton=='Triangular':

        b_dist=np.random.triangular(b*(1-triangularLeft/100), b, b*(1+triangularRight/100), iteration)
        Di_dist=np.random.triangular(Di*(1-triangularLeft/100), Di, Di*(1+triangularRight/100), iteration)
    if DistRadioButton=='Normal':
        b_dist=np.random.normal(b, b*normalSTD/100, iteration)
        Di_dist=np.random.normal(Di, Di*normalSTD/100, iteration)
        
    qi_dist=np.array(np.tile([qi], (iteration, 1)))
    df_dist=pd.DataFrame({'b': b_dist,
                   'Di':Di_dist})
                         
    mjddf=df_dist.apply(lambda row : Arps(x-t0, qi, row['b'], row['Di']), axis = 1).apply(np.array)
    mjddf=pd.DataFrame(df_dist.apply(lambda row : Arps(x-t0, qi, row['b'], row['Di']), axis = 1))
    mjddf=pd.DataFrame(mjddf[0].to_list())


    mjddfNp=df_dist.apply(lambda row : NpArps(x-t0, qi, row['b'], row['Di'], qa), axis = 1).apply(np.array)
    mjddfNp=pd.DataFrame(df_dist.apply(lambda row : NpArps(x-t0, qi, row['b'], row['Di'],qa), axis = 1))
    mjddfNp=pd.DataFrame(mjddfNp[0].to_list())
    
   
    dfFitted[yy.strip()+"ArpesMean"]=mjddf.mean()
    dfFitted[yy.strip()+"ArpesStdDev"]=mjddf.std()
    dfFitted[yy.strip()+"ArpesVar"]=mjddf.var()
    dfFitted[yy.strip()+"ArpesP05"]=mjddf.quantile(0.05)
    dfFitted[yy.strip()+"ArpesP95"]=mjddf.quantile(0.95)
    dfFitted[yy.strip()+"ArpesVar"]=mjddf.var()


    P05Np=mjddfNp.quantile(0.05)
    P95Np=mjddfNp.quantile(0.95)
    meanNp=mjddfNp.mean()

    return dfFitted , P05Np, P95Np, meanNp

def MonteCarloSimulationDuong(dfFitted, x,t0, q1,q_inf, a, m,numberOfMonths,qa,triangularLeft,triangularRight,normalSTD,DistRadioButton):
    iteration = 1000
    if DistRadioButton=='Triangular':
        q1_dist=np.random.triangular(q1*(1-triangularLeft/100), q1, q1*(1+triangularRight/100), iteration)
        q_inf_dist=np.random.triangular(q_inf*(1-triangularLeft/100), q_inf, q_inf*(1+triangularRight/100), iteration)
        a_dist=np.random.triangular(a-triangularLeft/100*np.abs(a), a, a+triangularRight/100*np.abs(a), iteration)
        m_dist=np.random.triangular(m-triangularLeft/100*np.abs(m), m, m+triangularRight/100*np.abs(m), iteration)
    if DistRadioButton=='Normal':
        q1_dist=np.random.normal(q1*0.8, q1, q1*1.2, iteration)
        q_inf_dist=np.random.normal(q_inf*0.8, q_inf, q_inf*1.2, iteration)
        a_dist=np.random.normal(a-0.2*np.abs(a), a, a+0.2*np.abs(a), iteration)
        m_dist=np.random.normal(m-0.2*np.abs(m), m, m+0.2*np.abs(m), iteration)
    
    df_dist=pd.DataFrame({'q1': q1_dist,
                   'q_inf':q_inf_dist,
                   'a':a_dist,
                   'm':m_dist})
                         
    mjddf=df_dist.apply(lambda row : Duong(x-t0, row['q1'], row['q_inf'], row['a'],row['m']), axis = 1).apply(np.array)
    mjddf=pd.DataFrame(df_dist.apply(lambda row : Duong(x-t0, row['q1'], row['q_inf'], row['a'],row['m']), axis = 1))
    mjddf=pd.DataFrame(mjddf[0].to_list())


    mjddfNp=df_dist.apply(lambda row : NpDuong(row['q1'], row['q_inf'], row['a'],row['m'], qa), axis = 1).apply(np.array)
    mjddfNp=pd.DataFrame(df_dist.apply(lambda row : NpDuong(row['q1'], row['q_inf'], row['a'],row['m'], qa), axis = 1))
    mjddfNp=pd.DataFrame(mjddfNp[0].to_list())
    
   
    dfFitted["DuongMean"]=mjddf.mean()
    dfFitted["DuongStdDev"]=mjddf.std()
    dfFitted["DuongVar"]=mjddf.var()
    dfFitted["DuongP05"]=mjddf.quantile(0.05)
    dfFitted["DuongP95"]=mjddf.quantile(0.95)
    dfFitted["DuongVar"]=mjddf.var()


    P05Np=mjddfNp.quantile(0.05)
    P95Np=mjddfNp.quantile(0.95)
    meanNp=mjddfNp.mean()

    return dfFitted , P05Np, P95Np, meanNp
