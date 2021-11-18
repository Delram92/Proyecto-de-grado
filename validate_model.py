# -*- coding: utf-8 -*-
"""
@author: Yohana Delgado Ramos
"""
import sarimax_model_test

class Modelamiento:
    def __init__(self):
        sarimax_model_test.Sarimax_Test('corriente')
        sarimax_model_test.Sarimax_Test('primera')

def main():
    Modelamiento()

if __name__ == '__main__':
    main()