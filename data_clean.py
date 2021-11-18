# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 19:32:40 2021

@author: Yohana Delgado Ramos
"""
"""Librerias necesarias proyecto"""
import pymongo
import pandas as pd
import numpy as np
import warnings
import data_analysis  as prf
warnings.filterwarnings('ignore')

class Clean:
    def  __init__(self, url_mongo):

        ##Dataset precios mora
        df = pd.read_csv('data/mora_castilla_v2.csv', index_col=[0], parse_dates=True)
        df['year'] = df.index.year
        df['month'] = df.index.month
        df['day'] = df.index.strftime('%A')

        df_dane= pd.read_json('data/mora_castilla_dane.json')
        df_dane= df_dane.drop(['NOM_ABASTO','COD_ART','NOM_ART','PROM_DIARIO','VAR_DIARIA'], axis=1)
        df_dane = df_dane.rename(
            columns={'Date': 'fecha','VAL_MAX':'primera','VAL_MIN':'corriente'})
        df_dane['extra'] = df_dane['primera']*7 ##Se multiplica por 7, dado que los valores del dane estan en kg
        df_dane['primera']=df_dane['primera']*7
        df_dane['corriente'] = df_dane['corriente'] * 7
        df_dane=df_dane.set_index('fecha')
        df_dane['year'] = df_dane.index.year
        df_dane['month'] = df_dane.index.month
        df_dane['day'] = df_dane.index.strftime('%A')
        df_dane=df_dane[['corriente','primera','extra','year','month','day']]
        #print(df_dane)
        df = df.combine_first(df_dane)
        ##Dataset IPC desde 2016 a la fecha
        df_ipc = pd.read_excel('data/1.2.5.IPC_Serie_variaciones.xlsx', skiprows=12,
                            names=['fecha', 'indice', 'inflacion_anual', 'inflacion_mensual', 'inflacion_anno_corrido'])
        df_ipc = df_ipc[df_ipc['fecha'] >= 201601]
        df_ipc['fecha'] = pd.to_datetime(df_ipc['fecha'].astype(str) + '01')
        df_ipc = df_ipc.set_index('fecha')
        df_ipc['year'] = df_ipc.index.year
        df_ipc['month'] = df_ipc.index.month
        ##Reemplazo de outliers
        df_clean = self.replace_outliers(df)
        df_clean['fecha'] = df_clean.index
        ##Validacion luego de limpieza
        col_graf = ['corriente', 'primera', 'extra']
        prf.Analisis.profiling_data(self, df_clean, '02_clean_', col_graf)
        df_merge= self.merge_dataset(df_clean,df_ipc)
        atributos = ['primera_actualkg', 'corriente_actualkg']
        prf.Analisis.profiling_data(self, df_merge, '03_real_', atributos)

    def replace_outliers(self, df):
        df_clean = df
        """Se itera por año, y mes  para sacar promedio por año y no del total, po la variacion de los datos
         el reemplazo de outliers realiza por la media del año-mes"""
        values = (max(df_clean.year) - min(df_clean.year)) + 1
        year = min(df_clean.year)
        for i in range(values):
            values_month = (max(df_clean.loc[str(year)].month) - min(df_clean.loc[str(year)].month)) + 1
            for j in range(values_month):
                """ reemplazar valores por debajo y encima de la media por la media por año mes 
                1. Precio primera
                """
                s = df_clean.loc[str(year) + '-' + str(j + 1)].primera
                iqr = (np.quantile(s, 0.75)) - (np.quantile(s, 0.25))
                upper_bound = np.quantile(s, 0.75) + (1.5 * iqr)
                lower_bound = np.quantile(s, 0.25) - (1.5 * iqr)
                df_clean.loc[str(year) + '-' + str(j + 1)]['primera'] = df_clean.loc[
                    str(year) + '-' + str(j + 1)].primera.mask(
                    df_clean.loc[str(year) + '-' + str(j + 1)].primera > upper_bound,
                    df_clean.loc[str(year) + '-' + str(j + 1)].primera.median())
                df_clean.loc[str(year) + '-' + str(j + 1)]['primera'] = df_clean.loc[
                    str(year) + '-' + str(j + 1)].primera.mask(
                    df_clean.loc[str(year) + '-' + str(j + 1)].primera < lower_bound,
                    df_clean.loc[str(year) + '-' + str(j + 1)].primera.median())
                """ reemplazar valores por debajo y encima de la media por la media por año mes 
                1. Precio corriente
                """
                s = df_clean.loc[str(year) + '-' + str(j + 1)].corriente
                iqr = (np.quantile(s, 0.75)) - (np.quantile(s, 0.25))
                upper_bound = np.quantile(s, 0.75) + (1.5 * iqr)
                lower_bound = np.quantile(s, 0.25) - (1.5 * iqr)
                df_clean.loc[str(year) + '-' + str(j + 1)]['corriente'] = df_clean.loc[
                    str(year) + '-' + str(j + 1)].corriente.mask(
                    df_clean.loc[str(year) + '-' + str(j + 1)].corriente > upper_bound,
                    df_clean.loc[str(year) + '-' + str(j + 1)].corriente.median())
                df_clean.loc[str(year) + '-' + str(j + 1)]['corriente'] = df_clean.loc[
                    str(year) + '-' + str(j + 1)].corriente.mask(
                    df_clean.loc[str(year) + '-' + str(j + 1)].corriente < lower_bound,
                    df_clean.loc[str(year) + '-' + str(j + 1)].corriente.median())
                """ reemplazar valores por debajo y encima de la media por la media por año mes 
                1. Precio extra
                """
                s = df_clean.loc[str(year) + '-' + str(j + 1)].extra
                iqr = (np.quantile(s, 0.75)) - (np.quantile(s, 0.25))
                upper_bound = np.quantile(s, 0.75) + (1.5 * iqr)
                lower_bound = np.quantile(s, 0.25) - (1.5 * iqr)
                df_clean.loc[str(year) + '-' + str(j + 1)]['extra'] = df_clean.loc[
                    str(year) + '-' + str(j + 1)].extra.mask(
                    df_clean.loc[str(year) + '-' + str(j + 1)].extra > upper_bound,
                    df_clean.loc[str(year) + '-' + str(j + 1)].extra.median())
                df_clean.loc[str(year) + '-' + str(j + 1)]['extra'] = df_clean.loc[
                    str(year) + '-' + str(j + 1)].extra.mask(
                    df_clean.loc[str(year) + '-' + str(j + 1)].extra < lower_bound,
                    df_clean.loc[str(year) + '-' + str(j + 1)].extra.median())
            year = year + 1
            #print(year)
        return df

    def save_data(url_mongo,df):
        client = pymongo.MongoClient(url_mongo)

        dbname = client['agroacacias']


        collection_name = dbname["mora_catilla"]
        for index, row in df.iterrows():  #Iterador para recorrer cada uno de los registros del archivo cargado

            doc={
                'fecha':index,
                'corriente': row["corriente"] ,
                'primera': row["primera"] ,
                'extra':row["extra"] ,
                'year':row["year"] ,
                'month':row["month"] ,
                'day':row["day"]

               }


            collection_name.insert_one(doc)

        client.close()

    def merge_dataset(self,df_mora, df_ipc):

        dataset_mora= pd.merge(df_mora, df_ipc, on= ['month', 'year'], how='outer')
        dataset_mora=dataset_mora.set_index('fecha')

        ipc_final= float((df_ipc.loc[max(df_ipc.index)].indice))
        dataset_mora["primerakg"]= (dataset_mora["primera"]/7)
        dataset_mora["corrientekg"]= (dataset_mora["corriente"]/7)
        dataset_mora["primera_actualkg"]= round(dataset_mora["primerakg"]*(ipc_final/dataset_mora["indice"])).round(decimals=2).astype(int)
        dataset_mora["corriente_actualkg"]= round(dataset_mora["corrientekg"]*(ipc_final/dataset_mora["indice"])).round(decimals=2).astype(int)
        atributos = ['primera_actualkg','corriente_actualkg']
        dataset_mora_save=  dataset_mora[atributos]
        dataset_mora_save=dataset_mora_save.asfreq('D', method='bfill') ##Se realiza llenado de valores vacios con el valor el metodo back Y SE ASIGNA LA FRECUENCIA A DIARIA
        dataset_mora_save.to_csv('data/mora_castilla_v3.csv')
        return dataset_mora