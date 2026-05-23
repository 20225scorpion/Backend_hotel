"""
Seed de datos de prueba para hotel_system.
Ejecutar desde la carpeta backend-hotel-finanzas:
    python seed_data.py
"""

import pymysql

DB = dict(host="localhost", user="root", password="1234",
          database="hotel_system", charset="utf8mb4")

# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------

HABITACIONES = [
    ("101", "libre",         90000, 130000, "Vista al jardín, primer piso"),
    ("102", "ocupada",       90000, 130000, "Vista a la calle, segundo piso"),
    ("103", "limpieza",      90000, 130000, "Habitación con balcón"),
    ("104", "mantenimiento", 90000, 130000, "En reparación eléctrica"),
    ("105", "libre",         90000, 130000, "Esquinera, mucha luz natural"),
]

HUESPEDES = [
    ("Carlos Andrés Pérez Ruiz",  "1020456789", "3101234567", "caperez@gmail.com",    None),
    ("María Fernanda López Díaz", "52684762",   "3209876543", "mflopez@hotmail.com",  "ABC123"),
    ("Juan Sebastián Torres Gil", "1143256830", "3155551234", None,                   None),
]

# usuario_id=1 = Mateo (admin existente)
INGRESOS = [
    (None, 270000, "Hospedaje hab. 102 - 3 noches (familia Pérez)",  "hospedaje",   1),
    (None,  45000, "Consumo restaurante - desayunos (2 personas)",   "restaurante", 1),
]

GASTOS = [
    ("Nómina mensual personal hotelero - mayo 2026", 2500000, 1, "nomina"),
    ("Servicios públicos - agua, luz, gas - mayo 2026", 380000, 1, "servicios"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def tabla_vacia(cur, tabla):
    cur.execute(f"SELECT COUNT(*) FROM {tabla}")
    return cur.fetchone()[0] == 0


def existe(cur, tabla, campo, valor):
    cur.execute(f"SELECT 1 FROM {tabla} WHERE {campo} = %s LIMIT 1", (valor,))
    return cur.fetchone() is not None


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------

def seed():
    conn = pymysql.connect(**DB)
    cur  = conn.cursor()
    conteo = {"habitaciones": 0, "huespedes": 0, "ingresos": 0, "gastos": 0}

    try:
        # ── Habitaciones ────────────────────────────────────────────────────
        print("\n[habitaciones]")
        for numero, estado, p1, p2, obs in HABITACIONES:
            if existe(cur, "habitaciones", "numero", numero):
                print(f"  omitida   hab {numero} (ya existe)")
                continue
            cur.execute(
                """INSERT INTO habitaciones
                       (numero, estado, precio_1_persona, precio_2_personas, observaciones)
                   VALUES (%s, %s, %s, %s, %s)""",
                (numero, estado, p1, p2, obs)
            )
            conteo["habitaciones"] += 1
            print(f"  insertada hab {numero} - {estado}")

        # ── Huespedes ────────────────────────────────────────────────────────
        print("\n[huespedes]")
        for nombre, cedula, tel, correo, placa in HUESPEDES:
            if existe(cur, "huespedes", "cedula", cedula):
                print(f"  omitido   {cedula} (ya existe)")
                continue
            cur.execute(
                """INSERT INTO huespedes (nombre, cedula, telefono, correo, placa)
                   VALUES (%s, %s, %s, %s, %s)""",
                (nombre, cedula, tel, correo, placa)
            )
            conteo["huespedes"] += 1
            print(f"  insertado {cedula} - {nombre}")

        # ── Ingresos ─────────────────────────────────────────────────────────
        print("\n[ingresos]")
        for hosp_id, monto, desc, tipo, uid in INGRESOS:
            cur.execute(
                """INSERT INTO ingresos (hospedaje_id, monto, descripcion, tipo, usuario_id)
                   VALUES (%s, %s, %s, %s, %s)""",
                (hosp_id, monto, desc, tipo, uid)
            )
            conteo["ingresos"] += 1
            print(f"  insertado ${monto:,.0f} - {tipo}")

        # ── Gastos ───────────────────────────────────────────────────────────
        print("\n[gastos]")
        for desc, monto, uid, cat in GASTOS:
            cur.execute(
                """INSERT INTO gastos (descripcion, monto, usuario_id, categoria)
                   VALUES (%s, %s, %s, %s)""",
                (desc, monto, uid, cat)
            )
            conteo["gastos"] += 1
            print(f"  insertado ${monto:,.0f} - {cat}")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] {e}")
        raise
    finally:
        cur.close()
        conn.close()

    return conteo


# ---------------------------------------------------------------------------
# Mostrar resumen
# ---------------------------------------------------------------------------

def mostrar_resumen():
    conn = pymysql.connect(**DB)
    cur  = conn.cursor()

    tablas = [
        ("habitaciones", "SELECT id, numero, estado, precio_1_persona, precio_2_personas FROM habitaciones ORDER BY numero"),
        ("huespedes",    "SELECT id, nombre, cedula, telefono FROM huespedes ORDER BY id"),
        ("ingresos",     "SELECT id, monto, tipo, descripcion, usuario_id FROM ingresos ORDER BY id"),
        ("gastos",       "SELECT id, monto, categoria, descripcion, usuario_id FROM gastos ORDER BY id"),
    ]

    for nombre, sql in tablas:
        cur.execute(sql)
        filas = cur.fetchall()
        cols  = [d[0] for d in cur.description]
        sep   = "-" * 90
        print(f"\n=== {nombre.upper()} ({len(filas)} registros) ===")
        print(sep)
        print("  ".join(f"{c:<22}" for c in cols))
        print(sep)
        for fila in filas:
            print("  ".join(f"{str(v):<22}" for v in fila))

    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("  SEED hotel_system")
    print("=" * 50)

    totales = seed()

    print("\n" + "=" * 50)
    print("  RESULTADO")
    print("=" * 50)
    total = sum(totales.values())
    for tabla, n in totales.items():
        print(f"  {tabla:<15} {n} insertado(s)")
    print(f"  {'TOTAL':<15} {total} registro(s)")

    print("\n" + "=" * 50)
    print("  ESTADO ACTUAL DE LAS TABLAS")
    print("=" * 50)
    mostrar_resumen()
