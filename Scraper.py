import requests
from bs4 import BeautifulSoup

def obtener_nombre_subasta(url):
    '''obtener_nombre_subasta(url): Obtiene el nombre de la subasta por medio de Web Scraping.

    Parámetros:
        url (string): Url de página de inicio de la subasta con los lotes.

    Retorno:
        Título de la subasta o en caso de error "None".
    '''

    # Petición a la subasta con los lotes
    hg = requests.get(url)
    if hg.status_code != 200:
        return None
    
    # Obteniendo apartado con todos los lotes
    s = BeautifulSoup(hg.text, 'lxml')
    seccion = s.find('section', attrs={'class': 'fondo-gris'})
    lote = seccion.find('div', attrs={'class': 'col-md-4 col-sm-12 col-xl-3 mb-3'})
    detalles = requests.get(lote.a.get('href'))
    if detalles.status_code != 200:
        return None
    
    # Página con los detalles del lote
    s_detalles = BeautifulSoup(detalles.text, 'lxml')
    sec_detalles = s_detalles.find('div', attrs={'class': 'bg-white'})
    
    # Accediendo a la sección de detalles del lote y obteniendo el nombre de la subasta
    desc = sec_detalles.find_all('div', attrs={'class': 'col-md-6 col-lg-6'})[1]
    if desc:
        return desc.find_all('div')[0].find('p').text
    else:
        return None



def obtener_datos_subasta(url):
    '''obtener_datos_subasta(url): Obtiene el listado de lotes, cada uno con:
    - num_lote: Número de lote.
    - title: Título del lote no mayor a 500 caracteres.
    - title_complement: Cadena restante de "title" en caso de ser mayor a 500, en caso contrario contiene "None".
    - location: Ubicación del lote.
    - image_link: Url de la imagen del lote que se muestra en la página principal de la subasta.
    - price: Precio del lote.
    - prefijo: Tipo de moneda.
    - link: Url de la página con los detalles del lote.
    - description: Descripción del lote no mayor a 5000 caracteres.
    - description_complement: Cadena restante de "description" en caso de ser mayor a 5000, en caso contrario contiene "None".
    - additional_image_link: Url's complementarias del lote.


    Parámetros:
        url (string): Url de página de inicio de la subasta con los lotes.

    Retorno:
        Arreglo de diccionarios con la información de cada lote dentro de la subasta. En caso de error retorna un arreglo vacío.
    '''

    # Petición a la subasta con los lotes
    hg = requests.get(url)
    if hg.status_code != 200:
        return None
    
    # Obteniendo apartado con todos los lotes
    s = BeautifulSoup(hg.text, 'lxml')
    seccion = s.find('section', attrs={'class': 'fondo-gris'})
    lotes = seccion.find_all('div', attrs={'class': 'col-md-4 col-sm-12 col-xl-3 mb-3'})
    
    # Obtener información de los lotes
    datos = []
    for lote in lotes:
        datos.append(obtener_info_lote(lote))
    
    return datos



def obtener_info_lote(lote):
    '''obtener_info_lote(lote): Obtiene la información del lote mostrado en la página principal:
    - num_lote: Número de lote.
    - title: Título del lote no mayor a 500 caracteres.
    - title_complement: Cadena restante de "title" en caso de ser mayor a 500, en caso contrario contiene "None".
    - location: Ubicación del lote.
    - image_original: Url de la imagen del lote que se muestra en la página principal de la subasta.
    - image_link: Url de la imagen del lote que se muestra en la página principal de la subasta (puede cambiar por una de Cloudinary).

    Parámetros:
        lote (BeautifulSoup): Tarjeta o sección mostrada en la página principal.

    Retorno:
        Diccionario con la información de cada lote dentro de la subasta. Los valores del diccionario pueden tener "None" si no se encuentran las etiquetas analizadas con Scraping.
    '''

    info_lote = {}
    
    # Número de lote
    num_lote = lote.find('span', attrs={'class': 'icon'})
    if num_lote:
        info_lote['num_lote'] = num_lote.text.split(' ')[-1]
    else:
        info_lote['num_lote'] = None
    
    # Titulo y complemento del lote
    nombre = lote.find('p', attrs={'class': 'p-2 bold fs18 mt-2'})
    if nombre:
        resp_formato = formato_subcadena(500, 'Lote ' + info_lote['num_lote'] + ' - ' + nombre.text)
        info_lote['title'] = resp_formato['complete']
        info_lote['title_complement'] = resp_formato['complement']
    else:
        info_lote['title'] = None
        
    # Ubicación del lote
    ubicacion = lote.find('p', attrs={'class': 'pt-0 pl-2 pr-2 m-0'})
    if ubicacion:
        info_lote['location'] = ' '.join(ubicacion.text.split(' ')[1:]).title()
    else:
        info_lote['location'] = None
    
    # Imagen en la página principal de la subasta
    imagen = lote.find('img')
    if imagen:
        info_lote['image_original'] = imagen.get('src')# Valor que no se modificara mas adelante
        info_lote['image_link'] = imagen.get('src')
    else:
        info_lote['image_original'] = None
        info_lote['image_link'] = None
    
    # Url de la página con detalles del lote
    info_lote.update(detalles_lote(lote.a.get('href')))
    
    return info_lote



