from lightgbm.sklearn import LGBMClassifier
import streamlit as st
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import json
import plotly.express as px
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_absolute_error
from datetime import timedelta
from sklearn.metrics import accuracy_score
import sklearn
import seaborn as sns
from lightgbm.sklearn import LGBMRegressor
from datetime import timedelta
import requests
from time import sleep
import datetime





st.set_page_config(page_title="Corón Machine Learning forecast",layout="wide")
st.write("## **All times UTC**")

def get_wind():
  #get actual des dir
  des_dir = requests.get("https://servizos.meteogalicia.gal/mgrss/observacion/ultimos10minEstacionsMeteo.action?idEst=10085&idParam=DV_SD_10m")
  json_data = json.loads(des_dir.content)
  instant = json_data['listUltimos10min'][0]['instanteLecturaUTC']
  des_dir = json_data['listUltimos10min'][0]['listaMedidas'][0]['valor']

  #get actual dir
  dir = requests.get("https://servizos.meteogalicia.gal/mgrss/observacion/ultimos10minEstacionsMeteo.action?idEst=10085&idParam=DV_AVG_10m")
  json_data = json.loads(dir.content)
  dir = json_data['listUltimos10min'][0]['listaMedidas'][0]['valor']

  #get actual mod
  mod = requests.get("https://servizos.meteogalicia.gal/mgrss/observacion/ultimos10minEstacionsMeteo.action?idEst=10085&idParam=VV_AVG_10m")
  json_data = json.loads(mod.content)
  mod = json_data['listUltimos10min'][0]['listaMedidas'][0]['valor']*1.94384

  #get actual des mod
  des_mod = requests.get("https://servizos.meteogalicia.gal/mgrss/observacion/ultimos10minEstacionsMeteo.action?idEst=10085&idParam=VV_SD_10m")
  json_data = json.loads(des_mod.content)
  des_mod = json_data['listUltimos10min'][0]['listaMedidas'][0]['valor']*1.94384
  
  return instant, dir, des_dir,mod, des_mod

def get_meteogalicia_model_4Km(coorde):
    """
    get meteogalicia model (4Km) from algo coordenates
    Returns
    -------
    dataframe with meteeorological variables forecasted.
    """
    
    #defining url to get model from Meteogalicia server
    today=pd.to_datetime("today")
    
    try:

      head1="http://mandeo.meteogalicia.es/thredds/ncss/modelos/WRF_HIST/d03"
      head2=today.strftime("/%Y/%m/wrf_arw_det_history_d03")
      head3=today.strftime("_%Y%m%d_0000.nc4?")
      head=head1+head2+head3
      
      var1="var=dir&var=mod&var=wind_gust&var=mslp&var=temp&var=rh&var=visibility&var=lhflx"
      var2="&var=lwflx&var=conv_prec&var=prec&var=swflx&var=shflx&var=cape&var=cin&var=cfh&var=T850"
      var3="&var=cfl&var=cfm&var=cft&var=HGT500&var=HGT850&var=T500&var=snow_prec&var=snowlevel"
      var=var1+var2+var3
  
      f_day=(today+timedelta(days=3)).strftime("%Y-%m-%d") 
      tail="&time_start="+today.strftime("%Y-%m-%d")+"T01%3A00%3A00Z&time_end="+f_day+"T23%3A00%3A00Z&accept=csv"
  
      dffinal=pd.DataFrame() 
      for coor in list(zip(coorde.lat.tolist(),coorde.lon.tolist(),np.arange(0,len(coorde.lat.tolist())).astype(str))):
          dffinal=pd.concat([dffinal,pd.read_csv(head+var+"&latitude="+str(coor[0])+"&longitude="+str(coor[1])+tail,).add_suffix(str(coor[2]))],axis=1)    
  
      
      #filter all columns with lat lon and date
      dffinal=dffinal.filter(regex='^(?!(lat|lon|date).*?)')
  
      #remove column string between brakets
      new_col=[c.split("[")[0]+c.split("]")[-1] for c in dffinal.columns]
      for col in zip(dffinal.columns,new_col):
          dffinal=dffinal.rename(columns = {col[0]:col[1]})
  
      dffinal=dffinal.set_index(pd.date_range(start=today.strftime("%Y-%m-%d"), end=(today+timedelta(days=4)).strftime("%Y-%m-%d"), freq="H")[1:-1])  
      
    except:
        
      today  = pd.to_datetime("today")-timedelta(1)
      head1="http://mandeo.meteogalicia.es/thredds/ncss/modelos/WRF_HIST/d03"
      head2=today.strftime("/%Y/%m/wrf_arw_det_history_d03")
      head3=today.strftime("_%Y%m%d_0000.nc4?")
      head=head1+head2+head3
     
      var1="var=dir&var=mod&var=wind_gust&var=mslp&var=temp&var=rh&var=visibility&var=lhflx"
      var2="&var=lwflx&var=conv_prec&var=prec&var=swflx&var=shflx&var=cape&var=cin&var=cfh&var=T850"
      var3="&var=cfl&var=cfm&var=cft&var=HGT500&var=HGT850&var=T500&var=snow_prec&var=snowlevel"
      var=var1+var2+var3
  
      f_day=(today+timedelta(days=3)).strftime("%Y-%m-%d") 
      tail="&time_start="+today.strftime("%Y-%m-%d")+"T01%3A00%3A00Z&time_end="+f_day+"T23%3A00%3A00Z&accept=csv"
  
      dffinal=pd.DataFrame() 
      for coor in list(zip(coorde.lat.tolist(),coorde.lon.tolist(),np.arange(0,len(coorde.lat.tolist())).astype(str))):
          dffinal=pd.concat([dffinal,pd.read_csv(head+var+"&latitude="+str(coor[0])+"&longitude="+str(coor[1])+tail,).add_suffix(str(coor[2]))],axis=1)    
  
      
      #filter all columns with lat lon and date
      dffinal=dffinal.filter(regex='^(?!(lat|lon|date).*?)')
  
      #remove column string between brakets
      new_col=[c.split("[")[0]+c.split("]")[-1] for c in dffinal.columns]
      for col in zip(dffinal.columns,new_col):
          dffinal=dffinal.rename(columns = {col[0]:col[1]})
  
      dffinal=dffinal.set_index(pd.date_range(start=today.strftime("%Y-%m-%d"), end=(today+timedelta(days=4)).strftime("%Y-%m-%d"), freq="H")[1:-1])  
           
             
    return dffinal 


