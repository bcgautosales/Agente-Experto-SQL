import streamlit as st
from orquestador import ejecutar_agente
from conocimientos import (
    listar_conocimientos,
    guardar_conocimiento,
    eliminar_conocimiento,
)
from streamlit_mic_recorder import speech_to_text
from voz import convertir_texto_a_voz
import json
from pathlib import Path

# ==========================================
# HISTORIAL PERSISTENTE DE SQL NEXUS
# ==========================================

ARCHIVO_HISTORIAL = Path(__file__).parent / "historial.json"


def cargar_historial():
    """Carga el historial guardado en el archivo JSON."""
    if ARCHIVO_HISTORIAL.exists():
        try:
            with open(
                ARCHIVO_HISTORIAL,
                "r",
                encoding="utf-8",
            ) as archivo:
                datos = json.load(archivo)

            if isinstance(datos, list):
                return datos

        except (json.JSONDecodeError, OSError):
            pass

    return []


def guardar_historial(historial):
    """Guarda el historial de consultas en un archivo JSON."""
    try:
        with open(
            ARCHIVO_HISTORIAL,
            "w",
            encoding="utf-8",
        ) as archivo:
            json.dump(
                historial,
                archivo,
                ensure_ascii=False,
                indent=4,
            )

    except OSError as error:
        print(f"No se pudo guardar el historial: {error}")


# =====================================================
# CONFIGURACION GENERAL
# =====================================================
st.set_page_config(
    page_title="SQL Nexus | Inteligencia SQL",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# ESTILOS CSS
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Variables del diseño */
:root {
    --fondo: #0B1120;
    --panel: #131E31;
    --panel2: #192840;
    --turquesa: #2DE2C5;
    --blanco: #F8FAFC;
    --texto: #D7E1EF;
    --borde: #30425B;
}

/* Navegación inferior: oculta por defecto */
.mobile-bottom-nav {
    display: none;
}

/* Estilos generales */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(ellipse at 80% 0%, #17334A 0%, transparent 38%), #0B1120;
    color: var(--blanco);
}

h1, h2, h3, h4, p, label,
[data-testid="stMarkdownContainer"] {
    color: var(--blanco);
}

[data-testid="stCaptionContainer"] {
    color: #B8C7DA !important;
}

.stApp p {
    line-height: 1.65;
}

/* Panel lateral */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #142137, #0F192B);
    border-right: 1px solid #2D4059;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #F8FAFC;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 8px;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    background: #192840;
    border: 1px solid #30425B;
    border-radius: 11px;
    padding: 10px 12px;
    transition: all .2s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #243B53;
    border-color: #2DE2C5;
}

/* Botones */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #2DE2C5, #16B8AE);
    color: #071521 !important;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    min-height: 43px;
    transition: all .2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #72F5DE;
    color: #071521 !important;
    border: none;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px #2DE2C522;
}

/* Tarjetas */
.tarjeta {
    background: linear-gradient(145deg, #192840, #121D30);
    border: 1px solid #30425B;
    border-radius: 17px;
    padding: 21px;
    min-height: 168px;
    height: 100%;
    transition: all .22s ease;
}

.tarjeta:hover {
    border-color: #2DE2C5;
    transform: translateY(-4px);
    box-shadow: 0 12px 30px #00000025;
}

.icono {
    font-size: 28px;
    margin-bottom: 12px;
}

.tarjeta h3 {
    color: #2DE2C5 !important;
    font-size: 17px;
    margin-bottom: 7px;
}

.tarjeta p {
    color: #D7E1EF !important;
    font-size: 13px;
    margin-bottom: 0;
}

/* Portada */
.hero {
    background: linear-gradient(115deg, #173047, #17243A 65%, #16383D);
    border: 1px solid #31536A;
    border-radius: 22px;
    padding: 30px;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
}

.hero h1 {
    font-size: clamp(29px, 3.5vw, 43px);
    font-weight: 800;
    letter-spacing: -1.5px;
    margin-bottom: 10px;
}

.hero p {
    color: #D7E8F2 !important;
    max-width: 680px;
}

.etiqueta {
    display: inline-block;
    background: #2DE2C51C;
    border: 1px solid #2DE2C566;
    color: #6FF7E0;
    padding: 6px 12px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 14px;
}

/* Campos de texto */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background-color: #101B2D !important;
    color: #FFF !important;
    border: 1px solid #3A506D !important;
    border-radius: 12px !important;
}

[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #2DE2C5 !important;
    box-shadow: 0 0 0 1px #2DE2C5;
}

[data-testid="stTextArea"] textarea::placeholder {
    color: #9BAEC5 !important;
}

/* Selectores y pestañas */
[data-baseweb="select"] > div {
    background-color: #192840;
    color: white;
    border-color: #30425B;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    color: #D7E1EF;
    background: #17243A;
    border-radius: 9px 9px 0 0;
    padding: 10px 16px;
}

.stTabs [aria-selected="true"] {
    color: #2DE2C5 !important;
}

/* Resultados */
.resultado {
    background: #131F31;
    border: 1px solid #30425B;
    border-left: 4px solid #2DE2C5;
    border-radius: 12px;
    padding: 20px;
    margin-top: 12px;
}

hr {
    border-color: #30425B;
}

/* Métricas */
[data-testid="stMetric"] {
    background: #17243A;
    border: 1px solid #30425B;
    border-radius: 13px;
    padding: 15px;
}

[data-testid="stMetricLabel"] {
    color: #D7E1EF !important;
}

[data-testid="stMetricValue"] {
    color: #2DE2C5 !important;
}

/* Ocultar elementos predeterminados */
footer, #MainMenu {
    visibility: hidden;
}