def detalles_lote(url_lote):
    '''detalles_lote(url_lote): Obtiene los detalles del lote mostrado en la página de "Ver mas detalles del lote":
    - price: Precio del lote.
    - prefijo: Tipo de moneda.
    - link: Url de la página con los detalles del lote.
    - id_detalles: Id final de la url de la página con los detalles del lote.
    - description: Descripción del lote no mayor a 5000 caracteres.
    - description_complement: Cadena restante de "description" en caso de ser mayor a 5000, en caso contrario contiene "None".
    - additional_image_link: Url's complementarias del lote.

    Parámetros:
        url_lote (string): Url de página de detalles del lote.

    Retorno:
        Diccionario con los detalles del lote. Los valores del diccionario pueden tener "None" si no se encuentran las etiquetas analizadas con Scraping.
    '''

    dict_detalles = {}
    
    # Petición a la página de detalles del lote
    detalles = requests.get(url_lote)
    if detalles.status_code != 200:
        return None
    
    # Obteniendo sección con la información del lote
    s_detalles = BeautifulSoup(detalles.text, 'lxml')
    sec_detalles = s_detalles.find('div', attrs={'class': 'bg-white'})
    
    # Precio y prefijo del lote
    det = sec_detalles.find_all('div', attrs={'class': 'col-md-6 col-lg-6'})[-1]
    costo = det.find_all('div')[1].find_all('ul')[-1].find('li').text.split(':')[-1].strip().split(' ')
    aux_precio = '{:,.2f}'.format(float(costo[0].replace(",", "").replace("$", "")))
    if aux_precio == '0.00':
        precio = '1.00'
    else:
        precio = aux_precio
    prefijo = costo[-1]
    if prefijo == "DLLS":
        prefijo = "USD"

    dict_detalles['price'] = precio
    if len(costo) == 2:
        dict_detalles['prefijo'] = prefijo
    
    # Url del producto
    dict_detalles['id_detalles'] = url_lote.split('/')[-1]
    dict_detalles['link'] = url_lote
    
    # Descripción y complemento del lote
    detalle = sec_detalles.find('p')
    if detalle:
        resp_formato = formato_subcadena(5000, formato_texto(detalle.text))
        dict_detalles['description'] = resp_formato['complete']
        dict_detalles['description_complement'] = resp_formato['complement']
    else:
        dict_detalles['description'] = None
    
    # Imagenes del lote
    imagenes = []
    for img in sec_detalles.find_all('img', attrs={'class': 'img-responsive'}):
        img_src = img.get('src')
        if len(img_src) > 0:
            imagenes.append(img_src)
    
    if len(imagenes) == 0:
        dict_detalles['additional_image_link'] = None
    elif len(imagenes) == 1:
        dict_detalles['additional_image_link'] = imagenes[0]
    else:
        dict_detalles['additional_image_link'] = ','.join(list(set(imagenes)))
    
    return dict_detalles



def formato_subcadena(limite, cadena):
    '''formato_subcadena(limite, cadena): Corta la "cadena" conforme al limíte establecido y lo acompleta con "...", en caso contrario que no supere el limíte devuelve la misma cadena.

    Parámetros:
        limite (int): Tamaño máximo de la cadena.
        cadena (string): Cadena a verificar.

    Retorno:
        Si la cadena supera el limite retorna un diccionario con la cadena cortada conforme al limíte establecido y el complemento. 
        En caso contrario retorna la cadena y el complemento con "None".
    '''

    form_dict = {}
    
    # Verifica el tamaño maximo de la cadena
    if len(cadena) <= limite:
        form_dict['complete'] = cadena
        form_dict['complement'] = None
        return form_dict
    else:
        form_dict['complete'] = cadena[:limite-3] + '...'
        form_dict['complement'] = cadena[limite-3:]
        return form_dict


