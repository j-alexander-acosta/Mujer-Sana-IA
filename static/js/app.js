let cuestionario = null;
let respuestas = {};
let preguntaActual = 0;
let totalPreguntas = 0;
let todasLasPreguntas = [];

// Validaciones de campos clave
function validateName(name) {
    if (!name || typeof name !== 'string') return false;
    const trimmed = name.trim();
    // Al menos dos palabras y solo letras, espacios y acentos básicos
    return /^[A-Za-zÁÉÍÓÚáéíóúÑñ]+(\s+[A-Za-zÁÉÍÓÚáéíóúÑñ]+)+$/.test(trimmed);
}

function validateRUT(rut) {
    if (!rut) return false;
    let s = String(rut).trim();
    s = s.replace(/\./g, '').replace(/\s/g, '');
    let cuerpo = '';
    let dv = '';
    if (s.includes('-')) {
        const parts = s.split('-');
        cuerpo = parts[0];
        dv = (parts[1] || '').toUpperCase();
    } else {
        // Si no tiene guion, tomar el último carácter como DV
        cuerpo = s.slice(0, -1);
        dv = s.slice(-1).toUpperCase();
    }
    if (!/^[0-9]+$/.test(cuerpo) || cuerpo.length === 0) return false;

    // Calculo del DV (mismo algoritmo que en servidor)
    let num = parseInt(cuerpo, 10);
    let M = 0, S = 1;
    while (num) {
        S = (S + (num % 10) * (9 - (M++ % 6))) % 11;
        num = Math.floor(num / 10);
    }
    const dvCalc = S ? String(S - 1) : 'K';
    return dv === dvCalc;
}

function validateEmail(email) {
    if (!email || typeof email !== 'string') return false;
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    if (!phone || typeof phone !== 'string') return false;
    const cleaned = phone.replace(/\s|\(|\)|-/g, '');
    return /^\+?[0-9]{8,15}$/.test(cleaned);
}

function validateAge(age) {
    if (age === undefined || age === null || age === '') return false;
    const n = Number(age);
    return Number.isInteger(n) && n >= 10 && n <= 120;
}

function validateWeight(w) {
    if (w === undefined || w === null || w === '') return false;
    const n = Number(w);
    return !isNaN(n) && n >= 20 && n <= 300;
}

