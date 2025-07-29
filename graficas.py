import pandas as pd
import unicodedata

def quitar_tildes(texto):
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8")

def cargar_datos_supervisores(csv_path="data/nueva_base_con_coordenadas.csv"):
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.upper()
    df = df.rename(columns={
        "LIDER (PERSONA QUE LE INVITÓ A DILIGENCIAR ESTE FORMULARIO)": "SUPERVISOR"
    })
    df["SUPERVISOR"] = df["SUPERVISOR"].fillna("DESCONOCIDO").apply(quitar_tildes)
   
    df.columns = df.columns.str.strip().str.upper()
    conteo = df["SUPERVISOR"].dropna().value_counts().sort_values(ascending=False)
    porcentajes = (conteo / conteo.sum() * 100).round(1)
    return conteo.index.tolist(), porcentajes.tolist()

def cargar_tabla_excel(ruta="data/nueva_base_con_coordenadas.csv"):
    df = pd.read_csv(ruta, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.upper()
    columnas_deseadas = [
        "NOMBRE", "1ER APELLIDO", "2DO APELLIDO", "GENERO", "EDAD",
        "ESTRATO", "NIVEL EDUCATIVO", "VOTA POR CONGRESO"
    ]
    df = df[columnas_deseadas]
    return df.to_dict(orient="records"), df.columns.tolist()

def cargar_tabla_excel(ruta="data/Tabla.xlsx"):
    df = pd.read_excel(ruta)
    return df.to_dict(orient="records"), df.columns.tolist()
print("Lo logramooos")   