def formato_texto(cadena):
    '''formato_texto(cadena): Le da formato capitalizado al texto por oraciones. Después de cada punto final o aparte la letra esta en mayusculas.
    Respeta los formatos de los siguientes casos "..." o "12.5 mm"

    Parámetros:
        cadena (string): Cadena a procesar.

    Retorno:
        Cadena con el formato capitalizado en cada oración (despues de cada punto).
    '''

    import re

    # Corte de cada cadena
    arr = [cad.strip().capitalize() for cad in re.split('[.]\s*', cadena)]
    desc = ''
    bandera = False

    # Formato capitalizado a cada oración
    for i in range(len(arr)):
        # Aplicando caso "..."
        if len(arr[i]) == 0:
            desc = desc + '.'
            continue

        # Aplicando caso "16.3" 
        if bandera:
            desc = desc + '.' + arr[i]
            bandera = False
        else:
            # Aplicando caso de "inicio de la oración"
            if i == 0:
                desc = desc + arr[i]
            else: # Aplicando caso "fin de una oración"
                desc = desc + '. ' + arr[i]
        # Caso "16.3"
        if (i+1) < len(arr): # Verifica que no supera el limíte del arreglo
            #Verifica que termina con numero y que la siguiente cadena empieze con numero
            if re.search('\d$', arr[i]) and re.search('^\d', arr[i+1]):
                bandera = True
    return desc


def verifica_columnas_df(columnas, dataframe):
    """verifica_columnas_df(columnas, dataframe): Comprueba en el "dataframe" que se encuentren "columnas". 
        
        Parámetros:
            columnas (list <string>): Lista con el nombre de las columnas.
            dataframe (DataFrame): Conjunto de datos.

        Retorno:
            Valor True en caso de que se encuentran todas las "columnas", y en caso de faltar al menos una False.  
    """
    valida = True
    # Recorre las "columnas"
    for columna in columnas:
        # Verifica si la columna no esta dentro de las columnas del "dataframe"
        if not columna in dataframe.columns:
            print(f'La columnas {columna} no se encuentra.')
            valida = False
            break
    return valida


