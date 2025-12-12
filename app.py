from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Estructura del cuestionario CPC-28
CUESTIONARIO = {
    "titulo": "CPC-28 - Cuestionario sobre Creencias del Papanicolaou y el Cáncer Cervicouterino",
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
                    "id": "I1",
                    "texto": "¿Cuál es su sexo asignado al nacer?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "hombre", "texto": "Hombre"},
                        {"valor": "mujer", "texto": "Mujer"}
                    ]
                },
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
            "titulo": "III. SALUD MENTAL Y BIENESTAR GENERAL",
            "preguntas": [
                {
                    "id": "II1",
                    "texto": "¿Cómo calificaría su calidad de vida?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": 1, "texto": "Muy mala"},
                        {"valor": 2, "texto": "Mala"},
                        {"valor": 3, "texto": "Ni buena ni mala"},
                        {"valor": 4, "texto": "Buena"},
                        {"valor": 5, "texto": "Muy buena"}
                    ]
                },
                {
                    "id": "II2",
                    "texto": "Durante las dos últimas semanas, ¿con qué frecuencia ha sentido molestias debido a los siguientes problemas?",
                    "tipo": "subpreguntas",
                    "instrucciones": "Escala: 1. Nunca | 2. Algunos días | 3. Más de la mitad de los días | 4. Casi todos los días",
                    "preguntas": [
                        {
                            "id": "II2A",
                            "texto": "Siente poco interés o placer en hacer cosas",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": 1, "texto": "Nunca"},
                                {"valor": 2, "texto": "Algunos días"},
                                {"valor": 3, "texto": "Más de la mitad de los días"},
                                {"valor": 4, "texto": "Casi todos los días"}
                            ]
                        },
                        {
                            "id": "II2B",
                            "texto": "Se ha sentido decaído(a), deprimido(a) o sin esperanzas",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": 1, "texto": "Nunca"},
                                {"valor": 2, "texto": "Algunos días"},
                                {"valor": 3, "texto": "Más de la mitad de los días"},
                                {"valor": 4, "texto": "Casi todos los días"}
                            ]
                        },
                        {
                            "id": "II2C",
                            "texto": "Se ha sentido nervioso(a), ansioso(a) o con los nervios de punta",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": 1, "texto": "Nunca"},
                                {"valor": 2, "texto": "Algunos días"},
                                {"valor": 3, "texto": "Más de la mitad de los días"},
                                {"valor": 4, "texto": "Casi todos los días"}
                            ]
                        },
                        {
                            "id": "II2D",
                            "texto": "No ha sido capaz de parar o controlar su preocupación",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": 1, "texto": "Nunca"},
                                {"valor": 2, "texto": "Algunos días"},
                                {"valor": 3, "texto": "Más de la mitad de los días"},
                                {"valor": 4, "texto": "Casi todos los días"}
                            ]
                        }
                    ]
                },
                {
                    "id": "II3",
                    "texto": "¿Alguna vez un doctor o médico le ha dicho que tiene o padece de Depresión?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"}
                    ]
                }
            ]
        },
        {
            "id": "III",
            "titulo": "IV. HISTORIA CLÍNICA Y BIOMETRÍA",
            "preguntas": [
                {
                    "id": "III1",
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
                    "id": "III2",
                    "texto": "Datos Biométricos (Aproximados)",
                    "tipo": "subpreguntas",
                    "preguntas": [
                        {
                            "id": "III2A",
                            "texto": "Peso actual (Kg)",
                            "tipo": "numero",
                            "unidad": "Kg"
                        },
                        {
                            "id": "III2B",
                            "texto": "Estatura (cm)",
                            "tipo": "numero",
                            "unidad": "cm"
                        }
                    ]
                },
                {
                    "id": "III3",
                    "texto": "¿Alguna vez se ha realizado...?",
                    "tipo": "subpreguntas",
                    "preguntas": [
                        {
                            "id": "III3A",
                            "texto": "Una mamografía",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": "si", "texto": "Sí"},
                                {"valor": "no", "texto": "No"}
                            ]
                        },
                        {
                            "id": "III3B",
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
                    "id": "III4",
                    "texto": "(Si respondió SÍ en la anterior) ¿Se ha realizado estos exámenes en los últimos 3 años?",
                    "tipo": "subpreguntas",
                    "condicional": True,
                    "preguntas": [
                        {
                            "id": "III4A",
                            "texto": "Mamografía",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": "si", "texto": "Sí"},
                                {"valor": "no", "texto": "No"}
                            ]
                        },
                        {
                            "id": "III4B",
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
            "id": "IV",
            "titulo": "V. SALUD SEXUAL Y REPRODUCTIVA",
            "preguntas": [
                {
                    "id": "IV1",
                    "texto": "¿A qué edad aproximadamente tuvo su primera menstruación o regla?",
                    "tipo": "numero",
                    "unidad": "años"
                },
                {
                    "id": "IV2",
                    "texto": "¿Ha tenido menstruación o regla en el último año?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"}
                    ]
                },
                {
                    "id": "IV3",
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
                    "id": "IV4",
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
                    "id": "IV5",
                    "texto": "¿Ha estado embarazada alguna vez en su vida?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"}
                    ]
                },
                {
                    "id": "IV6",
                    "texto": "¿Cuántos embarazos ha tenido a lo largo de su vida? (Incluya partos, abortos o pérdidas)",
                    "tipo": "numero",
                    "condicional": True
                },
                {
                    "id": "IV7",
                    "texto": "Su último embarazo terminó con:",
                    "tipo": "opcion_unica",
                    "condicional": True,
                    "opciones": [
                        {"valor": "parto_termino", "texto": "Parto de término (vivo)"},
                        {"valor": "parto_prematuro", "texto": "Parto prematuro (vivo)"},
                        {"valor": "perdida_mayor", "texto": "Pérdida o mortinato (mayor a 13 semanas)"},
                        {"valor": "perdida_menor", "texto": "Pérdida o aborto (menor o igual a 12 semanas)"}
                    ]
                },
                {
                    "id": "IV8",
                    "texto": "(Si tuvo parto) ¿Algún médico(a) le diagnosticó depresión postparto?",
                    "tipo": "opcion_unica",
                    "condicional": True,
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"}
                    ]
                }
            ]
        },
        {
            "id": "V",
            "titulo": "VI. FUNCIONALIDAD SEXUAL Y ANTICONCEPCIÓN",
            "preguntas": [
                {
                    "id": "V1",
                    "texto": "En su última relación sexual (o actualmente), ¿Ustedes usaron algún método anticonceptivo?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"}
                    ]
                },
                {
                    "id": "V2",
                    "texto": "¿Cuál método utiliza principalmente?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "condon", "texto": "Condón (masculino/femenino)"},
                        {"valor": "pildora", "texto": "Píldora o pastillas"},
                        {"valor": "diu", "texto": "DIU / T de cobre"},
                        {"valor": "implante", "texto": "Implante / Inyección"},
                        {"valor": "esterilizacion", "texto": "Esterilización"},
                        {"valor": "ninguno", "texto": "Ninguno / Natural"},
                        {"valor": "otro", "texto": "Otro"}
                    ]
                },
                {
                    "id": "V3",
                    "texto": "En los últimos 12 meses, ¿con qué frecuencia usted ha experimentado alguna de las siguientes situaciones en su vida sexual?",
                    "tipo": "subpreguntas",
                    "instrucciones": "Escala: Nunca | A veces | Frecuentemente",
                    "preguntas": [
                        {
                            "id": "V3A",
                            "texto": "Ausencia o bajo deseo sexual",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": 1, "texto": "Nunca"},
                                {"valor": 2, "texto": "A veces"},
                                {"valor": 3, "texto": "Frecuentemente"}
                            ]
                        },
                        {
                            "id": "V3B",
                            "texto": "Ausencia de orgasmos",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": 1, "texto": "Nunca"},
                                {"valor": 2, "texto": "A veces"},
                                {"valor": 3, "texto": "Frecuentemente"}
                            ]
                        },
                        {
                            "id": "V3C",
                            "texto": "Dolor o dificultad en la penetración",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": 1, "texto": "Nunca"},
                                {"valor": 2, "texto": "A veces"},
                                {"valor": 3, "texto": "Frecuentemente"}
                            ]
                        },
                        {
                            "id": "V3D",
                            "texto": "Dificultad para la lubricación vaginal",
                            "tipo": "opcion_unica",
                            "opciones": [
                                {"valor": 1, "texto": "Nunca"},
                                {"valor": 2, "texto": "A veces"},
                                {"valor": 3, "texto": "Frecuentemente"}
                            ]
                        }
                    ]
                },
                {
                    "id": "V4",
                    "texto": "¿Alguna vez un médico le ha dicho que tiene alguna Infección de Transmisión Sexual (VIH, VPH, Sífilis, etc.)?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"}
                    ]
                }
            ]
        },
        {
            "id": "VI",
            "titulo": "VII. EXPERIENCIAS SENSIBLES (Autoaplicado sugerido)",
            "preguntas": [
                {
                    "id": "VI1",
                    "texto": "En el marco de sus visitas a servicios de ginecología, ¿alguna vez sintió que el personal juzgaba sus prácticas, hizo comentarios inapropiados o le realizaron procedimientos bruscos/dolorosos?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si_una_vez", "texto": "Sí, una vez"},
                        {"valor": "si_mas_veces", "texto": "Sí, más de una vez"},
                        {"valor": "nunca", "texto": "Nunca"}
                    ]
                },
                {
                    "id": "VI2",
                    "texto": "¿Alguna vez en su vida alguien le tocó sus partes privadas bajo manipulación, engaño o fuerza sin su consentimiento?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"},
                        {"valor": "prefiere_no_responder", "texto": "Prefiero no responder"}
                    ]
                },
                {
                    "id": "VI3",
                    "texto": "¿Alguna vez en su vida ha experimentado situaciones de acoso (agarrones, punteos, exhibicionismo) en lugares públicos?",
                    "tipo": "opcion_unica",
                    "opciones": [
                        {"valor": "si", "texto": "Sí"},
                        {"valor": "no", "texto": "No"},
                        {"valor": "prefiere_no_responder", "texto": "Prefiero no responder"}
                    ]
                }
            ]
        },
        {
            "id": "A",
            "titulo": "VIII. BARRERAS PARA ADHERIR AL TAMIZAJE REPORTADAS POR LAS MUJERES",
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
            "titulo": "IX. SEÑALES DE ACCIÓN (MOTIVACIÓN) PARA ADHERIR AL TAMIZAJE REPORTADAS POR LAS MUJERES",
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
            "titulo": "X. SEVERIDAD DEL CÁNCER CÉRVICOUTERINO Y SUSCEPTIBILIDAD PERCIBIDA PARA DESARROLLARLO REPORTADA POR LAS MUJERES",
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cuestionario', methods=['GET'])
def get_cuestionario():
    return jsonify(CUESTIONARIO)

@app.route('/api/respuestas', methods=['POST'])
def guardar_respuestas():
    try:
        data = request.json
        respuestas = data.get('respuestas', {})
        timestamp = data.get('timestamp')
        
        # Crear directorio de respuestas si no existe
        os.makedirs('respuestas', exist_ok=True)
        
        # Guardar respuestas en archivo JSON
        filename = f"respuestas/respuestas_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'respuestas': respuestas
            }, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'Respuestas guardadas correctamente',
            'filename': filename
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al guardar respuestas: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)




