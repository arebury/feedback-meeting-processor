# Feedback Meeting Processor MCP

Servidor MCP (Model Context Protocol) para ChatGPT que procesa transcripciones de reuniones de feedback y devuelve los puntos organizados por categoría y prioridad en un widget HTML.

## 🚀 Inicio Rápido

### Instalación

```bash
cd server
pip install -r requirements.txt
```

### Ejecutar localmente

```bash
uvicorn main:app --reload --port 8000
```

El servidor estará disponible en `http://localhost:8000`

## 📡 Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información del servidor |
| `/health` | GET | Health check |
| `/mcp` | POST | Endpoint JSON-RPC 2.0 para MCP |

## 🔧 Tool: process_meeting_feedback

### Input

```json
{
  "feedback_items": [
    {
      "item": "Descripción del punto",
      "category": "UI" | "UX" | "Copy" | "Tech",
      "priority": "critical" | "improvement" | "nice_to_have",
      "original_quote": "Frase original de donde sale"
    }
  ]
}
```

### Categorías

| Emoji | Categoría |
|-------|-----------|
| 🎨 | UI |
| 🧠 | UX |
| ✍️ | Copy |
| ⚙️ | Tech |

### Prioridades

| Emoji | Prioridad |
|-------|-----------|
| 🔴 | Crítico |
| 🟡 | Mejora |
| 🟢 | Nice-to-have |

### Output

Widget HTML embebido con MIME type `text/html+skybridge` que muestra:
- Items agrupados por prioridad
- Contadores por categoría
- Quote original de cada feedback

## 📝 Ejemplo de Uso

### Listar herramientas disponibles

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### Procesar feedback

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "process_meeting_feedback",
      "arguments": {
        "feedback_items": [
          {
            "item": "El botón de login es muy pequeño",
            "category": "UI",
            "priority": "critical",
            "original_quote": "No encuentro donde hacer login"
          },
          {
            "item": "El mensaje de error es confuso",
            "category": "Copy",
            "priority": "improvement",
            "original_quote": "No entiendo este mensaje"
          }
        ]
      }
    },
    "id": 2
  }'
```

## 🚀 Deploy en Render

1. Conecta tu repositorio a Render
2. El archivo `render.yaml` configurará automáticamente el servicio
3. La URL de tu servidor será: `https://feedback-meeting-processor.onrender.com`

## 📄 Licencia

MIT
