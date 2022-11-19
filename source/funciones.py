# Librerías
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Defino el user agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def extraer_tienda_xiaomi():
    """
    Extrae la información de los productos (nombre, precio, categoría)
    de la tienda de Xiaomi Ecuador.

    Retorna:
        df (DataFrame): Tabla con los datos de los productos.
    """
    # Defino la URL de la página a raspar
    pagina = "https://mistore.com.ec/todos-los-productos"
    # Realizo la petición a la web
    htmlContent = requests.get(pagina, headers=headers)
    # Doy formato a la información
    soup = BeautifulSoup(htmlContent.content, "html.parser")
    # Tomo solo la sección de id wrap
    wrap = soup.find(id="wrap")
    # Inicializo el diccionario de datos
    datos = {'producto': [], 'precio': [], 'categoria': []}
    # Itero sobre todos las secciones
    for cat in wrap.find_all("section", {"data-name": "Title"}):
        # Tomo el nombre de la categoría
        categoria = cat.text.strip()
        # Tomo la siguiente sección
        productos = cat.find_next_sibling()
        # Tomo una sección hijo
        productos = productos.find("section")
        # Itero sobre todos los productos
        for producto in productos.find_all("section"):
            # Tomo el texto
            texto = producto.text.strip()
            # Elimino los saltos de línea y caracteres especiales
            texto = texto.replace("\n", "")
            texto = texto.replace("\xa0", "")
            texto = texto.replace(".", "")
            # Separo el nombre del precio
            nombre, precio = texto.split("$")
            # Eliminar espacios en blanco al final
            nombre = nombre.rstrip()
            # Agrego los datos a la lista
            datos['producto'].append(nombre)
            datos['precio'].append(float(precio)/100)
            datos['categoria'].append(categoria)
    # Transformo los datos en un DataFrame temporal
    df_temp = pd.DataFrame(datos)
    df_temp = df_temp[df_temp['categoria'].str.contains("Teléfonos")]
    # Genero el dataframe final
    df = pd.DataFrame()
    # Defino marca
    df["marca"] = df_temp['categoria'].str.replace("Teléfonos ", "")
    df["marca"] = df['marca'].str.lower()
    # Defino el modelo
    # Elimino la primera palabra
    df["modelo"] = df_temp['producto'].str.split(" ", n=1, expand=True)[1]
    df["modelo"] = df['modelo'].str.replace(" ", "-")
    df["modelo"] = df["modelo"].str.lower()
    # Defino el precio
    df["precio"] = df_temp['precio']

    return df


def extraer_anuncio(enlace):
    """
    Extrae la información de un anuncio de venta de teléfono
    dado un enlace de mercadolibre.

    Parámetros:
        enlace (str): Enlace del producto.

    Retorna:
        caracteristicas (dict): Diccionario con los datos del producto.
    """
    # Diccionario de características
    caracteristicas = {
        "Memoria interna": [],
        "Memoria RAM": [],
        "Resolución de la cámara trasera principal": [],
        "Resolución de la cámara frontal principal": [],
        "Tamaño de la pantalla": [],
        "Resolución de la pantalla": [],
        "Capacidad de la batería": [],
        "Peso": [],
        "Altura x Ancho x Profundidad": [],
        "Velocidad del GPU": [],
        "Velocidad del procesador": [],
        "Cantidad de núcleos del procesador": []
    }
    # Pruebo la conexión
    k = 0
    while True:
        # Realizo la petición a la web
        htmlContent = requests.get(enlace, headers=headers)
        # Doy formato a la información
        soup = BeautifulSoup(htmlContent.content, "html.parser")
        # Compruebo si existe el elemento
        if soup.find("th", text="Memoria interna"):
            break
        else:
            time.sleep(3)
            if k == 3:
                # Lleno las características con vacío
                for key in caracteristicas.keys():
                    caracteristicas[key].append("")
                # Retorno las características
                return caracteristicas
            k += 1
    # Itero sobre las características
    for caracteristica in caracteristicas:
        try:
            # Busco la característica
            dato = soup.find("th", text=caracteristica)
            dato = dato.find_next_sibling().text.strip()
            # Agrego el dato a la característica
            caracteristicas[caracteristica].append(dato)
        except AttributeError:
            caracteristicas[caracteristica].append("")
    # Retorno las características
    return caracteristicas


def extraer_dusqueda(marca, modelo, max=100):
    """
    Busca un modelo de teléfono en mercadolibre y devuelve la información
    de los anuncios de teléfonos que resultan en la búsqueda (solo la primera
    página).

    Parámetros:
        marca (str): Marca del teléfono.
        modelo (str): Modelo del teléfono.
        max (int): Número máximo de anuncios a extraer.

    Retorna:
        df (DataFrame): Tabla con los datos de los productos.
    """
    # Defino la URL de la página a raspar
    url = f"https://celulares.mercadolibre.com.ec/celulares-smartphones"
    url = url+f"/{marca}/{modelo}/"
    # Realizo la petición a la web
    htmlContent = requests.get(url, headers=headers)
    # Doy formato a la información
    soup = BeautifulSoup(htmlContent.content, "html.parser")
    # Defino la clase de la sección de resultados
    clase = "ui-search-layout__item shops__layout-item"
    # Tomo solo la sección de resultados
    resultados = soup.find_all("li", {"class": clase})
    # Inicializo el diccionario de características y nombres
    caracteristicas = {
        "Memoria interna": [],
        "Memoria RAM": [],
        "Resolución de la cámara trasera principal": [],
        "Resolución de la cámara frontal principal": [],
        "Tamaño de la pantalla": [],
        "Resolución de la pantalla": [],
        "Capacidad de la batería": [],
        "Peso": [],
        "Altura x Ancho x Profundidad": [],
        "Velocidad del GPU": [],
        "Velocidad del procesador": [],
        "Cantidad de núcleos del procesador": []
    }
    nombre_precio = {
        "Nombre": [],
        "Precio": []
    }
    n = 0
    # Itero sobre los resultados
    for resultado in resultados:
        n += 1
        if n > max:
            break
        # Tomo el nombre
        clase = "ui-search-item__title shops__item-title"
        nombre = resultado.find("h2", {"class": clase}).text.strip()
        # Tomo el precio
        clase = "price-tag-fraction"
        precio = resultado.find("span", {"class": clase}).text.strip()
        # Guardo la información
        nombre_precio["Nombre"].append(nombre)
        nombre_precio["Precio"].append(precio)
        # Tomo el enlace del anuncio
        enlace = resultado.find("a", {"class": "ui-search-link"})['href']
        # Extraigo la información y la guardo en el diccionario
        info = extraer_anuncio(enlace)
        for caracteristica in caracteristicas:
            caracteristicas[caracteristica].append(info[caracteristica][0])
    # Uno los diccionarios
    nombre_precio.update(caracteristicas)
    # Transformo los datos en un DataFrame
    df = pd.DataFrame(nombre_precio)

    return df