#score machine learning versus WRF
score_ml = 0
score_wrf = 0

#load algorithm file gust
algo_g_d0 = pickle.load(open("algorithms/gust_coron_d0.al","rb"))
algo_g_d1 = pickle.load(open("algorithms/gust_coron_d1.al","rb"))
algo_g_d2 = pickle.load(open("algorithms/gust_coron_d2.al","rb"))
algo_g_d3 = pickle.load(open("algorithms/gust_coron_d3.al","rb"))


meteo_model = get_meteogalicia_model_4Km(algo_g_d0["coor"])

#add time variables
meteo_model["hour"] = meteo_model.index.hour
meteo_model["month"] = meteo_model.index.month
meteo_model["dayofyear"] = meteo_model.index.dayofyear
meteo_model["weekofyear"] = meteo_model.index.isocalendar().week.astype(int)

#get station dat
r_gust = requests.get("https://servizos.meteogalicia.gal/mgrss/observacion/ultimosHorariosEstacions.action?idEst=10085&idParam=VV_RACHA_10m&numHoras=36")
json_data = json.loads(r_gust.content)

gust_o, time = [],[]
for c in json_data["listHorarios"]:
  for c1 in c['listaInstantes']:
    time.append(c1['instanteLecturaUTC'])  
    gust_o.append(c1['listaMedidas'][0]["valor"])

df_st = pd.DataFrame(np.array(gust_o),columns=["observed_gust"],index= time)  
df_st.index = pd.to_datetime(df_st.index )

#select x _var
model_x_var_p0 = meteo_model[:24][algo_g_d0["x_var"]]
model_x_var_p1 = meteo_model[24:48][algo_g_d1["x_var"]]
model_x_var_p2 = meteo_model[48:72][algo_g_d2["x_var"]]
model_x_var_p3 = meteo_model[72:96][algo_g_d3["x_var"]]

#forecast machine learning precipitation
gust_ml0 = algo_g_d0["pipe"].predict(model_x_var_p0)
gust_ml1 = algo_g_d1["pipe"].predict(model_x_var_p1)
gust_ml2 = algo_g_d2["pipe"].predict(model_x_var_p2)
gust_ml3 = algo_g_d3["pipe"].predict(model_x_var_p3)


#compare results
df_mod=pd.DataFrame({"time":meteo_model[:96].index,
                      "ML_gust": np.concatenate((gust_ml0,gust_ml1,gust_ml2,gust_ml3),axis=0),
                      "WRF_gust": meteo_model.wind_gust1})


df_res = pd.concat([df_mod.set_index("time"),df_st],axis=1).dropna()
mae_ml = round(mean_absolute_error(df_res["observed_gust"],df_res["ML_gust"]),2)
mae_wrf = round(mean_absolute_error(df_res["observed_gust"],df_res["WRF_gust"]),2)

if mae_ml < mae_wrf:
  score_ml+=1
if mae_ml > mae_wrf:  
  score_wrf+=1

