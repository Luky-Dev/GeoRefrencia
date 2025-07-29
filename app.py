from flask import Flask, render_template
import pandas as pd
import hashlib
from graficas import cargar_datos_supervisores, cargar_tabla_excel
import unicodedata
from flask import request, redirect
from geocodificar import procesar_csv


procesar_csv()

app = Flask(__name__)

def color_from_name(name):
    h = hashlib.md5(name.encode()).hexdigest()
    return f"#{h[:6]}"

def quitar_tildes(texto):
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8")

@app.route("/")
def mapa():
    df = pd.read_csv("data/nueva_base_con_coordenadas.csv", encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.upper()
    df = df.dropna(subset=["LAT", "LON"])

    # Renombrar columnas clave
    df = df.rename(columns={
        "LIDER (PERSONA QUE LE INVITÓ A DILIGENCIAR ESTE FORMULARIO)": "SUPERVISOR",
        "DIRECCIÓN": "DIRECCION",
        "GÉNERO": "GENERO",
        "CÉDULA DE CIUDADANÍA (SIN PUNTOS)": "CEDULA"
    })

    df["ETAPA"] = "Adulto"  # Dummy si no hay etapas

    # Quitar tildes a los nombres de supervisores
    df["SUPERVISOR"] = df["SUPERVISOR"].fillna("DESCONOCIDO").apply(quitar_tildes)


    # Generar colores únicos por supervisor
    supervisores = df["SUPERVISOR"].unique()
    colores = {sup: color_from_name(sup) for sup in supervisores}
    df["COLOR"] = df["SUPERVISOR"].map(colores).fillna("#888888")

    # Renombrar para compatibilidad JS
    df = df.rename(columns={"LAT": "lat", "LON": "lon", "COLOR": "color"})

    marcadores = df[[ 
        "NOMBRE", "CEDULA", "EDAD", "GENERO", "NIVEL EDUCATIVO", 
        "VOTA POR ALCALDÍA", "VOTA POR CONGRESO", "VOTA POR PRESIDENCIA",
        "ESTRATO", "lat", "lon", "SUPERVISOR", "color", "ETAPA"
    ]].rename(columns={
        "NOMBRE": "NOMBRE COMPLETO",
        "CÉDULA": "CEDULA"
    }).to_dict(orient="records")

    supervisor_labels, supervisor_values = cargar_datos_supervisores()
    tabla_data, tabla_columnas = cargar_tabla_excel()

    return render_template(
        "mapa.html",
        marcadores=marcadores,
        supervisor_labels=supervisor_labels,
        supervisor_values=supervisor_values,
        tabla_data=tabla_data,
        tabla_columnas=tabla_columnas
    )

@app.route("/editar", methods=["GET"])
def editar():
    df = pd.read_csv("data/nueva_base_con_coordenadas.csv", encoding="utf-8-sig")
    df = df.rename(columns={"GÉNERO": "GENERO"})
    df.columns = df.columns.str.strip().str.upper()
    columnas = df.columns.tolist()
    
    filas = [{col: "" for col in columnas}]  # Solo 1 fila vacía por defecto

    # Campos con opciones fijas
    opciones_fijas = {
        "GENERO": ["Masculino", "Femenino", "Otro"],
        "ESTRATO": ["1", "2", "3", "4", "5", "6"],
        "NIVEL EDUCATIVO": ["Primaria", "Secundaria", "Técnico", "Universitario", "Otro"],
        "VOTA POR ALCALDÍA": ["Sí", "No", "NS/NR"],
        "VOTA POR CONGRESO": ["Sí", "No", "NS/NR"],
        "VOTA POR PRESIDENCIA": ["Sí", "No", "NS/NR"],
        "ETAPA": ["Adulto", "Joven", "Niño"]
    }

    return render_template("editar.html", columnas=columnas, filas=filas, opciones_fijas=opciones_fijas)




@app.route("/guardar_edicion", methods=["POST"])
def guardar_edicion():
    df = pd.read_csv("data/nueva_base_con_coordenadas.csv", encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.upper()

    total_filas = int(request.form.get("total_filas", 0))

    nuevas_filas = []
    for i in range(total_filas):
        nueva_fila = {}
        tiene_datos = False

        for col in df.columns:
            key = f"{col}_{i}"
            valor = request.form.get(key, "").strip()

            if valor:
                tiene_datos = True
            nueva_fila[col] = valor

        if tiene_datos:
            nueva_fila["GEOINTENTADO"] = False
            nuevas_filas.append(nueva_fila)

    if nuevas_filas:
        df = pd.concat([df, pd.DataFrame(nuevas_filas)], ignore_index=True)

    # 🧹 Eliminar filas completamente vacías (solo espacios vacíos o NaN)
    df.replace("", pd.NA, inplace=True)
    df.dropna(how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)

    df.to_csv("data/nueva_base_con_coordenadas.csv", index=False, encoding="utf-8-sig")
    
    procesar_csv()

    return redirect("/")



@app.route("/ver_base")
def ver_base():
    df = pd.read_csv("data/nueva_base_con_coordenadas.csv", encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.upper()

    columnas = df.columns.tolist()
    filas = df.to_dict(orient="records")

    return render_template("ver_base.html", columnas=columnas, filas=filas)


if __name__ == "__main__":
    from os import environ
    app.run(host='0.0.0.0', port=int(environ.get('PORT', 5000)))
