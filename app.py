from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
import random
import re
import google.generativeai as genai  # Importamos la librería de Google
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE GEMINI ---
# Obtener la API KEY del archivo .env
GEMINI_API_KEY = "********************************"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Configuramos el modelo que usaremos (Flash es rápido y económico)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Cliente de Google Gemini configurado correctamente.")
else:
    model = None
    print("⚠️ GEMINI_API_KEY no configurada. La funcionalidad de IA estará deshabilitada.")

# Diccionario de videos educativos por categoría
# Referencias de videos:
# - MIEDO: https://www.youtube.com/watch?v=w0IGSfv-RXI
# - VERGUENZA: https://www.youtube.com/watch?v=RfvLpWviqS4, https://www.youtube.com/watch?v=5IFVtTf7YvI
# - MOTIVACION/RECOMENDACION: https://www.youtube.com/watch?v=SVF-rtQf3oU, https://www.youtube.com/watch?v=H1tKM5pZ7KA, https://www.youtube.com/watch?v=hM--fghdaUE
VIDEOS_EDUCATIVOS = {
    'MIEDO': {
        'url': 'https://www.youtube.com/embed/w0IGSfv-RXI',
        'titulo': 'Superando el miedo al Papanicolaou',
        'descripcion': 'Video educativo sobre cómo enfrentar el miedo al examen',
        'referencia': 'https://www.youtube.com/watch?v=w0IGSfv-RXI'
    },
    'VERGUENZA': {
        'url': 'https://www.youtube.com/embed/RfvLpWviqS4',
        'titulo': 'Entendiendo el Papanicolaou: Un examen rutinario',
        'descripcion': 'Información sobre la normalidad del procedimiento',
        'referencia': 'https://www.youtube.com/watch?v=RfvLpWviqS4',
        'alternativas': [
            {
                'url': 'https://www.youtube.com/embed/5IFVtTf7YvI',
                'titulo': 'Video alternativo sobre vergüenza',
                'referencia': 'https://www.youtube.com/watch?v=5IFVtTf7YvI'
            }
        ]
    },
    'MOTIVACION': {
        'url': 'https://www.youtube.com/embed/SVF-rtQf3oU',
        'titulo': 'La importancia del Papanicolaou para tu salud',
        'descripcion': 'Video motivacional sobre la importancia del tamizaje',
        'referencia': 'https://www.youtube.com/watch?v=SVF-rtQf3oU',
        'alternativas': [
            {
                'url': 'https://www.youtube.com/embed/H1tKM5pZ7KA',
                'titulo': 'Video motivacional alternativo 1',
                'referencia': 'https://www.youtube.com/watch?v=H1tKM5pZ7KA'
            },
            {
                'url': 'https://www.youtube.com/embed/hM--fghdaUE',
                'titulo': 'Video motivacional alternativo 2',
                'referencia': 'https://www.youtube.com/watch?v=hM--fghdaUE'
            }
        ]
    },
    'BARRERAS_LOGISTICAS': {
        'url': 'https://www.youtube.com/embed/H1tKM5pZ7KA',
        'titulo': 'Cómo agendar tu Papanicolaou en el CESFAM',
        'descripcion': 'Guía práctica para agendar tu examen',
        'referencia': 'https://www.youtube.com/watch?v=H1tKM5pZ7KA'
    },
    'PRIORIDAD_ALTA': {
        'url': 'https://www.youtube.com/embed/hM--fghdaUE',
        'titulo': 'Tu primer Papanicolaou: Todo lo que necesitas saber',
        'descripcion': 'Información completa para tu primer examen',
        'referencia': 'https://www.youtube.com/watch?v=hM--fghdaUE'
    },
    'GENERAL': {
        'url': 'https://www.youtube.com/embed/SVF-rtQf3oU',
        'titulo': 'Papanicolaou: Prevención del cáncer cervicouterino',
        'descripcion': 'Video educativo general sobre el Papanicolaou',
        'referencia': 'https://www.youtube.com/watch?v=SVF-rtQf3oU'
    }
}

