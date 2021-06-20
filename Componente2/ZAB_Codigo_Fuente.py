#!/usr/bin/env python
# coding: utf-8

# In[1]:


#IMPORTAR LIBRERIAS NECESARIAS
from bs4 import BeautifulSoup
import requests
import pandas as pd
import urllib3
import re
import unicodedata
from datetime import datetime


# In[2]:


#DEFINIR NUMERO DE PAGINAS A SCRAPEAR
num_pagina = 5


# In[3]:


#FUNCION PARA EXTRAER DATOS DE CADA LICITACION
def funcion_data (paginas):
    #Definir URL
    URL = 'https://www.contrataciones.gov.py/buscador/general.html?filtro=+Instituto+de+Previsi%C3%B3n+Social+&page='+str(paginas)

    #Establecer el header
    headers = {
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36", 
                "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
                "DNT":"1",
                "Connection":"close", 
                "Upgrade-Insecure-Requests":"1"
                }

    #Deshabilitar advertencias de py
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

    #Obtener datos con metodo GET
    html = requests.get (URL, headers = headers, verify=False)

    #Extraer info con formato html (identificador del parser: html)
    soup = BeautifulSoup (html.content, 'html.parser')

    #Extraer información requerida
    contenido = soup.find_all('ul',  attrs={'class':'results'}) 

    otros_datos = [i.get_text() for i in contenido[0].find_all('div', {'class':'col-lg-8'})]
    otros_datos = [ item for item in otros_datos if item != '']
    otros_datos = [unicodedata.normalize("NFKD", item) for item in otros_datos]
  
    return (otros_datos)


# In[4]:


#FUNCION PARA EXTRAER EL MONTO DE CADA LICITACION - CON SU LINK CORRESPONDIENTE
def monto (href):
    #Definir URL
    url = 'https://www.contrataciones.gov.py'+ href
    
    #Establecer el header
    headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36", 
            "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
            "DNT":"1",
            "Connection":"close", 
            "Upgrade-Insecure-Requests":"1"
            }
    
    #Deshabilitar advertencias de py
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 
   
    #Obtener datos con metodo GET
    html = requests.get (url, headers = headers, verify=False)
    
    #Extraer info con formato html 
    soup = BeautifulSoup (html.content)
    
    #Extraer información requerida
    contenido = soup.find_all('div',  attrs={'class':'info-panel-body'})
    
    #Recorrer dentro del contenido y extraer solo el monto
    monto = [i.get_text() for i in contenido[0].find_all('div', class_='col-sm-8 col-md-5')]
    if monto == []:
        monto = 0
        monto = [i.get_text() for i in contenido[0].find_all('div', class_='col-sm-12')]
        monto = monto[8] #Posicion en la que se encuentra el monto (Etapa: Cancelada)
        if len(monto) == 18:
            monto = 0 
    else:        
        monto = [ item for item in monto if item != '']
        monto = [unicodedata.normalize("NFKD", item) for item in monto]
        monto = monto[6] #Posicion en la que se encuentra el monto (Etapa: Convcatoria Abierta)
    
    return monto


# In[5]:


