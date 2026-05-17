from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.common.custom_exception import CustomException
from app.core.ai_agent import get_response_from_ai_agents
from app.config.settings import settings
from app.common.logger import get_logger

logger = get_logger(__name__)
app = FastAPI(title="Multi Agent API", version="0.1")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/")
def root():
    return {"message": "Multi Agent API is running"}

@app.get("/favicon.ico")
def favicon():
    return JSONResponse(status_code=204, content=None)

class RequestState(BaseModel):
    model_name: str
    system_prompt: str
    messages: List[str]
    allow_search: bool

@app.post("/chat")
@limiter.limit("10/minute")
def chat_endpoint(request:RequestState):
    logger.info(f"Received request for model: {request.model_name}")

    if request.model_name not in settings.ALLOWED_MODEL_NAMES:
        logger.warning("Invalid model name")
        raise HTTPException(status_code=400 , detail="Invalid model name")
    
    try:
        response = get_response_from_ai_agents(
            request.model_name,
            request.messages,
            request.allow_search,
            request.system_prompt
        )

        logger.info(f"Sucesfully got response from AI Agent {request.model_name}")

        return {"response" : response}
    
    except Exception as e:
        logger.error("Some error ocuured during reponse generation")
        raise HTTPException(
            status_code=500 , 
            detail=str(CustomException("Failed to get AI response" , error_detail=e))
            )