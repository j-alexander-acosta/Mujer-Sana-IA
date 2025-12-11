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
            // Si la pregunta tiene subpreguntas, agregarlas también
            if (pregunta.tipo === 'subpreguntas' && pregunta.preguntas) {
                pregunta.preguntas.forEach(subpregunta => {
                    todasLasPreguntas.push({
                        ...subpregunta,
                        seccionId: seccion.id,
                        seccionTitulo: seccion.titulo,
                        preguntaPadre: pregunta.id,
                        instrucciones: pregunta.instrucciones,
                        condicional: pregunta.condicional || subpregunta.condicional
                    });
                });
            } else {
                todasLasPreguntas.push({
                    ...pregunta,
                    seccionId: seccion.id,
                    seccionTitulo: seccion.titulo
                });
            }
        });
    });

    // Calcular total de preguntas (excluyendo condicionales no aplicables inicialmente)
    totalPreguntas = todasLasPreguntas.length;
    
    // Ocultar loading y mostrar cuestionario
    document.getElementById('loading').style.display = 'none';
    document.getElementById('cuestionario-container').style.display = 'block';
    
    // Ir a la primera pregunta válida
    irAPrimeraPreguntaValida();
    actualizarProgreso();
}

function irAPrimeraPreguntaValida() {
    // Buscar la primera pregunta que no sea condicional o que deba mostrarse
    while (preguntaActual < totalPreguntas) {
        const pregunta = todasLasPreguntas[preguntaActual];
        if (!pregunta.condicional || debeMostrarPreguntaCondicional(pregunta)) {
            renderizarPregunta();
            return;
        }
        preguntaActual++;
    }
    // Si no hay preguntas válidas, mostrar la primera
    preguntaActual = 0;
    renderizarPregunta();
}