# Estructura del cuestionario CPC-28
CUESTIONARIO = {
    "titulo": "CPC-28 - Cuestionario sobre Creencias del Papanicolaou y el Cáncer de Cuello Uterino",
    "secciones": [
        {
            "id": "PRESENTACION",
            "titulo": "I. PRESENTACIÓN Y CONSENTIMIENTO INFORMADO",
            "preguntas": [
                {
                    "id": "PRESENTACION_INFO",
                    "texto": "Bienvenida",
                    "tipo": "texto_informativo",
                    "contenido": "Gracias por participar en esta iniciativa pionera. Usted ha sido invitada a formar parte de \"Mujer Sana IA\", un proyecto de investigación y desarrollo tecnológico enfocado en la salud integral de la mujer."
                },
                {
                    "id": "PRESENTACION_OBJETIVO",
                    "texto": "Objetivo del Estudio",
                    "tipo": "texto_informativo",
                    "contenido": "El propósito de este cuestionario es recopilar información multidimensional (biológica, psicológica, reproductiva y social) para entrenar un modelo de Inteligencia Artificial especializado. Su participación permitirá crear algoritmos capaces de detectar riesgos tempranos, personalizar recomendaciones de salud y mejorar la calidad de vida de mujeres mediante tecnología predictiva."
                },
                {
                    "id": "PRESENTACION_CONFIDENCIALIDAD",
                    "texto": "Confidencialidad y Manejo de Datos",
                    "tipo": "texto_informativo",
                    "contenido": "Entendemos que la información solicitada es de carácter sensible. Queremos garantizarle que:\n\n1. Privacidad: Sus respuestas serán tratadas con estricta confidencialidad bajo los protocolos de seguridad de datos vigentes (Ley 19.628 sobre Protección de la Vida Privada).\n2. Uso de Datos: Su RUT y Nombre se solicitan únicamente para fines de registro único y seguimiento longitudinal. Estos datos serán encriptados y no serán compartidos con terceros.\n3. Voluntariedad: No hay respuestas \"correctas\" o \"incorrectas\". Lo más importante es su sinceridad para que la IA pueda aprender de casos reales."
                },
                {
                    "id": "PRESENTACION_INSTRUCCIONES",
                    "texto": "Instrucciones",
                    "tipo": "texto_informativo",
                    "contenido": "Por favor, responda todas las preguntas con la mayor honestidad posible. Si alguna pregunta le resulta incómoda o prefiere no responderla, tendrá la opción de omitirla en las secciones sensibles."
                },
                {
                    "id": "DATOS_FECHA",
                    "texto": "Fecha de Ingreso de la Encuesta",
                    "tipo": "fecha",
                    "formato": "DD/MM/AAAA",
                    "obligatorio": True
                },
                {
                    "id": "DATOS_NOMBRE",
                    "texto": "Nombre Completo",
                    "tipo": "texto",
                    "obligatorio": True
                },
                {
                    "id": "DATOS_RUT",
                    "texto": "R.U.T. (con dígito verificador)",
                    "tipo": "texto",
                    "placeholder": "Ej: 12345678-9",
                    "obligatorio": True
                },
                {
                    "id": "DATOS_EMAIL",
                    "texto": "Correo Electrónico de Contacto",
                    "tipo": "email",
                    "obligatorio": True
                },
                {
                    "id": "DATOS_TELEFONO",
                    "texto": "Teléfono (Opcional)",
                    "tipo": "texto",
                    "placeholder": "+56",
                    "obligatorio": False
                },
                {
                    "id": "CONSENTIMIENTO",
                    "texto": "Acepto participar voluntariamente: He leído la información anterior, comprendo el objetivo de \"Mujer Sana IA\" y acepto entregar mis datos para fines de investigación y análisis de salud, entendiendo que mi identidad será protegida.",
                    "tipo": "consentimiento",
                    "obligatorio": True
                }
            ]
        },
        {
            "id": "I",
            "titulo": "II. PERFIL Y DETERMINANTES SOCIALES",
            "preguntas": [
                {
                    "id": "I2",
                    "texto": "¿Cuál es el género con el que Usted se identifica?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "masculino", "texto": "Masculino"},
                        {"valor": "femenino", "texto": "Femenino"},
                        {"valor": "transmasculino", "texto": "Transmasculino u hombre trans"},
                        {"valor": "transfemenino", "texto": "Transfemenino o mujer trans"},
                        {"valor": "no_binario", "texto": "No binario"},
                        {"valor": "otro", "texto": "Otro"},
                        {"valor": "prefiere_no_responder", "texto": "Prefiere no responder"}
                    ]
                },
                {
                    "id": "I3",
                    "texto": "¿Qué edad tiene? (años)",
                    "tipo": "numero",
                    "unidad": "años"
                },
                {
                    "id": "I4",
                    "texto": "¿Cuál es su nivel educacional más alto alcanzado?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "basica", "texto": "Educación Básica (Primaria)"},
                        {"valor": "media", "texto": "Educación Media (Secundaria)"},
                        {"valor": "tecnico", "texto": "Técnico Nivel Superior"},
                        {"valor": "profesional", "texto": "Profesional (Universitario)"},
                        {"valor": "postgrado", "texto": "Postgrado"},
                        {"valor": "otro", "texto": "Otro / Ninguno"}
                    ]
                },
                {
                    "id": "I5",
                    "texto": "¿Cuál es su estado conyugal o civil actual?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "casada", "texto": "Casada(o) / Conviviente Civil"},
                        {"valor": "conviviente", "texto": "Conviviente o pareja (sin acuerdo legal)"},
                        {"valor": "soltera", "texto": "Soltera(o)"},
                        {"valor": "separada", "texto": "Separada(o) / Divorciada(o) / Anulada(o)"},
                        {"valor": "viuda", "texto": "Viuda(o)"}
                    ]
                },
                {
                    "id": "I6",
                    "texto": "Actualmente, ¿Usted tiene pareja?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"}
                    ]
                }
            ]
        },
        {
            "id": "II",
            "titulo": "III. HISTORIA CLÍNICA Y BIOMETRÍA",
            "preguntas": [
                {
                    "id": "II1",
                    "texto": "¿Alguna vez un doctor o médico le ha dicho que tiene o padece de alguna de las siguientes condiciones? (Marque todas las que correspondan)",
                    "tipo": "opcion_multiple",
                    "opciones": [
                        {"valor": "migranas", "texto": "Migrañas o dolores de cabeza frecuentes"},
                        {"valor": "trastorno_musculoesqueletico", "texto": "Trastorno musculoesquelético (dolor crónico espalda, etc.)"},
                        {"valor": "diabetes", "texto": "Diabetes"},
                        {"valor": "tiroides", "texto": "Enfermedad a la tiroides (hipotiroidismo, hipertiroidismo, bocio)"},
                        {"valor": "sobrepeso", "texto": "Sobrepeso u obesidad"},
                        {"valor": "hipertension", "texto": "Hipertensión"},
                        {"valor": "infertilidad", "texto": "Infertilidad"},
                        {"valor": "ninguno", "texto": "Ninguno"}
                    ]
                },
                {
                    "id": "II2",
                    "texto": "Datos Biométricos (Aproximados)",
                    "tipo": "subpreguntas",
                    "preguntas": [
                        {
                            "id": "II2A",
                            "texto": "Peso actual (Kg)",
                            "tipo": "numero",
                            "unidad": "Kg"
                        },
                        {
                            "id": "II2B",
                            "texto": "Estatura (cm)",
                            "tipo": "numero",
                            "unidad": "cm"
                        }
                    ]
                },
                {
                    "id": "II3",
                    "texto": "¿Alguna vez se ha realizado...?",
                    "tipo": "subpreguntas",
                    "preguntas": [
                        {
                            "id": "II3A",
                            "texto": "Una mamografía",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": "si", "texto": "Sí"},
                                {"valor": "no", "texto": "No"}
                            ]
                        },
                        {
                            "id": "II3B",
                            "texto": "Un papanicolaou (PAP)",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": "si", "texto": "Sí"},
                                {"valor": "no", "texto": "No"}
                            ]
                        }
                    ]
                },
                {
                    "id": "II4",
                    "texto": "(Si respondió SÍ en la anterior) ¿Se ha realizado estos exámenes en los últimos 3 años?",
                    "tipo": "subpreguntas",
                    "condicional": True,
                    "preguntas": [
                        {
                            "id": "II4A",
                            "texto": "Mamografía",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": "si", "texto": "Sí"},
                                {"valor": "no", "texto": "No"}
                            ]
                        },
                        {
                            "id": "II4B",
                            "texto": "Papanicolaou",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": "si", "texto": "Sí"},
                                {"valor": "no", "texto": "No"}
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "III",
            "titulo": "IV. SALUD SEXUAL Y REPRODUCTIVA",
            "preguntas": [
                {
                    "id": "III1",
                    "texto": "¿A qué edad aproximadamente tuvo su primera menstruación o regla?",
                    "tipo": "numero",
                    "unidad": "años"
                },
                {
                    "id": "III2",
                    "texto": "¿Ha tenido menstruación o regla en el último año?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"}
                    ]
                },
                {
                    "id": "III3",
                    "texto": "(Si respondió NO) ¿Cuál es la razón por la cual no ha tenido menstruación?",
                    "tipo": "opcion_unica",
                    "condicional": True,
                    "opciones": [
                        {"valor": "embarazo", "texto": "Embarazo o Lactancia"},
                        {"valor": "menopausia", "texto": "Menopausia"},
                        {"valor": "histerectomia", "texto": "Histerectomía (le sacaron el útero)"},
                        {"valor": "tratamiento_hormonal", "texto": "Tratamiento hormonal / anticonceptivo que corta la regla"},
                        {"valor": "otra", "texto": "Otra razón"}
                    ]
                },
                {
                    "id": "III4",
                    "texto": "(Si aplica Menopausia) ¿Ha tomado hormonas (terapia hormonal) para la menopausia?",
                    "tipo": "opcion_unica",
                    "condicional": True,
                    "opciones": [
                        {"valor": "nunca", "texto": "Nunca"},
                        {"valor": "pasado", "texto": "Sí, en el pasado"},
                        {"valor": "actualmente", "texto": "Sí, actualmente"}
                    ]
                },
                {
                    "id": "III5",
                    "texto": "¿Ha estado embarazada alguna vez en su vida?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"}
                    ]
                },
                {
                    "id": "III6",
                    "texto": "¿Cuántos embarazos ha tenido a lo largo de su vida? (Incluya partos, abortos o pérdidas)",
                    "tipo": "numero",
                    "condicional": True,
                    "depende_de": "IV5",
                    "requiere_valor": "si"
                },
                {
                    "id": "III7",
                    "texto": "Su último embarazo terminó con:",
                    "tipo": "opcion_unica",
                    "condicional": True,
                    "depende_de": "IV5",
                    "requiere_valor": "si",
                    "opciones": [
                        {"valor": "parto_termino", "texto": "Parto de término (vivo)"},
                        {"valor": "parto_prematuro", "texto": "Parto prematuro (vivo)"},
                        {"valor": "perdida_mayor", "texto": "Pérdida o mortinato (mayor a 13 semanas)"},
                        {"valor": "perdida_menor", "texto": "Pérdida o aborto (menor o igual a 12 semanas)"}
                    ]
                },
                {
                    "id": "III8",
                    "texto": "(Si tuvo parto) ¿Algún médico(a) le diagnosticó depresión postparto?",
                    "tipo": "opcion_unica",
                    "condicional": True,
                    "depende_de": "IV7",
                    "requiere_valor": ["parto_termino", "parto_prematuro"],
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"}
                    ]
                }
            ]
        },
        {
            "id": "A",
            "titulo": "V. BARRERAS PARA ADHERIR AL TAMIZAJE REPORTADAS POR LAS MUJERES",
            "preguntas": [
                {
                    "id": "A1",
                    "texto": "Yo no sé a qué edad es necesario tomarse el Pap"
                },
                {
                    "id": "A2",
                    "texto": "Yo no sé cada cuanto tiempo necesito ir a tomarme el Pap"
                },
                {
                    "id": "A3",
                    "texto": "No me tomo el Pap porque cuando voy necesito esperar largo tiempo para ser atendida"
                },
                {
                    "id": "A4",
                    "texto": "No me tomo el Pap porque cuesta mucho sacar una hora de atención"
                },
                {
                    "id": "A5",
                    "texto": "No me tomo el Pap porque el consultorio atiende en horarios en los que no puedo ir"
                },
                {
                    "id": "A6",
                    "texto": "No me tomo el Pap porque me da miedo saber que tengo cáncer"
                },
                {
                    "id": "A7",
                    "texto": "No me tomo el Pap porque me da vergüenza que me examinen los genitales"
                },
                {
                    "id": "A8",
                    "texto": "No me tomo el Pap porque en el consultorio me tratan mal"
                },
                {
                    "id": "A9",
                    "texto": "No tengo tiempo para tomarme el Pap"
                }
            ]
        },
        {
            "id": "B",
            "titulo": "VI. SEÑALES DE ACCIÓN (MOTIVACIÓN) PARA ADHERIR AL TAMIZAJE REPORTADAS POR LAS MUJERES",
            "preguntas": [
                {
                    "id": "B1",
                    "texto": "Porque un doctor me lo pide"
                },
                {
                    "id": "B2",
                    "texto": "Porque una enfermera o matrona me lo pide"
                },
                {
                    "id": "B3",
                    "texto": "Porque escuche o lei en el diario o en algún programa de televisión o radio"
                },
                {
                    "id": "B4",
                    "texto": "Porque mi madre me habla sobre eso"
                },
                {
                    "id": "B5",
                    "texto": "Porque miembros de mi familia me dijeron que lo tomara"
                },
                {
                    "id": "B6",
                    "texto": "Porque mi amiga o vecina me habla sobre eso"
                },
                {
                    "id": "B7",
                    "texto": "Tomarme el Pap me hace sentir bien porque significa que yo cuido de mi salud"
                },
                {
                    "id": "B8",
                    "texto": "Una razón para tomarme el Pap es cuidar de mi salud"
                },
                {
                    "id": "B9",
                    "texto": "El Pap puede salvar mi vida"
                },
                {
                    "id": "B10",
                    "texto": "Si no he tenido hijos, no necesito tomarme el Pap"
                },
                {
                    "id": "B11",
                    "texto": "Si no estoy teniendo relaciones sexuales, no necesito tomarme el Pap"
                },
                {
                    "id": "B12",
                    "texto": "Si no tengo síntomas o molestias, no necesito tomarme el Pap"
                }
            ]
        },
        {
            "id": "C",
            "titulo": "VII. SEVERIDAD DEL CÁNCER CÉRVICOUTERINO Y SUSCEPTIBILIDAD PERCIBIDA PARA DESARROLLARLO REPORTADA POR LAS MUJERES",
            "preguntas": [
                {
                    "id": "C1",
                    "texto": "El cáncer cérvicouterino es un problema de salud serio"
                },
                {
                    "id": "C2",
                    "texto": "El cáncer cérvicouterino puede llevar a una mujer a tener que realizarse un tratamiento con quimioterapia o radioterapia"
                },
                {
                    "id": "C3",
                    "texto": "El cáncer cérvicouterino puede llevar a una mujer a tener que someterse a una histerectomía"
                },
                {
                    "id": "C4",
                    "texto": "El cáncer cérvicouterino puede causar la muerte"
                },
                {
                    "id": "C5",
                    "texto": "Yo tengo riesgo de desarrollar un cáncer cérvicouterino"
                },
                {
                    "id": "C6",
                    "texto": "Si yo tengo cáncer cérvicouterino me puedo morir"
                },
                {
                    "id": "C7",
                    "texto": "El cáncer cérvicouterino es uno de los cánceres más comunes entre las mujeres de mi edad"
                }
            ]
        }
    ],
    "opciones": [
        {"valor": 4, "texto": "Muy de acuerdo"},
        {"valor": 3, "texto": "De acuerdo"},
        {"valor": 2, "texto": "En desacuerdo"},
        {"valor": 1, "texto": "Muy en desacuerdo"}
    ]
}

