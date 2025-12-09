# Mujer Sana IA 🩺🤖

## Descripción del Proyecto
**Mujer Sana IA** es una aplicación educativa y preventiva diseñada para abordar la alta mortalidad del cáncer de cuello uterino (CaCu) en la Región de Ñuble, Chile. 

El proyecto busca resolver las limitaciones del examen de Papanicolaou tradicional y las brechas de acceso en zonas rurales mediante el uso de **Inteligencia Artificial**. La solución combina educación personalizada con un sistema de apoyo al diagnóstico clínico basado en visión computacional.

## 🚀 Características Principales

El sistema se divide en módulos funcionales desarrollados bajo una metodología híbrida (Design Thinking + Incremental)

* **📚 Módulo Educativo:** Contenido interactivo (videos, reels) sobre el VPH, factores de riesgo y prevención adaptados a la usuaria.
* **⚠️ Evaluación de Riesgo:** Herramienta personalizada que identifica factores de riesgo (ej. tabaquismo, historial) y genera recomendaciones preventivas.
* **🧠 Módulo de IA (Visión Computacional):**
    * Implementación de **Redes Neuronales Convolucionales (CNN)** y modelos de segmentación **U-Net / nnU-Net**.
    * Capacidad para analizar imágenes de citología y colposcopía para identificar lesiones precancerosas.
    * Objetivo de métricas: Precisión diagnóstica ≥ 90% y Dice Score ≥ 0.80.

## 🛠️ Stack Tecnológico y Arquitectura
*(Basado en la propuesta técnica)*

* **Modelo de IA:** Python, Deep Learning (Segmentación Semántica).
* **Arquitectura:** Backend seguro con API REST, Frontend móvil/web y almacenamiento en la nube.
* **Infraestructura:** Despliegue propuesto en servicios Cloud (AWS/Azure).

## 🎯 Impacto Esperado
Este proyecto, enmarcado en el concurso FONIS 2026, busca:
1.  Reducir la variabilidad humana en el diagnóstico mediante IA objetiva.
2.  Facilitar el triage y la priorización de casos en zonas rurales.
3.  Empoderar a las pacientes mediante el acceso a información confiable.

## 📋 Aplicación Web CPC-28

Esta aplicación web permite administrar el cuestionario **CPC-28** (Creencias sobre el Papanicolaou y el Cáncer Cervicouterino) de forma digital y accesible desde cualquier dispositivo móvil o de escritorio.

### Características de la Aplicación Web

* ✅ **Diseño Responsive:** Optimizado para móviles, tablets y escritorio
* ✅ **Interfaz Intuitiva:** Navegación fácil con barra de progreso
* ✅ **Validación de Respuestas:** Asegura que todas las preguntas sean respondidas
* ✅ **Almacenamiento de Datos:** Guarda las respuestas en formato JSON
* ✅ **28 Preguntas Organizadas:** Divididas en 3 secciones temáticas

### Instalación y Uso

#### Requisitos Previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

#### Pasos de Instalación

1. **Clonar o descargar el proyecto** (si aplica)
   ```bash start.sh

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

4. **Acceder a la aplicación:**
   - Abre tu navegador web
   - Visita: `http://localhost:5000`
   - O desde otro dispositivo en la misma red: `http://[IP-DEL-SERVIDOR]:5000`

#### Estructura del Proyecto

```
Mujer Sana IA/
├── app.py                 # Servidor Flask principal
├── requirements.txt       # Dependencias del proyecto
├── templates/
│   └── index.html        # Página principal
├── static/
│   ├── css/
│   │   └── style.css     # Estilos responsive
│   └── js/
│       └── app.js        # Lógica del frontend
└── respuestas/           # Directorio donde se guardan las respuestas (se crea automáticamente)
```

#### Secciones del Cuestionario

1. **Sección A:** Barreras para adherir al tamizaje (9 preguntas)
2. **Sección B:** Señales de acción y motivación (12 preguntas)
3. **Sección C:** Severidad y susceptibilidad percibida (7 preguntas)

#### Opciones de Respuesta

Cada pregunta tiene 4 opciones:
- Muy de acuerdo
- De acuerdo
- En desacuerdo
- Muy en desacuerdo

### Desarrollo

Para ejecutar en modo desarrollo con recarga automática:
```bash
export FLASK_ENV=development
python app.py
```

### Notas de Seguridad

- Las respuestas se guardan localmente en el servidor
- No se almacena información personal identificable
- Cumple con normativas de privacidad de datos (Ley 19.628 y Ley 20.584)

## 👥 Autores e Investigadores
* **Alexander Acosta Zambrano**

---
*Este proyecto cumple con las normativas chilenas de privacidad de datos (Ley 19.628 y Ley 20.584) y utiliza datos clínicos anonimizados para su entrenamiento.*