function renderizarPregunta() {
    const pregunta = todasLasPreguntas[preguntaActual];
    const container = document.getElementById('secciones-container');
    
    // Verificar si la pregunta es condicional y si debe mostrarse
    if (pregunta.condicional && !debeMostrarPreguntaCondicional(pregunta)) {
        // Saltar a la siguiente pregunta
        if (preguntaActual < totalPreguntas - 1) {
            preguntaActual++;
            renderizarPregunta();
            return;
        }
    }
    
    // Determinar si es primera pregunta de una sección
    const esPrimeraDeSeccion = preguntaActual === 0 || 
        todasLasPreguntas[preguntaActual - 1].seccionId !== pregunta.seccionId;
    
    let html = '';
    
    if (esPrimeraDeSeccion) {
        html += `<div class="seccion activa">
            <h2 class="seccion-titulo">${pregunta.seccionTitulo}</h2>`;
    }
    
    // Mostrar instrucciones si existen
    if (pregunta.instrucciones) {
        html += `<div class="instrucciones">${pregunta.instrucciones}</div>`;
    }
    
    html += `
        <div class="pregunta ${respuestas[pregunta.id] ? 'respondida' : ''}" data-pregunta-id="${pregunta.id}">
            <div class="pregunta-texto">${pregunta.texto}</div>
            <div class="opciones">
    `;
    
    // Renderizar según el tipo de pregunta
    const tipo = pregunta.tipo || 'escala'; // Por defecto escala Likert
    
    if (tipo === 'opcion_unica' && pregunta.opciones) {
        // Pregunta de opción única con opciones personalizadas
        pregunta.opciones.forEach(opcion => {
            const valor = typeof opcion.valor === 'string' ? opcion.valor : opcion.valor;
            const checked = respuestas[pregunta.id] === valor ? 'checked' : '';
            html += `
                <div class="opcion">
                    <input type="radio" 
                           name="pregunta_${pregunta.id}" 
                           id="${pregunta.id}_${valor}" 
                           value="${valor}" 
                           ${checked}
                           onchange="guardarRespuesta('${pregunta.id}', '${valor}')">
                    <label for="${pregunta.id}_${valor}">${opcion.texto}</label>
                </div>
            `;
        });
    } else if (tipo === 'opcion_multiple' && pregunta.opciones) {
        // Pregunta de opción múltiple (checkboxes)
        const valoresSeleccionados = respuestas[pregunta.id] || [];
        pregunta.opciones.forEach(opcion => {
            const valor = typeof opcion.valor === 'string' ? opcion.valor : opcion.valor;
            const checked = Array.isArray(valoresSeleccionados) && valoresSeleccionados.includes(valor) ? 'checked' : '';
            html += `
                <div class="opcion">
                    <input type="checkbox" 
                           name="pregunta_${pregunta.id}" 
                           id="${pregunta.id}_${valor}" 
                           value="${valor}" 
                           ${checked}
                           onchange="guardarRespuestaMultiple('${pregunta.id}', '${valor}', this.checked)">
                    <label for="${pregunta.id}_${valor}">${opcion.texto}</label>
                </div>
            `;
        });
    } else if (tipo === 'numero') {
        // Pregunta numérica
        const valor = respuestas[pregunta.id] || '';
        const unidad = pregunta.unidad ? ` (${pregunta.unidad})` : '';
        html += `
            <div class="opcion numero">
                <input type="number" 
                       name="pregunta_${pregunta.id}" 
                       id="${pregunta.id}" 
                       value="${valor}"
                       placeholder="Ingrese un número"
                       onchange="guardarRespuesta('${pregunta.id}', this.value)"
                       onblur="guardarRespuesta('${pregunta.id}', this.value)">
                <label for="${pregunta.id}">${unidad}</label>
            </div>
        `;
    } else {
        // Pregunta de escala Likert (por defecto)
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
    }
    
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

function debeMostrarPreguntaCondicional(pregunta) {
    // Si la pregunta no es condicional, siempre mostrarla
    if (!pregunta.condicional) {
        return true;
    }
    
    // Buscar la pregunta padre o la pregunta anterior relacionada
    if (pregunta.preguntaPadre) {
        // Buscar la pregunta padre en el cuestionario
        for (const seccion of cuestionario.secciones) {
            for (const preg of seccion.preguntas) {
                if (preg.id === pregunta.preguntaPadre) {
                    // Verificar si la pregunta padre tiene respuesta
                    if (preg.tipo === 'subpreguntas' && preg.preguntas) {
                        // Verificar las subpreguntas anteriores
                        const indice = preg.preguntas.findIndex(p => p.id === pregunta.id);
                        if (indice > 0) {
                            const preguntaAnterior = preg.preguntas[indice - 1];
                            const respuestaAnterior = respuestas[preguntaAnterior.id];
                            
                            // Si la pregunta anterior requiere "Sí" o "No" específico
                            if (pregunta.texto.includes('Si respondió SÍ') || pregunta.texto.includes('Si respondió NO')) {
                                const requiereSi = pregunta.texto.includes('Si respondió SÍ');
                                return requiereSi ? respuestaAnterior === 'si' : respuestaAnterior === 'no';
                            }
                            
                            // Si la pregunta anterior requiere respuesta específica
                            if (pregunta.texto.includes('Si aplica Menopausia')) {
                                // Buscar la pregunta sobre menopausia
                                const preguntaMenopausia = preg.preguntas.find(p => 
                                    p.texto && p.texto.includes('razón por la cual no ha tenido menstruación')
                                );
                                if (preguntaMenopausia) {
                                    return respuestas[preguntaMenopausia.id] === 'menopausia';
                                }
                            }
                            
                            return respuestaAnterior !== undefined && respuestaAnterior !== '';
                        }
                    }
                    return respuestas[preg.id] !== undefined && respuestas[preg.id] !== '';
                }
            }
        }
    }
    
    // Verificar si la pregunta depende de una pregunta anterior en el mismo array
    const indiceActual = todasLasPreguntas.findIndex(p => p.id === pregunta.id);
    if (indiceActual > 0) {
        const preguntaAnterior = todasLasPreguntas[indiceActual - 1];
        const respuestaAnterior = respuestas[preguntaAnterior.id];
        
        // Verificar condiciones comunes
        if (pregunta.texto.includes('Si respondió SÍ') || pregunta.texto.includes('Si respondió NO')) {
            const requiereSi = pregunta.texto.includes('Si respondió SÍ');
            return requiereSi ? respuestaAnterior === 'si' : respuestaAnterior === 'no';
        }
        
        if (pregunta.texto.includes('Si respondió NO')) {
            return respuestaAnterior === 'no';
        }
        
        if (pregunta.texto.includes('Si tuvo parto')) {
            // Verificar si la respuesta anterior indica un parto
            return respuestaAnterior === 'parto_termino' || respuestaAnterior === 'parto_prematuro';
        }
    }
    
    return true; // Por defecto mostrar la pregunta
}

function guardarRespuestaMultiple(preguntaId, valor, checked) {
    if (!respuestas[preguntaId]) {
        respuestas[preguntaId] = [];
    }
    
    if (checked) {
        if (!respuestas[preguntaId].includes(valor)) {
            respuestas[preguntaId].push(valor);
        }
    } else {
        respuestas[preguntaId] = respuestas[preguntaId].filter(v => v !== valor);
    }
    
    // Marcar pregunta como respondida si tiene al menos una opción seleccionada
    const preguntaElement = document.querySelector(`[data-pregunta-id="${preguntaId}"]`);
    if (preguntaElement) {
        if (respuestas[preguntaId].length > 0) {
            preguntaElement.classList.add('respondida');
        } else {
            preguntaElement.classList.remove('respondida');
        }
    }
    
    actualizarBotones();
}

function guardarRespuesta(preguntaId, valor) {
    // Convertir valor a número si es posible y necesario
    if (valor !== '' && !isNaN(valor) && valor !== null) {
        const numValor = parseFloat(valor);
        if (!isNaN(numValor)) {
            respuestas[preguntaId] = numValor;
        } else {
            respuestas[preguntaId] = valor;
        }
    } else {
        respuestas[preguntaId] = valor;
    }
    
    // Marcar pregunta como respondida
    const preguntaElement = document.querySelector(`[data-pregunta-id="${preguntaId}"]`);
    if (preguntaElement) {
        if (valor !== '' && valor !== null && valor !== undefined) {
            preguntaElement.classList.add('respondida');
        } else {
            preguntaElement.classList.remove('respondida');
        }
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
        // Retroceder saltando preguntas condicionales que no aplican
        while (preguntaActual > 0) {
            const preguntaAnterior = todasLasPreguntas[preguntaActual];
            if (!preguntaAnterior.condicional || debeMostrarPreguntaCondicional(preguntaAnterior)) {
                break;
            }
            preguntaActual--;
        }
        renderizarPregunta();
        actualizarProgreso();
        // Scroll al inicio
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

document.getElementById('btn-siguiente').addEventListener('click', () => {
    const pregunta = todasLasPreguntas[preguntaActual];
    
    // Validar que la pregunta esté respondida
    const tieneRespuesta = respuestas[pregunta.id] !== undefined && 
                          respuestas[pregunta.id] !== null && 
                          respuestas[pregunta.id] !== '';
    
    // Para preguntas de opción múltiple, verificar que tenga al menos una selección
    const esMultiple = pregunta.tipo === 'opcion_multiple';
    const tieneSeleccionMultiple = esMultiple ? 
        (Array.isArray(respuestas[pregunta.id]) && respuestas[pregunta.id].length > 0) : true;
    
    if (!tieneRespuesta || !tieneSeleccionMultiple) {
        const mensaje = pregunta.tipo === 'numero' ? 
            'Por favor, ingresa un valor numérico antes de continuar.' :
            pregunta.tipo === 'opcion_multiple' ?
            'Por favor, selecciona al menos una opción antes de continuar.' :
            'Por favor, selecciona una respuesta antes de continuar.';
        alert(mensaje);
        return;
    }
    
    if (preguntaActual < totalPreguntas - 1) {
        preguntaActual++;
        // Saltar preguntas condicionales que no aplican
        while (preguntaActual < totalPreguntas) {
            const siguientePregunta = todasLasPreguntas[preguntaActual];
            if (!siguientePregunta.condicional || debeMostrarPreguntaCondicional(siguientePregunta)) {
                break;
            }
            preguntaActual++;
        }
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
    const tieneRespuesta = respuestas[pregunta.id] !== undefined && 
                          respuestas[pregunta.id] !== null && 
                          respuestas[pregunta.id] !== '';
    const esMultiple = pregunta.tipo === 'opcion_multiple';
    const tieneSeleccionMultiple = esMultiple ? 
        (Array.isArray(respuestas[pregunta.id]) && respuestas[pregunta.id].length > 0) : true;
    
    if (!tieneRespuesta || !tieneSeleccionMultiple) {
        const mensaje = pregunta.tipo === 'numero' ? 
            'Por favor, ingresa un valor numérico antes de enviar.' :
            pregunta.tipo === 'opcion_multiple' ?
            'Por favor, selecciona al menos una opción antes de enviar.' :
            'Por favor, selecciona una respuesta antes de enviar.';
        alert(mensaje);
        return;
    }
    
    // Validar que todas las preguntas estén respondidas (excluyendo condicionales no aplicables)
    const preguntasSinResponder = todasLasPreguntas.filter(p => {
        if (p.condicional && !debeMostrarPreguntaCondicional(p)) {
            return false; // No contar preguntas condicionales que no aplican
        }
        const tieneResp = respuestas[p.id] !== undefined && 
                         respuestas[p.id] !== null && 
                         respuestas[p.id] !== '';
        if (p.tipo === 'opcion_multiple') {
            return !(Array.isArray(respuestas[p.id]) && respuestas[p.id].length > 0);
        }
        return !tieneResp;
    });
    
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