# ---------------- Validaciones de entrada ----------------

def rut_valido(rut):
    """Valida un RUT chileno aplicando el algoritmo módulo 11.
    Acepta formatos como '12.345.678-5', '12345678-5' o '123456785'.
    Devuelve True si es válido, False en otro caso.
    """
    if not rut:
        return False
    try:
        s = str(rut).strip()
        # Eliminar espacios y puntos
        s = s.replace('.', '').replace(' ', '')
        # Separar cuerpo y dígito verificador si hay guion
        if '-' in s:
            cuerpo, dv = s.split('-')
        else:
            cuerpo, dv = s[:-1], s[-1]
        dv = dv.upper()
        if not cuerpo.isdigit() or len(cuerpo) == 0:
            return False

        suma = 0
        multiplicador = 2
        for digit in reversed(cuerpo):
            suma += int(digit) * multiplicador
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2

        resto = 11 - (suma % 11)
        if resto == 11:
            dv_calc = '0'
        elif resto == 10:
            dv_calc = 'K'
        else:
            dv_calc = str(resto)

        return dv == dv_calc
    except Exception:
        return False

def validar_email(email):
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+'
    return re.match(pattern, email) is not None

def validar_telefono(tel):
    if tel is None or tel == '':
        return True  # Opcional
    if not isinstance(tel, str):
        return False
    cleaned = re.sub(r'[\s\-()]+', '', tel)
    return re.match(r'^\+?[0-9]{8,15}$', cleaned) is not None

