# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 20:10:00 2021

@author: Yohana Delgado Ramos
"""
import data_analysis
import data_clean
import sys

class Procesamiento:
	def __init__(self):
		fecha_inicio = '2016-01-01'
		fecha_fin = '2021-10-30'
		url_corabastos = "https://api.precioscorabastos.com.co/precios/public/tendencia/producto?codigo_producto=204401&inicio=" + fecha_inicio + "&fin=" + fecha_fin
		data_analysis.Analisis(url_corabastos)
		##Clean data
		data_clean.Clean('')

def main():
	Procesamiento()

if __name__ == '__main__':
	main()

