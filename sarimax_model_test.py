# -*- coding: utf-8 -*-
"""

@author: Yohana Delgado Ramos
"""
"""Librerias necesarias proyecto"""
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.tsa.api as smt
import seaborn as sns
from statsmodels.tsa.statespace.sarimax import SARIMAX
import itertools
import warnings
warnings.filterwarnings("ignore")

class Sarimax_Test:
    def __init__(self,precio):
        #Lectura de los datos
        df = pd.read_csv ('data/mora_castilla_v3.csv', parse_dates=True)
        print('Ser_datos_final', df)
        if precio=='corriente':
            dataset= df.drop(['primera'], axis=1)
        else :
            dataset= df.drop(['corriente'], axis=1)

        dataset['fecha'] = dataset['fecha'].astype(str)
        dataset['fecha'] = pd.to_datetime(dataset['fecha'])
        dataset = dataset.set_index('fecha')
        """Se setea el dataset a una frecuencia diaria, adicional un ordenado por index"""
        dataset= dataset.asfreq('D')
        dataset = dataset.sort_index()
        ##Validacion de estacionalidad
        valida_dataset = dataset[precio]
        self.valida_estacionalidad(valida_dataset,precio,'')
        ##Graficos estadisticos
        self.grafico_est(dataset, precio)

        serie_semanal = dataset.resample('W').mean()
        serie_dif=self.difference(serie_semanal[precio])
        serie_dif.index = serie_semanal.index[1:]
        self.valida_estacionalidad(serie_dif, precio, 'serie semanal dif')
        self.grafico_est(serie_dif, precio+'semal_dif')



        """Validacion de parametros para el modelo
        Division en prueba y test """
        n_sample = dataset.shape[0]
        n_train = int(0.95 * n_sample) + 1 ##Entrenamiento
        n_forecast = n_sample - n_train ##Prueba
        ts_train = dataset[:n_train] ##Datos entrenamiento
        ts_test = dataset[n_train:] ##Datos test
        self.validate_param(ts_train,precio)  # Metodo para validar parametros del modelo sarimax

    def valida_estacionalidad(self, dataset,precio, grafico):
        ##Dickey Fuller Aumentada (ADF)
        from statsmodels.tsa.stattools import adfuller
        # Aquí se usa un año como ventana, y el valor de cada vez t se reemplaza por el valor medio de los 12 meses anteriores (incluido él mismo), y la desviación estándar es la misma.
        rolmean = dataset.rolling(12).mean()
        rolstd = dataset.rolling(12).std()
        # plot rolling statistics:
        fig = plt.figure()
        fig.add_subplot()
        orig = plt.plot(dataset, color='blue', label='Original')
        mean = plt.plot(rolmean, color='red', label='Rolling mean')
        std = plt.plot(rolstd, color='black', label='Rolling standard deviation')
        plt.legend(loc='best')
        plt.title('Rolling Mean & Standard Deviation '+ precio)
        plt.savefig('results/04_Validacion_estacionalidad_ADF_'+ precio+grafico+'.png')
        # Dickey-Fuller test:
        dftest = adfuller(dataset, autolag='AIC')
        variables=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used']
       # print((dft))
        #El  elemento   anterior   de    la    salida    de  # dftest es el valor de detección, el valor p, el número de rezagos, el número de observaciones utilizadas y el valor crítico bajo cada nivel de confianza.
        dfoutput = pd.Series(dftest[0:4], index=variables)
        #print(dfoutput)
        for key, value in dftest[4].items():
            dfoutput['Critical value (%s)' % key] = value
            variables.append('Critical value (%s)' % key)
        print(dfoutput)
        ##Guardar resultados en txt
        f = open('results/04_estacionalidad_'+precio+grafico+".txt", "w")
        print('estacionalidad precio mora '+precio,file=f)
        print(dfoutput,file=f)
        f.close()



    #Gráfico estadístico, ACF, gráfico PACF
    def grafico_est(self,dataset,titulo ):
        lags = 30
        title = 'Serie de tiempo Mora '+titulo
        figsize = (14, 8)
        fig = plt.figure(figsize=figsize)
        layout = (2, 2)
        ts_ax = plt.subplot2grid(layout, (0, 0))
        hist_ax = plt.subplot2grid(layout, (0, 1))
        acf_ax = plt.subplot2grid(layout, (1, 0))
        pacf_ax = plt.subplot2grid(layout, (1, 1))
        dataset.plot(ax=ts_ax)
        ts_ax.set_title(title)
        dataset.plot(ax=hist_ax, kind='hist', bins=25)
        hist_ax.set_title('Histogram')
        smt.graphics.plot_acf(dataset, lags=lags, ax=acf_ax)
        smt.graphics.plot_pacf(dataset, lags=lags, ax=pacf_ax)
        [ax.set_xlim(0) for ax in [acf_ax, pacf_ax]]
        sns.despine()
        fig.tight_layout()
        plt.savefig('results/04_grafica_estadistica_'+titulo+'.png')
        return ts_ax, acf_ax, pacf_ax

    def sarimax_param(self,dataset, parameters):
        results = []
        for param in parameters:
            try:
                model = SARIMAX(dataset, order=(param[0]),
                                seasonal_order=(param[1]))
                res = model.fit()
                results.append((res.aic, param))
            except Exception as e:
                print(e)
                continue
        return results  # set parameter range

    def validate_param(self,ts_train,precio):
        p,d,q = range(0,3),[1],range(0,3)
        P,D,Q,s = range(0,3),[1],range(0,3),[7]
        # list of all parameter combos
        pdq = list(itertools.product(p, d, q))
        seasonal_pdq = list(itertools.product(P, D, Q, s))
        all_param = list(itertools.product(pdq,seasonal_pdq))
        all_res = self.sarimax_param(ts_train,all_param)
        ##Validar mejor resultado
        table_res=pd.DataFrame(all_res, columns=['aic','param'])
        table_res=table_res.sort_values('aic', ascending=True).reset_index(drop=True)
        res_best=table_res[0:6]
        res_best.to_csv('results/'+precio+'res_best.csv')##Guardar como plano mejores resultados
        # creacion de una serie diferencial

    def difference(self, datos):
        diff = list()
        for i in range(1, len(datos)):
            value = datos[i] - datos[i - 1]
            diff.append(value)
        return pd.Series(diff)