def validar_respuestas(respuestas):
    errors = []
    # Nombre (obligatorio)
    nombre = respuestas.get('DATOS_NOMBRE')
    if not nombre or not isinstance(nombre, str) or len(nombre.strip().split()) < 2:
        errors.append('DATOS_NOMBRE: Nombre completo requerido (nombre y apellido).')

    # RUT (obligatorio)
    rut = respuestas.get('DATOS_RUT')
    if not rut or not rut_valido(str(rut)):
        errors.append('DATOS_RUT: RUT inválido. Formato esperado 12345678-9')

    # Email (obligatorio)
    email = respuestas.get('DATOS_EMAIL')
    if not email or not validar_email(str(email)):
        errors.append('DATOS_EMAIL: Correo electrónico inválido.')

    # Teléfono (opcional)
    telefono = respuestas.get('DATOS_TELEFONO')
    if telefono is not None and telefono != '' and not validar_telefono(str(telefono)):
        errors.append('DATOS_TELEFONO: Teléfono inválido.')

    # Edad I3 (si presente validar rango)
    edad = respuestas.get('I3')
    if edad is not None and edad != '':
        try:
            edad_n = int(edad)
            if edad_n < 10 or edad_n > 120:
                errors.append('I3: Edad fuera de rango (10-120).')
        except Exception:
            errors.append('I3: Edad debe ser un número entero.')

    # Peso II2A (si presente)
    peso = respuestas.get('II2A')
    if peso is not None and peso != '':
        try:
            p = float(peso)
            if p < 20 or p > 300:
                errors.append('II2A: Peso fuera de rango (20-300 Kg).')
        except Exception:
            errors.append('II2A: Peso debe ser numérico.')

    # Estatura II2B (si presente)
    est = respuestas.get('II2B')
    if est is not None and est != '':
        try:
            h = float(est)
            if h < 50 or h > 250:
                errors.append('II2B: Estatura fuera de rango (50-250 cm).')
        except Exception:
            errors.append('II2B: Estatura debe ser numérica.')

    return (len(errors) == 0, errors)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cuestionario', methods=['GET'])
