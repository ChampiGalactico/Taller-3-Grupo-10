import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.environ["MONGO_URI"])
db = client[os.environ["MONGO_DB"]]


@app.get("/")
def inicio():
    return {"estado": "API funcionando correctamente"}


# ---------- COMENTARIOS ----------
@app.get("/bares/{bar_id}/comentarios")
def get_comentarios(bar_id: int):
    return list(db.comentarios_bares.find({"bar_id": bar_id}, {"_id": 0}).sort("fecha", -1))


@app.post("/bares/{bar_id}/comentarios")
def crear_comentario(bar_id: int, datos: dict):
    if not datos.get("texto"):
        raise HTTPException(status_code=400, detail="El texto es obligatorio")
    comentario = {
        "bar_id": bar_id,
        "autor": datos.get("autor", "anónimo"),
        "texto": datos["texto"],
        "fecha": datetime.now().isoformat(),
    }
    db.comentarios_bares.insert_one(comentario)
    comentario.pop("_id", None)
    return comentario


# ---------- EVENTOS ----------
@app.get("/bares/{bar_id}/eventos")
def get_eventos(bar_id: int):
    return list(db.eventos.find({"bar_id": bar_id}, {"_id": 0}))


@app.post("/bares/{bar_id}/eventos")
def crear_evento(bar_id: int, datos: dict):
    if not datos.get("nombre"):
        raise HTTPException(status_code=400, detail="El nombre es obligatorio")
    evento = {k: v for k, v in datos.items() if v not in (None, "")}
    evento["bar_id"] = bar_id
    evento["fecha_creacion"] = datetime.now().isoformat()
    db.eventos.insert_one(evento)
    evento.pop("_id", None)
    return evento
