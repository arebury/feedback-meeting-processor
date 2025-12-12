"""
MCP Server for Meeting Feedback Processing
FastAPI implementation with JSON-RPC 2.0 protocol
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional, Any, Union
import json

app = FastAPI(
    title="Feedback Meeting Processor MCP",
    description="MCP server that processes meeting feedback and returns organized HTML widgets",
    version="1.0.0"
)

# CORS middleware for ChatGPT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Data Models
# ============================================

class FeedbackItem(BaseModel):
    item: str
    category: Literal["UI", "UX", "Copy", "Tech"]
    priority: Literal["critical", "improvement", "nice_to_have"]
    original_quote: str

class ProcessFeedbackArgs(BaseModel):
    feedback_items: list[FeedbackItem]

class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[dict] = None
    id: Optional[Union[int, str]] = None

# ============================================
# Constants
# ============================================

CATEGORY_EMOJIS = {
    "UI": "🎨",
    "UX": "🧠",
    "Copy": "✍️",
    "Tech": "⚙️"
}

PRIORITY_CONFIG = {
    "critical": {"emoji": "🔴", "label": "Crítico", "order": 0},
    "improvement": {"emoji": "🟡", "label": "Mejora", "order": 1},
    "nice_to_have": {"emoji": "🟢", "label": "Nice-to-have", "order": 2}
}

TOOL_DEFINITION = {
    "name": "process_meeting_feedback",
    "description": "Procesa items de feedback de reuniones y los muestra agrupados por prioridad con categorías visuales",
    "inputSchema": {
        "type": "object",
        "properties": {
            "feedback_items": {
                "type": "array",
                "description": "Lista de items de feedback extraídos de la transcripción",
                "items": {
                    "type": "object",
                    "properties": {
                        "item": {
                            "type": "string",
                            "description": "Descripción del punto de feedback"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["UI", "UX", "Copy", "Tech"],
                            "description": "Categoría del feedback"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "improvement", "nice_to_have"],
                            "description": "Nivel de prioridad"
                        },
                        "original_quote": {
                            "type": "string",
                            "description": "Frase original de donde se extrae el feedback"
                        }
                    },
                    "required": ["item", "category", "priority", "original_quote"]
                }
            }
        },
        "required": ["feedback_items"]
    }
}

# ============================================
# HTML Widget Generator
# ============================================

def generate_html_widget(feedback_items: list[dict]) -> str:
    """Generate HTML widget grouped by priority with categories"""
    
    # Group items by priority
    grouped = {"critical": [], "improvement": [], "nice_to_have": []}
    for item in feedback_items:
        priority = item.get("priority", "nice_to_have")
        if priority in grouped:
            grouped[priority].append(item)
    
    # Count totals
    counts = {p: len(items) for p, items in grouped.items()}
    total = sum(counts.values())
    
    # Generate items HTML for each priority group
    def render_items(items: list[dict]) -> str:
        if not items:
            return '<p style="color: #6b7280; font-style: italic; margin: 0;">Sin items en esta categoría</p>'
        
        html_items = []
        for item in items:
            category = item.get("category", "UI")
            category_emoji = CATEGORY_EMOJIS.get(category, "📌")
            html_items.append(f'''
                <div style="background: #f8fafc; border-radius: 8px; padding: 12px; margin-bottom: 8px; border-left: 3px solid #e2e8f0;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span style="font-size: 14px;">{category_emoji}</span>
                        <span style="font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">{category}</span>
                    </div>
                    <p style="margin: 0 0 8px 0; color: #1e293b; font-size: 14px; line-height: 1.5;">{item.get("item", "")}</p>
                    <p style="margin: 0; font-size: 12px; color: #94a3b8; font-style: italic;">"{item.get("original_quote", "")}"</p>
                </div>
            ''')
        return ''.join(html_items)
    
    # Generate priority sections
    priority_sections = []
    for priority_key in ["critical", "improvement", "nice_to_have"]:
        config = PRIORITY_CONFIG[priority_key]
        items = grouped[priority_key]
        count = counts[priority_key]
        
        priority_sections.append(f'''
            <div style="margin-bottom: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 18px;">{config["emoji"]}</span>
                        <h3 style="margin: 0; font-size: 16px; font-weight: 600; color: #334155;">{config["label"]}</h3>
                    </div>
                    <span style="background: #e2e8f0; color: #475569; font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 12px;">{count}</span>
                </div>
                <div style="padding-left: 4px;">
                    {render_items(items)}
                </div>
            </div>
        ''')
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feedback de Reunión</title>
</head>
<body style="margin: 0; padding: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: #ffffff;">
    <div style="max-width: 600px; margin: 0 auto;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 20px; margin-bottom: 20px; color: white;">
            <h1 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 700;">📋 Resumen de Feedback</h1>
            <p style="margin: 0; font-size: 14px; opacity: 0.9;">Total de items procesados: <strong>{total}</strong></p>
        </div>
        
        <!-- Summary Badges -->
        <div style="display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 100px; background: #fef2f2; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #dc2626;">{counts["critical"]}</div>
                <div style="font-size: 11px; color: #991b1b; text-transform: uppercase; letter-spacing: 0.5px;">Críticos</div>
            </div>
            <div style="flex: 1; min-width: 100px; background: #fefce8; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #ca8a04;">{counts["improvement"]}</div>
                <div style="font-size: 11px; color: #854d0e; text-transform: uppercase; letter-spacing: 0.5px;">Mejoras</div>
            </div>
            <div style="flex: 1; min-width: 100px; background: #f0fdf4; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="font-size: 24px; font-weight: 700; color: #16a34a;">{counts["nice_to_have"]}</div>
                <div style="font-size: 11px; color: #166534; text-transform: uppercase; letter-spacing: 0.5px;">Nice-to-have</div>
            </div>
        </div>
        
        <!-- Priority Sections -->
        {''.join(priority_sections)}
        
        <!-- Footer -->
        <div style="text-align: center; padding-top: 16px; border-top: 1px solid #e2e8f0;">
            <p style="margin: 0; font-size: 11px; color: #94a3b8;">Generado por Feedback Meeting Processor MCP</p>
        </div>
    </div>
</body>
</html>'''
    
    return html

# ============================================
# MCP Endpoint Handlers
# ============================================

def handle_tools_list() -> dict:
    """Handle tools/list method"""
    return {
        "tools": [TOOL_DEFINITION]
    }

def handle_tools_call(params: dict) -> dict:
    """Handle tools/call method"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name != "process_meeting_feedback":
        return {
            "isError": True,
            "content": [{
                "type": "text",
                "text": f"Unknown tool: {tool_name}"
            }]
        }
    
    try:
        feedback_items = arguments.get("feedback_items", [])
        html_widget = generate_html_widget(feedback_items)
        
        return {
            "content": [{
                "type": "resource",
                "resource": {
                    "uri": "feedback://widget",
                    "mimeType": "text/html+skybridge",
                    "text": html_widget
                }
            }]
        }
    except Exception as e:
        return {
            "isError": True,
            "content": [{
                "type": "text",
                "text": f"Error processing feedback: {str(e)}"
            }]
        }