def get_cuestionario():
    return jsonify(CUESTIONARIO)

def analizar_respuestas_cpc28(respuestas):
    """
    Analiza las respuestas del cuestionario CPC-28 y genera recomendaciones personalizadas.
    Actúa como 'Mujer Sana IA', una asistente virtual experta en salud ginecológica.
    """
    recomendaciones = []
    prioridad_alta = False
    
    # 1. Analizar Barreras (Sección A)
    barreras_emocionales = []
    barreras_logisticas = []
    
    # Miedo al cáncer (A6)
    if respuestas.get('A6') and respuestas['A6'] >= 3:  # De acuerdo o Muy de acuerdo
        barreras_emocionales.append('miedo')
    
    # Vergüenza (A7)
    if respuestas.get('A7') and respuestas['A7'] >= 3:
        barreras_emocionales.append('verguenza')
    
    # Dolor o espera (A3)
    if respuestas.get('A3') and respuestas['A3'] >= 3:
        barreras_logisticas.append('espera')
    
    # 2. Analizar Motivación (Sección B)
    falta_recordatorios = True
    if respuestas.get('B1') and respuestas['B1'] >= 3:  # Doctor le pide
        falta_recordatorios = False
    if respuestas.get('B2') and respuestas['B2'] >= 3:  # Enfermera/matrona le pide
        falta_recordatorios = False
    
    # 3. Contexto Demográfico
    edad = respuestas.get('I3')
    nunca_pap = False
    
    # Verificar si se ha hecho PAP (II3B)
    if respuestas.get('II3B') == 'no':
        nunca_pap = True
    
    # Prioridad alta: >25 años y nunca se ha hecho PAP
    if edad and edad > 25 and nunca_pap:
        prioridad_alta = True
    
    # Construir recomendaciones
    parrafo1 = ""
    parrafo2 = ""
    parrafo3 = ""
    
    # Párrafo 1: Mensaje principal (sin enfoque emocional)
    if prioridad_alta:
        parrafo1 = f"Hola, veo que tienes {edad} años y aún no te has realizado el Papanicolaou. Este examen es esencial para tu salud, especialmente a partir de los 25 años según las recomendaciones del MINSAL. No te preocupes, nunca es tarde para empezar a cuidarte."
    else:
        parrafo1 = "Gracias por completar el cuestionario. El Papanicolaou es una herramienta clave para prevenir el cáncer de cuello uterino y cuidar tu salud."
    
    # Párrafo 2: Motivación y recordatorios
    if falta_recordatorios:
        parrafo2 = "Noto que no has recibido recordatorios recientes de profesionales de salud sobre el PAP. Te sugiero que pidas a tu médico o matrona que te recuerde en tu próxima consulta, o bien, puedes activar recordatorios en tu calendario personal. También puedes agendar tu hora hoy mismo en tu CESFAM más cercano."
    elif barreras_logisticas:
        parrafo2 = "Entiendo que los tiempos de espera pueden ser un desafío. Te recomiendo llamar temprano en la mañana para agendar tu hora, o consultar si hay horarios de atención extendida en tu consultorio. Tu salud vale la pena el esfuerzo."
    elif prioridad_alta:
        parrafo2 = "El cáncer de cuello uterino es prevenible cuando se detecta a tiempo. El Papanicolaou es gratuito en la red pública de salud y está disponible en todos los CESFAM. No requiere preparación especial y es un examen rápido que puede salvar tu vida."
    else:
        parrafo2 = "Mantener tus controles al día es la mejor forma de cuidarte. El Papanicolaou debe realizarse cada 3 años si tus resultados anteriores fueron normales, según las guías del MINSAL."
    
    # Párrafo 3: Llamado a la acción
    if prioridad_alta:
        parrafo3 = "Te invito a agendar tu hora para el Papanicolaou esta semana en tu CESFAM. Puedes llamar al consultorio o acercarte personalmente. Si tienes dudas, puedes hablar con una matrona que te explicará todo el proceso. Tu salud es prioridad, y este examen es un acto de autocuidado importante."
    elif barreras_emocionales or barreras_logisticas:
        parrafo3 = "Si te sientes lista, agenda tu hora en el CESFAM. Recuerda que puedes pedir que te atienda una profesional mujer si eso te hace sentir más cómoda. El examen es rápido, y estarás cuidando tu salud de la mejor manera posible."
    else:
        parrafo3 = "Mantén tus controles al día. Si ya pasaron más de 3 años desde tu último PAP, agenda tu hora en el CESFAM. Si tienes dudas, consulta con tu matrona o médico de cabecera."
    
    # Combinar párrafos
    recomendacion_completa = f"{parrafo1}\n\n{parrafo2}\n\n{parrafo3}"
    
    # Determinar categoría de video
    categoria_video = 'GENERAL'
    if 'miedo' in barreras_emocionales:
        categoria_video = 'MIEDO'
    elif 'verguenza' in barreras_emocionales:
        categoria_video = 'VERGUENZA'
    elif prioridad_alta:
        categoria_video = 'PRIORIDAD_ALTA'
    elif falta_recordatorios:
        categoria_video = 'MOTIVACION'
    elif barreras_logisticas:
        categoria_video = 'BARRERAS_LOGISTICAS'
        
    video_obj = VIDEOS_EDUCATIVOS.get(categoria_video, VIDEOS_EDUCATIVOS['GENERAL'])
    video_alt = None
    if isinstance(video_obj, dict) and 'alternativas' in video_obj and video_obj['alternativas']:
        video_alt = video_obj['alternativas'][0]
    
    return {
        'recomendacion': recomendacion_completa,
        'prioridad_alta': prioridad_alta,
        'barreras_detectadas': {
            'emocionales': barreras_emocionales,
            'logisticas': barreras_logisticas
        },
        'falta_recordatorios': falta_recordatorios,
        'categoria_video': categoria_video,
        'video': video_obj,
        'video_alt': video_alt
    }