def subir_imagenes_cloudinary(dataframe, nombre_carpeta_principal, cred_cloudinary):
    """subir_imagenes_cloudinary(dataframe): Sube las imagenes de "additional_image_link" (dentro del "dataframe") a Cloudinary. Y las descarga en formato PNG separadas por "num_lote" dentro de la carpeta "nombre_carpeta_principal".

        Parámetros:
            dataframe (DataFrame): Conjunto de datos con las columnas "num_lote", "image_link" y "additional_image_link".
            nombre_carpeta_principal (string): Nombre de la carpeta en donde se descargan las imagenes de los lotes.
            cred_cloudinary (dict): Diccionario con credenciales de cloudinary, contiene:
                - cloud_name (string) 
                - api_key (string)
                - api_secret (string)
        Retorno:
            Dataframe con las url de cloudinary en las columnas "additional_image_link" e "image_link". En caso de no poder subir la imagen a Cloudinary se elimina la url. Al igual, alamacena las imagenes en EXCEL_IMGS/IMGS_"nombre_carpeta_principal".xlsx
    """

    # Verifica las columnas necesarias para ejecutar la función
    if not verifica_columnas_df(["link", "id_detalles", "image_link", "additional_image_link"], dataframe):
        print('No se encuentran las columnas requeridas')
        return None

    dataframe_copia = dataframe.copy()

    import pandas as pd
    from PIL import Image
    import requests
    import io
    import os

    import cloudinary
    import cloudinary.uploader
    
    # Datos del usuario de Cloudinary
    #cloudinary.config(cloud_name = "dl1zxyeaa", api_key = "471925251237136", api_secret = "kyRNVkCNcn_FmAbgaaqzkb7o2Dw")
    # Solo utilizada para MULTIMARCAS-NOVIEMBRE
    # cloudinary.config(cloud_name = "dcyckahnx", api_key = "239751129392853", api_secret = "pjoTd5TyscB6hSZ0bEU0c1kR7LA")
    cloudinary.config(cloud_name = cred_cloudinary['cloud_name'], api_key = cred_cloudinary['api_key'], api_secret = cred_cloudinary['api_secret'])

    lista_dict_url = []
    # Recorrido del dataframe
    for i in range(len(dataframe_copia)):
        # Crea la carpeta del lote
        os.makedirs(f"{nombre_carpeta_principal}/{dataframe_copia.loc[i, 'id_detalles']}", exist_ok=True)
        
        # Contador utilizado para el id del nombre del archivo
        num = 1
        # Url's de Cloudinary
        urls_img_adicionales = []
        
        # Url's del lote
        for url_imagen in dataframe_copia.loc[i, 'additional_image_link'].split(','):
                
            # Caso de error al solicitar la imagen a la url de la subasta
            try:
                # Solicita la imagen
                resp = requests.get(url_imagen)
            except:
                print(f"Error al solicitar HILCO GLOBAL: {url_imagen}")
                continue

            if resp.status_code != 200:
                continue

            # Casteo de la respuesta de la imagen
            img_bytes = io.BytesIO(resp.content)
            
            # Tamaño en memoria de la imagen
            with io.BytesIO(resp.content) as img:
                # Obteniendo el tamaño de la imagen
                aux = img.read()
                tam = len(aux)

                # Verifica que el tamaño sea menor a 8MG
                if (tam / 1e6) > 8:
                    continue
            
            # Resolución de la imagen
            image = Image.open(img_bytes)
            # Verifica si el tamaño es menor 600x600 px
            try:
                if not((image.size[0] > 600) and (image.size[1] > 600)):
                    # Tamaño o medidas de la imagen
                    size = image.size
                    # Se Obtiene la medida mas pequeña
                    if size[0] < size[1]:
                        tam_image = size[0]
                    else: 
                        tam_image = size[1]
                    
                    # Se cambia las medidas de la imagen sin perder la proporcionalidad
                    tam_final = 610/tam_image
                    # Se establecen las nuevas medidas en enteros
                    image = image.resize((int(size[0]*tam_final),int(size[1]*tam_final)))

                # Se guarda la imagen en la ruta especificada
                image.save(f"{nombre_carpeta_principal}/{dataframe_copia.loc[i, 'id_detalles']}/{num}.png")

                # Verifica que no supere los 10 MG la imagen
                size_bytes = os.path.getsize(f"{nombre_carpeta_principal}/{dataframe_copia.loc[i, 'id_detalles']}/{num}.png")
                if (size_bytes / 1e6) > 10:
                    print(f"Tamaño máximo superado: {nombre_carpeta_principal}/{dataframe_copia.loc[i, 'id_detalles']}/{num}.png")
                else:
                    # Caso de error con Cloudinary
                    try:
                        # Carga la imagen a Cloudinary
                        resp_dict = cloudinary.uploader.upload(open(f"{nombre_carpeta_principal}/{dataframe_copia.loc[i, 'id_detalles']}/{num}.png" ,'rb'),
                                                public_id = f"{num}", folder=f"{nombre_carpeta_principal}/{dataframe_copia.loc[i, 'id_detalles']}")
                        # Verifica si es la imagen mostrada en la página principal de la subasta
                        if dataframe_copia.loc[i, 'image_link'] == url_imagen:
                            # Cambia el link al de Cloudinary
                            dataframe_copia.loc[i, 'image_link'] = resp_dict['secure_url']
                        # Cambia el link al de Cloudinary
                        urls_img_adicionales.append(resp_dict['secure_url'])
                        # Almacena ambas url's
                        lista_dict_url.append({'url_original': url_imagen, 'url_cloudinary': resp_dict['secure_url']})
                        
                    except:
                        print(f"Error cloudinary: {nombre_carpeta_principal}/{dataframe_copia.loc[i, 'id_detalles']}/{num}.png")
            except:
                print(f'No se pudo guardar la imagen: {url_imagen}')
            num = num + 1
        # Cambio a url's de Cloudinary
        dataframe_copia.loc[i, 'additional_image_link'] = ','.join(urls_img_adicionales)

    # Dataframe con las urls priginiales y su respectiva url en Cloudinary
    df_urls = pd.DataFrame(lista_dict_url)

    # Crea la carpeta del lote
    os.makedirs("EXCEL_IMGS", exist_ok=True)

    # Verifica si el archivo existe
    if os.path.exists(f'EXCEL_IMGS/IMGS_{nombre_carpeta_principal}.xlsx'):
        # Obtiene el df con las iameges antes guardadas
        df_local = pd.read_excel(f'EXCEL_IMGS/IMGS_{nombre_carpeta_principal}.xlsx')
        df_final = pd.concat([df_local, df_urls], axis = 0, ignore_index=True)
    else:
        df_final = df_urls
    # Excel con las imagenes
    with pd.ExcelWriter(f'EXCEL_IMGS/IMGS_{nombre_carpeta_principal}.xlsx', engine='xlsxwriter', engine_kwargs={'options':{'strings_to_urls': False}}) as writer:
        df_final.to_excel(writer, index=False, encoding='utf-8')
    return dataframe_copia 


