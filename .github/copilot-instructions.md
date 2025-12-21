# Instrucciones para agentes de IA — Mujer Sana IA

Objetivo rápido
- Repositorio pequeño: backend Flask monolítico + frontend estático. La app sirve un cuestionario CPC-28, guarda respuestas en JSON y opcionalmente solicita una recomendación a Google Gemini.

Arquitectura y flujo de datos (resumen)
- Backend principal: [app.py](app.py). Expone:
  - `GET /api/cuestionario` → devuelve el objeto `CUESTIONARIO`.
  - `POST /api/respuestas` → guarda `respuestas` en `respuestas/respuestas_<timestamp>.json`. Si `usar_ia=true` llama a Gemini y añade `recomendacion_ia` al response.
  - `POST /api/analisis` → análisis local usando `analizar_respuestas_cpc28()` (fallback sin IA).
- Frontend: archivos estáticos en `templates/index.html` y `static/js/app.js` que consumen los endpoints anteriores.

Puntos críticos y convenciones del proyecto
- Guardado local: la carpeta `respuestas/` se crea automáticamente; los ficheros usan el prefijo `respuestas_` + timestamp (ver `guardar_respuestas` en `app.py`).
- Estructuras de datos: `CUESTIONARIO` y `VIDEOS_EDUCATIVOS` están definidos en `app.py` como literales Python; las modificaciones a la UI/orden de preguntas deben sincronizarse aquí.
- Flag de IA: el payload a `/api/respuestas` puede incluir `usar_ia` booleano; si es `true` el servidor intentará usar Gemini.
- Integración Gemini: usa `google.generativeai` y `model.generate_content(...)` con `response_mime_type="application/json"`. El código espera que la salida sea JSON estricto (ver `generar_recomendacion_ia`).

Dependencias y ejecución
- Instalar: `pip install -r requirements.txt`.
- Ejecutar local: `python app.py` o `./start.sh` (README contiene instrucciones). Para recarga automática:
  ```bash
  export FLASK_ENV=development
  python app.py
  ```

Patrones a respetar al editar
- Cambios de datos del cuestionario: actualizar `CUESTIONARIO` en `app.py` y la interfaz en `templates/index.html` / `static/js/app.js` simultáneamente.
- No cambiar la firma de los endpoints sin actualizar el frontend estático.
- Los videos y categorías están en `VIDEOS_EDUCATIVOS`; referenciar esa constante para cualquier cambio de contenido multimedia.

Seguridad y secretos (detectados)
- `app.py` configura Gemini con una API key; revisar `.env` y la variable `GEMINI_API_KEY`. Actualmente el código contiene una asignación directa — revisar para mover la clave a `.env` y evitar commits.

Debugging rápido
- Revisar logs en consola (Flask imprime errores). Los fallos de IA suelen fallar en `generar_recomendacion_ia()`; hay prints y fallbacks que devuelven texto simple.
- Verificar que `respuestas/` tenga permisos de escritura cuando el endpoint falla al guardar.

Ejemplos útiles (curl)
- Obtener cuestionario:
  ```bash
  curl http://localhost:5000/api/cuestionario
  ```
- Enviar respuestas sin IA:
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"respuestas": {...}, "timestamp": "2025-12-21T12-00-00"}' http://localhost:5000/api/respuestas
  ```

Dónde mirar primero (archivos clave)
- [app.py](app.py) — lógica completa del servidor, cuestionario y reglas de negocio.
- [README.md](README.md) — contexto del proyecto y comandos básicos.
- [templates/index.html](templates/index.html) y [static/js/app.js](static/js/app.js) — cómo la UI consume la API.
- `respuestas/` — ejemplo de salida y patrón de nombres.

Notas para PRs y cambios de IA
- Si actualizar la interacción con Gemini, agregar pruebas manuales: enviar `{"usar_ia": true}` y comprobar `recomendacion_ia` en la respuesta.
- Evitar introducir claves en el repo; añadir comprobación en `app.py` para leer `os.getenv('GEMINI_API_KEY')` si se cambia la implementación.

Feedback
- ¿Quisieras que incluya snippets concretos de payloads del frontend o reglas de validación JSON extraídas de `static/js/app.js`? Indica qué detalle necesitas y lo agrego.