def generar_recomendacion_ia(respuestas, datos_demograficos=None):
    """
    Genera una recomendación personalizada usando la API de Google Gemini.
    """
    if not model:
        print("Error: Modelo Gemini no inicializado. Configure GEMINI_API_KEY.")
        return None
    
    try:
        # Prompt del Sistema (Instrucciones de comportamiento)
        system_instruction = """Eres una matrona experta de la aplicación 'Mujer Sana IA'. Tu misión es analizar las respuestas de un cuestionario sobre el PAP y generar un consejo personalizado.
        
        Debes actuar con un tono empático, cercano y adaptado a la cultura de Chile (usando un lenguaje suave y acogedor).
        
        Tu salida debe ser SIEMPRE un objeto JSON estricto con la siguiente estructura:
        {
            "consejo": "Texto de exactamente 3 párrafos: 1. Validación emocional, 2. Análisis de barreras, 3. Pasos a seguir.",
            "categoria_video": "Una de las siguientes opciones: MIEDO, VERGUENZA, MOTIVACION, BARRERAS_LOGISTICAS, PRIORIDAD_ALTA, GENERAL"
        }
        """

        # Prompt del Usuario (Datos a analizar)
        user_prompt = f"""Por favor analiza los siguientes datos y genera el JSON solicitado:
        
        RESPUESTAS DEL CUESTIONARIO:
        {json.dumps(respuestas, indent=2, ensure_ascii=False)}
        DATOS DEMOGRÁFICOS:
        {json.dumps(datos_demograficos or {}, indent=2, ensure_ascii=False)}
        """
        
        # Configuración de generación para forzar JSON
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7
        )

        # Llamada a Gemini
        # Combinamos las instrucciones del sistema y el prompt del usuario
        full_prompt = system_instruction + "\n\n" + user_prompt
        
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        # Procesar respuesta
        respuesta_texto = response.text
        
        # Parsear el JSON
        try:
            respuesta_json = json.loads(respuesta_texto)
            consejo = respuesta_json.get('consejo', '')
            categoria_video = respuesta_json.get('categoria_video', 'GENERAL').upper()
            
            # Validar que la categoría exista, si no, usar GENERAL
            if categoria_video not in VIDEOS_EDUCATIVOS:
                categoria_video = 'GENERAL'
            
            video = VIDEOS_EDUCATIVOS[categoria_video]
            video_alt = None
            if isinstance(video, dict) and 'alternativas' in video and video['alternativas']:
                video_alt = video['alternativas'][0]
            
            return {
                'consejo': consejo,
                'video': video,
                'video_alt': video_alt,
                'categoria': categoria_video
            }
            
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON de Gemini: {str(e)}")
            # Fallback en caso de error de parseo
            return {
                'consejo': "Hubo un pequeño error técnico al generar el consejo, pero recuerda que realizarte el PAP es fundamental para tu salud. Acude a tu CESFAM más cercano.",
                'video': VIDEOS_EDUCATIVOS['GENERAL'],
                'video_alt': VIDEOS_EDUCATIVOS['GENERAL'].get('alternativas', [None])[0] if isinstance(VIDEOS_EDUCATIVOS['GENERAL'], dict) else None,
                'categoria': 'GENERAL'
            }
            
    except Exception as e:
        print(f"Error crítico al conectar con Gemini: {str(e)}")
        return None