def obtener_analisis_subasta(df_original, df_actualizado, col_base, columnas, nombre_carpeta_principal):
    """obtener_analisis_subasta(df_original, df_actualizado, col_base, columnas): Actualiza los valores de las "columnas" del "df_original" con los datos del "df_actualizado", toma como identificador de los lotes la columna "col_base".

        Parámetros:
            df_original (DataFrame): Ultima versión del conjunto de lotes obtenidos (últimos lotes descargados).
            df_actualizado (DataFrame): Conjunto de lotes actuales en la página web.
            col_base (string): Nombre la columna identificadora de cada lote.
            columnas (list <string>): Nombre de las columnas a actualizar. 
    
        Retorno:
            Diccionario con los siguientes dataframe:
                'nuevos': Nuevos lotes scrapeados de la subasta web ("df_actualizado").
                'eliminados': Lotes no encontrados de "df_original" en la web ("df_actualizado").
                'coincidencias': Lotes de "df_original" actualizados.
            También los dataframe del diccionario puede contener None en caso de no contener ningun valor.

            En caso de error retorna un None.
    """
    import os
    import pandas as pd

    print('Numero de lotes actuales:', len(df_original))
    print('Numero de lotes en la WEB:', len(df_actualizado))

    # Verifica las columnas necesarias para ejecutar la función
    if not verifica_columnas_df(columnas, df_original) or not (col_base in df_original.columns) or not ('image_original' in df_original.columns):
        print('No se encuentran las columnas df_original.')
        return None

    # Verifica las columnas necesarias para ejecutar la función
    if not verifica_columnas_df(columnas, df_actualizado) or not (col_base in df_actualizado.columns) or not ('image_original' in df_actualizado.columns):
        print('No se encuentran las columnas df_actualizado.')
        return None

    df = df_original.copy()

    # Cambio para manejar el mismo tipo de dato en df y df_actualizado
    df[col_base] = df[col_base].astype('string')
    df_actualizado[col_base] = df_actualizado[col_base].astype('string')
    df['additional_image_link'] = df['additional_image_link'].astype('string')
    df['image_original'] = df['image_original'].astype('string')
    df_actualizado['image_original'] = df_actualizado['image_original'].astype('string')
    for col in columnas:
        df[col] = df[col].astype('string')
        df_actualizado[col] = df_actualizado[col].astype('string')
    
    # Verifica si el archivo con las imagenes cargadas (anteriormente) existe
    if os.path.exists(f'EXCEL_IMGS/IMGS_{nombre_carpeta_principal}.xlsx'):
        # Obtiene el df con las iameges antes guardadas
        df_local = pd.read_excel(f'EXCEL_IMGS/IMGS_{nombre_carpeta_principal}.xlsx')
        df_local['url_original'] = df_local['url_original'].astype('string')
        df_local['url_cloudinary'] = df_local['url_cloudinary'].astype('string')
    else:
        df_local = pd.read_excel([])

    # Variable para afirmar si se encontro el lote
    coincide = False
    # Variable con los index (del DataFrame df) de los lotes eliminados en la Web.
    index_eliminados = []
    act_valida = True

    # Recorrido datos originales
    for i in range(len(df)):
        # Recorrido datos actualizados
        for j in range(len(df_actualizado)):
            # Coincidencia de las columnas "col_base"
            if df.loc[i, col_base] == df_actualizado.loc[j, col_base]:
                coincide = True
                # Verifica si el lote ha cambiado
                if df.loc[i, 'num_lote'] != df_actualizado.loc[j, 'num_lote']:
                    df.loc[i, 'id'] = df.loc[i, 'id'].replace(df.loc[i, 'id'], df_actualizado.loc[j, 'num_lote'])
                    print(f"num_lote: Lote ant.: {df.loc[i, 'num_lote']} - Lote nuevo: {df_actualizado.loc[j, 'num_lote']}")

                # Verifica si la image_original ha cambiado   
                if df.loc[i, 'image_original'] != df_actualizado.loc[j, 'image_original']:
                    print(f"Cambio la imagen principal: {df.loc[i, col_base]}")
                    for x in range(len(df_local)):
                        act_valida = False
                        # Busca la url en las imagenes cargadas anteriormente en Cloudinary
                        if df_local.loc[x, 'url_original'] == df_actualizado.loc[j, 'image_original']:
                            # Busca la imagen en las cargadas anteriormente
                            if df.loc[i, 'additional_image_link'].find(df_local.loc[x, 'url_cloudinary']) != -1:
                                # Cambia la imagen por la actualizada
                                df.loc[i, 'image_original'] = df_actualizado.loc[j, 'image_original']
                                # Cambia la imagen por una de Cloudinary
                                df.loc[i, 'image_link'] = df_local.loc[x, 'url_cloudinary']
                                act_valida = True
                                break
                            else:
                                print(f"La imagen principal no se encontro: {df.loc[i, 'id_detalles']} - {df.loc[i, col_base]}")
                                act_valida = True
                                coincide = False
                                break
                    if not act_valida:
                        print(f"image_original : Lote: {df.loc[i, 'num_lote']} - Lote en HG: {df_actualizado.loc[j, 'num_lote']}")
                # Actualizando datos
                for columna in columnas:
                    # Actualizando el valor dentro del "df"
                    df.loc[i, columna] = df_actualizado.loc[j, columna]
                break
        # Eliminando de "df_actualizado" el lote que coincide entre "df" y "df_actualizado"
        if coincide == True:
            df_actualizado = df_actualizado[df_actualizado[col_base] != df.loc[i, col_base]]
            df_actualizado = df_actualizado.reset_index(drop = True)
            coincide = False
        # Agregando index de los que no se encontraron en "df_actualizado"
        else:
            index_eliminados.append(i)
    
    if act_valida:
        return {
            'nuevos': df_actualizado, # Nuevos lotes en la web
            'eliminados': df.iloc[index_eliminados].reset_index(drop=True).copy(), # Lotes no encontrados en la web
            'coincidencias': df.drop(index_eliminados, axis=0).reset_index(drop=True) # Lotes encontrados en la web
        }
    else:
        return None


