import sqlite3

DB = "padron.db"

def buscar_por_cedula(cedula: int):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # para poder acceder a columnas por nombre
    cur = conn.cursor()

    query = """
        SELECT 
            r.CEDULA,
            r.NOMBRE,
            r.APELLIDO,
            r.SEXO,
            r.MESA,
            r.TIPO_VOTO,
            dep.DESCRIP AS DEPARTAMENTO,
            dis.DESCRIP AS DISTRITO,
            loc.DESCRIP AS LOCAL_VOTACION
        FROM regciv r
        LEFT JOIN dep ON r.DEPART = dep.DEPART
        LEFT JOIN dis ON r.DEPART = dis.DEPART AND r.DISTRITO = dis.DISTRITO
        LEFT JOIN loc ON r.DEPART = loc.DPTO AND r.DISTRITO = loc.DISTRITO 
                      AND r.ZONA = loc.ZONA AND r.LOCAL = loc.LOCAL
        WHERE r.CEDULA = ?
    """

    cur.execute(query, (cedula,))
    resultado = cur.fetchone()
    conn.close()
    return dict(resultado) if resultado else None


if __name__ == "__main__":
    import time

    cedula_prueba = 2404465  # la que vimos en el primer registro de ejemplo

    inicio = time.time()
    datos = buscar_por_cedula(cedula_prueba)
    duracion = time.time() - inicio

    if datos:
        print(f"\n✅ Encontrado en {duracion*1000:.1f} ms\n")
        for clave, valor in datos.items():
            print(f"  {clave:18}: {valor}")
    else:
        print(f"\n❌ No se encontró la cédula {cedula_prueba}")