fig, ax = plt.subplots(figsize=(10,6))
df_res = round(df_res*1.94384,0)
df_res.plot(grid=True, ax=ax, color=["b","r","g"], linestyle='--');
ax.set_title("Wind gust max hour before (knots)\nActual MAE (m/s)  meteorological model (point 1): {}. Reference: 2.26\nActual MAE (m/s) machine learning: {}. Reference: 1.68".format(mae_wrf,mae_ml))
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

df_mod = df_mod.set_index("time")
df_mod = round(df_mod*1.94384,0)
fig, ax = plt.subplots(figsize=(10,6))
df_mod[:24].plot(grid=True,ax=ax,color=["b","r"]);
ax.set_title("Wind gust max hour before day=0 (knots)\nMAE (m/s) meteorological model (point 1): 2.26\nMAE (m/s) machine learning: 1.68")
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10,6))
df_mod[24:48].plot(grid=True,ax=ax,color=["b","r"]);
ax.set_title("Wind gust max hour before day=1 (knots)\nMAE (m/s) meteorological model (point 1): 2.49\nMAE (m/s) machine learning: 1.91")
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10,6))
df_mod[48:72].plot(grid=True,ax=ax,color=["b","r"]);
ax.set_title("Wind gust max hour before day=2 (knots)\nMAE (m/s) meteorological model (point 1): 2.67\nMAE (m/s) machine learning: 2.03")
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig) 

fig, ax = plt.subplots(figsize=(10,6))
df_mod[72:96].plot(grid=True,ax=ax,color=["b","r"]);
ax.set_title("Wind gust max hour before day=3 (knots)\nMAE (m/s) meteorological model (point 1): 2.93\nMAE (m/s) machine learning: 2.23")
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)


#@title wind direction 


#load algorithm file 
algo_d0 = pickle.load(open("algorithms/dir_coron_d0.al","rb"))
algo_d1 = pickle.load(open("algorithms/dir_coron_d1.al","rb"))
algo_d2 = pickle.load(open("algorithms/dir_coron_d2.al","rb"))
algo_d3 = pickle.load(open("algorithms/dir_coron_d3.al","rb"))

#select x _var
model_x_var_d0 = meteo_model[:24][algo_d0["x_var"]]
model_x_var_d1 = meteo_model[24:48][algo_d1["x_var"]]
model_x_var_d2 = meteo_model[48:72][algo_d2["x_var"]]
model_x_var_d3 = meteo_model[72:96][algo_d3["x_var"]]

#forecast machine learning wind direction degrees
dir_ml_d0 = algo_d0["pipe"].predict(model_x_var_d0)
dir_ml_d1 = algo_d1["pipe"].predict(model_x_var_d1)
dir_ml_d2 = algo_d2["pipe"].predict(model_x_var_d2)
dir_ml_d3 = algo_d2["pipe"].predict(model_x_var_d3)

#compare results
df_mod=pd.DataFrame({"time":meteo_model[:96].index,
                      "ML_dir": np.concatenate((dir_ml_d0,dir_ml_d1,dir_ml_d2,dir_ml_d3),axis=0),
                      "WRF_dir1": meteo_model.dir1})
interval_d = pd.IntervalIndex.from_tuples([(-0.5,20), (20, 40), (40, 60),
                                           (60,80),(80,100),(100,120),(120,140),(140,160),
                                           (160,180),(180,200),(200,220),(220,240),
                                           (240,260),(260,280),(280,300),(300,320),
                                           (320,340),(340,360)])
labels_d = ['[0, 20]', '(20, 40]', '(40, 60]','(60, 80]', '(80, 100]',
          '(100, 120]', '(120, 140]','(140, 160]', '(160, 180]', '(180, 200]',
          '(200, 220]','(220, 240]', '(240, 260]', '(260, 280]', '(280, 300]',
          '(300, 320]', '(320, 340]', '(340, 360]']
df_mod["dir1_l"] = pd.cut(df_mod["WRF_dir1"], bins = interval_d,retbins=False,
                        labels = labels_d).map({a:b for a,b in zip(interval_d,labels_d)}).astype('category')          


#get actual wind dir
r_dir = requests.get("https://servizos.meteogalicia.gal/mgrss/observacion/ultimosHorariosEstacions.action?idEst=10085&idParam=DV_AVG_10m&numHoras=36")
json_data = json.loads(r_dir.content)

dir_o, time = [],[]
for c in json_data["listHorarios"]:
  for c1 in c['listaInstantes']:
    time.append(c1['instanteLecturaUTC'])  
    dir_o.append(c1['listaMedidas'][0]["valor"])

df_st = pd.DataFrame(np.array(dir_o),columns=["dir_o"],index= time)  
df_st.index = pd.to_datetime(df_st.index )

#label observed direction
df_st["dir_o_l"] = pd.cut(df_st["dir_o"], bins = interval_d,retbins=False,
                        labels = labels_d).map({a:b for a,b in zip(interval_d,labels_d)}).astype('category')