def eliminar_carpetas_dataframe(dataframe, nombre_final, cred_cloudinary):
    import cloudinary
    import cloudinary.api
    # Datos del usuario de Cloudinary
    #cloudinary.config(cloud_name = "dl1zxyeaa", api_key = "471925251237136", api_secret = "kyRNVkCNcn_FmAbgaaqzkb7o2Dw")
    cloudinary.config(cloud_name = cred_cloudinary['cloud_name'], api_key = cred_cloudinary['api_key'], api_secret = cred_cloudinary['api_secret'])

    for i in range(len(dataframe)):
        try:
            cloudinary.api.delete_folder(f"{nombre_final}/{dataframe.loc[i, 'id_detalles']}")
        except:
            print(f"Error en carpeta cloudinary: {nombre_final}/{dataframe.loc[i, 'id_detalles']}")


def actualiza_dataframe_subasta(df_actual, url, col_base, columnas, nombre_final, prefijo_id, columnas_nuevas, cred_cloudinary):
    """dataframe_subasta(df_actual, url, col_base, columnas, nombre_final, prefijo_id, columnas_nuevas): Actualiza los valores de las "columnas" del "df_actual" con los datos de la "url" obtenidos mediante Scraping, toma como identificador de los lotes la columna "col_base".

        Parámetros:
            df_actual (DataFrame): Ultima versión del conjunto de lotes obtenidos (últimos lotes descargados).
            url (string): Dirección o url donde se obtuvo el conjunto "df_actual".
            col_base (string): Nombre la columna identificadora de cada lote.
            columnas (list <string>): Nombre de las columnas a actualizar.
                Columnas validas: [num_lote, title, title_complement, location, price, prefijo, description, description_complement]
            nombre_final (string): Cadena utilizada para el nombre de los archivos y la carpeta en donde se descargan las imagenes de los lotes.
            prefijo_id (string): Cadena utilizada para generar el id personalizado de los lotes dentro del conjunto obtenido de la "url".
            columnas_nuevas (dict): Diccionario en donde las llaves son el nombre de las columnas y cada una con su respectivo valor, son utilizados para los datos obtenidos de la "url"
            cred_cloudinary (dict): Diccionario con credenciales de cloudinary, contiene:
                - cloud_name (string) 
                - api_key (string)
                - api_secret (string)
                
        Retorno:
            Dataframe actualizado en las "columnas" y con los nuevos lotes de la "url", también elimina lotes que no se encuentren en la página web. En caso de error retorna "df_actual".
    """
    import pandas as pd
    from nlp_estados import Predictor
    from corrector_error import Corrector as cr
    import os

    # Obtiene los lotes de la subasta (url)
    try:
        datos = obtener_datos_subasta(url)
    except:
        datos = []
    # En caso de error retorna un arreglo vacio
    if len(datos) == 0:
        print('No se pudo acceder a la URL.')
        return df_actual
    df = pd.DataFrame(datos)

    sintaxis_columnas = ['title', 'title_complement', 'description', 'description_complement']
    # Verifica que el dataframe de la url no contenga error en las columnas
    temp = cr.valida_sintaxis(df, sintaxis_columnas)
    if temp['ok']:
        df = temp['dataframe']
    else: 
        print('ERROR: No se pudo actualizar el dataframe, la sintaxis no es válida.')
        return df_actual


    # Compración de los datos actual con estos
    # Dataframe's con datos: "nuevos", "eliminados" y "coincidencias"
    mapa_df = obtener_analisis_subasta(df_actual, df, col_base, columnas, nombre_final)
    if not mapa_df:
        print('ERROR: image_original no coinciden con la columna link.')
        return df_actual
    
    # Transforma las ubicaciones de los dataframes nuevos
    for key in mapa_df:
        if not mapa_df[key].empty:
            mapa_df[key]['location'] = Predictor.init_nlp(mapa_df[key]['location'])
        print(key, len(mapa_df[key]))

    # Sube las imagenes a Cloudinary y hace el res
    df_nuevos = subir_imagenes_cloudinary(mapa_df['nuevos'], nombre_final, cred_cloudinary).copy()
    df_nuevos.insert(0, 'id', df_nuevos['num_lote'].apply(lambda num: prefijo_id + str(num)))

    if not df_nuevos.empty:# Caso en el que si hay lotes nuevos
        # Realiza el nlp de estados en la columna location
        df_nuevos['location'] = Predictor.init_nlp(df_nuevos['location'])

        # Agrega las columnas al dataframe de los nuevos lotes
        for key in columnas_nuevas:
            df_nuevos[key] = columnas_nuevas[key]

        # Dataframe final con la oncatenación del dataframe actualizado con los nuevos lotes (Con el formato respectivo)
        df_final = pd.concat([mapa_df['coincidencias'], df_nuevos], axis = 0, ignore_index=True)
    else: # Caso en el que no hay lotes nuevos
        df_final = mapa_df['coincidencias'].copy()

    # Carpeta para los lotes eliminados y lotes nuevos
    os.makedirs(f"Resultados_{nombre_final}", exist_ok=True)

    # Elimina las carpetas de CLoudinary
    eliminar_carpetas_dataframe(mapa_df['eliminados'], nombre_final, cred_cloudinary)

    # Excel con los lotes actualizados y los nuevos lotes
    with pd.ExcelWriter(f'excel/{nombre_final}.xlsx', engine='xlsxwriter', engine_kwargs={'options':{'strings_to_urls': False}}) as writer:
        df_final.to_excel(writer, index=False, encoding='utf-8')
        print('Excel actualizado')

    # Excel con los nuevos lotes
    with pd.ExcelWriter(f'Resultados_{nombre_final}/Nuevos_{nombre_final}.xlsx', engine='xlsxwriter', engine_kwargs={'options':{'strings_to_urls': False}}) as writer:
        df_nuevos.to_excel(writer, index=False, encoding='utf-8')

    # Excel con los lotes eliminados
    with pd.ExcelWriter(f'Resultados_{nombre_final}/Eliminados_{nombre_final}.xlsx', engine='xlsxwriter', engine_kwargs={'options':{'strings_to_urls': False}}) as writer:
        mapa_df['eliminados'].to_excel(writer, index=False, encoding='utf-8')

    return df_final


