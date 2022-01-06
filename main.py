import Scraper
import schedule
import time

# Columnas que se van a actualizar
cols_actualizar = ['title', 'title_complement', 'location','price', 'prefijo', 
                  'num_lote', 'description', 'description_complement']
# jesusdafton12@gmail.com
# dafton12345
# Cloudinary: Dafton12345$
# Lista de subastas a actualizar
subastas = []
dict_multimarcas = {
    'nombre_final': 'SUBASTA_MULTIMARCAS_ENERO',
    'url': 'https://www.subastashilcoacetec.mx/proyecto/49',
    'custom_label_0': 'MULTIMARCAS',
    'prefijo_id': 'MULTIMARCAS01-',
    'cred_cloudinary': {
        'cloud_name': 'dzytawyip',
        'api_key': '136656627597356',
        'api_secret': 'aOJ4lLdB0-jzv8GML7pfXRY2haU'
    }
}
dict_bafamsa = {
    'nombre_final': 'SUBASTA_ASCENDO_ENERO',
    'url': 'https://www.subastashilcoacetec.mx/proyecto/50',
    'custom_label_0': 'ASCENDO',
    'prefijo_id': 'ASCENDO01-',
    'cred_cloudinary': {
        'cloud_name': 'dzytawyip',
        'api_key': '136656627597356',
        'api_secret': 'aOJ4lLdB0-jzv8GML7pfXRY2haU'
    }
}
subastas.append(dict_multimarcas)
subastas.append(dict_bafamsa)
Scraper.actualiza_lista_subastas(subastas, cols_actualizar)

# FUNCIONALIDAD DE AGENDA DE ACTUALIZACIONES
# # Funcion que se encarga de ejecutar la lista de actualizaciones
# def script():
#     Scraper.actualiza_lista_subastas(subastas, cols_actualizar)

# # Asignación de tareas
# schedule.every().day.at("18:48").do(script)
# #schedule.every(10).minutes.do(script)
# #schedule.every().hour.do(script)
# #schedule.every().wednesday.at("13:15").do(script)

# print('Iniciando actualización...')
# # Ciclo para ejecutar las tareas
# while True:
#     schedule.run_pending()
#     time.sleep(1)