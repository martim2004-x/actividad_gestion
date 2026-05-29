# Pipeline de Datos - Clínica Veterinaria

Este proyecto automatiza la limpieza y transformación del dataset `mascotas.csv`, preparándolo para fases posteriores de análisis, asegurando su calidad y consistencia.

## Estructura del Proyecto
- `/data/raw/`: Contiene el dataset original con errores (`mascotas.csv`).
- `/data/processed/`: Contiene el dataset limpio y transformado (`mascotas_clean.csv`).
- `pipeline.py`: Script modularizado de Python.

## Decisiones de Limpieza
1. **Duplicados:** Se eliminaron los duplicados exactos en todo el DataFrame para evitar sesgos en el análisis.
2. **Imputación de Nulos:** La columna `edad_años` presentaba valores nulos. Se decidió imputar estos vacíos utilizando la mediana de la edad agrupada por la especie correspondiente, manteniendo la integridad estadística.
3. **Estandarización de Texto:** Se homogeneizó la columna `especie` (transformando textos como "Cat", "GATO" a "gato") para permitir una correcta categorización.
4. **Fechas:** Se forzó la conversión de `fecha_consulta` a `datetime`, manejando los errores mediante coerción (convirtiéndolos a NaT).

## Transformaciones Aplicadas
- **Ingeniería de Características (Features):** - Se creó la columna categórica `rango_peso` utilizando `pd.cut()`.
  - Se extrajeron `mes_consulta` y `año_consulta`.
  - Se calculó la antigüedad del paciente (`años_cliente`) calculando la diferencia entre la fecha actual y la fecha mínima registrada por cada `id_mascota`.
- **Codificación:** Se aplicó One-Hot Encoding (`pd.get_dummies()`) sobre la columna `especie` para preparar los datos para posibles modelos de Machine Learning futuros.

## Ejecución
Para ejecutar el pipeline:
\`\`\`bash
python pipeline.py
\`\`\`