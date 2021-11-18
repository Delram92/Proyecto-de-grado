# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 20:10:00 2021

@author: Yohana Delgado Ramos
"""

"""Librerias necesarias proyecto"""
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Analisis:
    def __init__(self, url_corabastos):
        self.download_data(url_corabastos)
        ##Validacion dataset inicial , procesado para dejar indices dentro de los datos.
        df = pd.read_csv('data/mora_castilla.csv', index_col=1, parse_dates=True)
        df = df.drop(['Unnamed: 0'], axis=1)
        df['year'] = df.index.year
        df['month'] = df.index.month
        df['day'] = df.index.strftime('%A')
        """ Comando para ver datos """
        print('Cantidad de Filas y columnas:', df.shape, '\n')
        print('Nombre columnas:', df.columns, '\n')
        print(df.corr(), '\n')
        print(df.info)
        print('\n')
        col_graf = ['corriente', 'primera', 'extra']
        self.profiling_data(df,'01_analisis_pre_',col_graf)
        ##guardar_datos v2
        df.to_csv('data/mora_castilla_v2.csv')

    def download_data(self, url_corabastos):
        prec = requests.post(url_corabastos)
        precio_mora = prec.text
        datos = precio_mora.replace('{"nombre":"MORA DE CASTILLA","corriente":"', '').replace('","primera":"',':').replace('","extra":"', ':').replace('","fecha":"', ':').replace('"}', '')
        datos = datos.split(":")
        corriente = datos[0].split(',')
        primera = datos[1].split(',')
        extra = datos[2].split(',')
        fecha = datos[3].split(',')
        df = pd.DataFrame(list(zip(fecha, corriente, primera, extra)),
                              columns=['fecha', 'corriente', 'primera', 'extra'])
        df.to_csv('data/mora_castilla.csv')  ##Guardar como plano

    def profiling_data(self, df, imagen, col_graf):
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
        fig, ejes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
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
        fig, ejes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
        for nombre, eje in zip(['corriente', 'primera', 'extra'], ejes):
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