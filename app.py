from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import sqlite3
import re

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

DB = "padron.db"

MENSAJES_TIPO_VOTO = {
    0: "Mesa normal",
    1: "Mesa accesible",
    2: "Voto en casa"
}


def limpiar_cedula(texto: str) -> str:
    return re.sub(r"[^\d]", "", texto)


def buscar_por_cedula(cedula: int):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query = """
        SELECT 
            r.CEDULA, r.NOMBRE, r.APELLIDO, r.MESA, r.ORDEN, r.TIPO_VOTO,
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


PAGINA_BASE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>¿Dónde voto? · Padrón Electoral</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #EEF2F1;
    --paper-line: #D9DEDC;
    --navy: #12233F;
    --navy-deep: #0C1B2E;
    --red: #A93226;
    --green: #2F7D5A;
    --amber: #9A6B00;
    --muted: #5B6470;
    --card: #FFFFFF;
  }}

  * {{ box-sizing: border-box; }}

  body {{
    margin: 0;
    background: var(--bg);
    background-image:
      radial-gradient(circle at 1px 1px, rgba(18,35,63,0.05) 1px, transparent 0);
    background-size: 22px 22px;
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--navy);
    display: flex;
    justify-content: center;
    padding: 48px 20px 80px;
  }}

  main {{ width: 100%; max-width: 460px; }}

  .eyebrow {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--red);
    font-weight: 600;
    margin-bottom: 10px;
  }}
  .eyebrow::before {{
    content: "";
    width: 18px;
    height: 2px;
    background: var(--red);
    display: inline-block;
  }}

  h1 {{
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 34px;
    line-height: 1.15;
    margin: 0 0 8px;
    color: var(--navy-deep);
  }}

  .subtitulo {{
    color: var(--muted);
    font-size: 15px;
    line-height: 1.5;
    margin: 0 0 28px;
    max-width: 38ch;
  }}

  /* --- Panel tipo carnet / cédula --- */
  .carnet {{
    background: var(--card);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(12,27,46,0.06), 0 12px 28px -12px rgba(12,27,46,0.22);
    border: 1px solid var(--paper-line);
  }}

  .carnet-header {{
    background: var(--navy);
    background-image: repeating-linear-gradient(
      135deg,
      rgba(255,255,255,0.035) 0px,
      rgba(255,255,255,0.035) 1px,
      transparent 1px,
      transparent 7px
    );
    color: #E8ECF1;
    padding: 14px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .carnet-header .marca {{
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 600;
    opacity: 0.85;
  }}

  .sello {{
    width: 26px; height: 26px;
    border-radius: 50%;
    border: 1.5px solid rgba(232,236,241,0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
  }}

  .carnet-body {{ padding: 24px 22px 26px; }}

  label.campo-label {{
    display: block;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 600;
    margin-bottom: 8px;
  }}

  input[type="text"] {{
    width: 100%;
    padding: 14px 16px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 20px;
    letter-spacing: 0.04em;
    color: var(--navy-deep);
    background: #F6F7F6;
    border: 1.5px solid var(--paper-line);
    border-radius: 8px;
    margin-bottom: 6px;
  }}
  input[type="text"]:focus {{
    outline: 3px solid rgba(169,50,38,0.35);
    outline-offset: 1px;
    border-color: var(--red);
  }}

  .ayuda {{
    font-size: 12.5px;
    color: var(--muted);
    margin-bottom: 18px;
  }}

  button {{
    width: 100%;
    padding: 13px;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.01em;
    color: #fff;
    background: var(--navy);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.15s ease;
  }}
  button:hover {{ background: var(--navy-deep); }}
  button:focus-visible {{
    outline: 3px solid rgba(18,35,63,0.35);
    outline-offset: 2px;
  }}

  /* --- Comprobante de resultado (estilo talón perforado) --- */
  .comprobante {{
    margin-top: 22px;
    border-radius: 0 0 14px 14px;
  }}

  .perforado {{
    position: relative;
    border-top: 1.5px dashed var(--paper-line);
    margin: 0 22px;
  }}
  .perforado::before, .perforado::after {{
    content: "";
    position: absolute;
    top: -8px;
    width: 16px; height: 16px;
    background: var(--bg);
    border-radius: 50%;
  }}
  .perforado::before {{ left: -30px; }}
  .perforado::after {{ right: -30px; }}

  .resultado {{ padding: 20px 22px 24px; }}

  .resultado-ok .nombre {{
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 19px;
    color: var(--navy-deep);
    margin: 0 0 14px;
  }}

  .fila {{
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid #EEF0EF;
    font-size: 14.5px;
  }}
  .fila:last-of-type {{ border-bottom: none; }}
  .fila .k {{ color: var(--muted); }}
  .fila .v {{ font-weight: 600; text-align: right; }}

  .badge {{
    display: inline-block;
    margin-top: 14px;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12.5px;
    font-weight: 600;
    background: rgba(47,125,90,0.1);
    color: var(--green);
  }}

  .mensaje {{
    padding: 16px 22px;
    font-size: 14px;
    line-height: 1.5;
  }}
  .mensaje.error {{ color: var(--red); }}
  .mensaje.aviso {{ color: var(--amber); }}

  footer {{
    max-width: 460px;
    margin: 22px auto 0;
    text-align: center;
    font-size: 12px;
    color: var(--muted);
    line-height: 1.6;
  }}
</style>
</head>
<body>
<main>
  <div class="eyebrow">Padrón electoral · Paraguay</div>
  <h1>¿Dónde voto?</h1>
  <p class="subtitulo">Ingresá tu número de cédula para saber tu local, mesa y distrito de votación.</p>

  <div class="carnet">
    <div class="carnet-header">
      <span class="marca">Elección Municipal - Villa Elisa</span>
      <span class="sello">fv</span>
    </div>
    <div class="carnet-body">
      <form method="get" action="/">
        <label class="campo-label" for="cedula">N.º de cédula</label>
        <input type="text" id="cedula" name="cedula" placeholder="0.000.000" value="{cedula_valor}" inputmode="numeric" {autofocus_attr}>
        <div class="ayuda">Podés escribirla con o sin puntos.</div>
        <button type="submit">Buscar</button>
      </form>
    </div>
    {resultado_html}
  </div>

  <footer>Solo se muestran los datos necesarios para ubicar tu mesa de votación.</footer>
</main>
</body>
</html>
"""

