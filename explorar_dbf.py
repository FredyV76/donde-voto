from dbfread import DBF

ruta_archivo = r"C:\Users\GTFVERA\Downloads\RCP 2026-10-04 Padron\RCP 2026-10-04 Padron\data\PART.dbf"

tabla = DBF(ruta_archivo, encoding='latin1', load=False)

print(f"Archivo: {ruta_archivo}")
print(f"Cantidad de campos: {len(tabla.fields)}")
print("\n--- Campos ---")
for campo in tabla.fields:
    print(f"Nombre: {campo.name:20} Tipo: {campo.type:5} Tamaño: {campo.length}")

print("\n--- Primeros 3 registros (formato legible) ---")
contador = 0
for registro in tabla:
    print(f"\nRegistro {contador + 1}:")
    for clave, valor in registro.items():
        print(f"  {clave:15}: {valor}")
    contador += 1
    if contador >= 3:
        break