# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 20:10:00 2021

@author: Yohana Delgado Ramos
"""
import sys

"""Librerias necesarias proyecto"""
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas_profiling import ProfileReport

class Analisis:
    def __init__(self, url_corabastos):
        self.download_data(url_corabastos)
        ##Validacion dataset inicial , procesado para dejar indices dentro de los datos.
        df = pd.read_csv('data/mora_castilla.csv', index_col=1, parse_dates=True)
        df = df.drop(['Unnamed: 0'], axis=1)

        f = open('results/01_validacion_set_datos.txt', "w")
        print('Set de datos original',file=f)
        print(df.head() , file=f)
        print('\n',file=f)
        print('Cantidad de Filas y columnas:', df.shape, '\n',file=f)
        print('Nombre columnas:', df.columns, '\n',file=f)

        df['year'] = df.index.year
        df['month'] = df.index.month
        df['day'] = df.index.strftime('%A')

        print('Set de datos modificado',file=f)
        print(df.head(),file=f )
        print('\n',file=f)
        print('Cantidad de Filas y columnas:', df.shape, '\n',file=f)
        print('Nombre columnas:', df.columns, '\n',file=f)
        f.close()
        profile = df.profile_report(title="Perfilado set de datos corabastos")
        profile.to_file(output_file="results/01_profiling_corabastos.html")

        col_graf = ['corriente', 'primera', 'extra']
        self.profiling_data(df,'01_analisiscorabastos_pre_',col_graf)
        ##guardar_datos v2
        df.to_csv('data/mora_castilla_v2.csv')

        #####################Validacion set de datos DANE ##################
        df_dane = pd.read_json('data/mora_castilla_dane.json')
        f = open('results/01_validacion_set_datosdane.txt', "w")
        print('Set de datos original', file=f)
        print(df_dane.head(), file=f)
        print('\n', file=f)
        print('Cantidad de Filas y columnas:', df_dane.shape, '\n', file=f)
        print('Nombre columnas:', df_dane.columns, '\n', file=f)
        f.close()
        df_dane = df_dane.drop(['NOM_ABASTO', 'COD_ART', 'NOM_ART', 'PROM_DIARIO', 'VAR_DIARIA'], axis=1)
        df_dane = df_dane.rename(
            columns={'Date': 'fecha'})
        df_dane['VAL_MAX'] = df_dane['VAL_MAX'] * 7  ##Se multiplica por 7, dado que los valores del dane estan en kg
        df_dane['VAL_MIN'] = df_dane['VAL_MIN'] * 7
        df_dane = df_dane.set_index('fecha')
        df_dane['year'] = df_dane.index.year
        df_dane['month'] = df_dane.index.month
        df_dane['day'] = df_dane.index.strftime('%A')
        df_dane = df_dane[['VAL_MAX',  'VAL_MIN', 'year', 'month', 'day']]
        profile = df_dane.profile_report(title="Perfilado set de datos dane")
        profile.to_file(output_file="results/01_profiling_dane.html")

        col_graf = ['VAL_MAX', 'VAL_MIN']
        self.profiling_data(df_dane, '01_analisisDANE_pre_', col_graf)

        #####################Validacion set de datos IPC ##################
        ##Dataset IPC desde 2016 a la fecha
        df_ipc = pd.read_excel('data/1.2.5.IPC_Serie_variaciones.xlsx', skiprows=7,
                               names=['fecha', 'indice', 'inflacion_anual', 'inflacion_mensual',
                                      'inflacion_anno_corrido'])
        f = open('results/01_validacion_IPC.txt', "w")
        print('Set de datos original', file=f)
        print(df_ipc.head(), file=f)
        print('\n', file=f)
        print('Cantidad de Filas y columnas:', df_ipc.shape, '\n', file=f)
        print('Nombre columnas:', df_ipc.columns, '\n', file=f)
        f.close()

        df_ipc = df_ipc[df_ipc['fecha'] >= 201601]
        df_ipc['fecha'] = pd.to_datetime(df_ipc['fecha'].astype(str) + '01')
        df_ipc = df_ipc.set_index('fecha')
        df_ipc['year'] = df_ipc.index.year
        df_ipc['month'] = df_ipc.index.month
        df_ipc = df_ipc.drop(['inflacion_anual','inflacion_mensual','inflacion_anno_corrido'], axis=1)
        profile = df_ipc.profile_report(title="Perfilado set de datos IPC")
        profile.to_file(output_file="results/01_profiling_IPC.html")




    def download_data(self, url_corabastos):
        prec = requests.post(url_corabastos)
        precio_mora = prec.text
        try:
            datos = precio_mora.replace('{"nombre":"MORA DE CASTILLA","corriente":"', '').replace('","primera":"',':').replace('","extra":"', ':').replace('","fecha":"', ':').replace('"}', '')
            datos = datos.split(":")
            corriente = datos[0].split(',')
            primera = datos[1].split(',')
            extra = datos[2].split(',')
            fecha = datos[3].split(',')
            df = pd.DataFrame(list(zip(fecha, corriente, primera, extra)),
                                  columns=['fecha', 'corriente', 'primera', 'extra'])
            df.to_csv('data/mora_castilla.csv')  ##Guardar como plano
        except :
            print(sys.exc_info()[0])


    def profiling_data(self, df, imagen, col_graf):
        profile = df.profile_report(title= imagen +'Perfilado set de datos')
        profile.to_file(output_file='results/'+imagen +'profiling.html')

        num_subplots = len(col_graf)
        """Validacion de atributos a travez de bigotes, validaciones pertinentes"""
        #color = '#0f4b78'
        df.plot(kind='box', subplots=True, layout=(5, 4), sharex=False, sharey=False, figsize=(14, 14),
                    title='Gráfico de bigotes para cada atributo')
        plt.savefig('results/'+imagen+'bigotes_mora_01.png')
        plt.close()

        """Validacion de atributos por histogramas"""
        df.hist(bins=30, figsize=(14, 14), color='blue')
        plt.suptitle("Histograma para cada atributo", fontsize=10)
        plt.savefig('results/'+imagen+'hist_mora_02.png')
        plt.close()

        """Validacion de atributos series de tiempo"""
        ejes = df[col_graf].plot(figsize=(20, 20), subplots=True)
        for eje in ejes:
            eje.set_ylabel('Precio diario')
        plt.savefig('results/'+imagen+'time_series_03.png')
        plt.close()

        """Validacion de datos, enfocados por mes, para revisar comportamiento en pandemia"""

        fig, ejes = plt.subplots(num_subplots, 1, figsize=(11, 10), sharex=True)
        for nombre, eje in zip(col_graf, ejes):
            sns.boxplot(data=df, x='month', y=nombre, ax=eje)
            eje.set_title(nombre)
            if eje != ejes[-1]:
                eje.set_xlabel('')
            for eje in ejes:
                eje.set_ylabel('Precio diario')
        plt.savefig('results/'+imagen+'meses_04.png')
        plt.close()

        """Validacion de datos, enfocados por dia, para revisar comportamiento en pandemia"""
        fig, ejes = plt.subplots(num_subplots, 1, figsize=(11, 10), sharex=True)
        for nombre, eje in zip(col_graf, ejes):
            sns.boxplot(data=df, x='day', y=nombre, ax=eje)
            eje.set_title(nombre)
            if eje != ejes[-1]:
                eje.set_xlabel('')
            for eje in ejes:
                eje.set_ylabel('Precio diario')
        plt.savefig('results/'+imagen+'dia_05.png')
        plt.close()

        """Validacion de datos, enfocados en 2020, para revisar comportamiento en pandemia"""
        df_2020 = df.loc['2020']
        ejes = df_2020[col_graf].plot(figsize=(15, 15), subplots=True)
        for eje in ejes:
            eje.set_ylabel('Precio diario')
        plt.savefig('results/'+imagen+'time_series_2020_06.png')
        plt.close()