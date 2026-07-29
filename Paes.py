"""
SIMULADOR PAES PROFESIONAL - VERSIÓN 5.0 CON IA
Con todas las funciones: login, preguntas, cronómetro, resultados, progreso, 
carga de Excel, dashboard, metas, logros, notificaciones y ANÁLISIS CON IA
"""

import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import datetime
import os
import random
import time
import json
from pathlib import Path
import io

# ============ CONFIGURACIÓN INICIAL ============
st.set_page_config(
    page_title="Simulador PAES 2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ ESTILOS CSS MEJORADOS ============
def load_css():
    """Carga estilos CSS mejorados"""
    
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    """, unsafe_allow_html=True)
    
    css_path = Path("assets/styles.css")
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .header-container {
                background: linear-gradient(135deg, #1a237e, #283593);
                padding: 1rem 2rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: white;
            }
            .header-title { font-size: 1.8rem; font-weight: 700; margin: 0; }
            .header-user span {
                background: rgba(255,255,255,0.2);
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.9rem;
            }
            .card {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                margin-bottom: 1rem;
                transition: all 0.3s ease;
            }
            .card:hover {
                box-shadow: 0 4px 16px rgba(0,0,0,0.12);
                transform: translateY(-2px);
            }
            .card-principal {
                background: linear-gradient(135deg, #ffffff, #e8eaf6);
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(26,35,126,0.15);
                margin-bottom: 1rem;
                border: 2px solid #1a237e;
            }
            .question-container {
                background: white;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                margin: 1rem 0;
                border-left: 4px solid #1a237e;
            }
            .timer-container {
                background: #1a237e;
                color: white;
                padding: 0.8rem 1.5rem;
                border-radius: 30px;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 1.3rem;
                font-weight: 700;
                font-family: 'Courier New', monospace;
            }
            .login-container {
                max-width: 450px;
                margin: 0 auto;
                padding: 2rem;
                background: white;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                margin-top: 2rem;
            }
            .main-title { font-size: 2.5rem; font-weight: 700; color: #1a237e; text-align: center; }
            .sub-title { font-size: 1.2rem; color: #455a64; text-align: center; margin-bottom: 2rem; }
            .result-card {
                background: linear-gradient(135deg, #1a237e, #283593);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                margin: 1rem 0;
            }
            .result-card .big-number { font-size: 3.5rem; font-weight: 700; }
            .badge-principal {
                background: #1a237e;
                color: white;
                padding: 0.2rem 0.8rem;
                border-radius: 12px;
                font-size: 0.7rem;
                font-weight: 600;
            }
            .badge-disponible {
                background: #4caf50;
                color: white;
                padding: 0.2rem 0.8rem;
                border-radius: 12px;
                font-size: 0.7rem;
                font-weight: 600;
            }
            .badge-sin-preguntas {
                background: #999;
                color: white;
                padding: 0.2rem 0.8rem;
                border-radius: 12px;
                font-size: 0.7rem;
                font-weight: 600;
            }
            .footer {
                text-align: center;
                color: #78909c;
                padding: 2rem 0;
                font-size: 0.9rem;
                border-top: 1px solid #e0e0e0;
                margin-top: 2rem;
            }
            @media (max-width: 768px) {
                .header-title { font-size: 1.2rem; }
                .header-container { flex-direction: column; gap: 0.5rem; }
                .main-title { font-size: 1.8rem; }
            }
        </style>
        """, unsafe_allow_html=True)

# ============ BASE DE DATOS ============
def init_database():
    db_path = "simulador_paes.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            nombre_completo TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_acceso TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS intentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tipo TEXT CHECK(tipo IN ('practica', 'oficial')),
            asignatura TEXT,
            puntaje_total INTEGER,
            respuestas_correctas INTEGER,
            respuestas_incorrectas INTEGER,
            respuestas_omitidas INTEGER,
            tiempo_utilizado INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS respuestas_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intento_id INTEGER,
            pregunta_id INTEGER,
            respuesta_usuario TEXT,
            es_correcta BOOLEAN,
            tiempo_por_pregunta INTEGER,
            FOREIGN KEY (intento_id) REFERENCES intentos(id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS preguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asignatura TEXT NOT NULL,
            numero INTEGER,
            texto TEXT NOT NULL,
            opcion_a TEXT NOT NULL,
            opcion_b TEXT NOT NULL,
            opcion_c TEXT NOT NULL,
            opcion_d TEXT NOT NULL,
            opcion_e TEXT,
            respuesta_correcta TEXT NOT NULL,
            dificultad TEXT CHECK(dificultad IN ('facil', 'media', 'dificil')),
            imagen_url TEXT,
            formula_latex TEXT,
            explicacion TEXT
        )
    ''')
    
    c.execute("SELECT COUNT(*) FROM preguntas")
    count = c.fetchone()[0]
    
    if count == 0:
        insertar_preguntas_ejemplo(c)
    
    conn.commit()
    conn.close()
    return db_path

def insertar_preguntas_ejemplo(cursor):
    preguntas_ejemplo = [
        {
            "asignatura": "Competencia Lectora",
            "numero": 1,
            "texto": "¿Cuál es el propósito principal del texto?",
            "opcion_a": "Informar sobre un descubrimiento",
            "opcion_b": "Convencer al lector sobre una idea",
            "opcion_c": "Entretener al público lector",
            "opcion_d": "Describir un proceso histórico",
            "opcion_e": "Analizar una situación social",
            "respuesta_correcta": "A",
            "dificultad": "media",
            "explicacion": "El texto tiene como objetivo principal informar sobre el descubrimiento científico."
        },
        {
            "asignatura": "Matemática 1",
            "numero": 1,
            "texto": "Si 2x + 5 = 13, ¿cuál es el valor de x?",
            "opcion_a": "2",
            "opcion_b": "3",
            "opcion_c": "4",
            "opcion_d": "5",
            "opcion_e": "6",
            "respuesta_correcta": "C",
            "dificultad": "facil",
            "explicacion": "2x + 5 = 13 → 2x = 8 → x = 4"
        }
    ]
    
    for p in preguntas_ejemplo:
        cursor.execute('''
            INSERT INTO preguntas 
            (asignatura, numero, texto, opcion_a, opcion_b, opcion_c, opcion_d, opcion_e, 
             respuesta_correcta, dificultad, formula_latex, explicacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            p["asignatura"],
            p["numero"],
            p["texto"],
            p["opcion_a"],
            p["opcion_b"],
            p["opcion_c"],
            p["opcion_d"],
            p.get("opcion_e", ""),
            p["respuesta_correcta"],
            p["dificultad"],
            p.get("formula_latex", ""),
            p.get("explicacion", "")
        ))

