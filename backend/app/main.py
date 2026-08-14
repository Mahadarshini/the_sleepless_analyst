import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File

from app.agents.workflow import build_graph

from contextlib import asynccontextmanager

from app.db.init_db import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield


app = FastAPI(
    title="Document Intelligence API",
    version="0.1.0",
    lifespan=lifespan,
)

graph = build_graph()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {
        "message": "Document Intelligence API",
        "status": "running",
    }


@app.post("/documents/analyze")
async def analyze_document(
    file: UploadFile = File(...)
):

    run_id = str(uuid.uuid4())

    file_path = UPLOAD_DIR / file.filename

    contents = await file.read()

    file_path.write_bytes(contents)

    state = {
        "run_id": run_id,
        "document_id": str(uuid.uuid4()),
        "file_path": str(file_path),
        "filename": file.filename,
    }

    result = graph.invoke(state)

    return {
        "run_id": run_id,
        "document": file.filename,
        "document_type": result.get(
            "document_type"
        ),
        "facts": result.get(
            "extracted_facts",
            [],
        ),
        "report": result.get(
            "report"
        ),
    }