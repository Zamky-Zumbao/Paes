"""
SISTEMA DE NOTIFICACIONES - SIMULADOR PAES
Módulo opcional para mostrar alertas y recordatorios
"""

import streamlit as st
import sqlite3
from datetime import datetime, timedelta

def mostrar_notificaciones():
    """Muestra un panel de notificaciones en el menú principal"""
    
    if st.session_state.modo_demo:
        return
    
    try:
        conn = sqlite3.connect("simulador_paes.db")
        c = conn.cursor()
        
        # Obtener estadísticas del usuario
        c.execute("""
            SELECT 
                COUNT(*) as total,
                MAX(fecha) as ultima_simulacion,
                AVG(puntaje_total) as promedio,
                MIN(fecha) as primera_simulacion
            FROM intentos 
            WHERE usuario_id = ?
        """, (st.session_state.user_id,))
        
        stats = c.fetchone()
        conn.close()
        
        notificaciones = []
        
        # Notificación 1: Sin simulaciones
        if stats[0] == 0:
            notificaciones.append({
                "tipo": "info",
                "mensaje": "📝 ¡Comienza tu primera simulación! Selecciona una asignatura y empieza a practicar."
            })
        
        # Notificación 2: Última simulación hace más de 7 días
        if stats[1]:
            ultima = datetime.strptime(stats[1], '%Y-%m-%d %H:%M:%S')
            dias = (datetime.now() - ultima).days
            if dias > 7:
                notificaciones.append({
                    "tipo": "warning",
                    "mensaje": f"⏳ Han pasado {dias} días desde tu última simulación. ¡Sigue practicando para no perder el ritmo!"
                })
            elif dias > 30:
                notificaciones.append({
                    "tipo": "warning",
                    "mensaje": f"⚠️ ¡Han pasado {dias} días! ¿Qué esperas para volver a practicar? ¡Tú puedes!"
                })
        
        # Notificación 3: Logro cercano
        if stats[0] == 9:
            notificaciones.append({
                "tipo": "success",
                "mensaje": "🎯 ¡Ya completaste 9 simulaciones! Una más y desbloquearás el logro '🏃‍♂️ Diez Simulaciones'"
            })
        elif stats[0] == 49:
            notificaciones.append({
                "tipo": "success",
                "mensaje": "🏆 ¡Ya completaste 49 simulaciones! Una más y serás un EXPERTO"
            })
        
        # Notificación 4: Mejora de puntaje (si hay al menos 2 simulaciones)
        if stats[0] >= 2 and stats[2]:
            conn = sqlite3.connect("simulador_paes.db")
            c = conn.cursor()
            c.execute("""
                SELECT puntaje_total 
                FROM intentos 
                WHERE usuario_id = ?
                ORDER BY fecha DESC
                LIMIT 2
            """, (st.session_state.user_id,))
            
            puntajes = [row[0] for row in c.fetchall()]
            conn.close()
            
            if len(puntajes) >= 2:
                if puntajes[0] > puntajes[1]:
                    mejora = puntajes[0] - puntajes[1]
                    notificaciones.append({
                        "tipo": "success",
                        "mensaje": f"📈 ¡Mejoraste {mejora} puntos en tu última simulación! Sigue así."
                    })
                elif puntajes[0] < puntajes[1]:
                    baja = puntajes[1] - puntajes[0]
                    notificaciones.append({
                        "tipo": "info",
                        "mensaje": f"📊 Tu puntaje bajó {baja} puntos. Revisa las respuestas para identificar áreas de mejora."
                    })
        
        # Mostrar notificaciones
        if notificaciones:
            st.markdown("### 🔔 Notificaciones")
            for notif in notificaciones:
                if notif["tipo"] == "info":
                    st.info(notif["mensaje"])
                elif notif["tipo"] == "warning":
                    st.warning(notif["mensaje"])
                elif notif["tipo"] == "success":
                    st.success(notif["mensaje"])
                elif notif["tipo"] == "error":
                    st.error(notif["mensaje"])
    
    except Exception as e:
        # Si hay error, no mostrar nada
        pass

def agregar_notificacion(tipo, mensaje):
    """Agrega una notificación a la sesión para mostrarla después"""
    if 'notificaciones' not in st.session_state:
        st.session_state.notificaciones = []
    st.session_state.notificaciones.append({"tipo": tipo, "mensaje": mensaje})

def limpiar_notificaciones():
    """Limpia todas las notificaciones de la sesión"""
    if 'notificaciones' in st.session_state:
        st.session_state.notificaciones = []

# ============ FUNCIONES PARA NOTIFICACIONES EN TIEMPO REAL ============

def notificar_exito(mensaje):
    """Muestra una notificación de éxito"""
    st.success(f"✅ {mensaje}")

def notificar_error(mensaje):
    """Muestra una notificación de error"""
    st.error(f"❌ {mensaje}")

def notificar_advertencia(mensaje):
    """Muestra una notificación de advertencia"""
    st.warning(f"⚠️ {mensaje}")

def notificar_informacion(mensaje):
    """Muestra una notificación informativa"""
    st.info(f"ℹ️ {mensaje}")