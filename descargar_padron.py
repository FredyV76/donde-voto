import os
import urllib.request

URL_PADRON = "https://github.com/FredyV76/donde-voto/releases/download/v1.0/padron.db"
DESTINO = "padron.db"


def descargar_si_falta():
    if os.path.exists(DESTINO):
        print(f"{DESTINO} ya existe, no hace falta descargar.")
        return

    print(f"Descargando {DESTINO} desde GitHub Releases...")
    urllib.request.urlretrieve(URL_PADRON, DESTINO)

    tamano_mb = os.path.getsize(DESTINO) / (1024 * 1024)
    print(f"Descarga completa: {tamano_mb:.1f} MB")


if __name__ == "__main__":
    descargar_si_falta()