df_res = pd.concat([df_mod.set_index("time"),df_st],axis=1).dropna()
acc_ml = round(accuracy_score(df_res["dir_o_l"],df_res["ML_dir"]),2)
acc_wrf = round(accuracy_score(df_res["dir_o_l"],df_res["dir1_l"]),2)

if acc_ml < acc_wrf:
  score_wrf+=1
if acc_ml > acc_wrf:  
  score_ml+=1


#labels_d = np.array(pd.Categorical(np.asarray(labels_d)))

#show results wind direction
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_res.index, df_res['ML_dir'], marker="^", color="b",markersize=10, 
         markerfacecolor='w', linestyle='')
plt.plot(df_res.index, df_res['dir_o_l'], marker="*", color="g",markersize=10, 
         markerfacecolor='g', linestyle='')
plt.plot(df_res.index, df_res['dir1_l'], color="r",marker="v", markersize=10,
         markerfacecolor='w', linestyle='');
plt.grid(True)
#plt.yticks(np.arange(0,len(labels_d)),labels_d)
plt.legend(('Ml_dir', 'Observed_dir',"WRF_dir"),)
plt.title("Wind direction mean hour before (intervals)\nActual accuracy meteorologic model (point 1): {:.0%}. Reference: 29%\nActual accuracy machine learning: {:.0%}. Reference: 45%".format(acc_wrf,acc_ml))            
st.pyplot(fig)

#forecast d0
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][:24], df_mod['ML_dir'][:24], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][:24], df_mod['dir1_l'][:24], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_dir','WRF_dir'),)
plt.title("Wind direction mean hour before day=0 (intervals)\nAccuracy meteorological model (point 1) reference: 29%\nAccuracy machine learning reference: 45%")
#plt.yticks(np.arange(0,len(labels_d)-1),labels_d)
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#forecast d1

fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][24:48], df_mod['ML_dir'][24:48], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][24:48], df_mod['dir1_l'][24:48], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_dir','WRF_dir'),)
plt.title("Wind direction mean hour before day=1 (intervals)\nAccuracy meteorological model (point 1): 28%\nAccuracy machine learning: 42%")
#plt.yticks(np.arange(0,len(labels_d)),labels_d)
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#forecast d2
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][48:72], df_mod['ML_dir'][48:72], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][48:72], df_mod['dir1_l'][48:72], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_dir','WRF_dir'),)
plt.title("Wind direction mean hour before day=2 (intervals)\nAccuracy meteorological model (point 1): 26%\nAccuracy machine learning: 40%")
#plt.yticks(np.arange(0,len(labels_d)),labels_d)
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#forecast d3
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][72:96], df_mod['ML_dir'][72:96], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][72:96], df_mod['dir1_l'][72:96], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_dir','WRF_dir'),)
plt.title("Wind direction mean hour before day=3 (intervals)\nAccuracy meteorological model (point 1): 25%\nAccuracy machine learning: 39%")
#plt.yticks(np.arange(0,len(labels_d)),labels_d)
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#@title wind direction probabilities day 0

#probabilistic results
prob = (np.concatenate((algo_d0["pipe"].predict_proba(model_x_var_d0),
                        algo_d1["pipe"].predict_proba(model_x_var_d1),
                        algo_d2["pipe"].predict_proba(model_x_var_d2),
                        algo_d3["pipe"].predict_proba(model_x_var_d3)),
                       axis =0)).transpose()
df_prob = pd.DataFrame(prob,index = (algo_d0["pipe"].classes_ )).T
df_prob = df_prob[labels_d]
df_prob.index = meteo_model[:96].index.strftime('%b %d %H:%M Z')

# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[:24].columns[df_prob[:24].apply(lambda x: x <= 0.05).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
df_prob[:24].columns = pd.CategoricalIndex(df_prob.columns[:24], ordered=True)

