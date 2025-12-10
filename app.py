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
            "id": "A",
            "titulo": "BARRERAS PARA ADHERIR AL TAMIZAJE REPORTADAS POR LAS MUJERES",
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
            "titulo": "SEÑALES DE ACCIÓN (MOTIVACIÓN) PARA ADHERIR AL TAMIZAJE REPORTADAS POR LAS MUJERES",
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
            "titulo": "SEVERIDAD DEL CÁNCER CÉRVICOUTERINO Y SUSCEPTIBILIDAD PERCIBIDA PARA DESARROLLARLO REPORTADA POR LAS MUJERES",
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



