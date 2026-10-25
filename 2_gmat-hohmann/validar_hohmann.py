# Validacion analitica de la transferencia Hohmann 450 -> 500 km
import numpy as np

MU = 398600.4418      # parametro gravitacional de la Tierra [km^3/s^2]
RE = 6378.137         # radio ecuatorial terrestre [km]

r1 = RE + 450         # radio orbita inicial [km]
r2 = RE + 500         # radio orbita final [km]
a_t = (r1 + r2) / 2   # semieje mayor de la elipse de transferencia [km]

v1 = np.sqrt(MU / r1)                       # velocidad circular inicial
v2 = np.sqrt(MU / r2)                       # velocidad circular final
vp = np.sqrt(MU * (2/r1 - 1/a_t))           # velocidad en el perigeo de la elipse
va = np.sqrt(MU * (2/r2 - 1/a_t))           # velocidad en el apogeo de la elipse

dv1 = (vp - v1) * 1000                      # 1er impulso [m/s]
dv2 = (v2 - va) * 1000                      # 2do impulso [m/s]
t_transf = np.pi * np.sqrt(a_t**3 / MU) / 60  # media orbita de la elipse [min]

print(f"dv1 = {dv1:.3f} m/s")
print(f"dv2 = {dv2:.3f} m/s")
print(f"dv total = {dv1 + dv2:.3f} m/s")
print(f"tiempo de transferencia = {t_transf:.2f} min")