#Show results day 0
fig, ax = plt.subplots()
sns.heatmap(df_prob[:24], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
ax.set_title("Wind direction probabilities intervals")
st.pyplot(fig)

#@title wind direction probabilities day 1
# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[24:48].columns[df_prob[24:48].apply(lambda x: x <= 0.05).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
fig, ax = plt.subplots()
sns.heatmap(df_prob[24:48], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
ax.set_title("Wind direction probabilities intervals")
st.pyplot(fig)

#@title wind direction probabilities day 2
# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[48:72].columns[df_prob[48:72].apply(lambda x: x <= 0.05).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
fig, ax = plt.subplots()
sns.heatmap(df_prob[48:72], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
ax.set_title("Wind direction probabilities intervals")
st.pyplot(fig)

#@title wind direction probabilities day 3
# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[72:96].columns[df_prob[72:96].apply(lambda x: x <= 0.05).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
fig, ax = plt.subplots()
sns.heatmap(df_prob[72:96], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
ax.set_title("Wind direction probabilities intervals")
st.pyplot(fig)


#@title wind speed Beaufort


#load algorithm file 
algo_d0 = pickle.load(open("algorithms/spd_coron_d0.al","rb"))
algo_d1 = pickle.load(open("algorithms/spd_coron_d1.al","rb"))
algo_d2 = pickle.load(open("algorithms/spd_coron_d2.al","rb"))
algo_d3 = pickle.load(open("algorithms/spd_coron_d3.al","rb"))


#select x _var
model_x_var_d0 = meteo_model[:24][algo_d0["x_var"]]
model_x_var_d1 = meteo_model[24:48][algo_d1["x_var"]]
model_x_var_d2 = meteo_model[48:72][algo_d2["x_var"]]
model_x_var_d3 = meteo_model[72:96][algo_d3["x_var"]]

#forecast machine learning wind speed beaufort
spd_ml_d0 = algo_d0["pipe"].predict(model_x_var_d0)
spd_ml_d1 = algo_d1["pipe"].predict(model_x_var_d1)
spd_ml_d2 = algo_d2["pipe"].predict(model_x_var_d2)
spd_ml_d3 = algo_d2["pipe"].predict(model_x_var_d3)


#compare results
df_mod=pd.DataFrame({"time":meteo_model[:96].index,
                      "ML_spd": np.concatenate((spd_ml_d0,spd_ml_d1,spd_ml_d2,spd_ml_d3),axis=0),
                      "WRF_spd1": meteo_model.mod1})
labels = ["F0","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12"]
interval = pd.IntervalIndex.from_tuples([(-1, 0.5), (.5, 1.5), (1.5, 3.3),(3.3,5.5),
                                     (5.5,8),(8,10.7),(10.7,13.8),(13.8,17.1),
                                     (17.1,20.7),(20.7,24.4),(24.4,28.4),(28.4,32.6),(32.6,60)])




df_mod["spd1_l"] = pd.cut(df_mod["WRF_spd1"], bins = interval,retbins=False,
                        labels = labels_d).map({a:b for a,b in zip(interval,labels)}).astype('category')          


#get actual wind dir
r_spd = requests.get("https://servizos.meteogalicia.gal/mgrss/observacion/ultimosHorariosEstacions.action?idEst=10085&idParam=VV_AVG_10m&numHoras=36")
json_data = json.loads(r_spd.content)

spd_o, time = [],[]
for c in json_data["listHorarios"]:
  for c1 in c['listaInstantes']:
    time.append(c1['instanteLecturaUTC'])  
    spd_o.append(c1['listaMedidas'][0]["valor"])

df_st = pd.DataFrame(np.array(spd_o),columns=["spd_o"],index= time)  
df_st.index = pd.to_datetime(df_st.index )

#label observed speed
df_st["spd_o_l"] = pd.cut(df_st["spd_o"], bins = interval,retbins=False,
                        labels = labels_d).map({a:b for a,b in zip(interval,labels)}).astype('category')


df_res = pd.concat([df_mod.set_index("time"),df_st],axis=1).dropna()
acc_ml = round(accuracy_score(df_res["spd_o_l"],df_res["ML_spd"]),2)
acc_wrf = round(accuracy_score(df_res["spd_o_l"],df_res["spd1_l"]),2)

if acc_ml < acc_wrf:
  score_wrf+=1
if acc_ml > acc_wrf:  
  score_ml+=1

#show results wind direction
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_res.index, df_res['ML_spd'], marker="^", color="b",markersize=16, 
         markerfacecolor='w', linestyle='')
plt.plot(df_res.index, df_res['spd_o_l'], marker="*", color="g",markersize=10, 
         markerfacecolor='g', linestyle='')
plt.plot(df_res.index, df_res['spd1_l'], color="r",marker="v", markersize=16,
         markerfacecolor='w', linestyle='');
plt.grid(True)
plt.legend(('Ml_spd', 'Observed_spd',"WRF_spd"),)
plt.title("Wind speed mean hour before (Beaufort)\nActual accuracy meteorologic model (point 0): {:.0%}. Reference: 36%\nActual accuracy machine learning: {:.0%}. Reference: 42%".format(acc_wrf,acc_ml))            
st.pyplot(fig)


#forecast d0
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][:24], df_mod['ML_spd'][:24], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][:24], df_mod['spd1_l'][:24], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_spd','WRF_spd'),)
plt.title("Wind speed mean hour before day=0 (Beaufort)\nAccuracy meteorologic model (point 0): 36%\nAccuracy machine learning: 42%")
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#forecast d1
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][24:48], df_mod['ML_spd'][24:48], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][24:48], df_mod['spd1_l'][24:48], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_spd','WRF_spd'),)
plt.title("Wind speed mean hour before day=1 (Beaufort)\nAccuracy meteorologic model (point 0): 34%\nAccuracy machine learning: 43%")
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#forecast d2
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][48:72], df_mod['ML_spd'][48:72], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][48:72], df_mod['spd1_l'][48:72], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_spd','WRF_spd'),)
plt.title("Wind speed mean hour before day=2 (Beaufort)\nAccuracy meteorologic model (point 0): 32%\nAccuracy machine learning: 38%")
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#forecast d3
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][72:96], df_mod['ML_spd'][72:96], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][72:96], df_mod['spd1_l'][72:96], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_spd','WRF_spd'),)
plt.title("Wind speed mean hour before day=3 (Beaufort)\nAccuracy meteorologic model (point 0): 31%\nAccuracy machine learning: 36%")
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#@title wind speed probabilities day 0