/* Navegación inferior únicamente en teléfonos */
@media (max-width: 768px) {
    .mobile-bottom-nav {
        display: block;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        background: #131E31;
        border-top: 1px solid #30425B;
        padding: 8px 5px;
        box-shadow: 0 -5px 18px #00000035;
    }

    .mobile-bottom-nav button {
        font-size: 11px !important;
        min-height: 48px !important;
        padding: 4px 2px !important;
        white-space: normal !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding-bottom: 100px !important;
    }
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# ESTADO DE LA APLICACION
# =====================================================
if "historial" not in st.session_state:
    st.session_state.historial = cargar_historial()
if "pregunta" not in st.session_state:
    st.session_state.pregunta = ""
if "seccion" not in st.session_state:
    st.session_state.seccion = "Inicio"
if "ultima_pregunta_voz" not in st.session_state:
    st.session_state.ultima_pregunta_voz = ""

# =====================================================
# FUNCIONES
# =====================================================


def cambiar_seccion(nombre):
    st.session_state.seccion = nombre


def consultar_agente(texto_pregunta):
    """Envía una solicitud al agente existente."""
    if not texto_pregunta or not texto_pregunta.strip():
        st.warning("Escribe una pregunta antes de consultar.")
        return

    try:
        with st.spinner("Analizando tu solicitud..."):
            resultado = ejecutar_agente(texto_pregunta.strip())

        if isinstance(resultado, dict):
            respuesta = resultado.get(
                "respuesta", "El agente no devolvió una respuesta.")
            origen = resultado.get("origen", "desconocido")
            herramienta = resultado.get("herramienta", "no especificada")
        else:
            respuesta = str(resultado)
            origen = "desconocido"
            herramienta = "no especificada"

        st.session_state.historial.append({
            "pregunta": texto_pregunta.strip(),
            "respuesta": respuesta,
            "origen": origen,
            "herramienta": herramienta,
        })
        guardar_historial(st.session_state.historial)
    except Exception as error:
        st.error(
            "No fue posible procesar la consulta. Revisa el error en la terminal de VS Code.")
        st.exception(error)


def mostrar_resultado():
    """Muestra la última respuesta y permite continuar la conversación."""
    if not st.session_state.historial:
        return

    ultimo = st.session_state.historial[-1]
    st.markdown("### ✨ Respuesta del agente")
    origen = str(ultimo.get("origen", "desconocido")).lower()

    if origen == "python":
        st.success("Respuesta local · Python")
    elif origen == "gemini":
        st.info("Respuesta generada · Gemini")
    else:
        st.caption(f"Origen: {ultimo.get('origen', 'desconocido')}")

    st.markdown('<div class="resultado">', unsafe_allow_html=True)
    st.markdown(ultimo.get("respuesta", "Sin respuesta."))
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 💬 Continúa la conversación")
    with st.form("form_seguimiento"):
        seguimiento = st.text_area(
            "Tu siguiente pregunta",
            placeholder="Ej.: ¿Puedes explicarme mejor el HAVING con otro ejemplo?",
            height=100,
        )
        continuar = st.form_submit_button(
            "Enviar pregunta →", use_container_width=True)

    if continuar:
        if not seguimiento.strip():
            st.warning("Escribe una pregunta para continuar.")
        else:
            solicitud = (
                "Responde a la siguiente pregunta teniendo en cuenta esta conversación anterior.\n\n"
                f"Pregunta anterior: {ultimo['pregunta']}\n\n"
                f"Respuesta anterior: {ultimo['respuesta']}\n\n"
                f"Pregunta de seguimiento del usuario: {seguimiento.strip()}\n\n"
                "Responde directamente y conserva el contexto anterior cuando sea relevante."
            )
            consultar_agente(solicitud)
            st.rerun()


# =====================================================
# BARRA LATERAL
# =====================================================
with st.sidebar:
    # Logo de SQL Nexus
    st.image(
        "img/logo.png",
        width=180,
    )

    # Encabezado
    st.markdown("""
    <div style="text-align:center;padding:0 0 18px;">
        <div style="font-size:25px;font-weight:800;letter-spacing:1px;">
            SQL <span style="color:#2DE2C5;">NEXUS</span>
        </div>
        <div style="font-size:12px;color:#D7E1EF!important;">
            AGENTE EXPERTO EN SQL
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Navegación
    st.markdown("### 🧭 Navegación")

    seccion = st.radio(
        "Selecciona una sección",
        [
            "Inicio",
            "Aprender SQL",
            "Generar consultas",
            "Revisar SQL",
            "Seguridad SQL",
            "Consulta libre",
            "Alimentar",
            "Conversación por voz",
            "Historial",
        ],
        key="seccion",
        label_visibility="collapsed",
    )

    st.divider()

    # Estado del agente
    st.markdown("### ⚡ Tu agente inteligente")

    st.markdown("""
    <div style="background:#192840;border:1px solid #30425B;padding:14px;border-radius:13px;">
        <div style="color:#2DE2C5;font-weight:700;">● Sistema preparado</div>
        <div style="color:#F8FAFC;font-size:13px;margin-top:7px;">Python · Conocimiento local</div>
        <div style="color:#F8FAFC;font-size:13px;margin-top:5px;">Gemini · Respaldo inteligente</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Limpiar historial
    if st.button("🧹 Limpiar historial", use_container_width=True):
        st.session_state.historial = []
        guardar_historial(st.session_state.historial)
        st.rerun()

    # Pie de la barra lateral
    st.markdown("""
    <div style="text-align:center;color:#CBD5E1;font-size:11px;padding-top:20px;">
        SQL NEXUS · PROYECTO ACADÉMICO
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# NAVEGACION RAPIDA PARA MOVILES
# =====================================================

if "mostrar_menu_movil" not in st.session_state:
    st.session_state.mostrar_menu_movil = False


def ir_a_seccion_movil(nombre):
    st.session_state.seccion = nombre
    st.session_state.mostrar_menu_movil = False
    st.session_state.desplazar_seccion_movil = True


with st.container(key="mobile_bottom_nav"):
    st.markdown(
        '<div class="mobile-bottom-nav"></div>',
        unsafe_allow_html=True,
    )

    nav1, nav2, nav3, nav4, nav5 = st.columns(5)

    with nav1:
        st.button(
            "🏠 Inicio",
            key="movil_inicio",
            use_container_width=True,
            on_click=ir_a_seccion_movil,
            args=("Inicio",),
        )

    with nav2:
        st.button(
            "📚 Aprender",
            key="movil_aprender",
            use_container_width=True,
            on_click=ir_a_seccion_movil,
            args=("Aprender SQL",),
        )

    with nav3:
        st.button(
            "⚙️ Consultas",
            key="movil_consultas",
            use_container_width=True,
            on_click=ir_a_seccion_movil,
            args=("Generar consultas",),
        )

    with nav4:
        st.button(
            "🎙️ Voz",
            key="movil_voz",
            use_container_width=True,
            on_click=ir_a_seccion_movil,
            args=("Conversación por voz",),
        )

    with nav5:
        st.button(
            "☰ Más",
            key="movil_mas",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                mostrar_menu_movil=not st.session_state.mostrar_menu_movil
            ),
        )

    if st.session_state.mostrar_menu_movil:
        st.markdown("### Más herramientas")

        herramienta_movil = st.selectbox(
            "Selecciona una sección",
            [
                "Revisar SQL",
                "Seguridad SQL",
                "Consulta libre",
                "Alimentar",
                "Historial",
            ],
            key="selector_mas_movil",
            label_visibility="collapsed",
        )

        st.button(
            "Abrir sección →",
            key="abrir_herramienta_movil",
            use_container_width=True,
            on_click=ir_a_seccion_movil,
            args=(herramienta_movil,),
        )
# =====================================================
# ENCABEZADO PRINCIPAL
# =====================================================
st.markdown("""
<div class="hero">
    <div class="etiqueta">✦ INTELIGENCIA PARA TUS DATOS</div>
    <h1>Piensa en SQL.<br><span style="color:#2DE2C5;">Resuelve con inteligencia.</span></h1>
    <p>Aprende bases de datos, genera consultas, analiza código SQL y fortalece la seguridad de tus proyectos con un agente que combina conocimiento local e inteligencia artificial.</p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Consultas en esta sesión", len(st.session_state.historial))
with m2:
    st.metric("Motor local", "Python",
              help="Responde con los conocimientos programados en el proyecto.")
with m3:
    st.metric("IA de respaldo", "Gemini",
              help="Se utiliza cuando el flujo del agente decide recurrir a la IA.")
st.write("")

# =====================================================
# INICIO
# =====================================================
if seccion == "Inicio":
    st.markdown("## Tu espacio de trabajo")
    st.markdown("Elige una herramienta para empezar a trabajar con tus datos.")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="tarjeta"><div class="icono">📚</div><h3>Aprende SQL</h3><p>Comprende JOIN, SELECT, funciones, relaciones, transacciones y otros conceptos esenciales.</p></div>', unsafe_allow_html=True)
        st.write("")
        st.button("Explorar conceptos →", key="ir_aprender", use_container_width=True,
                  on_click=cambiar_seccion, args=("Aprender SQL",))
    with c2:
        st.markdown('<div class="tarjeta"><div class="icono">⚙️</div><h3>Genera consultas</h3><p>Describe lo que necesitas obtener de una base de datos y solicita una consulta SQL.</p></div>', unsafe_allow_html=True)
        st.write("")
        st.button("Crear una consulta →", key="ir_generar", use_container_width=True,
                  on_click=cambiar_seccion, args=("Generar consultas",))
    c3, c4 = st.columns(2, gap="large")
    with c3:
        st.markdown('<div class="tarjeta"><div class="icono">🔍</div><h3>Analiza tu SQL</h3><p>Solicita explicaciones, revisión de consultas y sugerencias para mejorar tu código.</p></div>', unsafe_allow_html=True)
        st.write("")
        st.button("Revisar código →", key="ir_revisar", use_container_width=True,
                  on_click=cambiar_seccion, args=("Revisar SQL",))
    with c4:
        st.markdown('<div class="tarjeta"><div class="icono">🛡️</div><h3>Seguridad de datos</h3><p>Aprende sobre inyección SQL, permisos, consultas parametrizadas y buenas prácticas.</p></div>', unsafe_allow_html=True)
        st.write("")
        st.button("Explorar seguridad →", key="ir_seguridad", use_container_width=True,
                  on_click=cambiar_seccion, args=("Seguridad SQL",))

    st.write("")
    st.markdown("### 💬 Pregunta rápida")
    ejemplos = ["¿Qué es un INNER JOIN?",
                "¿Qué es una clave primaria?", "¿Cómo prevenir SQL injection?"]
    e1, e2, e3 = st.columns(3)
    for columna, ejemplo, indice in [(e1, ejemplos[0], 1), (e2, ejemplos[1], 2), (e3, ejemplos[2], 3)]:
        with columna:
            if st.button(ejemplo, key=f"ejemplo_{indice}", use_container_width=True):
                st.session_state.pregunta = ejemplo
                st.session_state.seccion = "Consulta libre"
                st.rerun()

# =====================================================
# APRENDER SQL
# =====================================================
elif seccion == "Aprender SQL":
    st.markdown("## 📚 Centro de aprendizaje")
    st.write("Pregunta por un concepto y solicita una explicación práctica.")
    st.markdown("#### Temas sugeridos")
    st.markdown(
        "`SELECT` · `JOIN` · `GROUP BY` · `PRIMARY KEY` · `FOREIGN KEY` · `INDEX` · `TRANSACCIONES`")
    with st.form("form_aprender"):
        pregunta = st.text_area("¿Qué concepto quieres aprender?",
                                placeholder="Ejemplo: Explícame las diferencias entre INNER JOIN y LEFT JOIN.", height=130)
        enviar = st.form_submit_button(
            "📚 Explicar concepto", use_container_width=True)
    if enviar:
        consultar_agente(pregunta)
        st.rerun()
    mostrar_resultado()

# =====================================================
# GENERAR CONSULTAS
# =====================================================
elif seccion == "Generar consultas":
    st.markdown("## ⚙️ Generador SQL")
    st.write("Describe el resultado que deseas obtener.")
    with st.form("form_generar"):
        solicitud = st.text_area("Instrucciones para el agente",
                                 placeholder="Ejemplo: Genera una consulta para mostrar los clientes que hayan realizado más de tres pedidos.", height=150)
        generar = st.form_submit_button(
            "⚡ Generar SQL", use_container_width=True)
    if generar:
        consultar_agente(solicitud)
        st.rerun()
    mostrar_resultado()

# =====================================================
# REVISAR SQL
# =====================================================
elif seccion == "Revisar SQL":
    st.markdown("## 🔍 Analizador de consultas")
    st.write("Pega tu consulta y pide al agente que revise su funcionamiento.")
    with st.form("form_revisar"):
        codigo = st.text_area(
            "Tu código SQL", placeholder="SELECT nombre FROM usuarios WHERE id = 1;", height=200)
        instruccion = st.text_input(
            "¿Qué deseas revisar?", placeholder="Ej.: Explica la consulta y busca posibles errores.")
        revisar = st.form_submit_button(
            "🔎 Analizar consulta", use_container_width=True)
    if revisar:
        solicitud = (
            f"{instruccion.strip()}\n\nConsulta SQL:\n{codigo.strip()}"
            if instruccion.strip()
            else f"Revisa y explica esta consulta SQL:\n{codigo.strip()}"
        )
        consultar_agente(solicitud)
        st.rerun()
    mostrar_resultado()

# =====================================================
# SEGURIDAD SQL
# =====================================================
elif seccion == "Seguridad SQL":
    st.markdown("## 🛡️ Laboratorio de seguridad")
    st.write("Aprende a proteger tus bases de datos y aplicaciones.")
    st.markdown('<div class="tarjeta"><h3>🔐 Principios fundamentales</h3><p>Consultas parametrizadas, permisos mínimos, validación de entradas y manejo seguro de credenciales.</p></div>', unsafe_allow_html=True)
    st.write("")
    with st.form("form_seguridad"):
        pregunta = st.text_area("¿Qué aspecto de seguridad quieres investigar?",
                                placeholder="Ejemplo: ¿Cómo funciona SQL injection y cómo se previene?", height=130)
        consultar = st.form_submit_button(
            "🛡️ Consultar seguridad", use_container_width=True)
    if consultar:
        consultar_agente(pregunta)
        st.rerun()
    mostrar_resultado()

# =====================================================
# CONSULTA LIBRE
# =====================================================
elif seccion == "Consulta libre":
    st.markdown("## 💬 Conversa con tu agente")
    st.write("Escribe una pregunta sobre SQL, bases de datos o tu proyecto.")
    with st.form("form_libre"):
        pregunta = st.text_area("Tu mensaje", value=st.session_state.pregunta,
                                placeholder="Escribe aquí tu pregunta...", height=150)
        enviar = st.form_submit_button(
            "Enviar consulta →", use_container_width=True)
    if enviar:
        st.session_state.pregunta = ""
        consultar_agente(pregunta)
        st.rerun()
    mostrar_resultado()

# =====================================================
# ALIMENTAR CONOCIMIENTOS
# =====================================================
elif seccion == "Alimentar":
    st.markdown("## 🧠 Alimentar SQL Nexus")
    st.write("Añade conceptos y respuestas propias. Se guardarán en un archivo local y el agente los consultará antes de acudir a Gemini.")
    st.markdown('<div class="tarjeta"><h3>📌 ¿Cómo funciona?</h3><p>Escribe una palabra, concepto o pregunta que identifique el tema y la respuesta que quieres que SQL Nexus entregue. Si vuelves a guardar el mismo concepto, su respuesta se actualizará.</p></div>', unsafe_allow_html=True)
    st.write("")
    with st.form("form_alimentar", clear_on_submit=True):
        concepto_nuevo = st.text_input(
            "Concepto o pregunta clave", placeholder="Ej.: ¿Qué es una clave primaria?")
        respuesta_nueva = st.text_area("Respuesta que debe aprender el agente",
                                       placeholder="Escribe aquí la explicación que quieres guardar...", height=180)
        guardar = st.form_submit_button(
            "💾 Guardar conocimiento", use_container_width=True)
    if guardar:
        if not concepto_nuevo.strip() or not respuesta_nueva.strip():
            st.warning("Completa tanto el concepto como la respuesta.")
        else:
            try:
                estado_guardado = guardar_conocimiento(
                    concepto_nuevo, respuesta_nueva)
                if estado_guardado == "actualizado":
                    st.success(
                        "Conocimiento actualizado. SQL Nexus utilizará la nueva respuesta.")
                else:
                    st.success(
                        "Conocimiento guardado. SQL Nexus ya puede utilizarlo.")
                st.rerun()
            except Exception as error:  # pylint: disable=broad-exception-caught
                st.error(
                    "No fue posible guardar el conocimiento. "
                    "Revisa el error en la terminal de VS Code."
                )
                st.exception(error)

    st.divider()
    conocimientos_guardados = listar_conocimientos()
    st.markdown(
        f"### 📚 Conocimientos guardados ({len(conocimientos_guardados)})")
    if not conocimientos_guardados:
        st.info("Todavía no has añadido conocimientos personalizados.")
    else:
        # Corregido: solo hay un ciclo for y su contenido tiene la sangría correcta.
        for indice, elemento in enumerate(conocimientos_guardados):
            concepto_guardado = (
                elemento.get("pregunta")
                or elemento.get("concepto")
                or "Sin concepto"
            )
            with st.expander(f"{indice + 1}. {concepto_guardado}"):
                st.markdown(elemento.get("respuesta", ""))
                if st.button("🗑️ Eliminar este conocimiento", key=f"eliminar_conocimiento_{indice}"):
                    if eliminar_conocimiento(concepto_guardado):
                        st.success("Conocimiento eliminado.")
                        st.rerun()
                    else:
                        st.warning(
                            "No se encontró el conocimiento para eliminar.")

# =====================================================
# CONVERSACION POR VOZ
# =====================================================


elif seccion == "Conversación por voz":
    st.markdown("## 🎙️ Conversación por voz")
    st.write(
        "Habla en español y SQL Nexus procesará tu pregunta "
        "y preparará una respuesta hablada."
    )

    texto_voz = speech_to_text(
        language="es",
        just_once=True,
        key="microfono_sql_nexus",
    )

    if texto_voz:
        pregunta_voz = texto_voz.strip()

        if pregunta_voz:
            st.markdown("### 🗣️ Pregunta reconocida")
            st.write(pregunta_voz)

            try:
                with st.spinner("SQL Nexus está pensando..."):
                    consultar_agente(pregunta_voz)

                if st.session_state.historial:
                    registro = st.session_state.historial[-1]

                    ultima_respuesta = registro.get("respuesta", "")
                    origen_respuesta = registro.get(
                        "origen", "No especificado"
                    )
                    herramienta_respuesta = registro.get(
                        "herramienta", "No especificada"
                    )

                    if ultima_respuesta:
                        st.markdown("### 🤖 Respuesta de SQL Nexus")
                        st.markdown(ultima_respuesta)

                        # Traducir los nombres técnicos a etiquetas visibles
                        origen_mostrado = {
                            "python": "Conocimientos locales de Python",
                            "gemini": "Inteligencia artificial Gemini",
                        }

                        herramienta_mostrada = {
                            "ensenar": "Enseñar",
                            "analizar_proyecto": "Analizar proyecto",
                            "generar_arquitectura": "Generar arquitectura",
                            "validar_arquitectura": "Validar arquitectura",
                            "normalizar_componentes": "Normalizar componentes",
                        }

                        origen_texto = origen_mostrado.get(
                            str(origen_respuesta).lower(),
                            str(origen_respuesta),
                        )

                        herramienta_texto = herramienta_mostrada.get(
                            str(herramienta_respuesta).lower(),
                            str(herramienta_respuesta).replace(
                                "_", " "
                            ).capitalize(),
                        )

                        # Traducir los nombres técnicos a etiquetas visibles
                        origen_mostrado = {
                            "python": "Conocimientos locales de Python",
                            "gemini": "Inteligencia artificial Gemini",
                        }

                        herramienta_mostrada = {
                            "ensenar": "Enseñar",
                            "enseñar": "Enseñar",
                            "analizar_proyecto": "Analizar proyecto",
                            "generar_arquitectura": "Generar arquitectura",
                            "validar_arquitectura": "Validar arquitectura",
                            "normalizar_componentes": "Normalizar componentes",
                        }

                        origen_texto = origen_mostrado.get(
                            str(origen_respuesta).strip().lower(),
                            str(origen_respuesta),
                        )

                        herramienta_texto = herramienta_mostrada.get(
                            str(herramienta_respuesta).strip().lower(),
                            str(herramienta_respuesta).replace(
                                "_", " "
                            ).capitalize(),
                        )

                        st.caption(f"📚 Origen: {origen_texto}")
                        st.caption(f"🔧 Herramienta: {herramienta_texto}")

                        with st.spinner("Preparando la respuesta hablada..."):
                            audio_respuesta = convertir_texto_a_voz(
                                ultima_respuesta
                            )

                        if audio_respuesta:
                            st.audio(
                                audio_respuesta,
                                format="audio/mp3",
                                autoplay=True,
                            )
                        else:
                            st.warning(
                                "No se pudo generar el audio de la respuesta."
                            )
                    else:
                        st.warning(
                            "El agente no devolvió una respuesta para reproducir."
                        )
                else:
                    st.warning("Todavía no hay respuestas en el historial.")

            except Exception as error:
                st.error("No se pudo completar la conversación por voz.")
                st.exception(error)


# =====================================================
# HISTORIAL
# =====================================================
elif seccion == "Historial":
    st.markdown("## 🕘 Historial de esta sesión")
    if not st.session_state.historial:
        st.info("Todavía no hay consultas en esta sesión.")
    else:
        for numero, elemento in enumerate(reversed(st.session_state.historial), start=1):
            with st.expander(f"{numero}. {elemento['pregunta'][:75]}"):
                st.markdown("**Respuesta:**")
                st.markdown(elemento["respuesta"])
                st.caption(
                    f"Origen: {elemento['origen']} · Herramienta: {elemento['herramienta']}")

# =====================================================
# DESPLAZAMIENTO AUTOMATICO AL CONTENIDO EN MOVILES
# =====================================================
if st.session_state.get("desplazar_seccion_movil", False):
    titulos_seccion = {
        "Inicio": "Tu espacio de trabajo",
        "Aprender SQL": "Centro de aprendizaje",
        "Generar consultas": "Generador SQL",
        "Revisar SQL": "Analizador de consultas",
        "Seguridad SQL": "Laboratorio de seguridad",
        "Consulta libre": "Conversa con tu agente",
        "Alimentar": "Alimentar SQL Nexus",
        "Conversación por voz": "Conversación por voz",
        "Historial": "Historial de esta sesión",
    }
    titulo_objetivo = titulos_seccion.get(st.session_state.seccion, "")
    st.components.v1.html(
        f"""
        <script>
        const tituloObjetivo = {json.dumps(titulo_objetivo)};
        window.setTimeout(() => {{
            try {{
                const documento = window.parent.document;
                const encabezados = documento.querySelectorAll(
                    '[data-testid="stMainBlockContainer"] h1, '
                    + '[data-testid="stMainBlockContainer"] h2, '
                    + '[data-testid="stMainBlockContainer"] h3'
                );
                for (const encabezado of encabezados) {{
                    if (encabezado.innerText.includes(tituloObjetivo)) {{
                        encabezado.scrollIntoView({{
                            behavior: "smooth",
                            block: "start"
                        }});
                        break;
                    }}
                }}
            }} catch (error) {{
                console.warn("No se pudo desplazar a la sección seleccionada.", error);
            }}
        }}, 250);
        </script>
        """,
        height=0,
    )
    st.session_state.desplazar_seccion_movil = False


# =====================================================
# PIE DE PAGINA
# =====================================================
st.divider()
st.markdown("""
<div style="text-align:center;padding:12px;color:#CBD5E1;">
    <strong>SQL <span style="color:#2DE2C5;">NEXUS</span></strong><br>
    <span style="font-size:12px;">Agente experto en SQL · Python + Gemini</span>
</div>
""", unsafe_allow_html=True)
