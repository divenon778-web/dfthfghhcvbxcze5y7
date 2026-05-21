from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional
import algorithms
import database

app = FastAPI(title="Vain Backend")

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
    <html>
        <head><style>
            body { background:#0a0a0a; color:#fff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }
            .panel { background:#00000080; backdrop-filter:blur(20px); border:1px solid #252525; padding:30px; border-radius:12px; width:300px; text-align:center; }
            input { width:90%; padding:10px; margin:10px 0; background:#00000033; border:1px solid #252525; color:#fff; border-radius:6px; }
            button { width:100%; padding:10px; background:rgba(255,255,255,0.3); border:1px solid #fff; color:#000; border-radius:6px; cursor:pointer; font-weight:bold; }
            button:hover { backdrop-filter:brightness(2); }
            #result { margin-top:15px; color:#4ade80; word-break:break-all; }
        </style></head>
        <body>
            <div class="panel">
                <h2>Admin Panel</h2>
                <input type="password" id="adminKey" placeholder="Admin Key">
                <button onclick="generate()">Generate Key</button>
                <div id="result"></div>
            </div>
            <script>
                async function generate() {
                    const key = document.getElementById('adminKey').value;
                    const res = await fetch('/admin/generate', {
                        method: 'POST',
                        headers: { 'X-Admin-Key': key }
                    });
                    const data = await res.json();
                    document.getElementById('result').textContent = data.key || data.detail;
                }
            </script>
        </body>
    </html>
    """
    return Response(content=html, media_type="text/html")

@app.post("/admin/generate")
async def generate_key(x_admin_key: str = Header(...)):
    if not database.check_admin(x_admin_key):
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return {"key": database.generate_key()}