prob = (np.concatenate((algo_d0["pipe"].predict_proba(model_x_var_d0),
                        algo_d1["pipe"].predict_proba(model_x_var_d1),
                        algo_d2["pipe"].predict_proba(model_x_var_d2),
                        algo_d3["pipe"].predict_proba(model_x_var_d3)),
                       axis =0)).transpose()
df_prob = pd.DataFrame(prob,index = (algo_d0["pipe"].classes_ )).T

df_prob.index = meteo_model[:96].index.strftime('%b %d %H:%M Z')

#Show results day 0
fig, ax = plt.subplots()
sns.heatmap(df_prob[:24], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
ax.set_title("Wind intensity Beaufort probabilities")
st.pyplot(fig)

# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[24:48].columns[df_prob[24:48].apply(lambda x: x <= 0.05).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
fig, ax = plt.subplots()
sns.heatmap(df_prob[24:48], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
ax.set_title("Wind intensity Beaufort probabilities")
st.pyplot(fig)

#@title wind direction probabilities day 2
# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[48:72].columns[df_prob[48:72].apply(lambda x: x <= 0.05).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
fig, ax = plt.subplots()
sns.heatmap(df_prob[48:72], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
ax.set_title("Wind intensity Beaufort probabilities")
st.pyplot(fig)

#@title wind direction probabilities day 3
# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[72:96].columns[df_prob[72:96].apply(lambda x: x <= 0.05).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
fig, ax = plt.subplots()
sns.heatmap(df_prob[72:96], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
ax.set_title("Wind intensity Beaufort probabilities")
st.pyplot(fig)

#@title Rain 

def HSS(y_true,y_pred):
  """
  Heidke skill score if cm 2x2 table else 0
  """
  try:
    cm = pd.crosstab(y_true, y_pred)
    a = cm.values[0,0]
    b = cm.values[1,0]
    c = cm.values[0,1]
    d = cm.values[1,1]
    hss = 2*(a*d-b*c)/((a+c)*(c+d)+(a+b)*(b+d))
  except:
    hss = 0
  return round(hss,2)


#load algorithm file 
algo_d0 = pickle.load(open("algorithms/prec_coron_d0.al","rb"))
algo_d1 = pickle.load(open("algorithms/prec_coron_d1.al","rb"))
algo_d2 = pickle.load(open("algorithms/prec_coron_d2.al","rb"))
algo_d3 = pickle.load(open("algorithms/prec_coron_d3.al","rb"))


#select x _var
model_x_var_d0 = meteo_model[:24][algo_d0["x_var"]]
model_x_var_d1 = meteo_model[24:48][algo_d1["x_var"]]
model_x_var_d2 = meteo_model[48:72][algo_d2["x_var"]]
model_x_var_d3 = meteo_model[72:96][algo_d3["x_var"]]

#forecast machine learning wind direction degrees
prec_ml_d0 = algo_d0["pipe"].predict(model_x_var_d0)
prec_ml_d1 = algo_d1["pipe"].predict(model_x_var_d1)
prec_ml_d2 = algo_d2["pipe"].predict(model_x_var_d2)
prec_ml_d3 = algo_d2["pipe"].predict(model_x_var_d3)


#compare results
df_mod=pd.DataFrame({"time":meteo_model[:96].index,
                      "ML_prec": np.concatenate((prec_ml_d0,prec_ml_d1,prec_ml_d2,prec_ml_d3),axis=0),
                      "WRF_prec0": meteo_model.prec0})
interval_d = pd.IntervalIndex.from_tuples([(-0.5,0.1), (0.1, 100)])
labels_d = ['No Rain', 'Rain']
df_mod["prec0_l"] = pd.cut(df_mod["WRF_prec0"], bins = interval_d,retbins=False,
                        labels = labels_d).map({a:b for a,b in zip(interval_d,labels_d)}).astype('category')          


#get actual wind dir
r_prec = requests.get("https://servizos.meteogalicia.gal/mgrss/observacion/ultimosHorariosEstacions.action?idEst=10085&idParam=PP_SUM_1.5m&numHoras=36")
json_data = json.loads(r_prec.content)

prec_o, time = [],[]
for c in json_data["listHorarios"]:
  for c1 in c['listaInstantes']:
    time.append(c1['instanteLecturaUTC'])  
    prec_o.append(c1['listaMedidas'][0]["valor"])

df_st = pd.DataFrame(np.array(prec_o),columns=["prec_o"],index= time)  
df_st.index = pd.to_datetime(df_st.index )

#label observed direction
df_st["prec_o_l"] = pd.cut(df_st["prec_o"], bins = interval_d,retbins=False,
                        labels = labels_d).map({a:b for a,b in zip(interval_d,labels_d)}).astype('category')


df_res = pd.concat([df_mod.set_index("time"),df_st],axis=1).dropna()
hss_ml = HSS(df_res.prec_o_l,df_res.ML_prec)
hss_wrf = HSS(df_res.prec_o_l,df_res.prec0_l)

if hss_ml < hss_wrf:
  score_wrf+=1
if hss_ml > hss_wrf:  
  score_ml+=1


labels_d = np.array(pd.Categorical(np.asarray(labels_d)))

#show results 
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_res.index, df_res['ML_prec'], marker="^", color="b",markersize=10, 
         markerfacecolor='w', linestyle='')
plt.plot(df_res.index, df_res['prec_o_l'], marker="*", color="g",markersize=10, 
         markerfacecolor='g', linestyle='')
plt.plot(df_res.index, df_res['prec0_l'], color="r",marker="v", markersize=10,
         markerfacecolor='w', linestyle='');
plt.grid(True)
plt.legend(('Ml_dir', 'Observed_prec',"WRF_dir"),)
plt.title("Precipitation hour before \nActual Heidke skill score meteorologic model: {}. Reference: 0.49\nActual Heidke skill score machine learning: {}. Reference: 0.54".format(hss_wrf,hss_ml))            
st.pyplot(fig)


#forecast d0
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][:24], df_mod['ML_prec'][:24], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][:24], df_mod['prec0_l'][:24], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_prec','WRF_prec'),)
plt.title("Precipitation Day=0\nHeidke skill score meteorologic model:0.49\nHeidke skill score Machine learning:0.54")
#plt.yticks(np.arange(0,len(labels_d)-1),labels_d)
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#forecast d1

fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][24:48], df_mod['ML_prec'][24:48], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][24:48], df_mod['prec0_l'][24:48], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_prec','WRF_prec'),)
plt.title("Precipitation Day=1\nHeidke skill score meteorologic model:0.44\nHeidke skill score Machine learning:0.5")
#plt.yticks(np.arange(0,len(labels_d)),labels_d)
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#forecast d2
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][48:72], df_mod['ML_prec'][48:72], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][48:72], df_mod['prec0_l'][48:72], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_prec','WRF_prec'),)
plt.title("Precipitation Day=2\nHeidke skill score meteorologic model:0.4\nHeidke skill score Machine learning:0.42")
#plt.yticks(np.arange(0,len(labels_d)),labels_d)
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)

