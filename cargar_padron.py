import sqlite3
from dbfread import DBF
import time

# --- Configuración de rutas ---
CARPETA = r"C:\Users\GTFVERA\Downloads\RCP 2026-10-04 Padron\RCP 2026-10-04 Padron\data"
DB_SALIDA = "padron.db"
LOTE = 5000  # cuántos registros insertar por vez

def crear_conexion():
    conn = sqlite3.connect(DB_SALIDA)
    conn.execute("PRAGMA journal_mode=WAL")  # mejor rendimiento para lecturas concurrentes
    return conn

def cargar_dep(conn):
    print("Cargando dep.dbf...")
    tabla = DBF(f"{CARPETA}\\dep.dbf", encoding='latin1', load=False)
    conn.execute("DROP TABLE IF EXISTS dep")
    conn.execute("""
        CREATE TABLE dep (
            DEPART INTEGER PRIMARY KEY,
            DESCRIP TEXT
        )
    """)
    filas = [(r['DEPART'], r['DESCRIP']) for r in tabla]
    conn.executemany("INSERT INTO dep VALUES (?, ?)", filas)
    conn.commit()
    print(f"  {len(filas)} departamentos cargados.")

def cargar_dis(conn):
    print("Cargando dis.dbf...")
    tabla = DBF(f"{CARPETA}\\dis.dbf", encoding='latin1', load=False)
    conn.execute("DROP TABLE IF EXISTS dis")
    conn.execute("""
        CREATE TABLE dis (
            DEPART INTEGER,
            DISTRITO INTEGER,
            DESCRIP TEXT,
            PRIMARY KEY (DEPART, DISTRITO)
        )
    """)
    filas = [(r['DEPART'], r['DISTRITO'], r['DESCRIP']) for r in tabla]
    conn.executemany("INSERT INTO dis VALUES (?, ?, ?)", filas)
    conn.commit()
    print(f"  {len(filas)} distritos cargados.")

def cargar_loc(conn):
    print("Cargando loc.dbf...")
    tabla = DBF(f"{CARPETA}\\loc.dbf", encoding='latin1', load=False)
    conn.execute("DROP TABLE IF EXISTS loc")
    conn.execute("""
        CREATE TABLE loc (
            DPTO INTEGER,
            DISTRITO INTEGER,
            ZONA INTEGER,
            LOCAL INTEGER,
            DESCRIP TEXT,
            PRIMARY KEY (DPTO, DISTRITO, ZONA, LOCAL)
        )
    """)
    filas = [(r['DPTO'], r['DISTRITO'], r['ZONA'], r['LOCAL'], r['DESCRIP']) for r in tabla]
    conn.executemany("INSERT INTO loc VALUES (?, ?, ?, ?, ?)", filas)
    conn.commit()
    print(f"  {len(filas)} locales cargados.")

def cargar_regciv(conn):
    print("Cargando regciv.dbf (esto puede tardar varios minutos por el tamaño)...")
    tabla = DBF(f"{CARPETA}\\regciv.dbf", encoding='latin1', load=False)
    conn.execute("DROP TABLE IF EXISTS regciv")
    conn.execute("""
        CREATE TABLE regciv (
            CEDULA INTEGER,
            NOMBRE TEXT,
            APELLIDO TEXT,
            SEXO TEXT,
            DEPART INTEGER,
            DISTRITO INTEGER,
            ZONA INTEGER,
            LOCAL INTEGER,
            MESA INTEGER,
            ORDEN INTEGER,
            TIPO_VOTO INTEGER
        )
    """)

    lote = []
    total = 0
    inicio = time.time()

    for r in tabla:
        lote.append((
            r.get('CEDULA'), r.get('NOMBRE'), r.get('APELLIDO'), r.get('SEXO'),
            r.get('DEPART'), r.get('DISTRITO'), r.get('ZONA'), r.get('LOCAL'),
            r.get('MESA'), r.get('ORDEN'), r.get('TIPO_VOTO')
        ))
        if len(lote) >= LOTE:
            conn.executemany("INSERT INTO regciv VALUES (?,?,?,?,?,?,?,?,?,?,?)", lote)
            conn.commit()
            total += len(lote)
            print(f"  {total} registros procesados... ({time.time()-inicio:.0f}s)")
            lote = []

    if lote:
        conn.executemany("INSERT INTO regciv VALUES (?,?,?,?,?,?,?,?,?,?,?)", lote)
        conn.commit()
        total += len(lote)

    print(f"  Total regciv: {total} registros en {time.time()-inicio:.0f}s")

    print("Creando índice en CEDULA...")
    conn.execute("CREATE INDEX idx_cedula ON regciv(CEDULA)")
    conn.commit()
    print("  Índice creado.")

if __name__ == "__main__":
    conn = crear_conexion()
    cargar_dep(conn)
    cargar_dis(conn)
    cargar_loc(conn)
    cargar_regciv(conn)
    conn.close()
    print("\n✅ Base de datos 'padron.db' creada con éxito.")