def handle_initialize() -> dict:
    """Handle initialize method"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "feedback-meeting-processor",
            "version": "1.0.0"
        }
    }

# ============================================
# Main JSON-RPC Endpoint
# ============================================

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """JSON-RPC 2.0 endpoint for MCP protocol"""
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None
        }
    
    rpc_request = JsonRpcRequest(**body)
    method = rpc_request.method
    params = rpc_request.params or {}
    request_id = rpc_request.id
    
    # Route to appropriate handler
    result = None
    error = None
    
    if method == "initialize":
        result = handle_initialize()
    elif method == "tools/list":
        result = handle_tools_list()
    elif method == "tools/call":
        result = handle_tools_call(params)
    elif method == "notifications/initialized":
        # Acknowledge notification
        return {"jsonrpc": "2.0", "result": {}, "id": request_id}
    else:
        error = {"code": -32601, "message": f"Method not found: {method}"}
    
    # Build response
    response = {"jsonrpc": "2.0", "id": request_id}
    if error:
        response["error"] = error
    else:
        response["result"] = result
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "feedback-meeting-processor-mcp"}

@app.get("/")
async def root():
    return {
        "name": "Feedback Meeting Processor MCP",
        "version": "1.0.0",
        "description": "MCP server for processing meeting feedback",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "process_feedback": "/process-feedback"
        }
    }

# ============================================
# REST Endpoint for ChatGPT Actions
# ============================================

class FeedbackRequest(BaseModel):
    """Request model for processing feedback - used by ChatGPT Actions"""
    feedback_items: list[FeedbackItem]

class FeedbackResponse(BaseModel):
    """Response model with HTML widget"""
    success: bool
    total_items: int
    critical_count: int
    improvement_count: int
    nice_to_have_count: int
    html_widget: str

@app.post("/process-feedback", response_model=FeedbackResponse, 
          summary="Process meeting feedback",
          description="Recibe items de feedback de reuniones y devuelve un widget HTML organizado por prioridad",
          tags=["Feedback"])
async def process_feedback(request: FeedbackRequest):
    """
    Procesa items de feedback de reuniones y genera un widget HTML visual.
    
    - **feedback_items**: Lista de items con descripción, categoría (UI/UX/Copy/Tech), 
      prioridad (critical/improvement/nice_to_have) y quote original.
    
    Retorna un widget HTML con los items agrupados por prioridad y contadores.
    """
    feedback_items = [item.dict() for item in request.feedback_items]
    html_widget = generate_html_widget(feedback_items)
    
    # Count by priority
    counts = {"critical": 0, "improvement": 0, "nice_to_have": 0}
    for item in feedback_items:
        priority = item.get("priority", "nice_to_have")
        if priority in counts:
            counts[priority] += 1
    
    return FeedbackResponse(
        success=True,
        total_items=len(feedback_items),
        critical_count=counts["critical"],
        improvement_count=counts["improvement"],
        nice_to_have_count=counts["nice_to_have"],
        html_widget=html_widget
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