#FUNCION QUE TRABAJARA POR CADA PAGINA
def funcion (paginas):    
    #Definir URL
    URL = 'https://www.contrataciones.gov.py/buscador/general.html?filtro=+Instituto+de+Previsi%C3%B3n+Social+&page='+str(paginas)

    #Establecer el header
    headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36", 
            "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
            "DNT":"1",
            "Connection":"close", 
            "Upgrade-Insecure-Requests":"1"
            }
    
    #Deshabilitar advertencias de py
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

    #Obtener datos con metodo GET
    html = requests.get (URL, headers = headers, verify=False)

    #Extraer info con formato html 
    soup = BeautifulSoup (html.content)

    #Traer datos
    contenido = soup.find_all('ul',  attrs={'class':'results'}) #tiene total

    #Declarar variables
    licitaciones = list()
    contador = 0
    
    for x in contenido:
            header = x.find_all('h3')
            for y in header:
                #Nombre de licitacion
                nombre = y.find('a').getText()
                href = y.find('a').get('href')
                
                #Caracteristicas especiales
                caracteristica = y.find('span').getText().split()
                
                #Datos generales de licitacion        
                data = funcion_data(paginas)
                
                #Monto de licitacion
                monto_lic = monto(href)

                #Declarar lista que hace referencia a licitaciones individuales
                licitacion = list()

                #Verificar campos vacios                
                if nombre is not None:
                    licitacion.append(nombre)                
                else:
                    licitacion.append("Desconocido")

                if caracteristica is not None:
                    caracteristica = " ".join(caracteristica)
                    licitacion.append(caracteristica)
                else:                
                    licitacion.append("Desconocido")

                if data is not None:
                    id_content = data[contador].split('\n')
                    id_new = [id for id in id_content if id != '']
                    licitacion.append(id_new[1])
                    contador += 1
                    
                    etapa_content = data[contador].split('\n')
                    etapa_new = [etapa for etapa in etapa_content if etapa != '']                    
                    licitacion.append(etapa_new[1])
                    contador += 1       
                    
                    convocante_content = data[contador].split('\n')
                    convocante_new = [convocante for convocante in convocante_content if convocante != '']                
                    licitacion.append(convocante_new[1])
                    contador += 1                    
                    
                    fecha_content = data[contador].split('\n')
                    fecha_new = [fecha for fecha in fecha_content if fecha != '']  
                    licitacion.append(fecha_new[1])
                    contador += 1
                    
                    categoria_content = data[contador].split('\n')
                    categoria_new = [categoria for categoria in categoria_content if categoria != '']
                    tipo_categoria = categoria_new[1].split('-')
                    licitacion.append(tipo_categoria[0])
                    licitacion.append(tipo_categoria[1])
                    contador += 1                    
                    
                    tipo_content = data[contador].split('\n')
                    tipo_new = [tipo for tipo in tipo_content if tipo != '']  
                    licitacion.append(tipo_new[1])
                    contador += 1
                else:
                    licitacion.append("Desconocido")

                if monto_lic is not None:
                    licitacion.append(monto_lic)
                else:
                    licitacion.append("Desconocido")                    
                            
                #Agregar minilistas a lista general (correspondiente a cada pagina)            
                licitaciones.append(licitacion)
            
    return licitaciones


# In[6]:


#ASIGNACION POR PAGINAS
#Definir lista correspondiente cada pagina
paginacion = []

#Ciclo que envia la pagina scrapeada
for num in range(num_pagina):
    paginacion.append(funcion(num+1))
    


# In[7]:


#PREPARACION PARA DATAFRAME
#Recorre las sublistas de la lista principal para obtener datos
flatten = lambda x: [item for sublist in x for item in sublist]

#Establecer dataframe
df = pd.DataFrame(flatten(paginacion),columns=['Nombre_Licitacion', 'Caracteristica(s)', 'ID_Licitacion', 'Etapa', 'Convocante', 
                                               'Fecha_Entrega_Oferta', 'Num_Categoria', 'Nombre_Categoria', 'Tipo_Procedimiento', 'Monto(Gs)'])


# In[8]:


#LIMPIAR Y TRANSFORMAR
#Transformar columnas ID_Licitacion y Num_Categoria | Numeros
df["ID_Licitacion"] = df["ID_Licitacion"].astype(int)
df["Num_Categoria"] = df["Num_Categoria"].astype(int)

#Transformar monto
df["Monto(Gs)"] = df["Monto(Gs)"].str.replace('.', '')
df["Monto(Gs)"] = df["Monto(Gs)"].str.replace('₲', '')
df["Monto(Gs)"] = pd.to_numeric(df["Monto(Gs)"], errors='coerce')

#Transformar fecha
df["Fecha_Entrega_Oferta"]= pd.to_datetime(df["Fecha_Entrega_Oferta"], infer_datetime_format=True)


# In[9]:


#Descargar datos scrapeados en formato .csv
df.to_csv('datos_licitaciones.csv', index=False, encoding='utf-8')

#Mostrar en pantalla
df.style.hide_index()

