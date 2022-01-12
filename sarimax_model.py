# -*- coding: utf-8 -*-
"""

@author: Yohana Delgado Ramos
"""
"""Librerias necesarias proyecto"""
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.eval_measures import rmse
import pickle
import warnings
warnings.filterwarnings('ignore')


class Sarimax:
    def __init__(self,precio):
        #Lectura de los datos
        df = pd.read_csv ('data/mora_castilla_v3.csv', parse_dates=True)
        params=''
        if precio=='corriente':
            dataset= df.drop(['primera'], axis=1)
             ##Se adicionan los parametros dados de la evaluacion del modelo para precio corriente 0,27567.67067487708,"((2, 1, 2), (1, 1, 2, 7))"
            result_best = pd.read_csv('results/'+precio+'res_best.csv')
            result_best=result_best['param']
            result_best=result_best[0].replace('((','').replace('))','').replace(')','').replace('(','').replace(' ','')
            result_best=result_best.split(',')

            params =  list([(int(result_best[0]),int(result_best[1]),int(result_best[2])), (int(result_best[3]),int(result_best[4]),int(result_best[5]),int(result_best[6]))])


        else :
            dataset= df.drop(['corriente'], axis=1)
            result_best = pd.read_csv('results/' + precio + 'res_best.csv')
            result_best = result_best['param']
            result_best = result_best[0].replace('((', '').replace('))', '').replace(')', '').replace('(', '')
            result_best = result_best.split(',')
            params =  list([(int(result_best[0]),int(result_best[1]),int(result_best[2])), (int(result_best[3]),int(result_best[4]),int(result_best[5]),int(result_best[6]))])

        dataset['fecha'] = dataset['fecha'].astype(str)
        dataset['fecha'] = pd.to_datetime(dataset['fecha'])
        dataset = dataset.set_index('fecha')
        """Se setea el dataset a una frecuencia diaria, adicional un ordenado por index"""
        dataset= dataset.asfreq('D')
        dataset = dataset.sort_index()

        """Validacion de parametros para el modelo
        Division en prueba y test """
        n_sample = dataset.shape[0]
        n_train = int(0.95 * n_sample) + 1 ##Entrenamiento
        n_forecast = n_sample - n_train ##Prueba
        ts_train = dataset[:n_train] ##Datos entrenamiento
        ts_test = dataset[n_train:] ##Datos test

        ##Creacion y entrenamiento del modelo
        start = len(ts_train)
        end = len(ts_train) + len(ts_test) - 1
        print ('start' , start,  'end' , end)

        model_sarimax= self.sarimax_model(dataset,params,precio)
        self.validate_results(model_sarimax,precio, start, end,ts_test)
    def sarimax_model(self,n_train,params,precio):
        print(params[0])
        arima_model = SARIMAX(n_train, order=params[0],
                                         seasonal_order=params[1])
        model_results = arima_model.fit()
        ##Guardar el modelo
        pickle.dump(model_results, open('model/sarimax_'+precio+'.pkl', 'wb'))

        return model_results

    def validate_results(self,model,precio, start, end, ts_test):

        f = open('results/05_resultados_'+precio+".txt", "w")
        print("Ljung-box p-values:\n" + str(model.test_serial_correlation(method='ljungbox')[0][1]),file=f)
        print('\n',file=f)
        print(model.summary(),file=f)

        pred_test = model.predict(start=start, end=end)
        pred_test = pd.DataFrame(pred_test)
        pred_test.columns = ['prediccion']
        pred_test.index.name = 'fecha'
        error = rmse(ts_test[precio], pred_test['prediccion'])
        print('\n'+'Error rmse='+str(round(error,2)), file=f)

        prediccion_graf = model.predict(start=start, end=end)
        prediccion_graf = pd.DataFrame(prediccion_graf)
        prediccion_graf.columns = ['prediccion']
        prediccion_graf.index.name = 'fecha'

        # Grafica de comparacion entre la prediccion y el valor real
        plt.close()

        dataset_prueba = pd.merge(ts_test, prediccion_graf, on=['fecha'], how='outer')
        col_graf = [precio, 'prediccion']
        ejes = dataset_prueba[col_graf].plot(figsize=(10, 9), fontsize=(12), title='Prediccion mora de castilla precio '+precio)
        plt.savefig('results/05_validacion_'+precio+'_prediccion.png')