# -*- coding: utf-8 -*-
"""
@author: Yohana Delgado Ramos
"""
import sarimax_model
import lstm_model

class Modelamiento:
    def __init__(self):
        sarimax_model.Sarimax('corriente')
        sarimax_model.Sarimax('primera')
       # lstm_model.Lstm_model('corriente')
        #lstm_model.Lstm_model('primera')
def main():
    Modelamiento()

if __name__ == '__main__':
    main()