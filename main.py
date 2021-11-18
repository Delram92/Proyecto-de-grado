
from flask import Flask, request, jsonify, render_template
import pickle
import os
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)
port = int(os.getenv("PORT", 8085))

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

start=1860
total_registros=2065


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    int_features = [int(x) for x in request.form.values()]
    precio=int_features[0]
    tipo_prediccion=''
    if precio==1 :
        tipo_prediccion='corriente'
    else :
        tipo_prediccion = 'primera'

    model = pickle.load(open('model/sarimax_'+tipo_prediccion+'.pkl', 'rb'))

    end =total_registros + int_features[1]
    prediction = model.predict(start, end )
    prediccion_graf = pd.DataFrame(prediction)
    prediccion_graf.columns = ['prediccion']
    prediccion_graf.index.name = 'fecha'
    prediccion_graf=prediccion_graf[total_registros-start:]
    col_graf = ['prediccion']
    eje = prediccion_graf[col_graf].plot(figsize=(20, 20))
    eje.set_ylabel('Precio diario mora '+tipo_prediccion)
    eje.set_title('Prediccion precio '+tipo_prediccion + ' Mora de castilla ')
    nombre_fig='sarimax_predict.png'
    print(nombre_fig)
    plt.savefig('static/images/'+nombre_fig)


    plt.close()


    return render_template('predict.html')




if __name__ == '__main__':
    app.run(host='localhost', port=port)

