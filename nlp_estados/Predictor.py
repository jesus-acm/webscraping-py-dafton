def init_nlp(datos_estados):
    '''init_nlp(datos_estados): Realiza un reconocimiento de estados en "datos_estados".

        Parámetros:
            datos_estados (DataFrame): Conjunto de datos con los posibles estados.

        Retorno:
            Dataframe con la predicción en cada dato de "datos_estados".
    '''
    import pandas as pd
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.svm import LinearSVC
    import os
    
    # Función para tokenizar cada dato
    def tokenize(sentence):
        return list(sentence.replace(" ", "").lower())

    # Conjunto de entrenamiento
    datos = pd.read_excel(f"{os.path.dirname(os.path.realpath(__file__))}/estado.xlsx")
    train_data = datos['Variable']
    train_labels = datos['Estado']
    
    # Separa las frases o textos en unidades sencillas de computar.
    real_vectorizer = CountVectorizer(tokenizer = tokenize, binary=True)

    # Transformacipon de los datos
    train_X = real_vectorizer.fit_transform(train_data)
    
    # Entrenamiento del modelo
    classifier = LinearSVC()
    classifier.fit(train_X, train_labels)
    
    # Predicción de los datos
    estados_X = real_vectorizer.transform(datos_estados)
    predicidos = classifier.predict(estados_X)

    # Cambio de valores predecidos en forma de DataFrame
    cont = 0
    copia_datos = datos_estados.copy()
    for index, valor in copia_datos.items():
        copia_datos.iloc[index] = predicidos[cont]
        cont = cont + 1
    
    return copia_datos