def obtener_dataframe_subasta(dict_subasta, prefijo_id, columnas_nuevas, cred_cloudinary):
    '''obtener_dataframe_subasta(dict_subasta, columnas_nuevas)
        
        Parámetros:
            dict_subasta (dict): Lista de diccionarios con el siguiente formato:
                    - nombre_final (string): Cadena utilizada para el nombre de los archivos y la carpeta en donde se descargan las imagenes de los lotes.
                    - url: Dirección o url donde se obtuvo la subasta.
            prefijo_id (string): Cadena utilizada para generar el id personalizado de los lotes dentro del conjunto obtenido de la "url".
            columnas_nuevas (dict): Nombre de las columnas nuevas.  
                    - custom_label: Nombre del grupo de subasta.
            cred_cloudinary (dict): Diccionario con credenciales de cloudinary, contiene:
                - cloud_name (string) 
                - api_key (string)
                - api_secret (string)

        Retorno:
            Retorna el dataframe con la información obtenida mediante Web Scraping, en caso de error retorna None.
    '''
    import pandas as pd
    from corrector_error import Corrector as cr
    from nlp_estados import Predictor

    # Web Scraping de la url
    datos = obtener_datos_subasta(dict_subasta['url'])
    if len(datos) == 0:
        print('No se obtuvo ningún dato nuevo.')
        return None

    df = pd.DataFrame(datos)

    sintaxis_columnas = ['title', 'title_complement', 'description', 'description_complement']
    # Verifica que el dataframe de la url no contenga error en las columnas
    temp = cr.valida_sintaxis(df, sintaxis_columnas)
    if temp['ok']:
        df = temp['dataframe']
    else: 
        print('ERROR: La sintaxis del dataframe no es válida.')
        return None
        
    # Realiza el nlp de estados en la columna location
    df['location'] = Predictor.init_nlp(df['location'])

    # Agrega las columnas al dataframe de los nuevos lotes
    for key in columnas_nuevas:
        df[key] = columnas_nuevas[key]
        
    # Sube las imagenes a Cloudinary y hace el res
    df = subir_imagenes_cloudinary(df, dict_subasta['nombre_final'], cred_cloudinary).copy()

    # Inserta el id en la primera posición del dataframe
    df.insert(0, 'id', df['num_lote'].apply(lambda num: prefijo_id + str(num)))

    return df