#forecast d3
fig, ax = plt.subplots(figsize=(10,6))
plt.plot(df_mod["time"][72:96], df_mod['ML_prec'][72:96], marker="^", color="b",markersize=8, 
         markerfacecolor='w', linestyle='')
plt.plot(df_mod["time"][72:96], df_mod['prec0_l'][72:96], color="r",marker="v", markersize=8,
         markerfacecolor='w', linestyle='');
plt.legend(('Ml_prec','WRF_prec'),)
plt.title("Precipitation Day=3\nHeidke skill score meteorologic model:0.36\nnHeidke skill score Machine learning:0.38")
#plt.yticks(np.arange(0,len(labels_d)),labels_d)
plt.grid(True, which = "both", axis = "both")
st.pyplot(fig)


#@title Rain probabilities day 0

prob = (np.concatenate((algo_d0["pipe"].predict_proba(model_x_var_d0),
                        algo_d1["pipe"].predict_proba(model_x_var_d1),
                        algo_d2["pipe"].predict_proba(model_x_var_d2),
                        algo_d3["pipe"].predict_proba(model_x_var_d3)),
                       axis =0)).transpose()
df_prob = pd.DataFrame(prob,index = (algo_d0["pipe"].classes_ )).T

df_prob.index = meteo_model[:96].index.strftime('%b %d %H:%M Z')

# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[:24].columns[df_prob[:24].apply(lambda x: x <= 0.01).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
fig, ax = plt.subplots()
sns.heatmap(df_prob[:24], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
plt.title('Rain probability')
st.pyplot(fig)

#@title Rain probabilities day 1

# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[24:48].columns[df_prob[24:48].apply(lambda x: x <= 0.01).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
fig, ax = plt.subplots()
sns.heatmap(df_prob[24:48], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
plt.title('Rain probability')
st.pyplot(fig)


#@title Rain probabilities day 2

# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[48:72].columns[df_prob[48:72].apply(lambda x: x <= 0.01).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
fig, ax = plt.subplots()
sns.heatmap(df_prob[48:72], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
plt.title('Rain probability')
st.pyplot(fig)



#@title Rain probabilities day 3

# Find the columns where all values are less than or equal to 5%
cols_to_drop = df_prob[72:96].columns[df_prob[72:96].apply(lambda x: x <= 0.01).all()]
df_prob.drop(cols_to_drop, axis=1, inplace=True)
fig, ax = plt.subplots()
sns.heatmap(df_prob[72:96], annot=True, cmap='coolwarm',
            linewidths=.2, linecolor='black',fmt='.0%',ax=ax)
plt.title('Rain probability')
st.pyplot(fig)





#global results
st.write("#### **Global results**")
st.write("Better meteorological model outcome: {}".format(score_wrf))
#st.write(best_wrf)
st.write("Better machine learning outcome: {}".format(score_ml))
#st.write(best_ml)


st.write("Project [link](https://github.com/granantuin/Coron)")
#load algorithm file gust
algo_rdir_d0 = pickle.load(open("algorithms/rdir_coron_d0.al","rb"))
algo_sddir_d0 = pickle.load(open("algorithms/sddir_coron_d0.al","rb"))
algo_rspd_d0 = pickle.load(open("algorithms/rspd_coron_d0.al","rb"))
algo_sdspd_d0 = pickle.load(open("algorithms/sdspd_coron_d0.al","rb"))


meteo_model = get_meteogalicia_model_4Km(algo_rdir_d0["coor"])

#add time variables
meteo_model["hour"] = meteo_model.index.hour
meteo_model["month"] = meteo_model.index.month
meteo_model["dayofyear"] = meteo_model.index.dayofyear
meteo_model["weekofyear"] = meteo_model.index.isocalendar().week.astype(int)


#select x _var
model_x_var_rdir = meteo_model[:24][algo_rdir_d0["x_var"]]
model_x_var_sddir = meteo_model[:24][algo_sddir_d0["x_var"]]
model_x_var_rspd = meteo_model[:24][algo_rspd_d0["x_var"]]
model_x_var_sdspd = meteo_model[:24][algo_sdspd_d0["x_var"]]

#forecast machine learning wind
rdir = algo_rdir_d0["pipe"].predict(model_x_var_rdir)
sddir = algo_sddir_d0["pipe"].predict(model_x_var_sddir)
rspd = algo_rspd_d0["pipe"].predict(model_x_var_rspd)
sdspd = algo_sdspd_d0["pipe"].predict(model_x_var_sdspd)


instant, dir, des_dir,mod, des_mod = get_wind()
dir_o, spd_o,time_now,dir_f,spd_f = [],[],[],[],[]

c=0
total_count= st.sidebar.number_input("intervals numbers", value=15, step=5)
while c<total_count:
  
  #Actual data
  #if((datetime.datetime.utcnow()-datetime.datetime.strptime(instant, '%Y-%m-%dT%H:%M:%S')).total_seconds()/60)>15:
    #instant, dir, des_dir,mod, des_mod = get_wind()

  dir_oi = abs(np.rint(np.random.normal(dir, des_dir)))
  if dir_oi> 360:
    dir_oi = dir_oi-360
  dir_o.append(dir_oi)

  spd_o.append(abs(round(np.random.normal(mod, des_mod),0)))

  time_now.append(datetime.datetime.utcnow().strftime("%H:%M:%S"))
  next_hour = (datetime.datetime.utcnow() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
  #machine learning forecast

  dir_fi = abs(np.rint(np.random.normal(rdir[next_hour.hour-1], sddir[next_hour.hour-1])))
  if dir_fi> 360:
    dir_fi = dir_fi-360
  dir_f.append(dir_fi)
  spd_f.append(abs(np.rint(np.random.normal(rspd[next_hour.hour-1], sdspd[next_hour.hour-1])*1.94384)))

  st.write(f"\rtime:",time_now[-1],"//","dir_f:",dir_f[-1],"dir_o:",dir_o[-1],"spd_f:",spd_f[-1],"spd_o:",spd_o[-1])
  c+=1
  sleep(3)
df_wind = pd.DataFrame({"dir_f": dir_f,
                          "spd_f": spd_f,
                          "dir_o":dir_o,
                          "spd_o":spd_o},
                         index = time_now)  

fig, ax = plt.subplots(figsize=(10,6))
df_wind[['dir_f',"dir_o"]].plot(grid=True, ax=ax, color = ["b","g"],title="time last measure: "+str(instant));
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10,6))
df_wind[['spd_f',"spd_o"]].plot(grid=True,ax=ax, color = ["b","g"],title="time last measure: "+str(instant));
st.pyplot(fig)



