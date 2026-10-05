# satelites.py
# Parte 1: descargar los datos de los satélites de Satellogic

import requests
from datetime import timedelta
from skyfield.api import load, wgs84, EarthSatellite
import numpy as np
import matplotlib.pyplot as plt

URL = "https://celestrak.org/NORAD/elements/gp.php?NAME=NUSAT&FORMAT=tle"
respuesta = requests.get(URL, timeout=30)


# Parte 2: separar cada satélite y filtrar solo los de Satellogic ---
lineas = respuesta.text.strip().splitlines()

satelites = []
for i in range(0, len(lineas), 3):
    nombre = lineas[i].strip()
    linea1 = lineas[i + 1].strip()
    linea2 = lineas[i + 2].strip()

    if nombre.startswith("NUSAT"):
        satelites.append([nombre, linea1, linea2])

print(f"Satélites de Satellogic encontrados: {len(satelites)}")
for sat in satelites:
    print(sat[0])


# Parte 3: calcular dónde está cada satélite ahora mismo
ts = load.timescale()
ahora = ts.now()

print(f"\nPosición de los satélites ahora ({ahora.utc_strftime('%Y-%m-%d %H:%M UTC')}):")
for nombre, linea1, linea2 in satelites:
    sat = EarthSatellite(linea1, linea2, nombre, ts)
    posicion = sat.at(ahora)
    lat, lon = wgs84.latlon_of(posicion)
    altura = wgs84.height_of(posicion).km
    print(f"{nombre:28} | Lat {lat.degrees:7.2f}° | Lon {lon.degrees:8.2f}° | Alt {altura:6.1f} km")


# Parte 4: pasadas sobre Buenos Aires en las próximas 24 horas
buenos_aires = wgs84.latlon(-34.6037, -58.3816, elevation_m=25)
manana = ts.tt_jd(ahora.tt + 1)

pasadas = []
for nombre, linea1, linea2 in satelites:
    sat = EarthSatellite(linea1, linea2, nombre, ts)
    tiempos, eventos = sat.find_events(buenos_aires, ahora, manana, altitude_degrees=10.0)

    inicio = None
    elev_max = 0
    for t, evento in zip(tiempos, eventos):
        if evento == 0:
            inicio = t
        elif evento == 1:
            elev, az, dist = (sat - buenos_aires).at(t).altaz()
            elev_max = elev.degrees
        elif evento == 2 and inicio is not None:
            duracion = (t.tt - inicio.tt) * 24 * 60
            pasadas.append((inicio.utc_datetime(), nombre, elev_max, duracion))
            inicio = None

pasadas.sort()
print(f"\nPasadas sobre Buenos Aires (próximas 24 h, elevación > 10°): {len(pasadas)}")
for inicio, nombre, elev_max, duracion in pasadas:
    hora_local = inicio - timedelta(hours=3)
    print(f"{hora_local:%d/%m %H:%M} (hora AR) | {nombre:28} | Elev máx {elev_max:5.1f}° | {duracion:4.1f} min")


# Parte 5: gráfico del ground track (recorrido sobre la Tierra)
nombre, linea1, linea2 = satelites[0]
sat = EarthSatellite(linea1, linea2, nombre, ts)

minutos = np.arange(0, 180, 1)
instantes = ts.tt_jd(ahora.tt + minutos / 1440)

posiciones = sat.at(instantes)
lat, lon = wgs84.latlon_of(posiciones)
lat = lat.degrees
lon = lon.degrees

saltos = np.where(np.abs(np.diff(lon)) > 180)[0] + 1
lat = np.insert(lat, saltos, np.nan)
lon = np.insert(lon, saltos, np.nan)

plt.figure(figsize=(12, 6))
plt.plot(lon, lat, label=f"{nombre} (próximas 3 h)")
plt.plot(-58.38, -34.60, "r*", markersize=15, label="Buenos Aires")
plt.xlim(-180, 180)
plt.ylim(-90, 90)
plt.xlabel("Longitud (°)")
plt.ylabel("Latitud (°)")
plt.title("Ground track de un satélite de Satellogic")
plt.grid(True)
plt.legend()
plt.savefig("ground_track.png", dpi=150)
plt.close()


# Parte 6: altitud media de toda la constelación
MU = 398600.4418
R_TIERRA = 6378.137

nombres = []
alturas = []
for nombre, linea1, linea2 in satelites:
    sat = EarthSatellite(linea1, linea2, nombre, ts)
    n = sat.model.no_kozai / 60
    a = (MU / n**2) ** (1 / 3)
    nombres.append(nombre.split(" (")[0])
    alturas.append(a - R_TIERRA)

orden = np.argsort(alturas)
nombres = [nombres[i] for i in orden]
alturas = [alturas[i] for i in orden]
colores = ["red" if h < 400 else "tab:blue" for h in alturas]

print("\nAltitud media de la constelación (de menor a mayor):")
for nombre, h in zip(nombres, alturas):
    print(f"{nombre:10} | {h:6.1f} km")

plt.figure(figsize=(12, 6))
plt.bar(nombres, alturas, color=colores)
plt.axhline(400, color="red", linestyle="--", label="400 km (arrastre fuerte)")
plt.ylabel("Altitud media (km)")
plt.title("Altitud media de la constelación de Satellogic")
plt.xticks(rotation=60)
plt.ylim(300, 560)
plt.legend()
plt.tight_layout()
plt.savefig("altitud_constelacion.png", dpi=150)
plt.close()


# Parte 7: guardar un reporte automático en un archivo de texto
fecha = ahora.utc_strftime("%Y-%m-%d")
nombre_archivo = f"reporte_{fecha}.txt"

with open(nombre_archivo, "w", encoding="utf-8") as archivo:
    archivo.write("REPORTE DIARIO - CONSTELACIÓN SATELLOGIC\n")
    archivo.write(f"Generado: {ahora.utc_strftime('%Y-%m-%d %H:%M UTC')}\n")
    archivo.write(f"Satélites analizados: {len(satelites)}\n\n")

    archivo.write("ALERTAS (altitud media < 400 km):\n")
    for nombre, h in zip(nombres, alturas):
        if h < 400:
            archivo.write(f"  ⚠ {nombre}: {h:.1f} km\n")

    archivo.write("\nALTITUD MEDIA (de menor a mayor):\n")
    for nombre, h in zip(nombres, alturas):
        archivo.write(f"  {nombre:10} {h:6.1f} km\n")

    archivo.write(f"\nPASADAS SOBRE BUENOS AIRES (próximas 24 h): {len(pasadas)}\n")
    for inicio, nombre, elev_max, duracion in pasadas:
        hora_local = inicio - timedelta(hours=3)
        archivo.write(f"  {hora_local:%d/%m %H:%M} (hora AR) | {nombre:28} | Elev máx {elev_max:5.1f}° | {duracion:4.1f} min\n")

print(f"\nReporte guardado en: {nombre_archivo}")