def actualiza_lista_subastas(lista_subastas, cols_actualizar):
    '''actualiza_lista_subastas(lista_subastas): Actualiza las subastas en las columnas "cols_actualizar".
        
        Parámetros:
            lista_subastas (list <dict>): Lista de diccionarios con el siguiente formato:
                    - nombre_final (string): Cadena utilizada para el nombre de los archivos y la carpeta en donde se descargan las imagenes de los lotes.
                    - url: Dirección o url donde se obtuvo la subasta.
                    - custom_label_0: Nombre del grupo de subasta.
                    - prefijo_id (string): Cadena utilizada para generar el id personalizado de los lotes dentro del conjunto obtenido de la "url".
                    - cred_cloudinary (dict): Diccionario con credenciales de cloudinary, contiene:
                        * cloud_name (string) 
                        * api_key (string)
                        * api_secret (string)
            cols_actualizar (list <string>): Nombre de las columnas a actualizar.  
        
        Retorno:
            Carpetas con la estructura "Resultado_" + "nombre_final", donde cada carpeta tiene los resultados de la subasta.        
    '''
    import pandas as pd
    import os

    # Recorre la lista de subastas
    for subasta in lista_subastas:
        # Verifica si existe el archivo
        if os.path.exists(f"excel/{subasta['nombre_final']}.xlsx"):
            print(f"Obteniendo subasta {subasta['nombre_final']}")
            # Obtiene el excel
            df_actual = pd.read_excel(f"excel/{subasta['nombre_final']}.xlsx")
            # Web Scraping de la url
            nombre = obtener_nombre_subasta(subasta['url'])
            columnas_nuevas = {'subasta': nombre, 'availability': 'In stock', 'condition': 'Used', 
                            'brand':'Hilco Global México', 'custom_label_0': subasta['custom_label_0']}

            # Actualiza "df_actual" con la "subasta['url']"
            df_final = actualiza_dataframe_subasta(df_actual, subasta['url'], 'link', cols_actualizar,
                                                subasta['nombre_final'], subasta['prefijo_id'], columnas_nuevas, subasta['cred_cloudinary'])
            print(subasta['nombre_final'], len(df_final))
        else:
            print(f"Obteniendo subasta {subasta['nombre_final']}")
            dict_subasta = {
                'url': subasta['url'],
                'nombre_final': subasta['nombre_final']
            }

            nombre = obtener_nombre_subasta(dict_subasta['url'])
            columnas_nuevas = {'subasta': nombre, 'availability': 'In stock', 'condition': 'Used', 
                            'brand':'Hilco Global México', 'custom_label_0': subasta['custom_label_0']}
            df = obtener_dataframe_subasta(dict_subasta, subasta['prefijo_id'], columnas_nuevas, subasta['cred_cloudinary'])

            with pd.ExcelWriter(f'excel/{subasta["nombre_final"]}.xlsx', engine='xlsxwriter', engine_kwargs={'options':{'strings_to_urls': False}}) as writer:
                df.to_excel(writer, index=False, encoding='utf-8')