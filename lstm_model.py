from math import sqrt

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tools.eval_measures import rmse
np.random.seed(4)
import matplotlib.pyplot as plt
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM, Dense

class Lstm_model:
    def __init__(self,precio):
        #Lectura de los datos
        df = pd.read_csv ('data/mora_castilla_v3.csv', parse_dates=True)
        if precio=='corriente':
            dataset= df.drop(['primera_actualkg'], axis=1)
            dataset = dataset.rename(
                columns={'corriente_actualkg': 'corriente'})  ##Renombramiento para el valor de la mora corriente
        else :
            dataset= df.drop(['corriente_actualkg'], axis=1)
            dataset = dataset.rename(
                columns={'primera_actualkg': 'primera'})  ##Renombramiento para el valor de la mora primera

        dataset['fecha'] = dataset['fecha'].astype(str)
        dataset['fecha'] = pd.to_datetime(dataset['fecha'])
        dataset = dataset.set_index('fecha')
        """Se setea el dataset a una frecuencia diaria, adicional un ordenado por index"""
        dataset = dataset.asfreq('D')
        dataset = dataset.sort_index()

        """Validacion de parametros para el modelo
        Division en prueba y test """
        n_sample = dataset.shape[0]
        n_train = int(0.90 * n_sample) + 1 ##Entrenamiento
        n_forecast = n_sample - n_train ##Prueba
        ts_train = dataset[:n_train] ##Datos entrenamiento
        ts_test = dataset[n_train:] ##Datos test
        sc = MinMaxScaler(feature_range=(0, 1))
        time_step = 15
        model=self.model(ts_train,time_step,sc)
        self.validate_model(model, precio,ts_test,time_step,sc)

    def graficar_predicciones( self, time_step,real, prediccion,precio):
        plt.plot(real[time_step:],color='red', label='Precio real mora '+precio)
        plt.plot(prediccion, color='blue', label='Prediccion')
        plt.ylim(1.1 * np.min(prediccion)/2, 1.1 * np.max(prediccion))
        plt.xlabel('Tiempo')
        plt.ylabel('Precio de mora de castilla')
        plt.legend()
        plt.savefig('results/06_validacion_lstm_prediccion_'+precio+'.png')
        plt.close()
    def model(self,set_entrenamiento,time_step,sc):
        ##Scikit-learn para normalizar estos valores en el rango de 0 a 1, usando la función MinMaxScaler
        set_entrenamiento_escalado = sc.fit_transform(set_entrenamiento)

        """15 datos consecutivos, y la idea es que cada uno de estos permita predecir el siguiente valor
        Los bloques de 15 datos serán almacenados en la variable X, mientras que el dato que se debe predecir (el dato 16 dentro de cada secuencia)
         se almacenará en la variable Y y será usado como la salida de la Red LSTM"""
        X_train = []
        Y_train = []
        m = len(set_entrenamiento_escalado)
        for i in range(time_step,m):
            # X: bloques de "time_step" datos: 0-time_step, 1-time_step+1, 2-time_step+2, etc
            X_train.append(set_entrenamiento_escalado[i-time_step:i,0])
            # Y: el siguiente dato
            Y_train.append(set_entrenamiento_escalado[i,0])
        X_train, Y_train = np.array(X_train), np.array(Y_train)
        """reajustar los sets que acabamos de obtener, para indicar que cada 
        ejemplo de entrenamiento a la entrada del modelo será un vector de 15x1"""
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
        """Creación y entrenamiento de la Red LSTM
        librerías de Keras correspondientes a las Redes LSTM. Usaremos el módulo Sequential para crear el contenedor, 
        al cual iremos añadiendo la Red LSTM (usando el módulo LSTM) y la capa de salida (usando el módulo Dense)"""
        dim_entrada = (X_train.shape[1],1)
        dim_salida = 1
        na = 50
        print(dim_entrada)
        "Contenedor usando el módulo Sequential"
        modelo = Sequential()
        modelo.add(LSTM(units=na, input_shape=dim_entrada))
        modelo.add(Dense(units=dim_salida))
        modelo.compile(optimizer='rmsprop', loss='mse')
        modelo.fit(X_train,Y_train,epochs=50,batch_size=32)
        return modelo
        """Predicción del precio de la mora"""

    def validate_model(self, modelo, precio,set_validacion,time_step,sc):
        x_test = set_validacion.values
        x_test = sc.transform(x_test)
        #Organizar el set `para tomar los bloques de 15 datos
        X_test = []
        for i in range(time_step,len(x_test)):
            X_test.append(x_test[i-time_step:i,0])
            print(x_test[i-time_step:i,0])
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))

        prediccion = modelo.predict(X_test)
        prediccion = sc.inverse_transform(prediccion)

        prediccion_graf=pd.DataFrame(prediccion)
        prediccion_graf.columns = ['prediccion']
        prediccion_graf.index=set_validacion.index[time_step:]
        dataset_prueba= pd.merge(set_validacion, prediccion_graf, on= ['fecha'], how='outer')
        col_graf = [precio, 'prediccion']
        ejes = dataset_prueba[col_graf].plot(figsize=(20, 20))
        plt.savefig('results/06_validaciongf01_lstm_prediccion_'+precio+'.png')
        plt.close()
        # Graficar resultados
        self.graficar_predicciones(time_step,set_validacion.values,prediccion,precio)

        from sklearn.metrics import mean_squared_error
        rmse = sqrt(mean_squared_error(set_validacion.values[time_step:],prediccion))
        print('RMSE: %.3f' % rmse)
