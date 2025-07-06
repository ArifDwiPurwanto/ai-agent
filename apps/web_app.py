"""
Web interface for AI Personal Assistant Agent using FastAPI
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import create_agent
from src.config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Personal Assistant Agent",
    description="Web interface for the modular AI personal assistant",
    version="1.0.0"
)

# Templates and static files
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    model: str = "openai"
    persona: str = "personal"

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

class AgentInfo(BaseModel):
    name: str
    available_models: List[str]
    available_personas: List[str]
    memory_status: dict

# Global agent instance
agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    try:
        agent = await create_agent(
            model=settings.DEFAULT_MODEL,
            persona="personal"
        )
        logger.info("AI Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "agent_name": settings.AGENT_NAME,
            "available_models": ["openai", "gemini"],
            "available_personas": ["personal", "research", "technical"]
        }
    )

@app.get("/api/agent/info", response_model=AgentInfo)
async def get_agent_info():
    """Get agent information and status"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Get memory status
    memory_status = {
        "stm_messages": len(agent.memory_manager.stm.get_messages()),
        "max_stm_messages": settings.STM_MAX_MESSAGES,
        "ltm_available": hasattr(agent.memory_manager, 'ltm') and agent.memory_manager.ltm is not None
    }
    
    return AgentInfo(
        name=settings.AGENT_NAME,
        available_models=["openai", "gemini"],
        available_personas=["personal", "research", "technical"],
        memory_status=memory_status
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatMessage):
    """Process a chat message"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Switch model/persona if requested
        if chat_request.model != agent.current_model:
            await agent.switch_model(chat_request.model)
        
        if chat_request.persona != agent.current_persona:
            await agent.switch_persona(chat_request.persona)
        
        # Process the message
        response = await agent.process_message(chat_request.message)
        
        return ChatResponse(
            response=response,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return ChatResponse(
            response="I'm sorry, I encountered an error processing your request.",
            success=False,
            error=str(e)
        )

@app.post("/api/agent/switch-model")
async def switch_model(model: str):
    """Switch AI model"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if model not in ["openai", "gemini"]:
        raise HTTPException(status_code=400, detail="Invalid model")
    
    try:
        await agent.switch_model(model)
        return {"success": True, "current_model": model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/switch-persona")
async def switch_persona(persona: str):
    """Switch agent persona"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if persona not in ["personal", "research", "technical"]:
        raise HTTPException(status_code=400, detail="Invalid persona")
    
    try:
        await agent.switch_persona(persona)
        return {"success": True, "current_persona": persona}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/history")
async def get_conversation_history():
    """Get conversation history"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    messages = agent.memory_manager.stm.get_messages()
    return {"messages": messages, "count": len(messages)}

@app.delete("/api/memory/clear")
async def clear_memory():
    """Clear conversation memory"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        agent.memory_manager.stm.clear_all()
        return {"success": True, "message": "Memory cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    if not agent:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Agent not initialized"
        }))
        await websocket.close()
        return
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "chat":
                # Process chat message
                user_message = message_data.get("message", "")
                model = message_data.get("model", "openai")
                persona = message_data.get("persona", "personal")
                
                # Switch model/persona if needed
                if model != agent.current_model:
                    await agent.switch_model(model)
                
                if persona != agent.current_persona:
                    await agent.switch_persona(persona)
                
                # Process message
                response = await agent.process_message(user_message)
                
                # Send response back
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "message": response,
                    "model": agent.current_model,
                    "persona": agent.current_persona
                }))
                
            elif message_data.get("type") == "ping":
                # Handle ping for connection keep-alive
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "timestamp": "2025-07-06T15:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting AI Personal Assistant Web Interface...")
    print(f"Agent: {settings.AGENT_NAME}")
    print(f"Model: {settings.DEFAULT_MODEL}")
    print("🌐 Open your browser to: http://localhost:8000")
    
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
