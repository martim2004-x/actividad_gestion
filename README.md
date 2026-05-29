# Pipeline de Datos - Clinica Veterinaria

Este proyecto automatiza la limpieza, transformacion y validacion del dataset `mascotas.csv`, asegurando su calidad y consistencia estructural y semantica antes de segmentar los datos en registros validos e invalidos.

## Estructura del Proyecto
- `/data/raw/`: Contiene el dataset original con errores (`mascotas.csv`).
- `/data/processed/`: Contiene los datasets filtrados (`mascotas_validas.csv` y `mascotas_invalidas.csv`).
- `pipeline.py`: Script modularizado de Python.

## Decisiones de Limpieza y Estandarizacion
1. **Duplicados:** Se eliminan duplicados basados en `id_mascota` (si la columna existe) o duplicados exactos en todo el DataFrame para evitar redundancia.
2. **Estandarizacion de Texto:** Se homogeneiza la columna `especie` eliminando espacios en blanco y convirtiendo a minusculas. Ademas, se mapean terminos en ingles (`cat` a `gato`, `dog` a `perro`).
3. **Imputacion de Nulos:** Los valores nulos en `edad_anos` se imputan dinamicamente utilizando la mediana de la edad agrupada por la especie correspondiente.
4. **Fechas:** Se fuerza la conversion de `fecha_consulta` a formato `datetime`, manejando los errores mediante coercion (registros malformados pasan a `NaT`).

## Transformaciones Aplicadas
- **Rango de Peso:** Se crea la columna categorica `rango_peso` utilizando rangos predefinidos (`bajo`, `normal`, `alto`, `obeso`) mediante `pd.cut()`.
- **Componentes de Tiempo:** Se extraen de forma independiente el `mes_consulta` y el `ano_consulta`.
- **Antiguedad del Cliente:** Se calcula la columna `anos_cliente` midiendo el tiempo transcurrido en anos desde la primera consulta registrada de la mascota hasta la fecha actual.

## Validaciones de Calidad de Datos

El pipeline somete el dataset transformado a dos capas estrictas de control antes de permitir su exportacion:

### 1. Validaciones Estructurales Pandera
Se evalua registro por registro utilizando un esquema estricto de `Pandera` para asegurar que los datos cumplan con los tipos y limites fisicos requeridos:
- **id_mascota:** Debe ser estrictamente de tipo entero (`int`) y no permite valores nulos.
- **especie:** Debe pertenecer unicamente a la lista permitida: `perro`, `gato`, `conejo`, `pez` o `loro`.
- **peso_kg:** Debe ser un valor flotante (`float`) posicionado explicitamente en el rango numerico de `0.05` a `120.0`.
- **fecha_consulta:** Debe ser un objeto `Timestamp` valido y no puede ser nulo.

### 2. Validaciones Semanticas Reglas de Negocio
Se aplican mascaras logicas de `Pandas` para identificar inconsistencias de logica interna o coherencia biologica:
- **Coherencia de Obesidad:** Si una mascota esta clasificada en `rango_peso` como `obeso`, se valida que su `peso_kg` sea coherente con su especie (debe ser mayor a 30 kg para perros o mayor a 6 kg para gatos).
- **Consistencia de Identidad:** Si un mismo dueno (`id_dueno`) registra multiples consultas, se verifica que su `email_dueno` sea exactamente el mismo en todos los registros para evitar duplicidad de perfiles o errores de digitacion.
- **Coherencia Biologica (Edad):** Se descartan registros donde la columna `edad_anos` este fuera del limite biologico razonable para las mascotas domesticas de la clinica (el valor debe estar estrictamente entre 0 y 30 anos).

## Segmentacion y Exportacion
Al finalizar el proceso, el script divide el dataset original en dos archivos CSV dentro de `/data/processed/`:
- **mascotas_validas.csv:** Registros limpios que aprobaron exitosamente el 100% de las validaciones estructurales y semanticas. Se eliminan las columnas auxiliares de control.
- **mascotas_invalidas.csv:** Registros que fallaron en una o mas reglas de validacion, preservando las columnas de diagnostico (`valido_estructural` y `valido_semantico`) para su posterior auditoria.

Al terminar la ejecucion, el pipeline imprime en consola el porcentaje exacto de registros validos obtenidos sobre el total analizado.

## Ejecucion
Para ejecutar el pipeline completo de manera secuencial:
```bash
python pipeline.py
