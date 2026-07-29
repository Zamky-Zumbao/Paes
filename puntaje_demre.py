"""
SISTEMA DE PUNTAJE DEMRE
Calcula puntajes oficiales basados en la tabla DEMRE
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Tabla de conversión DEMRE (aproximada según datos oficiales)
TABLA_DEMRE = {
    "Matemática 1": {
        "rangos": [
            (0, 5, 250, 350),
            (6, 10, 350, 450),
            (11, 15, 450, 530),
            (16, 20, 530, 600),
            (21, 25, 600, 670),
            (26, 30, 670, 740),
            (31, 35, 740, 790),
            (36, 40, 790, 830),
            (41, 45, 830, 860),
            (46, 50, 860, 890),
            (51, 55, 890, 920),
            (56, 60, 920, 950),
            (61, 65, 950, 1000)
        ],
        "total": 65
    },
    "Matemática 2": {
        "rangos": [
            (0, 5, 250, 350),
            (6, 10, 350, 450),
            (11, 15, 450, 530),
            (16, 20, 530, 600),
            (21, 25, 600, 670),
            (26, 30, 670, 730),
            (31, 35, 730, 780),
            (36, 40, 780, 820),
            (41, 45, 820, 860),
            (46, 50, 860, 900),
            (51, 55, 900, 950)
        ],
        "total": 55
    },
    "Competencia Lectora": {
        "rangos": [
            (0, 5, 250, 350),
            (6, 10, 350, 450),
            (11, 15, 450, 530),
            (16, 20, 530, 600),
            (21, 25, 600, 670),
            (26, 30, 670, 740),
            (31, 35, 740, 790),
            (36, 40, 790, 830),
            (41, 45, 830, 860),
            (46, 50, 860, 890),
            (51, 55, 890, 920),
            (56, 60, 920, 950),
            (61, 65, 950, 1000)
        ],
        "total": 65
    },
    "Historia y Ciencias Sociales": {
        "rangos": [
            (0, 5, 250, 350),
            (6, 10, 350, 450),
            (11, 15, 450, 530),
            (16, 20, 530, 600),
            (21, 25, 600, 670),
            (26, 30, 670, 740),
            (31, 35, 740, 790),
            (36, 40, 790, 830),
            (41, 45, 830, 860),
            (46, 50, 860, 890),
            (51, 55, 890, 920),
            (56, 60, 920, 950),
            (61, 65, 950, 1000)
        ],
        "total": 65
    },
    "Ciencias": {
        "rangos": [
            (0, 8, 250, 350),
            (9, 16, 350, 450),
            (17, 24, 450, 530),
            (25, 32, 530, 600),
            (33, 40, 600, 670),
            (41, 48, 670, 740),
            (49, 56, 740, 790),
            (57, 64, 790, 830),
            (65, 72, 830, 860),
            (73, 80, 860, 890)
        ],
        "total": 80
    },
    "Inglés": {
        "rangos": [
            (0, 5, 250, 350),
            (6, 10, 350, 450),
            (11, 15, 450, 530),
            (16, 20, 530, 600),
            (21, 25, 600, 670),
            (26, 30, 670, 740),
            (31, 35, 740, 790),
            (36, 40, 790, 830),
            (41, 45, 830, 860)
        ],
        "total": 45
    }
}

# Tabla de percentiles aproximados
PERCENTILES = {
    "Matemática 1": [
        (0, 1), (100, 5), (200, 10), (300, 15), (400, 20),
        (500, 30), (550, 40), (600, 50), (650, 60),
        (700, 70), (750, 80), (800, 90), (850, 95), (900, 98), (950, 99)
    ],
    "Competencia Lectora": [
        (0, 1), (100, 5), (200, 10), (300, 15), (400, 20),
        (500, 30), (550, 40), (600, 50), (650, 60),
        (700, 70), (750, 80), (800, 90), (850, 95), (900, 98), (950, 99)
    ],
    "Historia y Ciencias Sociales": [
        (0, 1), (100, 5), (200, 10), (300, 15), (400, 20),
        (500, 30), (550, 40), (600, 50), (650, 60),
        (700, 70), (750, 80), (800, 90), (850, 95), (900, 98), (950, 99)
    ],
    "Matemática 2": [
        (0, 1), (100, 5), (200, 10), (300, 15), (400, 20),
        (500, 30), (550, 40), (600, 50), (650, 60),
        (700, 70), (750, 80), (800, 90), (850, 95), (900, 98), (950, 99)
    ],
    "Ciencias": [
        (0, 1), (100, 5), (200, 10), (300, 15), (400, 20),
        (500, 30), (550, 40), (600, 50), (650, 60),
        (700, 70), (750, 80), (800, 90), (850, 95), (900, 98)
    ],
    "Inglés": [
        (0, 1), (100, 5), (200, 10), (300, 15), (400, 20),
        (500, 30), (550, 40), (600, 50), (650, 60),
        (700, 70), (750, 80), (800, 90), (850, 95), (900, 98)
    ]
}

def calcular_puntaje_demre(asignatura, correctas, total_preguntas):
    """
    Calcula el puntaje DEMRE estimado basado en la tabla de conversión
    
    Args:
        asignatura: Nombre de la asignatura
        correctas: Número de respuestas correctas
        total_preguntas: Total de preguntas en la prueba
    
    Returns:
        dict: {puntaje_bruto, puntaje_demre, percentil_estimado, nivel, rango_encontrado}
    """
    
    # Buscar la asignatura en la tabla
    if asignatura in TABLA_DEMRE:
        rangos = TABLA_DEMRE[asignatura]["rangos"]
        total = TABLA_DEMRE[asignatura]["total"]
    else:
        # Si no está en la tabla, usar fórmula aproximada
        return calcular_puntaje_aproximado(asignatura, correctas, total_preguntas)
    
    # Asegurar que total_preguntas coincida
    if total_preguntas != total:
        # Si no coincide, usar el total de la tabla pero ajustar
        pass
    
    # Calcular puntaje bruto
    puntaje_bruto = correctas
    
    # Buscar el rango correspondiente
    puntaje_demre = 250
    rango_encontrado = "0-0"
    for min_c, max_c, min_p, max_p in rangos:
        if min_c <= puntaje_bruto <= max_c:
            # Interpolación lineal dentro del rango
            if max_c == min_c:
                puntaje_demre = (min_p + max_p) // 2
            else:
                proporcion = (puntaje_bruto - min_c) / (max_c - min_c)
                puntaje_demre = int(min_p + (max_p - min_p) * proporcion)
            rango_encontrado = f"{min_c}-{max_c}"
            break
    
    # Si el puntaje está por encima del último rango
    if puntaje_bruto > rangos[-1][1]:
        puntaje_demre = rangos[-1][3]
        rango_encontrado = f">{rangos[-1][1]}"
    
    # Calcular percentil estimado
    percentil = calcular_percentil(asignatura, puntaje_demre)
    
    # Determinar nivel de rendimiento
    if puntaje_demre >= 800:
        nivel = "🌟 Excelente"
    elif puntaje_demre >= 650:
        nivel = "✅ Bueno"
    elif puntaje_demre >= 500:
        nivel = "📘 Regular"
    else:
        nivel = "📖 Necesita mejorar"
    
    return {
        "puntaje_bruto": puntaje_bruto,
        "puntaje_demre": puntaje_demre,
        "percentil_estimado": percentil,
        "nivel": nivel,
        "rango_encontrado": rango_encontrado
    }

def calcular_percentil(asignatura, puntaje_demre):
    """Calcula el percentil estimado basado en el puntaje DEMRE"""
    
    if asignatura in PERCENTILES:
        percentiles = PERCENTILES[asignatura]
        
        for i, (p_min, pct) in enumerate(percentiles):
            if i < len(percentiles) - 1:
                p_max = percentiles[i+1][0]
                if p_min <= puntaje_demre < p_max:
                    return pct
            else:
                if puntaje_demre >= p_min:
                    return pct
    
    # Si no hay tabla, estimar
    return min(99, max(1, int((puntaje_demre / 1000) * 100)))

def calcular_puntaje_aproximado(asignatura, correctas, total_preguntas):
    """Calcula un puntaje aproximado cuando no hay tabla específica"""
    porcentaje = (correctas / total_preguntas) * 100 if total_preguntas > 0 else 0
    
    if porcentaje >= 90:
        puntaje_demre = 850 + int((porcentaje - 90) * 3)
    elif porcentaje >= 75:
        puntaje_demre = 700 + int((porcentaje - 75) * 2)
    elif porcentaje >= 50:
        puntaje_demre = 500 + int((porcentaje - 50) * 4)
    elif porcentaje >= 25:
        puntaje_demre = 350 + int((porcentaje - 25) * 4)
    else:
        puntaje_demre = 250 + int(porcentaje * 4)
    
    puntaje_demre = min(1000, max(150, puntaje_demre))
    
    return {
        "puntaje_bruto": correctas,
        "puntaje_demre": puntaje_demre,
        "percentil_estimado": int(porcentaje),
        "nivel": "📘 Estimado",
        "rango_encontrado": "Aproximado"
    }

def obtener_nivel_demre(puntaje):
    """Obtiene el nivel de rendimiento basado en el puntaje DEMRE"""
    if puntaje >= 800:
        return {"nivel": "Excelente", "icono": "🌟", "color": "#4caf50", "descripcion": "Rendimiento sobresaliente"}
    elif puntaje >= 650:
        return {"nivel": "Bueno", "icono": "✅", "color": "#8bc34a", "descripcion": "Buen rendimiento"}
    elif puntaje >= 500:
        return {"nivel": "Regular", "icono": "📘", "color": "#ff9800", "descripcion": "Rendimiento aceptable"}
    else:
        return {"nivel": "Necesita mejorar", "icono": "📖", "color": "#f44336", "descripcion": "Áreas de mejora identificadas"}

def generar_recomendaciones(asignatura, puntaje_demre, correctas, incorrectas, omitidas):
    """Genera recomendaciones personalizadas basadas en el desempeño"""
    recomendaciones = []
    
    # Recomendaciones por puntaje
    if puntaje_demre >= 800:
        recomendaciones.append("🌟 ¡Excelente rendimiento! Estás en el nivel más alto.")
        recomendaciones.append("🎯 Sigue practicando para mantener tu nivel.")
        recomendaciones.append("📚 Revisa los temas más avanzados para seguir mejorando.")
    elif puntaje_demre >= 650:
        recomendaciones.append("✅ Buen rendimiento. Vas por buen camino.")
        recomendaciones.append("📝 Enfócate en los temas donde tienes más errores.")
        recomendaciones.append("⏰ Practica con preguntas de mayor dificultad.")
    elif puntaje_demre >= 500:
        recomendaciones.append("📘 Rendimiento regular. Puedes mejorar significativamente.")
        recomendaciones.append("📚 Dedica más tiempo a practicar con preguntas similares.")
        recomendaciones.append("📖 Repasa los conceptos básicos de la asignatura.")
    else:
        recomendaciones.append("📖 Necesitas mejorar. No te desanimes, ¡practica más!")
        recomendaciones.append("💪 Identifica tus áreas débiles y trabaja en ellas.")
        recomendaciones.append("📝 Comienza con preguntas más fáciles y aumenta gradualmente.")
    
    # Recomendaciones específicas por errores
    if incorrectas > correctas and incorrectas > 0:
        recomendaciones.append("⚠️ Tienes más respuestas incorrectas que correctas. Revisa los conceptos básicos.")
        recomendaciones.append("📖 Estudia la teoría antes de practicar.")
    
    if omitidas > 0:
        recomendaciones.append(f"⏳ Dejaste {omitidas} preguntas sin responder. Administra mejor tu tiempo.")
        if omitidas > 5:
            recomendaciones.append("🎯 Practica con simulacros completos para mejorar tu velocidad.")
    
    # Recomendaciones por asignatura
    recomendaciones_por_asignatura = {
        "Matemática 1": "📐 Practica ejercicios de álgebra y geometría diariamente.",
        "Matemática 2": "📊 Enfócate en funciones y probabilidades.",
        "Competencia Lectora": "📖 Lee textos variados y practica comprensión lectora.",
        "Historia y Ciencias Sociales": "📜 Estudia líneas de tiempo y conceptos clave.",
        "Ciencias": "🔬 Repasa experimentos y conceptos fundamentales.",
        "Inglés": "🌍 Practica vocabulario y comprensión de textos."
    }
    
    if asignatura in recomendaciones_por_asignatura:
        recomendaciones.append(recomendaciones_por_asignatura[asignatura])
    
    return recomendaciones

def obtener_estadisticas_detalladas(preguntas, respuestas):
    """Obtiene estadísticas detalladas de un intento"""
    total = len(preguntas)
    correctas = 0
    incorrectas = 0
    omitidas = 0
    por_dificultad = {"facil": {"correctas": 0, "incorrectas": 0, "omitidas": 0, "total": 0},
                      "media": {"correctas": 0, "incorrectas": 0, "omitidas": 0, "total": 0},
                      "dificil": {"correctas": 0, "incorrectas": 0, "omitidas": 0, "total": 0}}
    
    for p in preguntas:
        dificultad = p.get('dificultad', 'media')
        por_dificultad[dificultad]["total"] += 1
        
        if p['id'] in respuestas:
            if respuestas[p['id']] == p['correcta']:
                correctas += 1
                por_dificultad[dificultad]["correctas"] += 1
            else:
                incorrectas += 1
                por_dificultad[dificultad]["incorrectas"] += 1
        else:
            omitidas += 1
            por_dificultad[dificultad]["omitidas"] += 1
    
    # Calcular porcentajes por dificultad
    for dificultad in por_dificultad:
        total_d = por_dificultad[dificultad]["total"]
        if total_d > 0:
            por_dificultad[dificultad]["porcentaje_correctas"] = (por_dificultad[dificultad]["correctas"] / total_d) * 100
        else:
            por_dificultad[dificultad]["porcentaje_correctas"] = 0
    
    return {
        "total": total,
        "correctas": correctas,
        "incorrectas": incorrectas,
        "omitidas": omitidas,
        "por_dificultad": por_dificultad,
        "tasa_exito": (correctas / total * 100) if total > 0 else 0
    }

def generar_csv_resultados(resultado, estadisticas, asignatura, tiempo):
    """Genera un CSV con los resultados detallados"""
    import io
    
    data = {
        "Métrica": [
            "Asignatura", "Fecha", "Tiempo (segundos)", 
            "Total Preguntas", "Correctas", "Incorrectas", "Omitidas",
            "Tasa Éxito (%)", "Puntaje Bruto", "Puntaje DEMRE", 
            "Percentil", "Nivel"
        ],
        "Valor": [
            asignatura,
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            tiempo,
            estadisticas["total"],
            estadisticas["correctas"],
            estadisticas["incorrectas"],
            estadisticas["omitidas"],
            f"{estadisticas['tasa_exito']:.1f}",
            resultado["puntaje_bruto"],
            resultado["puntaje_demre"],
            resultado["percentil_estimado"],
            resultado["nivel"]
        ]
    }
    df = pd.DataFrame(data)
    
    # Agregar detalles por dificultad
    df_dificultad = pd.DataFrame([
        {"Dificultad": d, 
         "Total": stats["total"],
         "Correctas": stats["correctas"],
         "Incorrectas": stats["incorrectas"],
         "Omitidas": stats["omitidas"],
         "% Éxito": f"{stats['porcentaje_correctas']:.1f}"}
        for d, stats in estadisticas["por_dificultad"].items()
    ])
    
    return df, df_dificultad

def mostrar_resultados_demre(resultado, estadisticas, asignatura):
    """Muestra los resultados DEMRE en un formato visual"""
    
    nivel = obtener_nivel_demre(resultado['puntaje_demre'])
    
    html = f"""
    <div style="background: linear-gradient(135deg, {nivel['color']}, {nivel['color']}dd); 
                color: white; padding: 2rem; border-radius: 15px; 
                text-align: center; margin: 1rem 0;">
        <div style="font-size: 1.2rem; opacity: 0.9;">{nivel['icono']} {nivel['nivel']}</div>
        <div style="font-size: 4rem; font-weight: 700; margin: 0.5rem 0;">
            {resultado['puntaje_demre']}
        </div>
        <div style="font-size: 1rem; opacity: 0.9;">
            Puntaje DEMRE estimado - {asignatura}
        </div>
        <div style="font-size: 0.9rem; opacity: 0.7; margin-top: 0.5rem;">
            {estadisticas['correctas']}/{estadisticas['total']} correctas | 
            {resultado['percentil_estimado']}% percentil | 
            Tasa de éxito: {estadisticas['tasa_exito']:.1f}%
        </div>
    </div>
    """
    return html