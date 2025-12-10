let cuestionario = null;
let respuestas = {};
let preguntaActual = 0;
let totalPreguntas = 0;
let todasLasPreguntas = [];

// Cargar cuestionario al iniciar
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/cuestionario');
        cuestionario = await response.json();
        inicializarCuestionario();
    } catch (error) {
        console.error('Error al cargar cuestionario:', error);
        mostrarError('Error al cargar el cuestionario. Por favor, recarga la página.');
    }
});

function inicializarCuestionario() {
    // Aplanar todas las preguntas en un solo array
    todasLasPreguntas = [];
    cuestionario.secciones.forEach(seccion => {
        seccion.preguntas.forEach(pregunta => {
            todasLasPreguntas.push({
                ...pregunta,
                seccionId: seccion.id,
                seccionTitulo: seccion.titulo
            });
        });
    });

    totalPreguntas = todasLasPreguntas.length;
    
    // Ocultar loading y mostrar cuestionario
    document.getElementById('loading').style.display = 'none';
    document.getElementById('cuestionario-container').style.display = 'block';
    
    // Renderizar primera pregunta
    renderizarPregunta();
    actualizarProgreso();
}

function renderizarPregunta() {
    const pregunta = todasLasPreguntas[preguntaActual];
    const container = document.getElementById('secciones-container');
    
    // Determinar si es primera pregunta de una sección
    const esPrimeraDeSeccion = preguntaActual === 0 || 
        todasLasPreguntas[preguntaActual - 1].seccionId !== pregunta.seccionId;
    
    let html = '';
    
    if (esPrimeraDeSeccion) {
        html += `<div class="seccion activa">
            <h2 class="seccion-titulo">${pregunta.seccionTitulo}</h2>`;
    }
    
    html += `
        <div class="pregunta ${respuestas[pregunta.id] ? 'respondida' : ''}" data-pregunta-id="${pregunta.id}">
            <div class="pregunta-texto">${pregunta.texto}</div>
            <div class="opciones">
    `;
    
    cuestionario.opciones.forEach(opcion => {
        const checked = respuestas[pregunta.id] === opcion.valor ? 'checked' : '';
        html += `
            <div class="opcion">
                <input type="radio" 
                       name="pregunta_${pregunta.id}" 
                       id="${pregunta.id}_${opcion.valor}" 
                       value="${opcion.valor}" 
                       ${checked}
                       onchange="guardarRespuesta('${pregunta.id}', ${opcion.valor})">
                <label for="${pregunta.id}_${opcion.valor}">${opcion.texto}</label>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    if (preguntaActual === totalPreguntas - 1 || 
        (preguntaActual < totalPreguntas - 1 && 
         todasLasPreguntas[preguntaActual + 1].seccionId !== pregunta.seccionId)) {
        html += `</div>`;
    }
    
    container.innerHTML = html;
    
    // Actualizar botones
    actualizarBotones();
}

function guardarRespuesta(preguntaId, valor) {
    respuestas[preguntaId] = valor;
    
    // Marcar pregunta como respondida
    const preguntaElement = document.querySelector(`[data-pregunta-id="${preguntaId}"]`);
    if (preguntaElement) {
        preguntaElement.classList.add('respondida');
    }
    
    actualizarBotones();
}

function actualizarBotones() {
    const btnAnterior = document.getElementById('btn-anterior');
    const btnSiguiente = document.getElementById('btn-siguiente');
    const btnEnviar = document.getElementById('btn-enviar');
    
    // Botón anterior
    if (preguntaActual > 0) {
        btnAnterior.style.display = 'block';
    } else {
        btnAnterior.style.display = 'none';
    }
    
    // Botón siguiente/enviar
    if (preguntaActual === totalPreguntas - 1) {
        btnSiguiente.style.display = 'none';
        btnEnviar.style.display = 'block';
    } else {
        btnSiguiente.style.display = 'block';
        btnEnviar.style.display = 'none';
    }
}

function actualizarProgreso() {
    const porcentaje = ((preguntaActual + 1) / totalPreguntas) * 100;
    document.getElementById('progress-fill').style.width = porcentaje + '%';
    document.getElementById('progress-text').textContent = 
        `Pregunta ${preguntaActual + 1} de ${totalPreguntas}`;
}

// Event listeners para botones
document.getElementById('btn-anterior').addEventListener('click', () => {
    if (preguntaActual > 0) {
        preguntaActual--;
        renderizarPregunta();
        actualizarProgreso();
        // Scroll al inicio
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

document.getElementById('btn-siguiente').addEventListener('click', () => {
    const pregunta = todasLasPreguntas[preguntaActual];
    
    // Validar que la pregunta esté respondida
    if (!respuestas[pregunta.id]) {
        alert('Por favor, selecciona una respuesta antes de continuar.');
        return;
    }
    
    if (preguntaActual < totalPreguntas - 1) {
        preguntaActual++;
        renderizarPregunta();
        actualizarProgreso();
        // Scroll al inicio
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

document.getElementById('btn-enviar').addEventListener('click', async (e) => {
    e.preventDefault();
    
    const pregunta = todasLasPreguntas[preguntaActual];
    
    // Validar última pregunta
    if (!respuestas[pregunta.id]) {
        alert('Por favor, selecciona una respuesta antes de enviar.');
        return;
    }
    
    // Validar que todas las preguntas estén respondidas
    const preguntasSinResponder = todasLasPreguntas.filter(p => !respuestas[p.id]);
    if (preguntasSinResponder.length > 0) {
        if (!confirm(`Tienes ${preguntasSinResponder.length} pregunta(s) sin responder. ¿Deseas enviar de todas formas?`)) {
            return;
        }
    }
    
    // Enviar respuestas
    try {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const response = await fetch('/api/respuestas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                respuestas: respuestas,
                timestamp: timestamp
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            mostrarResultado();
        } else {
            alert('Error al guardar las respuestas: ' + result.message);
        }
    } catch (error) {
        console.error('Error al enviar respuestas:', error);
        alert('Error al enviar las respuestas. Por favor, intenta nuevamente.');
    }
});

document.getElementById('btn-nuevo').addEventListener('click', () => {
    // Reiniciar cuestionario
    respuestas = {};
    preguntaActual = 0;
    document.getElementById('resultado-container').style.display = 'none';
    document.getElementById('cuestionario-container').style.display = 'block';
    renderizarPregunta();
    actualizarProgreso();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

function mostrarResultado() {
    document.getElementById('cuestionario-container').style.display = 'none';
    document.getElementById('resultado-container').style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function mostrarError(mensaje) {
    const container = document.getElementById('cuestionario-container');
    container.innerHTML = `<div class="error">${mensaje}</div>`;
    document.getElementById('loading').style.display = 'none';
    container.style.display = 'block';
}



