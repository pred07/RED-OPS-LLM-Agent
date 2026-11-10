from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import threading
from datetime import datetime

from core.state_manager import StateManager
from core.chat_manager import ChatManager
from core.hybrid_brain import HybridBrain
from core.monitor import Monitor
from core.reasoning_engine import ReasoningEngine

app = FastAPI(title="REDOPS Strategic API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared Instances
sm = StateManager()
cm = ChatManager()
hb = HybridBrain(ollama_url="http://127.0.0.1:11434")
re_engine = ReasoningEngine()

# Start background monitor
mon = Monitor(sm, cm)
threading.Thread(target=mon.start, daemon=True).start()

class ChatQuery(BaseModel):
    query: str
    sender: str = "Operator"

def process_ai_response(query: str, state_summary: str, chat_history: list):
    """Background task to get AI response."""
    response = hb.get_chat_response(query, state_summary, chat_history)
    cm.add_message("ai", response, "REDOPS")

@app.get("/api/state")
async def get_state():
    sm.state = sm._load_state()
    return sm.get_all_targets()

@app.get("/api/history")
async def get_history():
    cm.messages = cm._load_history()
    return cm.messages

@app.get("/api/suggestions/{ip}")
async def get_suggestions(ip: str):
    target = sm.get_all_targets().get(ip)
    if not target:
        return []
    target["ip"] = ip # Inject IP for command replacement
    return re_engine.get_suggestions(target)

@app.post("/api/chat")
async def chat(data: ChatQuery, background_tasks: BackgroundTasks):
    # 1. Add user message instantly
    cm.add_message("user", data.query, data.sender)
    
    # 2. TACTICAL FAST-PATH: Instant response for simple greetings
    q = data.query.lower().strip()
    if q in ["hi", "hii", "hiii", "hiiii", "hello", "hey"]:
        cm.add_message("ai", "Standing by, Operator. I've analyzed the current findings. Ready for your tactical query.", "REDOPS")
        return {"status": "success", "message": "Fast-path response delivered."}
    
    # 3. Heavy Neural Task
    summary = hb.sanitize_state(sm.get_all_targets())
    history = cm.get_last_n(10)
    background_tasks.add_task(process_ai_response, data.query, summary, history)
    
    return {"status": "success", "message": "Neural processing initiated."}

@app.post("/api/clear")
async def clear_state():
    cm.clear()
    paths = ["reasoning_engine/results", "reasoning_engine/data/state.json"]
    for p in paths:
        try:
            if os.path.isdir(p): 
                import shutil
                shutil.rmtree(p)
                os.makedirs(p)
            elif os.path.isfile(p): os.remove(p)
        except: pass
    return {"status": "cleared"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