function validateHeight(h) {
    if (h === undefined || h === null || h === '') return false;
    const n = Number(h);
    return !isNaN(n) && n >= 50 && n <= 250;
}

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
                        preguntaPadreTexto: pregunta.texto,
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

    // Filtrar preguntas informativas del conteo (pero mantenerlas para mostrar)
    // Las preguntas informativas no requieren respuesta

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
    // Verificar límites antes de acceder al array
    if (preguntaActual >= totalPreguntas || preguntaActual < 0) {
        console.error('Índice de pregunta fuera de límites:', preguntaActual);
        // Si estamos fuera de límites, intentar encontrar la última pregunta válida
        if (preguntaActual >= totalPreguntas) {
            preguntaActual = totalPreguntas - 1;
        } else {
            preguntaActual = 0;
        }
        // Si aún no hay preguntas válidas, mostrar error
        if (preguntaActual < 0 || preguntaActual >= totalPreguntas) {
            mostrarError('No hay más preguntas disponibles.');
            return;
        }
    }
    
    const pregunta = todasLasPreguntas[preguntaActual];
    
    // Verificar que la pregunta existe
    if (!pregunta) {
        console.error('Pregunta no encontrada en índice:', preguntaActual);
        mostrarError('Error al cargar la pregunta. Por favor, recarga la página.');
        return;
    }
    
    const container = document.getElementById('secciones-container');
    
    // Verificar si la pregunta es condicional y si debe mostrarse
    if (pregunta.condicional && !debeMostrarPreguntaCondicional(pregunta)) {
        // Saltar a la siguiente pregunta
        if (preguntaActual < totalPreguntas - 1) {
            preguntaActual++;
            renderizarPregunta();
            return;
        } else {
            // Si no hay más preguntas, mostrar mensaje de finalización
            mostrarResultado();
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
    
    // Renderizar según el tipo de pregunta
    const tipo = pregunta.tipo || 'escala'; // Por defecto escala Likert
    
    // Si la pregunta es interactiva, abrir el contenedor con el texto
    if (tipo !== 'texto_informativo') {
        // Determinar si es la primera subpregunta de un grupo
        const esPrimeraSubpregunta = pregunta.preguntaPadre && 
            (preguntaActual === 0 || 
             todasLasPreguntas[preguntaActual - 1].preguntaPadre !== pregunta.preguntaPadre);
        
        html += `
        <div class="pregunta ${respuestas[pregunta.id] ? 'respondida' : ''}" data-pregunta-id="${pregunta.id}">`;
        
        // Si es la primera subpregunta, mostrar el texto de la pregunta principal
        if (esPrimeraSubpregunta && pregunta.preguntaPadreTexto) {
            html += `<div class="pregunta-principal">${pregunta.preguntaPadreTexto}</div>`;
        }
        
        html += `
            <div class="pregunta-texto">${pregunta.texto}</div>
            <div class="opciones">
        `;
    }
    
    if (tipo === 'texto_informativo') {
        // Texto informativo (solo lectura) - no requiere respuesta, marcarla como respondida automáticamente
        respuestas[pregunta.id] = true;
    html += `
        <div class="pregunta informativa respondida" data-pregunta-id="${pregunta.id}">
            <div class="pregunta-texto">${pregunta.texto}</div>
            <div class="texto-informativo">
                <p>${pregunta.contenido.replace(/\n/g, '<br>')}</p>
            </div>
        </div>
        `;
    } else if (tipo === 'fecha') {
        // Campo de fecha
        const valor = respuestas[pregunta.id] || '';
        const formato = pregunta.formato || 'YYYY-MM-DD';
        html += `
            <div class="opcion fecha">
                <input type="date" 
                       name="pregunta_${pregunta.id}" 
                       id="${pregunta.id}" 
                       value="${valor}"
                       ${pregunta.obligatorio ? 'required' : ''}
                       onchange="guardarRespuesta('${pregunta.id}', this.value)"
                       onblur="guardarRespuesta('${pregunta.id}', this.value)">
                <small class="formato-fecha">Formato: ${pregunta.formato || 'DD/MM/AAAA'}</small>
            </div>
        `;
    } else if (tipo === 'texto') {
        // Campo de texto
        const valor = respuestas[pregunta.id] || '';
        html += `
            <div class="opcion texto">
                <input type="text" 
                       name="pregunta_${pregunta.id}" 
                       id="${pregunta.id}" 
                       value="${valor}"
                       placeholder="${pregunta.placeholder || ''}"
                       ${pregunta.obligatorio ? 'required' : ''}
                       onchange="guardarRespuesta('${pregunta.id}', this.value)"
                       onblur="guardarRespuesta('${pregunta.id}', this.value)">
            </div>
        `;
    } else if (tipo === 'email') {
        // Campo de email
        const valor = respuestas[pregunta.id] || '';
        html += `
            <div class="opcion email">
                <input type="email" 
                       name="pregunta_${pregunta.id}" 
                       id="${pregunta.id}" 
                       value="${valor}"
                       placeholder="ejemplo@correo.com"
                       ${pregunta.obligatorio ? 'required' : ''}
                       onchange="guardarRespuesta('${pregunta.id}', this.value)"
                       onblur="guardarRespuesta('${pregunta.id}', this.value)">
            </div>
        `;
    } else if (tipo === 'consentimiento') {
        // Checkbox de consentimiento
        const checked = respuestas[pregunta.id] === true || respuestas[pregunta.id] === 'true' ? 'checked' : '';
        html += `
            <div class="opcion consentimiento">
                <input type="checkbox" 
                       name="pregunta_${pregunta.id}" 
                       id="${pregunta.id}" 
                       ${checked}
                       ${pregunta.obligatorio ? 'required' : ''}
                       onchange="guardarRespuesta('${pregunta.id}', this.checked)">
                <label for="${pregunta.id}" class="consentimiento-label">${pregunta.texto}</label>
            </div>
        `;
    } else if (tipo === 'opcion_unica' && pregunta.opciones) {
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
    
    // Cerrar divs solo si no es pregunta informativa
    if (tipo !== 'texto_informativo') {
    html += `
            </div>
        </div>
    `;
    }
    
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
    
    // Si tiene dependencia explícita (depende_de y requiere_valor)
    if (pregunta.depende_de && pregunta.requiere_valor !== undefined) {
        const respuestaDependiente = respuestas[pregunta.depende_de];
        if (Array.isArray(pregunta.requiere_valor)) {
            // Si requiere_valor es un array, verificar si la respuesta está en el array
            return pregunta.requiere_valor.includes(respuestaDependiente);
        } else {
            // Si requiere_valor es un valor único, verificar igualdad
            return respuestaDependiente === pregunta.requiere_valor;
        }
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
                            // Hay subpreguntas anteriores en el mismo grupo
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
                        } else if (indice === 0) {
                            // Es la primera subpregunta del grupo, verificar la pregunta anterior en el array principal
                            const indiceActual = todasLasPreguntas.findIndex(p => p.id === pregunta.id);
                            if (indiceActual > 0) {
                                // Verificar si el texto del padre indica que debe verificar el grupo anterior
                                if (preg.texto && (preg.texto.includes('Si respondió SÍ') || preg.texto.includes('Si respondió NO'))) {
                                    const requiereSi = preg.texto.includes('Si respondió SÍ');
                                    
                                    // Buscar el grupo de subpreguntas anterior en el array principal
                                    let grupoAnterior = null;
                                    for (let i = indiceActual - 1; i >= 0; i--) {
                                        const pregAnterior = todasLasPreguntas[i];
                                        if (pregAnterior.preguntaPadre) {
                                            // Encontrar el grupo padre de esta pregunta
                                            for (const seccion of cuestionario.secciones) {
                                                for (const pregPadre of seccion.preguntas) {
                                                    if (pregPadre.id === pregAnterior.preguntaPadre && 
                                                        pregPadre.tipo === 'subpreguntas' && 
                                                        pregPadre.preguntas) {
                                                        grupoAnterior = pregPadre;
                                                        break;
                                                    }
                                                }
                                                if (grupoAnterior) break;
                                            }
                                            if (grupoAnterior) break;
                                        }
                                    }
                                    
                                    // Si encontramos un grupo anterior, verificar si alguna subpregunta tiene la respuesta requerida
                                    if (grupoAnterior && grupoAnterior.preguntas) {
                                        const tieneRespuestaRequerida = grupoAnterior.preguntas.some(subp => {
                                            const respuesta = respuestas[subp.id];
                                            return requiereSi ? respuesta === 'si' : respuesta === 'no';
                                        });
                                        return tieneRespuestaRequerida;
                                    }
                                    
                                    // Si no encontramos grupo anterior, verificar la pregunta anterior directa
                                    const preguntaAnteriorPrincipal = todasLasPreguntas[indiceActual - 1];
                                    const respuestaAnteriorPrincipal = respuestas[preguntaAnteriorPrincipal.id];
                                    return requiereSi ? respuestaAnteriorPrincipal === 'si' : respuestaAnteriorPrincipal === 'no';
                                }
                                
                                // Si no hay condición específica en el texto del padre, verificar la pregunta anterior
                                const preguntaAnteriorPrincipal = todasLasPreguntas[indiceActual - 1];
                                const respuestaAnteriorPrincipal = respuestas[preguntaAnteriorPrincipal.id];
                                
                                // Verificar condiciones comunes basadas en el texto de la pregunta
                                if (pregunta.texto.includes('Si respondió SÍ') || pregunta.texto.includes('Si respondió NO')) {
                                    const requiereSi = pregunta.texto.includes('Si respondió SÍ');
                                    return requiereSi ? respuestaAnteriorPrincipal === 'si' : respuestaAnteriorPrincipal === 'no';
                                }
                                
                                // Verificar si la pregunta anterior fue respondida
                                return respuestaAnteriorPrincipal !== undefined && respuestaAnteriorPrincipal !== null && respuestaAnteriorPrincipal !== '';
                            }
                        }
                    }
                    // Si no es subpreguntas o no se encontró lógica específica, no verificar el padre (que no tiene respuesta directa)
                    // En su lugar, verificar la pregunta anterior en el array principal
                    const indiceActual = todasLasPreguntas.findIndex(p => p.id === pregunta.id);
                    if (indiceActual > 0) {
                        const preguntaAnterior = todasLasPreguntas[indiceActual - 1];
                        const respuestaAnterior = respuestas[preguntaAnterior.id];
                        return respuestaAnterior !== undefined && respuestaAnterior !== null && respuestaAnterior !== '';
                    }
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
    // Validaciones específicas por campo
    if (preguntaId === 'DATOS_NOMBRE') {
        if (!validateName(valor)) {
            alert('Nombre inválido. Ingrese nombre completo (al menos nombre y apellido).');
            const el = document.getElementById(preguntaId);
            if (el) {
                el.classList.add('input-invalid');
                el.focus();
            }
            return;
        }
        // limpiar estado visual si ahora es válido
        const elNombre = document.getElementById(preguntaId);
        if (elNombre) elNombre.classList.remove('input-invalid');
    }
    if (preguntaId === 'DATOS_RUT') {
        if (!validateRUT(String(valor || '')) ) {
            alert('RUT inválido. Asegúrese de incluir guion y dígito verificador (ej: 12345678-9).');
            const el = document.getElementById(preguntaId);
            if (el) {
                el.classList.add('input-invalid');
                el.focus();
            }
            return;
        }
        const elRut = document.getElementById(preguntaId);
        if (elRut) elRut.classList.remove('input-invalid');
    }
    if (preguntaId === 'DATOS_EMAIL') {
        if (!validateEmail(String(valor || ''))) {
            alert('Correo electrónico inválido. Ingrese una dirección válida.');
            const el = document.getElementById(preguntaId);
            if (el) {
                el.classList.add('input-invalid');
                el.focus();
            }
            return;
        }
        const elEmail = document.getElementById(preguntaId);
        if (elEmail) elEmail.classList.remove('input-invalid');
    }
    if (preguntaId === 'DATOS_TELEFONO') {
        if (valor !== '' && valor !== null && !validatePhone(String(valor))) {
            alert('Teléfono inválido. Ingrese solo dígitos y opcionalmente +, entre 8 y 15 caracteres.');
            const el = document.getElementById(preguntaId);
            if (el) {
                el.classList.add('input-invalid');
                el.focus();
            }
            return;
        }
        const elTel = document.getElementById(preguntaId);
        if (elTel) elTel.classList.remove('input-invalid');
    }
    if (preguntaId === 'I3') {
        if (!validateAge(valor)) {
            alert('Edad inválida. Ingrese un número entero entre 10 y 120.');
            const el = document.getElementById(preguntaId);
            if (el) {
                el.classList.add('input-invalid');
                el.focus();
            }
            return;
        }
        const elEdad = document.getElementById(preguntaId);
        if (elEdad) elEdad.classList.remove('input-invalid');
    }
    if (preguntaId === 'II2A') { // Peso
        if (!validateWeight(valor)) {
            alert('Peso inválido. Ingrese un valor en Kg entre 20 y 300.');
            const el = document.getElementById(preguntaId);
            if (el) {
                el.classList.add('input-invalid');
                el.focus();
            }
            return;
        }
        const elPeso = document.getElementById(preguntaId);
        if (elPeso) elPeso.classList.remove('input-invalid');
    }
    if (preguntaId === 'II2B') { // Estatura
        if (!validateHeight(valor)) {
            alert('Estatura inválida. Ingrese un valor en cm entre 50 y 250.');
            const el = document.getElementById(preguntaId);
            if (el) {
                el.classList.add('input-invalid');
                el.focus();
            }
            return;
        }
        const elEst = document.getElementById(preguntaId);
        if (elEst) elEst.classList.remove('input-invalid');
    }
    // Para checkboxes de consentimiento, guardar como booleano
    if (typeof valor === 'boolean') {
        respuestas[preguntaId] = valor;
    }
    // Convertir valor a número si es posible y necesario
    else if (valor !== '' && !isNaN(valor) && valor !== null && typeof valor !== 'boolean') {
        const numValor = parseFloat(valor);
        if (!isNaN(numValor)) {
            respuestas[preguntaId] = numValor;
        } else {
            respuestas[preguntaId] = valor;
        }
    } else {
    respuestas[preguntaId] = valor;
    }
    // Almacenar quitando clase de error si existe
    const elemento = document.getElementById(preguntaId);
    if (elemento) elemento.classList.remove('input-invalid');
    
    // Marcar pregunta como respondida
    const preguntaElement = document.querySelector(`[data-pregunta-id="${preguntaId}"]`);
    if (preguntaElement) {
        const pregunta = todasLasPreguntas.find(p => p.id === preguntaId);
        if (pregunta && pregunta.tipo === 'consentimiento') {
            if (valor === true || valor === 'true') {
                preguntaElement.classList.add('respondida');
            } else {
                preguntaElement.classList.remove('respondida');
            }
        } else if (valor !== '' && valor !== null && valor !== undefined) {
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
        while (preguntaActual >= 0) {
            const preguntaAnterior = todasLasPreguntas[preguntaActual];
            // Verificar que la pregunta existe antes de acceder a sus propiedades
            if (!preguntaAnterior) {
                break;
            }
            if (!preguntaAnterior.condicional || debeMostrarPreguntaCondicional(preguntaAnterior)) {
                break;
            }
            preguntaActual--;
        }
        
        // Asegurar que no salimos de los límites
        if (preguntaActual < 0) {
            preguntaActual = 0;
        }
        
        renderizarPregunta();
        actualizarProgreso();
        // Scroll al inicio
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

document.getElementById('btn-siguiente').addEventListener('click', () => {
    // Verificar límites antes de acceder
    if (preguntaActual >= totalPreguntas || preguntaActual < 0) {
        console.error('Índice de pregunta fuera de límites:', preguntaActual);
        return;
    }
    
    const pregunta = todasLasPreguntas[preguntaActual];
    
    // Verificar que la pregunta existe
    if (!pregunta) {
        console.error('Pregunta no encontrada en índice:', preguntaActual);
        return;
    }
    
    // Las preguntas informativas no requieren validación
    if (pregunta.tipo === 'texto_informativo') {
        if (preguntaActual < totalPreguntas - 1) {
            preguntaActual++;
            while (preguntaActual < totalPreguntas) {
                const siguientePregunta = todasLasPreguntas[preguntaActual];
                // Verificar que la pregunta existe antes de acceder a sus propiedades
                if (!siguientePregunta) {
                    break;
                }
                if (!siguientePregunta.condicional || debeMostrarPreguntaCondicional(siguientePregunta)) {
                    break;
                }
                preguntaActual++;
            }
            
            // Verificar que no excedimos los límites
            if (preguntaActual >= totalPreguntas) {
                mostrarResultado();
                return;
            }
            
            renderizarPregunta();
            actualizarProgreso();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        return;
    }
    
    // Validar que la pregunta esté respondida
    const tieneRespuesta = respuestas[pregunta.id] !== undefined && 
                          respuestas[pregunta.id] !== null && 
                          respuestas[pregunta.id] !== '';
    
    // Para preguntas de opción múltiple, verificar que tenga al menos una selección
    const esMultiple = pregunta.tipo === 'opcion_multiple';
    const tieneSeleccionMultiple = esMultiple ? 
        (Array.isArray(respuestas[pregunta.id]) && respuestas[pregunta.id].length > 0) : true;
    
    // Para consentimiento, verificar que esté marcado
    const esConsentimiento = pregunta.tipo === 'consentimiento';
    const tieneConsentimiento = esConsentimiento ? 
        (respuestas[pregunta.id] === true || respuestas[pregunta.id] === 'true') : true;
    
    if (!tieneRespuesta || !tieneSeleccionMultiple || !tieneConsentimiento) {
        // Mensajes específicos por campo
        let mensaje = null;
        if (pregunta.tipo === 'numero') mensaje = 'Por favor, ingresa un valor numérico antes de continuar.';
        else if (pregunta.tipo === 'opcion_multiple') mensaje = 'Por favor, selecciona al menos una opción antes de continuar.';
        else if (pregunta.tipo === 'consentimiento') mensaje = 'Por favor, acepta el consentimiento informado para continuar.';
        else if (pregunta.id === 'DATOS_NOMBRE') mensaje = 'Por favor, ingresa tu nombre completo (nombre y apellido).';
        else if (pregunta.id === 'DATOS_RUT') mensaje = 'Por favor, ingresa tu RUT con dígito verificador (ej: 12345678-9).';
        else if (pregunta.id === 'DATOS_EMAIL') mensaje = 'Por favor, ingresa un correo electrónico válido.';
        else if (pregunta.id === 'DATOS_TELEFONO') mensaje = 'Por favor, ingresa un teléfono válido o déjalo vacío si no aplica.';
        else if (pregunta.id === 'I3') mensaje = 'Por favor, ingresa tu edad (número entre 10 y 120).';
        else if (pregunta.id === 'II2A') mensaje = 'Por favor, ingresa tu peso en Kg (20-300).';
        else if (pregunta.id === 'II2B') mensaje = 'Por favor, ingresa tu estatura en cm (50-250).';
        else mensaje = 'Por favor, completa este campo antes de continuar.';

        alert(mensaje);
        return;
    }
    
    if (preguntaActual < totalPreguntas - 1) {
        preguntaActual++;
        // Saltar preguntas condicionales que no aplican
        while (preguntaActual < totalPreguntas) {
            const siguientePregunta = todasLasPreguntas[preguntaActual];
            // Verificar que la pregunta existe antes de acceder a sus propiedades
            if (!siguientePregunta) {
                break;
            }
            if (!siguientePregunta.condicional || debeMostrarPreguntaCondicional(siguientePregunta)) {
                break;
            }
            preguntaActual++;
        }
        
        // Verificar que no excedimos los límites
        if (preguntaActual >= totalPreguntas) {
            // Si todas las preguntas restantes eran condicionales y no aplicaban, finalizar
            mostrarResultado();
            return;
        }
        
        renderizarPregunta();
        actualizarProgreso();
        // Scroll al inicio
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

document.getElementById('btn-enviar').addEventListener('click', async (e) => {
    e.preventDefault();
    
    // Verificar límites antes de acceder
    if (preguntaActual >= totalPreguntas || preguntaActual < 0) {
        console.error('Índice de pregunta fuera de límites:', preguntaActual);
        mostrarError('Error al acceder a la pregunta. Por favor, recarga la página.');
        return;
    }
    
    const pregunta = todasLasPreguntas[preguntaActual];
    
    // Verificar que la pregunta existe
    if (!pregunta) {
        console.error('Pregunta no encontrada en índice:', preguntaActual);
        mostrarError('Error al acceder a la pregunta. Por favor, recarga la página.');
        return;
    }
    
    // Validar última pregunta
    const tieneRespuesta = respuestas[pregunta.id] !== undefined && 
                          respuestas[pregunta.id] !== null && 
                          respuestas[pregunta.id] !== '';
    const esMultiple = pregunta.tipo === 'opcion_multiple';
    const tieneSeleccionMultiple = esMultiple ? 
        (Array.isArray(respuestas[pregunta.id]) && respuestas[pregunta.id].length > 0) : true;
    
    if (!tieneRespuesta || !tieneSeleccionMultiple) {
        let mensaje = null;
        if (pregunta.tipo === 'numero') mensaje = 'Por favor, ingresa un valor numérico antes de enviar.';
        else if (pregunta.tipo === 'opcion_multiple') mensaje = 'Por favor, selecciona al menos una opción antes de enviar.';
        else if (pregunta.id === 'DATOS_NOMBRE') mensaje = 'Por favor, ingresa tu nombre completo (nombre y apellido).';
        else if (pregunta.id === 'DATOS_RUT') mensaje = 'Por favor, ingresa tu RUT con dígito verificador (ej: 12345678-9).';
        else if (pregunta.id === 'DATOS_EMAIL') mensaje = 'Por favor, ingresa un correo electrónico válido.';
        else mensaje = 'Por favor, selecciona una respuesta antes de enviar.';
        alert(mensaje);
        return;
    }
    
    // Validar que todas las preguntas estén respondidas (excluyendo condicionales no aplicables e informativas)
    const preguntasSinResponder = todasLasPreguntas.filter(p => {
        // Excluir preguntas informativas y condicionales no aplicables
        if (p.tipo === 'texto_informativo') {
            return false; // Las preguntas informativas no requieren respuesta
        }
        if (p.condicional && !debeMostrarPreguntaCondicional(p)) {
            return false; // No contar preguntas condicionales que no aplican
        }
        const tieneResp = respuestas[p.id] !== undefined && 
                         respuestas[p.id] !== null && 
                         respuestas[p.id] !== '';
        if (p.tipo === 'opcion_multiple') {
            return !(Array.isArray(respuestas[p.id]) && respuestas[p.id].length > 0);
        }
        if (p.tipo === 'consentimiento') {
            return !(respuestas[p.id] === true || respuestas[p.id] === 'true');
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
                timestamp: timestamp,
                usar_ia: true  // Activar generación de recomendación con IA
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Si hay recomendación de IA, usarla; si no, usar análisis tradicional
            if (result.recomendacion_ia && result.recomendacion_ia.consejo) {
                mostrarResultado({
                    recomendacion: result.recomendacion_ia.consejo,
                    video: result.recomendacion_ia.video,
                    categoria: result.recomendacion_ia.categoria,
                    fuente: 'ia'
                });
            } else {
                // Obtener análisis y recomendaciones tradicionales
                try {
                    const analisisResponse = await fetch('/api/analisis', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            respuestas: respuestas
                        })
                    });
                    
                    const analisisResult = await analisisResponse.json();
                    
                    if (analisisResult.success && analisisResult.analisis) {
                        mostrarResultado(analisisResult.analisis);
                    } else {
                        mostrarResultado();
                    }
                } catch (error) {
                    console.error('Error al obtener análisis:', error);
                    mostrarResultado();
                }
            }
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

function mostrarResultado(analisis = null) {
    document.getElementById('cuestionario-container').style.display = 'none';
    document.getElementById('resultado-container').style.display = 'block';
    
    // Mostrar recomendaciones si hay análisis
    if (analisis && analisis.recomendacion) {
        const analisisContainer = document.getElementById('analisis-container');
        const recomendacionesTexto = document.getElementById('recomendaciones-texto');
        const videoContainer = document.getElementById('video-container');
        const videoIframe = document.getElementById('video-iframe');
        const videoTitulo = document.getElementById('video-titulo');
        const videoDescripcion = document.getElementById('video-descripcion');
        const video2Container = document.getElementById('video2-container');
        const video2Iframe = document.getElementById('video2-iframe');
        const video2Titulo = document.getElementById('video2-titulo');
        const video2Descripcion = document.getElementById('video2-descripcion');
        
        // Formatear el texto con saltos de línea
        // La IA puede devolver texto con saltos de línea, así que los preservamos
        let textoFormateado = analisis.recomendacion;
        
        // Si viene de IA, puede tener párrafos separados por doble salto de línea
        textoFormateado = textoFormateado.replace(/\n\n+/g, '</p><p>');
        // También manejar saltos de línea simples
        textoFormateado = textoFormateado.replace(/\n/g, '<br>');
        
        recomendacionesTexto.innerHTML = `<p>${textoFormateado}</p>`;
        
        // Actualizar título si es de IA
        const titulo = analisisContainer.querySelector('h3');
        if (analisis.fuente === 'ia' && titulo) {
            titulo.textContent = '💬 Recomendaciones de Mujer Sana IA (Generado con Inteligencia Artificial)';
        }
        
        // Mostrar video si está disponible
        if (analisis.video && analisis.video.url) {
            videoIframe.src = analisis.video.url;
            if (analisis.video.titulo) {
                videoTitulo.textContent = analisis.video.titulo;
            }
            if (analisis.video.descripcion) {
                videoDescripcion.textContent = analisis.video.descripcion;
            }
            videoContainer.style.display = 'block';
        } else {
            videoContainer.style.display = 'none';
        }

        // Mostrar segundo video si está disponible
        if (analisis.video_alt && analisis.video_alt.url) {
            video2Iframe.src = analisis.video_alt.url;
            if (analisis.video_alt.titulo) {
                video2Titulo.textContent = analisis.video_alt.titulo;
            }
            if (analisis.video_alt.descripcion) {
                video2Descripcion.textContent = analisis.video_alt.descripcion;
            }
            video2Container.style.display = 'block';
        } else {
            video2Container.style.display = 'none';
        }
        
        analisisContainer.style.display = 'block';
    } else {
        document.getElementById('analisis-container').style.display = 'none';
        document.getElementById('video-container').style.display = 'none';
        document.getElementById('video2-container').style.display = 'none';
    }
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function mostrarError(mensaje) {
    const container = document.getElementById('cuestionario-container');
    container.innerHTML = `<div class="error">${mensaje}</div>`;
    document.getElementById('loading').style.display = 'none';
    container.style.display = 'block';
}




