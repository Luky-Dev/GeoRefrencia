import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep
import os

def procesar_csv(input_path="data/nueva_base_con_coordenadas.csv",
                 output_path="data/nueva_base_con_coordenadas.csv",
                 registro_path="data/direcciones_geoprocesadas.txt"):

    df = pd.read_csv(input_path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.upper()

    if "DIRECCIÓN" not in df.columns:
        print("❌ La columna 'DIRECCIÓN' no existe. Estas son las columnas:")
        print(df.columns.tolist())
        return

    # Crear registro si no existe
    if not os.path.exists(registro_path):
        open(registro_path, 'w', encoding="utf-8").close()

    # Leer direcciones ya procesadas
    with open(registro_path, 'r', encoding='utf-8') as f:
        direcciones_procesadas = set([line.strip() for line in f.readlines()])

    # Agregar columnas si no existen
    if "LAT" not in df.columns:
        df["LAT"] = None
    if "LON" not in df.columns:
        df["LON"] = None
    if "GEOINTENTADO" not in df.columns:
        df["GEOINTENTADO"] = False

    # Convertir la columna a booleanos reales solo una vez
    df["GEOINTENTADO"] = df["GEOINTENTADO"].astype(str).str.lower() == "true"

    # Filtrar las filas que aún no han sido geoprocesadas
    filas_a_procesar = df[(df["GEOINTENTADO"] != True) & (df["LAT"].isna() | df["LON"].isna())]

    geolocator = Nominatim(user_agent="mi_app_georef", timeout=10)
    counter = 0

    with open(registro_path, 'a', encoding='utf-8') as log_file:
        for idx, row in filas_a_procesar.iterrows():
            nombre = row.get("NOMBRE", "")
            direccion_formateada = f"{row['DIRECCIÓN']}, {row.get('LOCALIDAD', 'Colombia')}"


            if direccion_formateada in direcciones_procesadas:
                if pd.notna(row["LAT"]) and pd.notna(row["LON"]):
                    continue  # Ya está geolocalizada correctamente
                else:
                    print(f"⚠️ Dirección ya registrada pero sin coordenadas: {direccion_formateada}")


            print(f"\n📍 Buscando: {nombre} – {direccion_formateada}")

            try:
                location = geolocator.geocode(direccion_formateada)
                df.at[idx, "GEOINTENTADO"] = True
                if location:
                    df.at[idx, "LAT"] = location.latitude
                    df.at[idx, "LON"] = location.longitude
                    print(f"✅ Coordenadas: ({location.latitude}, {location.longitude})")
                    counter += 1
                else:
                    print("⚠️ No se encontró la dirección")
            except Exception as e:
                df.at[idx, "GEOINTENTADO"] = True
                print(f"💥 Error con '{direccion_formateada}': {e}")

            # Registrar como ya intentada
            log_file.write(direccion_formateada + "\n")
            direcciones_procesadas.add(direccion_formateada)

            sleep(1.5)

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ Archivo guardado como {output_path}")
    print(f"📌 Total direcciones geolocalizadas esta vez: {counter}")