RESULTADO_OK = """
<div class="comprobante">
  <div class="perforado"></div>
  <div class="resultado resultado-ok">
    <p class="nombre">{nombre} {apellido}</p>
    <div class="fila"><span class="k">Departamento</span><span class="v">{departamento}</span></div>
    <div class="fila"><span class="k">Distrito</span><span class="v">{distrito}</span></div>
    <div class="fila"><span class="k">Local de votación</span><span class="v">{local}</span></div>
    <div class="fila"><span class="k">Mesa</span><span class="v">{mesa}</span></div>
    <div class="fila"><span class="k">N.º de orden</span><span class="v">{orden}</span></div>
    <span class="badge">{tipo_voto}</span>
  </div>
</div>
"""

RESULTADO_MSG = """
<div class="comprobante">
  <div class="perforado"></div>
  <div class="mensaje {clase}">{texto}</div>
</div>
"""


@app.get("/", response_class=HTMLResponse)
@limiter.limit("13/minute")
def home(request: Request, cedula: str = ""):
    resultado_html = ""
    cedula_original = cedula.strip()

    if cedula_original:
        cedula_limpia = limpiar_cedula(cedula_original)

        if not cedula_limpia:
            resultado_html = RESULTADO_MSG.format(
                clase="error",
                texto="⚠️ Ingresá un número de cédula válido."
            )

        elif len(cedula_limpia) < 5 or len(cedula_limpia) > 8:
            resultado_html = RESULTADO_MSG.format(
                clase="aviso",
                texto="⚠️ Revisá el número: las cédulas paraguayas tienen entre 5 y 8 dígitos."
            )

        else:
            datos = buscar_por_cedula(int(cedula_limpia))
            if datos:
                tipo_voto_texto = MENSAJES_TIPO_VOTO.get(datos["TIPO_VOTO"], "No especificado")
                resultado_html = RESULTADO_OK.format(
                    nombre=datos['NOMBRE'],
                    apellido=datos['APELLIDO'],
                    departamento=datos['DEPARTAMENTO'],
                    distrito=datos['DISTRITO'],
                    local=datos['LOCAL_VOTACION'],
                    mesa=datos['MESA'],
                    orden=datos['ORDEN'],
                    tipo_voto=tipo_voto_texto
                )
            else:
                resultado_html = f'<div class="resultado error">❌ No se encontró la cédula {cedula_limpia}. Verificá que esté bien escrita.</div>'

    autofocus_attr = "" if cedula_original else "autofocus"

    return PAGINA_BASE.format(
        cedula_valor=cedula_original,
        resultado_html=resultado_html,
        autofocus_attr=autofocus_attr
    )
@app.head("/")
def home_head():
    return HTMLResponse(content="", status_code=200)