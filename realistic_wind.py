import streamlit as st
from lightgbm.sklearn import LGBMRegressor
import numpy as np
import pandas as pd
import pickle
import requests
import json
from datetime import timedelta
import sklearn
import requests
import json
import time
import datetime


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


#Show on line results
instant, dir, des_dir,mod, des_mod = get_wind()
placeholder = st.empty()
while True:
  
  #Actual data
  if((datetime.datetime.utcnow()-datetime.datetime.strptime(instant, '%Y-%m-%dT%H:%M:%S')).total_seconds()/60)>15:
    instant, dir, des_dir,mod, des_mod = get_wind()

  dir_o = abs(round(np.random.normal(dir, des_dir),0))
  spd_o =  abs(round(np.random.normal(mod, des_mod),0)) 
  
  if dir_o> 360:
    dir_o = dir_o-360

  time_now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") 
  next_hour = (datetime.datetime.utcnow() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
   
  st.write("time GMT:",time_now,"time last mesure:",instant)
  
  #machine learning forecast
  dir_f = np.rint(np.random.normal(rdir, sddir))
  spd_f = abs(np.rint(np.random.normal(rspd, sdspd)*1.94384))

  dir_f[dir_f > 360] -= 360
  dir_f[dir_f < 0] += 360

  #compare results
  df_wind = pd.DataFrame({"dir": dir_f,
                          "spd": spd_f},
                         index = meteo_model[:24].index)
  df_wind["dir_obs"] = "*"
  df_wind["spd_obs"] = "*"

  df_wind.at[next_hour,"dir_obs"]= dir_o
  df_wind.at[next_hour,"spd_obs"]= spd_o
  
  st.dataframe(df_wind[["dir","dir_obs","spd","spd_obs"]])
  placeholder.empty()
  time.sleep(2)
  