@app.route('/api/respuestas', methods=['POST'])
def guardar_respuestas():
    try:
        data = request.json
        respuestas = data.get('respuestas', {})
        timestamp = data.get('timestamp')
        usar_ia = data.get('usar_ia', False)
        # Validar campos críticos antes de guardar
        valido, errores = validar_respuestas(respuestas)
        if not valido:
            return jsonify({'success': False, 'message': 'Errores de validación', 'errors': errores}), 400
        
        os.makedirs('respuestas', exist_ok=True)
        
        filename = f"respuestas/respuestas_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'respuestas': respuestas
            }, f, indent=2, ensure_ascii=False)
        
        response_data = {
            'success': True,
            'message': 'Respuestas guardadas correctamente',
            'filename': filename
        }
        
        if usar_ia:
            if model: # Verificamos si Gemini está configurado
                datos_demograficos = {
                    'edad': respuestas.get('I3'),
                    'sexo_asignado': respuestas.get('I1'),
                    'genero': respuestas.get('I2'),
                    'nivel_educacional': respuestas.get('I4'),
                    'estado_civil': respuestas.get('I5'),
                    'tiene_pareja': respuestas.get('I6')
                }
                
                resultado_ia = generar_recomendacion_ia(respuestas, datos_demograficos)
                
                if resultado_ia:
                    response_data['recomendacion_ia'] = {
                        'consejo': resultado_ia.get('consejo', ''),
                        'video': resultado_ia.get('video', VIDEOS_EDUCATIVOS['GENERAL']),
                        'video_alt': resultado_ia.get('video_alt'),
                        'categoria': resultado_ia.get('categoria', 'GENERAL')
                    }
                else:
                    response_data['recomendacion_ia'] = None
                    response_data['mensaje_ia'] = 'No se pudo generar la recomendación con IA'
            else:
                response_data['recomendacion_ia'] = None
                response_data['mensaje_ia'] = 'API Key de Gemini no configurada.'
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al guardar respuestas: {str(e)}'
        }), 500

# Endpoint de análisis manual (sin IA)
@app.route('/api/analisis', methods=['POST'])
def analizar_respuestas():
    try:
        data = request.json
        respuestas = data.get('respuestas', {})
        
        if not respuestas:
            return jsonify({'success': False, 'message': 'No se proporcionaron respuestas'}), 400
        # Validar datos antes del análisis
        valido, errores = validar_respuestas(respuestas)
        if not valido:
            return jsonify({'success': False, 'message': 'Errores de validación', 'errors': errores}), 400
        
        # Asegúrate de descomentar o incluir tu función analizar_respuestas_cpc28 completa arriba
        analisis_datos = analizar_respuestas_cpc28(respuestas)
        
        return jsonify({
            'success': True, 
            'analisis': {
                'recomendacion': analisis_datos['recomendacion'],
                'video': analisis_datos['video'],
                'video_alt': analisis_datos.get('video_alt'),
                'categoria': analisis_datos['categoria_video'],
                'fuente': 'tradicional'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
