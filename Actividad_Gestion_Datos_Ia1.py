import pandas as pd
import numpy as np
import logging
import os

# Configuración de Logging para trazabilidad
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cargar_datos(ruta_entrada):
    """Carga el dataset y retorna un DataFrame."""
    logging.info(f"Iniciando carga de datos desde: {ruta_entrada}")
    try:
        df = pd.read_csv(ruta_entrada)
        logging.info(f"Datos cargados exitosamente. Forma inicial: {df.shape}")
        return df
    except FileNotFoundError:
        logging.error("No se encontró el archivo. Verifica la ruta.")
        raise

def detectar_y_limpiar(df):
    """Fase 1 y 2: Detección y Limpieza de datos."""
    logging.info("--- INICIANDO DETECCIÓN Y LIMPIEZA ---")
    
    # 1. Detección y eliminación de duplicados
    duplicados_id = df.duplicated(subset=['id_mascota']).sum()
    duplicados_exactos = df.duplicated().sum()
    logging.info(f"Duplicados por id_mascota detectados: {duplicados_id}")
    logging.info(f"Duplicados exactos detectados: {duplicados_exactos}")
    
    df = df.drop_duplicates()
    logging.info(f"Duplicados exactos eliminados. Nueva forma: {df.shape}")

    # 2. Detección de nulos
    logging.info(f"Conteo de nulos por columna antes de limpieza:\n{df.isnull().sum()}")

    # 3. Estandarizar especie (ej: GATO, Cat -> gato)
    if 'especie' in df.columns:
        df['especie'] = df['especie'].astype(str).str.strip().str.lower()
        df['especie'] = df['especie'].replace({'cat': 'gato', 'dog': 'perro'})
        logging.info("Columna 'especie' estandarizada.")

    # 4. Imputar edad_años con la mediana por especie
    if 'edad_años' in df.columns and 'especie' in df.columns:
        mediana_por_especie = df.groupby('especie')['edad_años'].transform('median')
        df['edad_años'] = df['edad_años'].fillna(mediana_por_especie)
        logging.info("Valores nulos en 'edad_años' imputados con la mediana por especie.")

    # 5. Corregir fechas malformadas
    if 'fecha_consulta' in df.columns:
        df['fecha_consulta'] = pd.to_datetime(df['fecha_consulta'], errors='coerce')
        logging.info("Columna 'fecha_consulta' convertida a formato datetime.")

    # 6. Identificar outliers en peso_kg (Método IQR)
    if 'peso_kg' in df.columns:
        Q1 = df['peso_kg'].quantile(0.25)
        Q3 = df['peso_kg'].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df['peso_kg'] < (Q1 - 1.5 * IQR)) | (df['peso_kg'] > (Q3 + 1.5 * IQR))).sum()
        logging.info(f"Outliers detectados en 'peso_kg': {outliers}")
        # Opcional: df = df[~((df['peso_kg'] < (Q1 - 1.5 * IQR)) | (df['peso_kg'] > (Q3 + 1.5 * IQR)))]

    return df

def transformar_datos(df):
    """Fase 3: Transformación del dataset."""
    logging.info("--- INICIANDO TRANSFORMACIÓN ---")
    
    # 1. Crear columna 'rango_peso'
    if 'peso_kg' in df.columns:
        bins = [0, 5, 15, 25, np.inf]
        labels = ['bajo', 'normal', 'alto', 'obeso']
        df['rango_peso'] = pd.cut(df['peso_kg'], bins=bins, labels=labels)
        logging.info("Columna 'rango_peso' creada.")

    # 2. Extraer mes y año de fecha_consulta
    if 'fecha_consulta' in df.columns:
        df['mes_consulta'] = df['fecha_consulta'].dt.month
        df['año_consulta'] = df['fecha_consulta'].dt.year
        logging.info("Columnas de mes y año extraídas.")
        
        # 3. Calcular 'años_cliente' desde la primera visita
        primera_visita = df.groupby('id_mascota')['fecha_consulta'].transform('min')
        df['años_cliente'] = (pd.Timestamp.now() - primera_visita).dt.days / 365.25
        df['años_cliente'] = df['años_cliente'].fillna(0).round(1)
        logging.info("Columna 'años_cliente' calculada.")


    # 4. Codificar 'especie' (One-Hot Encoding)
    if 'especie' in df.columns:
        df = pd.get_dummies(df, columns=['especie'], prefix='esp', drop_first=False)
        # Convertir booleanos a enteros si es necesario: df = df.astype(int)
        logging.info("Columna 'especie' codificada con get_dummies.")

    return df

def exportar_datos(df, ruta_salida):
    """Fase 4: Exportar el dataset limpio."""
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    df.to_csv(ruta_salida, index=False)
    logging.info(f"Datos limpios guardados exitosamente en: {ruta_salida}")
    logging.info(f"Forma final del dataset: {df.shape}")

if __name__ == "__main__":
    # Definir rutas
    RUTA_RAW = 'data/raw/mascotas.csv'
    RUTA_PROCESSED = 'data/processed/mascotas_clean.csv'
    
    # Ejecutar pipeline
    dataset = cargar_datos(RUTA_RAW)
    dataset_limpio = detectar_y_limpiar(dataset)
    dataset_transformado = transformar_datos(dataset_limpio)
    exportar_datos(dataset_transformado, RUTA_PROCESSED)