# ============ SISTEMA DE LOGIN ============
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login(username, password):
    conn = sqlite3.connect("simulador_paes.db")
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute(
        "SELECT id, username, nombre_completo FROM usuarios WHERE username = ? AND password = ?",
        (username, password_hash)
    )
    user = c.fetchone()
    conn.close()
    return user

def registrar_usuario(username, password, email, nombre_completo):
    try:
        conn = sqlite3.connect("simulador_paes.db")
        c = conn.cursor()
        password_hash = hash_password(password)
        c.execute(
            "INSERT INTO usuarios (username, password, email, nombre_completo) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, nombre_completo)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def actualizar_ultimo_acceso(usuario_id):
    conn = sqlite3.connect("simulador_paes.db")
    c = conn.cursor()
    c.execute(
        "UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id = ?",
        (usuario_id,)
    )
    conn.commit()
    conn.close()

# ============ CARGA DE PREGUNTAS ============
def cargar_preguntas(asignatura, cantidad=None):
    conn = sqlite3.connect("simulador_paes.db")
    
    query = "SELECT * FROM preguntas WHERE asignatura = ?"
    params = [asignatura]
    
    if cantidad and cantidad > 0:
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(cantidad)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    preguntas = []
    for _, row in df.iterrows():
        opciones = []
        for letra in ['A', 'B', 'C', 'D', 'E']:
            col = f"opcion_{letra.lower()}"
            if col in row and row[col] and pd.notna(row[col]) and str(row[col]).strip():
                opciones.append(str(row[col]).strip())
        
        preguntas.append({
            "id": row["id"],
            "numero": row["numero"] if pd.notna(row["numero"]) else len(preguntas) + 1,
            "texto": row["texto"],
            "opciones": opciones,
            "correcta": row["respuesta_correcta"],
            "dificultad": row["dificultad"] if pd.notna(row["dificultad"]) else "media",
            "imagen": row["imagen_url"] if pd.notna(row["imagen_url"]) else None,
            "formula": row["formula_latex"] if pd.notna(row["formula_latex"]) else None,
            "explicacion": row["explicacion"] if pd.notna(row["explicacion"]) else None,
            "asignatura": row["asignatura"]
        })
    
    return preguntas

def contar_preguntas(asignatura=None):
    conn = sqlite3.connect("simulador_paes.db")
    c = conn.cursor()
    
    if asignatura:
        c.execute("SELECT COUNT(*) FROM preguntas WHERE asignatura = ?", (asignatura,))
    else:
        c.execute("SELECT COUNT(*) FROM preguntas")
    
    count = c.fetchone()[0]
    conn.close()
    return count

def obtener_asignaturas():
    conn = sqlite3.connect("simulador_paes.db")
    c = conn.cursor()
    c.execute("SELECT DISTINCT asignatura FROM preguntas ORDER BY asignatura")
    asignaturas = [row[0] for row in c.fetchall()]
    conn.close()
    return asignaturas

# ============ CRONÓMETRO ============
class Cronometro:
    @staticmethod
    def iniciar():
        st.session_state.tiempo_inicio = time.time()
        st.session_state.tiempo_pausa = 0
    
    @staticmethod
    def obtener_tiempo():
        if st.session_state.tiempo_inicio is None:
            return 0
        return int(time.time() - st.session_state.tiempo_inicio - st.session_state.tiempo_pausa)
    
    @staticmethod
    def formatear_tiempo(segundos):
        minutos = segundos // 60
        segundos_restantes = segundos % 60
        return f"{minutos:02d}:{segundos_restantes:02d}"
    
    @staticmethod
    def mostrar_timer():
        if not st.session_state.simulacion_activa:
            return
        
        tiempo = Cronometro.obtener_tiempo()
        tiempo_formateado = Cronometro.formatear_tiempo(tiempo)
        
        limites = {
            "Competencia Lectora": 70,
            "Matemática 1": 70,
            "Matemática 2": 70,
            "Ciencias": 80,
            "Historia y Ciencias Sociales": 70,
            "Inglés": 50
        }
        
        asignatura = st.session_state.get("asignatura_seleccionada", "")
        limite = limites.get(asignatura, 70)
        
        progreso_tiempo = min(tiempo / (limite * 60), 1) * 100
        tiempo_restante = limite * 60 - tiempo
        
        if tiempo_restante < 300:
            color = "#f44336"
            warning_class = "timer-warning"
        elif tiempo_restante < 600:
            color = "#ff9800"
            warning_class = ""
        else:
            color = "#1a237e"
            warning_class = ""
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem; justify-content: center; margin: 1rem 0;">
            <div class="timer-container {warning_class}" style="background: {color};">
                <i class="fas fa-clock"></i> {tiempo_formateado}
            </div>
            <div style="font-size: 0.9rem; color: #666;">
                <i class="fas fa-hourglass-half"></i> Límite: {limite} min
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.progress(progreso_tiempo / 100)
        
        if st.session_state.tipo_simulacion == "oficial" and tiempo >= limite * 60:
            st.warning("⏰ ¡El tiempo ha terminado!")
            if st.button("Finalizar automáticamente"):
                st.session_state.pagina_actual = "resultados"
                st.rerun()

# ============ FUNCIONES DE INTERFAZ ============
def mostrar_login():
    load_css()
    
    # Título
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h1 style="font-size: 2.8rem; font-weight: 700; color: #1a237e; margin: 0;">📚 Simulador PAES 2026</h1>
        <p style="font-size: 1.1rem; color: #455a64; margin-top: 0.2rem;">Prepara tu futuro con la mejor herramienta de simulación</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mensaje para Javier
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a237e, #283593); 
                padding: 0.8rem 1.5rem; 
                border-radius: 15px; 
                margin: 0 auto 1.5rem auto;
                max-width: 650px;
                box-shadow: 0 4px 16px rgba(26, 35, 126, 0.3);
                border: 2px solid #ff6f00;
                text-align: center;">
        <p style="color: white; font-size: 1.1rem; font-weight: 600; margin: 0;">
            🚀 Javier, tu futuro comienza aquí. ¡Dale con todo! 💪
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login container
    st.markdown("""
    <div style="max-width: 450px; margin: 0 auto; padding: 2rem; background: white; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
        <h2 style="font-size: 2rem; font-weight: 700; color: #1a237e; text-align: center; margin-bottom: 0.5rem;">🔐 Iniciar Sesión</h2>
        <p style="text-align: center; color: #78909c; margin-bottom: 2rem;">Accede a tu cuenta para comenzar</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs usando Streamlit nativo
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_login = st.form_submit_button("Ingresar", use_container_width=True)
            
            with col2:
                demo_clicked = st.form_submit_button("Modo Demo", use_container_width=True)
            
            if submit_login:
                if username and password:
                    user = verificar_login(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.username = user[1]
                        st.session_state.nombre_completo = user[2]
                        actualizar_ultimo_acceso(user[0])
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                else:
                    st.warning("⚠️ Por favor completa todos los campos")
            
            if demo_clicked:
                st.session_state.logged_in = True
                st.session_state.user_id = 999
                st.session_state.username = "demo"
                st.session_state.nombre_completo = "Usuario Demo"
                st.session_state.modo_demo = True
                st.rerun()
    
    with tab2:
        with st.form("register_form"):
            reg_username = st.text_input("Usuario", placeholder="Elige un nombre de usuario")
            reg_password = st.text_input("Contraseña", type="password", placeholder="Crea una contraseña segura")
            reg_email = st.text_input("Email", placeholder="tu@email.com")
            reg_nombre = st.text_input("Nombre completo", placeholder="Tu nombre completo")
            
            submit_register = st.form_submit_button("Registrarse", use_container_width=True)
            
            if submit_register:
                if all([reg_username, reg_password, reg_email, reg_nombre]):
                    if len(reg_password) >= 6:
                        if registrar_usuario(reg_username, reg_password, reg_email, reg_nombre):
                            st.success("✅ ¡Registro exitoso! Ahora inicia sesión")
                        else:
                            st.error("❌ El usuario ya existe")
                    else:
                        st.warning("⚠️ La contraseña debe tener al menos 6 caracteres")
                else:
                    st.warning("⚠️ Por favor completa todos los campos")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #78909c; padding: 2rem 0; font-size: 0.9rem; border-top: 1px solid #e0e0e0; margin-top: 2rem;">
        <p>Simulador PAES 2026 © Todos los derechos reservados</p>
        <p style="font-size: 0.9rem; color: #1a237e; font-weight: 600;">
            🚀 Desarrollado por <strong>Zamky_Zumbao</strong> | ❤️ Para Javier - ¡El futuro te espera! 💪
        </p>
        <p style="font-size: 0.7rem; color: #b0bec5; margin-top: 0.3rem;">
            Versión 5.0.0 - PAES 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_menu_principal():
    load_css()
    
    try:
        from notificaciones import mostrar_notificaciones
        mostrar_notificaciones()
    except:
        pass
    
    st.markdown(f"""
    <div class="header-container">
        <div>
            <div class="header-title"><span class="emoji">📚</span> Simulador PAES 2026</div>
            <div style="font-size: 0.9rem; opacity: 0.8;"><i class="fas fa-arrow-right"></i> Prepara tu futuro</div>
        </div>
        <div class="header-user">
            <span><i class="fas fa-user"></i> {st.session_state.nombre_completo}</span>
        </div>
    </div>
    
    <div style="background: linear-gradient(135deg, #1a237e, #283593); 
                padding: 0.8rem 1.5rem; 
                border-radius: 15px; 
                margin: 1rem 0 1.5rem 0;
                box-shadow: 0 4px 16px rgba(26, 35, 126, 0.3);
                border: 2px solid #ff6f00;
                text-align: center;">
        <p style="color: white; font-size: 1.1rem; font-weight: 600; margin: 0;">
            🚀 Javier, tu futuro comienza aquí. ¡Dale con todo! 💪
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    total_preguntas = contar_preguntas()
    if total_preguntas > 0:
        st.info(f"📊 Base de datos: {total_preguntas} preguntas disponibles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <div style="font-size: 3rem;">📝</div>
            <h3>Práctica</h3>
            <p>Entrena por asignatura con todas las preguntas</p>
            <p style="font-size: 0.9rem; color: #78909c;"><i class="fas fa-infinity"></i> Sin límite de tiempo</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Comenzar Práctica", key="btn_practica", use_container_width=True):
            st.session_state.pagina_actual = "seleccion_practica"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <div style="font-size: 3rem;">🏆</div>
            <h3>Simulación Oficial</h3>
            <p>Experiencia completa tipo PAES</p>
            <p style="font-size: 0.9rem; color: #78909c;"><i class="fas fa-clock"></i> Con cronómetro y puntaje DEMRE</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Simulación Oficial", key="btn_oficial", use_container_width=True):
            st.session_state.pagina_actual = "seleccion_oficial"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <div style="font-size: 3rem;">📊</div>
            <h3>Mi Progreso</h3>
            <p>Estadísticas detalladas de tu rendimiento</p>
            <p style="font-size: 0.9rem; color: #78909c;"><i class="fas fa-chart-line"></i> Historial y gráficos</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Progreso", key="btn_progreso", use_container_width=True):
            st.session_state.pagina_actual = "progreso"
            st.rerun()
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Dashboard Avanzado", use_container_width=True):
            st.session_state.pagina_actual = "dashboard"
            st.rerun()
    
    with col2:
        if st.button("🎯 Metas y Logros", use_container_width=True):
            st.session_state.pagina_actual = "metas"
            st.rerun()
    
    with col3:
        if st.button("🧠 Análisis con IA", use_container_width=True):
            st.session_state.pagina_actual = "analisis_ia"
            st.rerun()
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Cargar preguntas desde Excel", use_container_width=True):
            st.session_state.pagina_actual = "carga_excel"
            st.rerun()
    
    with col2:
        if st.button("📋 Ver todas las asignaturas", use_container_width=True):
            asignaturas = obtener_asignaturas()
            if asignaturas:
                st.info("Asignaturas disponibles:\n" + "\n".join([f"• {a}" for a in asignaturas]))
            else:
                st.warning("No hay asignaturas cargadas")
    
    with col3:
        if st.button("🔄 Reiniciar sesión", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📈 Tu progreso general")
    
    try:
        conn = sqlite3.connect("simulador_paes.db")
        if not st.session_state.modo_demo:
            c = conn.cursor()
            c.execute("""
                SELECT 
                    COUNT(*) as total_intentos,
                    AVG(puntaje_total) as promedio,
                    MAX(puntaje_total) as mejor_puntaje,
                    COUNT(CASE WHEN tipo = 'oficial' THEN 1 END) as oficiales
                FROM intentos 
                WHERE usuario_id = ?
            """, (st.session_state.user_id,))
            stats = c.fetchone()
            
            if stats and stats[0] > 0:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Intentos", stats[0])
                with col2:
                    st.metric("Promedio DEMRE", f"{stats[1]:.0f}" if stats[1] else "N/A")
                with col3:
                    st.metric("Mejor Puntaje", stats[2] if stats[2] else "N/A")
                with col4:
                    st.metric("Simulaciones Oficiales", stats[3])
            else:
                st.info("📝 Aún no has completado ninguna simulación. ¡Comienza ahora!")
        conn.close()
    except Exception as e:
        pass
    
    st.markdown("""
    <div class="footer">
        <p>Simulador PAES 2026 © Todos los derechos reservados</p>
        <p style="font-size: 0.9rem; color: #1a237e; font-weight: 600;">
            🚀 Desarrollado por <strong>Zamky_Zumbao</strong> | ❤️ Para Javier - ¡El futuro te espera! 💪
        </p>
        <p style="font-size: 0.7rem; color: #b0bec5; margin-top: 0.3rem;">
            Versión 5.0.0 - PAES 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_seleccion_asignatura(tipo):
    load_css()
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 2rem;">
        <h1 class="main-title" style="flex: 1; text-align: center; margin: 0;">
            { "📝" if tipo == "practica" else "🏆" } { "Práctica" if tipo == "practica" else "Simulación Oficial" }
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Volver al menú principal"):
        st.session_state.pagina_actual = "inicio"
        st.rerun()
    
    st.markdown("### Selecciona la asignatura")
    
    asignaturas_db = obtener_asignaturas()
    
    if not asignaturas_db:
        asignaturas_db = [
            "Competencia Lectora",
            "Matemática 1",
            "Matemática 2",
            "Ciencias",
            "Historia y Ciencias Sociales",
            "Inglés"
        ]
    
    orden_prioridad = [
        "Matemática 1",
        "Competencia Lectora", 
        "Historia y Ciencias Sociales",
        "Matemática 2",
        "Ciencias",
        "Inglés"
    ]
    
    asignaturas_ordenadas = []
    for asignatura in orden_prioridad:
        if asignatura in asignaturas_db:
            asignaturas_ordenadas.append(asignatura)
    for asignatura in asignaturas_db:
        if asignatura not in asignaturas_ordenadas:
            asignaturas_ordenadas.append(asignatura)
    
    if not asignaturas_ordenadas:
        asignaturas_ordenadas = orden_prioridad
    
    pruebas_principales = ["Matemática 1", "Competencia Lectora", "Historia y Ciencias Sociales", "Matemática 2"]
    
    iconos = {
        "Matemática 1": "📐",
        "Matemática 2": "📊",
        "Competencia Lectora": "📖",
        "Historia y Ciencias Sociales": "📜",
        "Ciencias": "🔬",
        "Inglés": "🌍"
    }
    colores = {
        "Matemática 1": "#4caf50",
        "Matemática 2": "#ff9800",
        "Competencia Lectora": "#2196f3",
        "Historia y Ciencias Sociales": "#f44336",
        "Ciencias": "#9c27b0",
        "Inglés": "#00bcd4"
    }
    
    cols = st.columns(3)
    
    for idx, asignatura in enumerate(asignaturas_ordenadas):
        with cols[idx % 3]:
            icono = iconos.get(asignatura, "📚")
            color = colores.get(asignatura, "#1a237e")
            cantidad = contar_preguntas(asignatura)
            es_principal = asignatura in pruebas_principales
            
            if cantidad > 0:
                card_class = "card-principal" if es_principal else "card"
                badge = "🎯 Principal" if es_principal else "✅ Disponible"
                badge_class = "badge-principal" if es_principal else "badge-disponible"
                
                st.markdown(f"""
                <div class="{card_class}" style="text-align: center; border-top: 4px solid {color};">
                    <div style="font-size: 3rem;">{icono}</div>
                    <h3>{asignatura}</h3>
                    <p style="color: #78909c; font-size: 0.9rem;">{cantidad} preguntas</p>
                    <span class="{badge_class}">{badge}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Comenzar {asignatura}", key=f"sel_{asignatura}_{tipo}", use_container_width=True):
                    st.session_state.asignatura_seleccionada = asignatura
                    st.session_state.tipo_simulacion = tipo
                    st.session_state.pagina_actual = "simulacion"
                    st.session_state.preguntas_actuales = None
                    st.session_state.tiempo_inicio = None
                    st.rerun()
            else:
                st.markdown(f"""
                <div class="card-disabled" style="text-align: center; border-top: 4px solid #ddd;">
                    <div style="font-size: 3rem; opacity: 0.5;">{icono}</div>
                    <h3 style="opacity: 0.5;">{asignatura}</h3>
                    <p style="color: #999; font-size: 0.9rem;">Sin preguntas</p>
                    <span class="badge-sin-preguntas">⚠️ No disponible</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.warning("⚠️ Sin preguntas cargadas")
    
    st.markdown("---")
    total_preguntas = contar_preguntas()
    st.info(f"📊 Total de preguntas disponibles: {total_preguntas}")
    
    st.markdown("""
    <div class="footer">
        <p>Simulador PAES 2026 © Todos los derechos reservados</p>
        <p style="font-size: 0.9rem; color: #1a237e; font-weight: 600;">
            🚀 Desarrollado por <strong>Zamky_Zumbao</strong> | ❤️ Para Javier - ¡El futuro te espera! 💪
        </p>
        <p style="font-size: 0.7rem; color: #b0bec5; margin-top: 0.3rem;">
            Versión 5.0.0 - PAES 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============ FUNCIONES RESTANTES ============
def mostrar_simulacion():
    load_css()
    
    if not st.session_state.preguntas_actuales:
        st.error("❌ No hay preguntas disponibles para esta asignatura.")
        if st.button("Volver al menú principal"):
            st.session_state.pagina_actual = "inicio"
            st.rerun()
        return
    
    st.markdown(f"""
    <div class="header-container">
        <div>
            <div class="header-title"><span class="emoji">📚</span> {st.session_state.asignatura_seleccionada}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">
                <i class="fas fa-arrow-right"></i> {st.session_state.tipo_simulacion.upper()}
            </div>
        </div>
        <div class="header-user">
            <span><i class="fas fa-user"></i> {st.session_state.nombre_completo}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.tiempo_inicio is None:
        Cronometro.iniciar()
    
    Cronometro.mostrar_timer()
    
    if "preguntas_marcadas" not in st.session_state:
        st.session_state.preguntas_marcadas = set()
    
    total = len(st.session_state.preguntas_actuales)
    idx = st.session_state.indice_pregunta
    pregunta = st.session_state.preguntas_actuales[idx]
    
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2><i class="fas fa-chart-pie"></i> Panel de Control</h2>
        </div>
        """, unsafe_allow_html=True)
        
        respondidas = len(st.session_state.respuestas_usuario)
        st.markdown(f"""
        <div class="sidebar-stats">
            <div class="number">{respondidas}/{total}</div>
            <div class="label">Preguntas Respondidas</div>
            <div style="margin-top: 0.5rem;">
                <span style="background: #4caf50; color: white; padding: 0.2rem 0.8rem; border-radius: 12px; font-size: 0.8rem;">
                    <i class="fas fa-check"></i> {len([r for r in st.session_state.respuestas_usuario.values() if r])}
                </span>
                <span style="background: #666; color: white; padding: 0.2rem 0.8rem; border-radius: 12px; font-size: 0.8rem; margin-left: 0.3rem;">
                    <i class="fas fa-square"></i> {total - respondidas}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📌 Navegación Rápida")
        st.info(f"Total: {total} preguntas")
        
        with st.container():
            for i, p in enumerate(st.session_state.preguntas_actuales):
                if i % 5 == 0:
                    cols = st.columns(5)
                
                with cols[i % 5]:
                    estado = "unanswered"
                    if i == idx:
                        estado = "current"
                    if p["id"] in st.session_state.respuestas_usuario:
                        if st.session_state.respuestas_usuario[p["id"]] == p["correcta"]:
                            estado = "answered"
                        else:
                            estado = "incorrect"
                    if p["id"] in st.session_state.preguntas_marcadas:
                        estado = "marked"
                    
                    color_map = {
                        "unanswered": "white",
                        "current": "#1a237e",
                        "answered": "#4caf50",
                        "incorrect": "#f44336",
                        "marked": "#ff9800"
                    }
                    text_color = "white" if estado != "unanswered" else "#666"
                    
                    if st.button(str(i + 1), key=f"nav_{i}", use_container_width=True):
                        st.session_state.indice_pregunta = i
                        st.rerun()
                    
                    st.markdown(f"""
                    <style>
                        div[data-testid="column"]:nth-child({i % 5 + 1}) div.stButton > button {{
                            background: {color_map[estado]} !important;
                            color: {text_color} !important;
                            border-color: {'#1a237e' if estado == 'current' else color_map[estado]} !important;
                            border-width: {'3px' if estado == 'current' else '2px'} !important;
                            font-weight: bold !important;
                            padding: 0.5rem 0 !important;
                            min-height: 40px !important;
                            font-size: 0.8rem !important;
                        }}
                        div[data-testid="column"]:nth-child({i % 5 + 1}) div.stButton > button:hover {{
                            transform: scale(1.05) !important;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
                        }}
                    </style>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🏁 Finalizar Simulación", use_container_width=True, type="primary"):
            st.session_state.pagina_actual = "resultados"
            st.rerun()
    
    st.markdown(f"""
    <div class="question-container">
        <div class="question-header">
            <span class="question-number"><i class="fas fa-question-circle"></i> Pregunta {idx + 1} de {total}</span>
            <span class="question-tag">
                {pregunta.get('dificultad', 'media').upper()}
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    if pregunta.get("imagen"):
        st.image(pregunta["imagen"], use_container_width=True)
    
    if pregunta.get("formula"):
        st.markdown(f"""
        <div class="question-formula">
            {pregunta["formula"]}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="question-text">
        {pregunta["texto"]}
    </div>
    """, unsafe_allow_html=True)
    
    opciones_letras = ["A", "B", "C", "D", "E"]
    respuesta_actual = st.session_state.respuestas_usuario.get(pregunta["id"])
    
    for opcion_idx, opcion_texto in enumerate(pregunta["opciones"]):
        letra = opciones_letras[opcion_idx]
        estilo = "primary" if respuesta_actual == letra else "secondary"
        
        if st.button(f"{letra}. {opcion_texto}", key=f"opt_{pregunta['id']}_{letra}", use_container_width=True, type=estilo):
            st.session_state.respuestas_usuario[pregunta["id"]] = letra
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if idx > 0:
            if st.button("⬅ Anterior", use_container_width=True):
                st.session_state.indice_pregunta -= 1
                st.rerun()
    
    with col2:
        marcada = pregunta["id"] in st.session_state.preguntas_marcadas
        label = "📌 Desmarcar" if marcada else "📌 Marcar"
        if st.button(label, use_container_width=True):
            if marcada:
                st.session_state.preguntas_marcadas.remove(pregunta["id"])
            else:
                st.session_state.preguntas_marcadas.add(pregunta["id"])
            st.rerun()
    
    with col4:
        if idx < total - 1:
            if st.button("Siguiente ➡", use_container_width=True):
                st.session_state.indice_pregunta += 1
                st.rerun()
    
    with col5:
        if pregunta["id"] in st.session_state.respuestas_usuario:
            if st.button("🗑️ Limpiar", use_container_width=True):
                del st.session_state.respuestas_usuario[pregunta["id"]]
                st.rerun()
    
    st.markdown("""
    <div class="footer">
        <p>Simulador PAES 2026 © Todos los derechos reservados</p>
        <p style="font-size: 0.9rem; color: #1a237e; font-weight: 600;">
            Desarrollado por <strong>Zamky_Zumbao</strong> 💪
        </p>
        <p style="font-size: 0.7rem; color: #b0bec5; margin-top: 0.3rem;">
            Versión 5.0.0 - PAES 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_resultados():
    load_css()
    
    st.markdown("""
    <h1 class="main-title">📊 Resultados</h1>
    <p class="sub-title">Revisa tu desempeño en esta simulación</p>
    """, unsafe_allow_html=True)
    
    if st.button("← Volver al menú principal"):
        st.session_state.pagina_actual = "inicio"
        st.session_state.preguntas_actuales = None
        st.session_state.respuestas_usuario = {}
        st.session_state.indice_pregunta = 0
        st.session_state.simulacion_activa = False
        st.rerun()
    
    total = len(st.session_state.preguntas_actuales)
    correctas = 0
    incorrectas = 0
    omitidas = 0
    
    for p in st.session_state.preguntas_actuales:
        if p['id'] in st.session_state.respuestas_usuario:
            if st.session_state.respuestas_usuario[p['id']] == p['correcta']:
                correctas += 1
            else:
                incorrectas += 1
        else:
            omitidas += 1
    
    asignatura = st.session_state.asignatura_seleccionada
    
    try:
        from puntaje_demre import calcular_puntaje_demre, obtener_nivel_demre, generar_recomendaciones
        
        resultado = calcular_puntaje_demre(asignatura, correctas, total)
        nivel = obtener_nivel_demre(resultado['puntaje_demre'])
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {nivel['color']}, {nivel['color']}dd); 
                    color: white; padding: 2rem; border-radius: 15px; 
                    text-align: center; margin: 1rem 0;">
            <div style="font-size: 1.2rem; opacity: 0.9;">{nivel['icono']} {nivel['nivel']}</div>
            <div style="font-size: 3rem; font-weight: 700; margin: 0.5rem 0;">
                {resultado['puntaje_demre']}
            </div>
            <div style="font-size: 1rem; opacity: 0.9;">
                Puntaje DEMRE estimado - {asignatura}
            </div>
            <div style="font-size: 0.9rem; opacity: 0.7; margin-top: 0.5rem;">
                {correctas}/{total} correctas | {resultado['percentil_estimado']}% percentil
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    except:
        puntaje_estimado = correctas * 2.5
        st.markdown(f"""
        <div class="result-card">
            <div class="label">Puntaje Estimado</div>
            <div class="big-number">{puntaje_estimado:.0f}</div>
            <div class="label">puntos (estimación)</div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Correctas", correctas, delta=f"{correctas/total*100:.1f}%")
    with col2:
        st.metric("❌ Incorrectas", incorrectas)
    with col3:
        st.metric("⬜ Omitidas", omitidas)
    with col4:
        st.metric("📝 Total", total)
    
    st.markdown("### 📊 Distribución de respuestas")
    data = {"Categoría": ["Correctas", "Incorrectas", "Omitidas"], "Cantidad": [correctas, incorrectas, omitidas]}
    df = pd.DataFrame(data)
    st.bar_chart(df.set_index("Categoría"))
    
    try:
        st.markdown("### 💡 Recomendaciones")
        recomendaciones = generar_recomendaciones(asignatura, resultado['puntaje_demre'], 
                                                  correctas, incorrectas, omitidas)
        for rec in recomendaciones:
            st.info(f"💡 {rec}")
    except:
        pass
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("📝 Revisar respuestas", use_container_width=True):
            st.session_state.pagina_actual = "revision"
            st.rerun()
    with col2:
        if st.button("🔄 Nueva simulación", use_container_width=True):
            st.session_state.preguntas_actuales = None
            st.session_state.respuestas_usuario = {}
            st.session_state.indice_pregunta = 0
            st.session_state.pagina_actual = "inicio"
            st.session_state.simulacion_activa = False
            st.rerun()
    with col3:
        if st.button("🧠 Análisis con IA", use_container_width=True):
            st.session_state.pagina_actual = "analisis_ia"
            st.rerun()
    
    if not st.session_state.modo_demo:
        try:
            conn = sqlite3.connect("simulador_paes.db")
            c = conn.cursor()
            
            try:
                puntaje_guardar = int(resultado.get('puntaje_demre', correctas * 2.5))
            except:
                puntaje_guardar = int(correctas * 2.5)
            
            c.execute("""
                INSERT INTO intentos 
                (usuario_id, tipo, asignatura, puntaje_total, respuestas_correctas, 
                 respuestas_incorrectas, respuestas_omitidas, tiempo_utilizado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                st.session_state.user_id,
                st.session_state.tipo_simulacion,
                asignatura,
                puntaje_guardar,
                correctas,
                incorrectas,
                omitidas,
                Cronometro.obtener_tiempo()
            ))
            
            conn.commit()
            conn.close()
            st.success("✅ Resultados guardados en tu historial")
        except Exception as e:
            st.warning("No se pudieron guardar los resultados")
    
    st.markdown("""
    <div class="footer">
        <p>Simulador PAES 2026 © Todos los derechos reservados</p>
        <p style="font-size: 0.9rem; color: #1a237e; font-weight: 600;">
            🚀 Desarrollado por <strong>Zamky_Zumbao</strong> | ❤️ Para Javier - ¡El futuro te espera! 💪
        </p>
        <p style="font-size: 0.7rem; color: #b0bec5; margin-top: 0.3rem;">
            Versión 5.0.0 - PAES 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_revision():
    load_css()
    
    st.markdown("""
    <h1 class="main-title">📝 Revisión de Respuestas</h1>
    <p class="sub-title">Revisa cada pregunta y tu respuesta</p>
    """, unsafe_allow_html=True)
    
    if st.button("← Volver a resultados"):
        st.session_state.pagina_actual = "resultados"
        st.rerun()
    
    for i, p in enumerate(st.session_state.preguntas_actuales):
        with st.expander(f"Pregunta {i+1}: {p['texto'][:50]}..."):
            st.markdown(f"**{p['texto']}**")
            
            if p.get("formula"):
                st.markdown(f"📐 **Fórmula:** {p['formula']}")
            
            opciones = ["A", "B", "C", "D", "E"]
            for opcion_idx, opcion_texto in enumerate(p["opciones"]):
                letra = opciones[opcion_idx]
                
                if p['id'] in st.session_state.respuestas_usuario:
                    respuesta = st.session_state.respuestas_usuario[p['id']]
                    es_correcta = respuesta == p['correcta']
                    
                    if letra == p['correcta']:
                        st.markdown(f"✅ **{letra}. {opcion_texto}** *(Correcta)*")
                    elif letra == respuesta and not es_correcta:
                        st.markdown(f"❌ **{letra}. {opcion_texto}** *(Tu respuesta)*")
                    else:
                        st.markdown(f"   {letra}. {opcion_texto}")
                else:
                    if letra == p['correcta']:
                        st.markdown(f"✅ **{letra}. {opcion_texto}** *(Correcta)*")
                    else:
                        st.markdown(f"   {letra}. {opcion_texto}")
            
            if p['id'] in st.session_state.respuestas_usuario:
                respuesta = st.session_state.respuestas_usuario[p['id']]
                if respuesta == p['correcta']:
                    st.success("✅ Respuesta correcta")
                else:
                    st.error(f"❌ Respuesta incorrecta. La correcta era: {p['correcta']}")
            
            if p.get("explicacion"):
                st.info(f"💡 **Explicación:** {p['explicacion']}")
    
    st.markdown("""
    <div class="footer">
        <p>Simulador PAES 2026 © Todos los derechos reservados</p>
        <p style="font-size: 0.9rem; color: #1a237e; font-weight: 600;">
            🚀 Desarrollado por <strong>Zamky_Zumbao</strong> | ❤️ Para Javier - ¡El futuro te espera! 💪
        </p>
        <p style="font-size: 0.7rem; color: #b0bec5; margin-top: 0.3rem;">
            Versión 5.0.0 - PAES 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_progreso():
    load_css()
    
    st.markdown("""
    <h1 class="main-title">📊 Mi Progreso</h1>
    <p class="sub-title">Sigue tu evolución en el simulador</p>
    """, unsafe_allow_html=True)
    
    if st.button("← Volver al menú principal"):
        st.session_state.pagina_actual = "inicio"
        st.rerun()
    
    if st.session_state.modo_demo:
        st.info("ℹ️ En modo demo no se guarda historial")
        return
    
    try:
        conn = sqlite3.connect("simulador_paes.db")
        
        c = conn.cursor()
        c.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(respuestas_correctas) as correctas_total,
                SUM(respuestas_incorrectas) as incorrectas_total,
                SUM(respuestas_omitidas) as omitidas_total,
                AVG(puntaje_total) as promedio
            FROM intentos 
            WHERE usuario_id = ?
        """, (st.session_state.user_id,))
        
        stats = c.fetchone()
        
        if stats and stats[0] > 0:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Simulaciones", stats[0])
            with col2:
                total_resp = stats[1] + stats[2] + stats[3]
                if total_resp > 0:
                    precision = (stats[1] / total_resp) * 100
                else:
                    precision = 0
                st.metric("Precisión", f"{precision:.1f}%")
            with col3:
                st.metric("Promedio DEMRE", f"{stats[4]:.0f}" if stats[4] else "N/A")
            with col4:
                st.metric("Total Correctas", stats[1])
            
            st.markdown("### 📈 Evolución de Puntajes")
            c.execute("""
                SELECT fecha, puntaje_total, asignatura
                FROM intentos 
                WHERE usuario_id = ?
                ORDER BY fecha
            """, (st.session_state.user_id,))
            
            datos = c.fetchall()
            if datos:
                df = pd.DataFrame(datos, columns=["Fecha", "Puntaje", "Asignatura"])
                st.line_chart(df.set_index("Fecha")["Puntaje"])
                
                st.markdown("### 📋 Historial Detallado")
                c.execute("""
                    SELECT fecha, tipo, asignatura, puntaje_total, 
                           respuestas_correctas, respuestas_incorrectas, respuestas_omitidas
                    FROM intentos 
                    WHERE usuario_id = ?
                    ORDER BY fecha DESC
                    LIMIT 20
                """, (st.session_state.user_id,))
                
                historial = c.fetchall()
                if historial:
                    df_historial = pd.DataFrame(historial, 
                        columns=["Fecha", "Tipo", "Asignatura", "Puntaje", "Correctas", "Incorrectas", "Omitidas"])
                    df_historial["Fecha"] = pd.to_datetime(df_historial["Fecha"]).dt.strftime("%d/%m/%Y %H:%M")
                    st.dataframe(df_historial, use_container_width=True, hide_index=True)
        else:
            st.info("📝 Aún no tienes simulaciones guardadas")
        
        conn.close()
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
    
    st.markdown("""
    <div class="footer">
        <p>Simulador PAES 2026 © Todos los derechos reservados</p>
        <p style="font-size: 0.9rem; color: #1a237e; font-weight: 600;">
            🚀 Desarrollado por <strong>Zamky_Zumbao</strong> | ❤️ Para Javier - ¡El futuro te espera! 💪
        </p>
        <p style="font-size: 0.7rem; color: #b0bec5; margin-top: 0.3rem;">
            Versión 5.0.0 - PAES 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_carga_excel():
    load_css()
    
    st.markdown("""
    <h1 class="main-title">📤 Cargar Preguntas desde Excel</h1>
    <p class="sub-title">Sube un archivo Excel con preguntas para agregarlas a la base de datos</p>
    """, unsafe_allow_html=True)
    
    if st.button("← Volver al menú principal"):
        st.session_state.pagina_actual = "inicio"
        st.rerun()
    
    total = contar_preguntas()
    st.info(f"📊 Actualmente hay {total} preguntas en la base de datos")
    
    with st.expander("📋 Ver formato del archivo Excel", expanded=False):
        st.markdown("""
        ### Formato requerido:
        
        El archivo Excel debe tener las siguientes columnas:
        
        | Columna | Descripción | Ejemplo |
        |---------|-------------|---------|
        | **asignatura** | Nombre de la asignatura | "Matemática 1" |
        | **numero** | Número de la pregunta | 1 |
        | **texto** | Enunciado de la pregunta | "¿Cuánto es 2+2?" |
        | **opcion_a** | Opción A | "2" |
        | **opcion_b** | Opción B | "3" |
        | **opcion_c** | Opción C | "4" |
        | **opcion_d** | Opción D | "5" |
        | **opcion_e** | Opción E (opcional) | "6" |
        | **respuesta_correcta** | Letra correcta | "C" |
        | **dificultad** | facil / media / dificil | "facil" |
        | **explicacion** | Explicación (opcional) | "2+2=4" |
        """)
    
    st.markdown("### 📁 Subir archivo")
    
    archivo = st.file_uploader(
        "Selecciona un archivo Excel (.xlsx o .xls)",
        type=["xlsx", "xls"],
        help="El archivo debe tener las columnas requeridas"
    )
    
    if archivo is not None:
        try:
            df = pd.read_excel(archivo)
            
            st.success(f"✅ Archivo cargado: {len(df)} filas")
            
            st.markdown("### 👁️ Vista previa de los datos:")
            st.dataframe(df.head(10), use_container_width=True)
            
            columnas_requeridas = [
                "asignatura", "numero", "texto", 
                "opcion_a", "opcion_b", "opcion_c", "opcion_d",
                "respuesta_correcta"
            ]
            
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                st.error(f"❌ Faltan columnas: {', '.join(columnas_faltantes)}")
                st.info("Asegúrate de que tu Excel tenga todas las columnas requeridas.")
                return
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Cargar preguntas (agregar)", use_container_width=True, type="primary"):
                    cargar_preguntas_excel(df, limpiar=False)
            
            with col2:
                if st.button("🔄 Reemplazar todas", use_container_width=True, type="secondary"):
                    if st.checkbox("¿Estás seguro? Esto eliminará TODAS las preguntas existentes"):
                        cargar_preguntas_excel(df, limpiar=True)
            
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {str(e)}")
    
    st.markdown("""
    <div class="footer">
        <p>Simulador PAES 2026 © Todos los derechos reservados</p>
        <p style="font-size: 0.9rem; color: #1a237e; font-weight: 600;">
            🚀 Desarrollado por <strong>Zamky_Zumbao</strong> | ❤️ Para Javier - ¡El futuro te espera! 💪
        </p>
        <p style="font-size: 0.7rem; color: #b0bec5; margin-top: 0.3rem;">
            Versión 5.0.0 - PAES 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

def cargar_preguntas_excel(df, limpiar=False):
    conn = sqlite3.connect("simulador_paes.db")
    c = conn.cursor()
    
    try:
        if limpiar:
            c.execute("DELETE FROM preguntas")
            st.info("🗑️ Preguntas existentes eliminadas")
        
        count = 0
        errores = 0
        
        for _, row in df.iterrows():
            try:
                asignatura = str(row["asignatura"]).strip()
                numero = int(row["numero"]) if pd.notna(row["numero"]) else count + 1
                texto = str(row["texto"]).strip()
                opcion_a = str(row["opcion_a"]).strip()
                opcion_b = str(row["opcion_b"]).strip()
                opcion_c = str(row["opcion_c"]).strip()
                opcion_d = str(row["opcion_d"]).strip()
                opcion_e = str(row.get("opcion_e", "")).strip() if pd.notna(row.get("opcion_e", "")) else ""
                respuesta_correcta = str(row["respuesta_correcta"]).strip().upper()
                dificultad = str(row.get("dificultad", "media")).strip().lower()
                explicacion = str(row.get("explicacion", "")).strip() if pd.notna(row.get("explicacion", "")) else ""
                
                if respuesta_correcta not in ["A", "B", "C", "D", "E"]:
                    errores += 1
                    continue
                
                c.execute('''
                    INSERT INTO preguntas 
                    (asignatura, numero, texto, opcion_a, opcion_b, opcion_c, opcion_d, opcion_e, 
                     respuesta_correcta, dificultad, explicacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    asignatura, numero, texto, opcion_a, opcion_b, opcion_c, opcion_d, opcion_e,
                    respuesta_correcta, dificultad, explicacion
                ))
                count += 1
                
            except Exception as e:
                errores += 1
                continue
        
        conn.commit()
        
        st.success(f"✅ {count} preguntas cargadas correctamente")
        if errores > 0:
            st.warning(f"⚠️ {errores} preguntas con errores fueron omitidas")
        
        c.execute("SELECT asignatura, COUNT(*) FROM preguntas GROUP BY asignatura")
        resultados = c.fetchall()
        
        st.markdown("### 📊 Resumen por asignatura:")
        if resultados:
            for asignatura, cantidad in resultados:
                st.write(f"  • {asignatura}: {cantidad} preguntas")
        else:
            st.write("  • No hay preguntas cargadas")
        
    except Exception as e:
        st.error(f"❌ Error al cargar preguntas: {str(e)}")
    
    finally:
        conn.close()

def mostrar_dashboard():
    try:
        from dashboard import mostrar_dashboard as dashboard_func
        dashboard_func()
    except:
        st.info("📊 Dashboard en desarrollo. Próximamente disponible.")
        if st.button("← Volver al menú principal"):
            st.session_state.pagina_actual = "inicio"
            st.rerun()

def mostrar_metas():
    try:
        from metas_logros import mostrar_metas as metas_func
        metas_func()
    except:
        st.info("🎯 Sistema de metas y logros en desarrollo. Próximamente disponible.")
        if st.button("← Volver al menú principal"):
            st.session_state.pagina_actual = "inicio"
            st.rerun()

def mostrar_analisis_ia():
    try:
        from analisis_ia import mostrar_analisis_ia as ia_func
        ia_func()
    except ImportError:
        st.info("🧠 Sistema de análisis con IA en desarrollo. Próximamente disponible.")
        if st.button("← Volver al menú principal"):
            st.session_state.pagina_actual = "inicio"
            st.rerun()
    except Exception as e:
        st.error(f"Error al cargar el análisis: {str(e)}")
        if st.button("← Volver al menú principal"):
            st.session_state.pagina_actual = "inicio"
            st.rerun()

def init_session_state():
    defaults = {
        'logged_in': False,
        'modo_demo': False,
        'pagina_actual': 'inicio',
        'preguntas_actuales': None,
        'indice_pregunta': 0,
        'respuestas_usuario': {},
        'tiempo_inicio': None,
        'tiempo_pausa': 0,
        'simulacion_activa': False,
        'asignatura_seleccionada': None,
        'tipo_simulacion': None,
        'preguntas_marcadas': set()
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    init_database()
    init_session_state()
    
    if not st.session_state.logged_in:
        mostrar_login()
    else:
        pagina = st.session_state.pagina_actual
        
        if pagina == "inicio":
            mostrar_menu_principal()
        elif pagina == "seleccion_practica":
            mostrar_seleccion_asignatura("practica")
        elif pagina == "seleccion_oficial":
            mostrar_seleccion_asignatura("oficial")
        elif pagina == "simulacion":
            if st.session_state.preguntas_actuales is None:
                asignatura = st.session_state.asignatura_seleccionada
                st.session_state.preguntas_actuales = cargar_preguntas(asignatura, None)
                
                if not st.session_state.preguntas_actuales:
                    st.error(f"No hay preguntas disponibles para {asignatura}")
                    preguntas_generadas = []
                    for i in range(10):
                        preguntas_generadas.append({
                            "id": i + 1000,
                            "numero": i + 1,
                            "texto": f"Pregunta de ejemplo {i+1} de {asignatura}",
                            "opciones": ["Opción A", "Opción B", "Opción C", "Opción D", "Opción E"],
                            "correcta": "A",
                            "dificultad": "media",
                            "explicacion": "Esta es una pregunta de ejemplo."
                        })
                    st.session_state.preguntas_actuales = preguntas_generadas
                
                st.session_state.simulacion_activa = True
                st.session_state.tiempo_inicio = None
            
            mostrar_simulacion()
        elif pagina == "resultados":
            mostrar_resultados()
        elif pagina == "revision":
            mostrar_revision()
        elif pagina == "progreso":
            mostrar_progreso()
        elif pagina == "carga_excel":
            mostrar_carga_excel()
        elif pagina == "dashboard":
            mostrar_dashboard()
        elif pagina == "metas":
            mostrar_metas()
        elif pagina == "analisis_ia":
            mostrar_analisis_ia()
        else:
            mostrar_menu_principal()

if __name__ == "__main__":
    main()