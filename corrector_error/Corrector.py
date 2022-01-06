def corrector_palabra(cadena):
    '''corrector_palabra(cadena): Corrigue las palabras con el caracter "�".

        Parámetros:
            cadena (string): Cadena carecteres a verificar.

        Retorno:
            Diccionario con la llave "cadena" que contienen la cadena correguida sin el caracter "�" y la llave "error" con None.
            En caso de contener aún palabras con "�", retorna la llave "error" con el mensaje de error y la cadena con las palabras que no se cambiaron.
    '''
    import pandas as pd
    import re
    
    dict_palabras = {
        'ba�o': 'baño',
        'cami�n': 'camión',
        'el�ctrico': 'eléctrico',
        'rob�tico': 'robótico',
        'eletroqu�mico': 'eletroquímico',
        'travesa�os': 'travesaños',
        'ni�o': 'niño',
        'caf�': 'café',
        'preparaci�n': 'preparación'
    }

    # Verifica si la cadena no None
    if not pd.isna(cadena):
        # Cambia los valores mediante el diccionario
        for llave in dict_palabras:
            # Palabra del diccionario en LowerCase
            cadena = cadena.replace(llave, dict_palabras[llave])
            # Palabra del diccionario capitalizada
            cadena = cadena.replace(llave.capitalize(), dict_palabras[llave].capitalize())
        # Busca todas las cadenas con �
        coincidencias = re.findall('\S*�\S*', cadena)
        # Verifica si no hay ninguna coincidencia
        if len(coincidencias) == 0:
            return {
                'error': None,
                'cadena': cadena
            }
        else:
            return {
                'error': f"Palabras con error: [{ ','.join(coincidencias) }]",
                'cadena': cadena
            }
    else:
        return {
            'error': None,
            'cadena': cadena
            }


def valida_sintaxis(dataframe, columnas):
    '''valida_sintaxis(dataframe, columnas): Verifica la sintaxis del "dataframe" en las "columnas" sea valida.

        Parámetros:
            dataframe (DataFrame): Conjunto de datos que contiene "columnas".
            columnas (list <string>): Nombre de las columnas a verificar.

        Retorna:
            Diccionario con las llave "dataframe" con el dataframe correguido y la llave "ok" con el valor boleano True en caso de ser válido.
            En caso contrario, la llave "ok" con el valor boleano False.
    '''
    valido = True
    df = dataframe.copy()

    # Recorre las columnas
    for col in columnas:
        # Castea el tipo de dato
        df[col] = df[col].astype('string')
        # Recorre la columna "col"
        for index, valor in df[col].items():
            # Cambia las coincidencias con �
            resp = corrector_palabra(valor)
            if resp['error']:
                print(resp['error'])
                valido = False
            df.loc[index, col] = resp['cadena']
    return {
        'ok': valido,
        'dataframe': df  
    }