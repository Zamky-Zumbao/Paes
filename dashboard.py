"""
DASHBOARD AVANZADO - SIMULADOR PAES
Gráficos interactivos con Plotly y estadísticas detalladas
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

def cargar_datos_usuario(usuario_id):
    """Carga todos los datos del usuario desde la base de datos"""
    conn = sqlite3.connect("simulador_paes.db")
    
    # Intentos del usuario
    query = """
        SELECT id, fecha, tipo, asignatura, puntaje_total, 
               respuestas_correctas, respuestas_incorrectas, respuestas_omitidas,
               tiempo_utilizado
        FROM intentos 
        WHERE usuario_id = ?
        ORDER BY fecha
    """
    df_intentos = pd.read_sql_query(query, conn, params=(usuario_id,))
    
    # Estadísticas generales
    query_stats = """
        SELECT 
            COUNT(*) as total_intentos,
            AVG(puntaje_total) as promedio_puntaje,
            MAX(puntaje_total) as max_puntaje,
            MIN(puntaje_total) as min_puntaje,
            SUM(respuestas_correctas) as total_correctas,
            SUM(respuestas_incorrectas) as total_incorrectas,
            SUM(respuestas_omitidas) as total_omitidas,
            AVG(tiempo_utilizado) as promedio_tiempo
        FROM intentos 
        WHERE usuario_id = ?
    """
    df_stats = pd.read_sql_query(query_stats, conn, params=(usuario_id,))
    
    conn.close()
    return df_intentos, df_stats

def mostrar_dashboard():
    """Muestra el dashboard completo con gráficos interactivos"""
    
    st.markdown("""
    <h1 class="main-title">📊 Dashboard Avanzado</h1>
    <p class="sub-title">Análisis detallado de tu rendimiento en el simulador</p>
    """, unsafe_allow_html=True)
    
    if st.button("← Volver al menú principal"):
        st.session_state.pagina_actual = "inicio"
        st.rerun()
    
    if st.session_state.modo_demo:
        st.info("ℹ️ En modo demo no se guarda historial. Regístrate para ver tu progreso.")
        return
    
    # Cargar datos
    df_intentos, df_stats = cargar_datos_usuario(st.session_state.user_id)
    
    if df_intentos.empty:
        st.info("📝 Aún no has completado ninguna simulación. ¡Comienza ahora!")
        return
    
    # ============ MÉTRICAS PRINCIPALES ============
    st.markdown("### 📈 Resumen General")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Simulaciones", 
            df_stats['total_intentos'].iloc[0],
            delta=None
        )
    
    with col2:
        promedio = df_stats['promedio_puntaje'].iloc[0]
        st.metric(
            "Promedio Puntaje", 
            f"{promedio:.0f}" if promedio else "N/A",
            delta=None
        )
    
    with col3:
        max_puntaje = df_stats['max_puntaje'].iloc[0]
        st.metric(
            "Mejor Puntaje", 
            f"{max_puntaje:.0f}" if max_puntaje else "N/A",
            delta="🎯"
        )
    
    with col4:
        total_preg = (df_stats['total_correctas'].iloc[0] + 
                     df_stats['total_incorrectas'].iloc[0] + 
                     df_stats['total_omitidas'].iloc[0])
        if total_preg > 0:
            precision = (df_stats['total_correctas'].iloc[0] / total_preg) * 100
        else:
            precision = 0
        st.metric(
            "Precisión Global", 
            f"{precision:.1f}%",
            delta=None
        )
    
    # ============ GRÁFICO 1: Evolución de Puntajes ============
    st.markdown("### 📈 Evolución de Puntajes por Simulación")
    
    fig1 = px.line(
        df_intentos, 
        x='fecha', 
        y='puntaje_total',
        color='asignatura',
        title='Evolución de Puntajes',
        labels={'fecha': 'Fecha', 'puntaje_total': 'Puntaje DEMRE', 'asignatura': 'Asignatura'},
        markers=True
    )
    fig1.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Puntaje DEMRE",
        legend_title="Asignatura",
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # ============ GRÁFICO 2: Distribución por Asignatura ============
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Rendimiento por Asignatura")
        
        # Agrupar por asignatura
        df_asignatura = df_intentos.groupby('asignatura').agg({
            'puntaje_total': 'mean',
            'respuestas_correctas': 'sum',
            'respuestas_incorrectas': 'sum',
            'respuestas_omitidas': 'sum'
        }).reset_index()
        
        fig2 = px.bar(
            df_asignatura,
            x='asignatura',
            y='puntaje_total',
            title='Puntaje Promedio por Asignatura',
            labels={'asignatura': 'Asignatura', 'puntaje_total': 'Puntaje Promedio'},
            color='puntaje_total',
            color_continuous_scale='Blues'
        )
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Distribución de Respuestas")
        
        # Calcular totales
        total_correctas = df_stats['total_correctas'].iloc[0]
        total_incorrectas = df_stats['total_incorrectas'].iloc[0]
        total_omitidas = df_stats['total_omitidas'].iloc[0]
        
        fig3 = go.Figure(data=[go.Pie(
            labels=['Correctas', 'Incorrectas', 'Omitidas'],
            values=[total_correctas, total_incorrectas, total_omitidas],
            hole=.3,
            marker_colors=['#4caf50', '#f44336', '#ff9800']
        )])
        fig3.update_layout(title='Distribución Global de Respuestas')
        st.plotly_chart(fig3, use_container_width=True)
    
    # ============ GRÁFICO 3: Análisis por Tipo ============
    st.markdown("### 📊 Práctica vs Simulación Oficial")
    
    df_tipo = df_intentos.groupby('tipo').agg({
        'puntaje_total': 'mean',
        'respuestas_correctas': 'sum',
        'respuestas_incorrectas': 'sum'
    }).reset_index()
    
    fig4 = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Puntaje Promedio', 'Distribución de Respuestas')
    )
    
    # Gráfico de barras - Puntaje promedio
    fig4.add_trace(
        go.Bar(x=df_tipo['tipo'], y=df_tipo['puntaje_total'], 
               name='Puntaje Promedio', marker_color='#1a237e'),
        row=1, col=1
    )
    
    # Gráfico de barras apiladas - Respuestas
    fig4.add_trace(
        go.Bar(x=df_tipo['tipo'], y=df_tipo['respuestas_correctas'], 
               name='Correctas', marker_color='#4caf50'),
        row=1, col=2
    )
    fig4.add_trace(
        go.Bar(x=df_tipo['tipo'], y=df_tipo['respuestas_incorrectas'], 
               name='Incorrectas', marker_color='#f44336'),
        row=1, col=2
    )
    
    fig4.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig4, use_container_width=True)
    
    # ============ GRÁFICO 4: Mapa de Calor - Rendimiento por Día ============
    st.markdown("### 🗓️ Calendario de Actividad")
    
    # Preparar datos por día
    df_intentos['fecha_dia'] = pd.to_datetime(df_intentos['fecha']).dt.date
    df_dias = df_intentos.groupby('fecha_dia').agg({
        'puntaje_total': 'mean',
        'id': 'count'
    }).reset_index()
    df_dias.columns = ['Fecha', 'Puntaje_Promedio', 'Simulaciones']
    
    # Heatmap con Plotly
    fig5 = px.density_heatmap(
        df_dias,
        x=pd.to_datetime(df_dias['Fecha']).dt.dayofweek,
        y=pd.to_datetime(df_dias['Fecha']).dt.isocalendar().week,
        z='Simulaciones',
        title='Actividad por Día de la Semana y Semana',
        labels={'x': 'Día de la Semana', 'y': 'Semana', 'z': 'Simulaciones'},
        color_continuous_scale='Blues'
    )
    fig5.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=[0,1,2,3,4,5,6],
            ticktext=['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        )
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    # ============ GRÁFICO 5: Radar de Habilidades ============
    st.markdown("### 🎯 Radar de Rendimiento por Asignatura")
    
    if len(df_asignatura) >= 3:
        fig6 = go.Figure()
        
        fig6.add_trace(go.Scatterpolar(
            r=df_asignatura['puntaje_total'],
            theta=df_asignatura['asignatura'],
            fill='toself',
            name='Puntaje Promedio',
            line_color='#1a237e'
        ))
        
        fig6.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(df_asignatura['puntaje_total']) * 1.1]
                )
            ),
            title='Comparativa por Asignatura'
        )
        st.plotly_chart(fig6, use_container_width=True)
    
    # ============ TABLA DETALLADA ============
    st.markdown("### 📋 Historial Detallado")
    
    # Preparar datos para tabla
    df_tabla = df_intentos.copy()
    df_tabla['fecha'] = pd.to_datetime(df_tabla['fecha']).dt.strftime('%d/%m/%Y %H:%M')
    df_tabla = df_tabla[['fecha', 'tipo', 'asignatura', 'puntaje_total', 
                         'respuestas_correctas', 'respuestas_incorrectas', 
                         'respuestas_omitidas', 'tiempo_utilizado']]
    df_tabla.columns = ['Fecha', 'Tipo', 'Asignatura', 'Puntaje', 
                        'Correctas', 'Incorrectas', 'Omitidas', 'Tiempo (s)']
    
    st.dataframe(df_tabla, use_container_width=True, hide_index=True)
    
    # ============ EXPORTAR ============
    st.markdown("### 📤 Exportar Datos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Exportar a CSV
        csv = df_tabla.to_csv(index=False)
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"historial_paes_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Exportar a Excel
        if st.button("📊 Descargar Excel", use_container_width=True):
            try:
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_tabla.to_excel(writer, sheet_name='Historial', index=False)
                    df_stats.to_excel(writer, sheet_name='Estadísticas', index=False)
                output.seek(0)
                st.download_button(
                    label="📊 Descargar Excel",
                    data=output,
                    file_name=f"historial_paes_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.warning("Instala openpyxl: pip install openpyxl")
    
    with col3:
        # Generar reporte
        if st.button("📄 Generar Reporte PDF", use_container_width=True):
            st.info("Función en desarrollo. Próximamente disponible.")

def mostrar_dashboard_completo():
    """Función principal del dashboard"""
    mostrar_dashboard()