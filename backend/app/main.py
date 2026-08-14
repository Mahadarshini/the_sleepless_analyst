import uuid
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Depends,
)

from sqlalchemy.orm import Session

from app.agents.workflow import (
    build_graph,
)

from app.db.database import (
    get_db,
)

from app.db.init_db import (
    init_database,
)

from app.services.document_service import (
    create_document,
)

from app.services.document_service import (
    save_chunks,
)

from app.services.hash_service import (
    calculate_file_hash,
)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    init_database()

    yield


app = FastAPI(
    title="Document Intelligence API",
    version="0.1.0",
    lifespan=lifespan,
)


graph = build_graph()


UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    exist_ok=True
)


@app.get("/")
def root():

    return {
        "message": (
            "Document Intelligence API"
        ),
        "status": "running",
    }


@app.post(
    "/documents/analyze"
)
async def analyze_document(

    file: UploadFile = File(...),

    db: Session = Depends(
        get_db
    ),
):

    run_id = str(
        uuid.uuid4()
    )

    file_path = (
        UPLOAD_DIR
        / file.filename
    )

    contents = await file.read()

    file_path.write_bytes(
        contents
    )

    content_hash = (
        calculate_file_hash(
            str(file_path)
        )
    )

    document = create_document(

        db=db,

        filename=file.filename,

        content_hash=content_hash,
    )

    # Do not analyze the same
    # document twice.

    if document.status == "processed":

        return {

            "message": (
                "Document already processed"
            ),

            "document_id": str(
                document.id
            ),

            "filename": (
                document.filename
            ),
        }

    try:

        state = {

            "run_id": run_id,

            "document_id": str(
                document.id
            ),

            "file_path": str(
                file_path
            ),

            "filename": (
                file.filename
            ),
        }

        result = graph.invoke(
            state
        )

        save_chunks(

            db=db,

            document_id=document.id,

            chunks=result[
                "chunks"
            ],
        )

        document.document_type = (
            result[
                "document_type"
            ]
        )

        document.status = (
            "processed"
        )

        db.commit()

        return {

            "run_id": run_id,

            "document_id": str(
                document.id
            ),

            "document": (
                file.filename
            ),

            "document_type": (
                result.get(
                    "document_type"
                )
            ),

            "facts": (
                result.get(
                    "extracted_facts",
                    [],
                )
            ),

            "report": (
                result.get(
                    "report"
                )
            ),
        }

    except Exception as error:

        document.status = (
            "failed"
        )

        db.commit()

        raise error