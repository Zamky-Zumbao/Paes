def mostrar_estadisticas_asignatura():
    """Muestra estadísticas detalladas por asignatura"""
    
    st.markdown("### 📊 Estadísticas por Asignatura")
    
    conn = sqlite3.connect("simulador_paes.db")
    
    # Obtener todas las asignaturas
    query_asignaturas = """
        SELECT DISTINCT asignatura 
        FROM intentos 
        WHERE usuario_id = ?
    """
    df_asignaturas = pd.read_sql_query(query_asignaturas, conn, params=(st.session_state.user_id,))
    
    if df_asignaturas.empty:
        st.info("No hay datos disponibles")
        conn.close()
        return
    
    asignatura_seleccionada = st.selectbox(
        "Selecciona una asignatura:",
        df_asignaturas['asignatura'].tolist()
    )
    
    # Estadísticas de la asignatura seleccionada
    query = """
        SELECT 
            COUNT(*) as total,
            AVG(puntaje_total) as promedio,
            MAX(puntaje_total) as maximo,
            MIN(puntaje_total) as minimo,
            SUM(respuestas_correctas) as correctas,
            SUM(respuestas_incorrectas) as incorrectas,
            SUM(respuestas_omitidas) as omitidas,
            AVG(tiempo_utilizado) as tiempo_promedio
        FROM intentos 
        WHERE usuario_id = ? AND asignatura = ?
    """
    df_stats = pd.read_sql_query(query, conn, params=(st.session_state.user_id, asignatura_seleccionada))
    conn.close()
    
    if not df_stats.empty:
        stats = df_stats.iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Simulaciones", stats['total'])
        with col2:
            st.metric("Promedio", f"{stats['promedio']:.0f}" if stats['promedio'] else "N/A")
        with col3:
            st.metric("Máximo", stats['maximo'] if stats['maximo'] else "N/A")
        with col4:
            st.metric("Mínimo", stats['minimo'] if stats['minimo'] else "N/A")
        
        # Gráfico de distribución
        st.markdown("#### Distribución de Respuestas")
        fig = go.Figure(data=[go.Pie(
            labels=['Correctas', 'Incorrectas', 'Omitidas'],
            values=[stats['correctas'], stats['incorrectas'], stats['omitidas']],
            hole=.3,
            marker_colors=['#4caf50', '#f44336', '#ff9800']
        )])
        fig.update_layout(title=f"Distribución - {asignatura_seleccionada}")
        st.plotly_chart(fig, use_container_width=True)