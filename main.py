from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import algorithms
import database

app = FastAPI(title="Vain Backend")

# Enable CORS so the userscript can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    history: List[dict]
    count: int
    algorithm: str = "vain"
    prediction_history: Optional[List[dict]] = []

@app.get("/")
async def root():
    html = """
    <!DOCTYPE html>
    <html>
        <head><style>
            body { background:#0a0a0a; color:#fff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }
            h1 { background:linear-gradient(310deg, #FFF 30%, #aaa 50%, #FFF 70%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:48px; }
            p { color:#ffffff7b; }
        </style></head>
        <body>
            <div style="text-align:center;">
                <h1>Vain API</h1>
                <p>Backend Operational</p>
            </div>
        </body>
    </html>
    """
    return Response(content=html, media_type="text/html")

@app.post("/predict")
async def predict(req: PredictionRequest, x_user_key: str = Header(...)):
    if not database.is_valid_key(x_user_key):
        raise HTTPException(status_code=401, detail="Invalid key")
        
    algo_map = {
        "vain": algorithms.vain_algo,
        "pastgames": algorithms.past_games,
        "aspect": algorithms.aspect_algo,
        "algo2": algorithms.algorithm2,
        "coxy": algorithms.coxy_mines2
    }
    
    func = algo_map.get(req.algorithm, algorithms.vain_algo)
    
    try:
        result = func(req.history, req.count, req.prediction_history)
        return {"safeIndices": result, "algorithm": req.algorithm}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin")
async def admin_panel():
    html = """
    <!DOCTYPE html>
    <html = """
    <!DOCTYPE html>
    <html
