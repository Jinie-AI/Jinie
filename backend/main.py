from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from srs.pipeline import run_srs_pipeline
from component_generator.router import router as components_router


app = FastAPI(title="Jinie Backend")


# Allow the React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stage 5 — Component Generator, exposed at POST /api/components/generate
app.include_router(components_router)


class SRSRequest(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {
        "message": "Jinie Backend is running"
    }


@app.post("/api/srs/generate")
def generate_srs(request: SRSRequest):
    try:
        if not request.prompt.strip():
            raise HTTPException(
                status_code=400,
                detail="Prompt cannot be empty"
            )

        result = run_srs_pipeline(request.prompt)

        return result.model_dump()

    except HTTPException:
        raise

    except Exception as e:
        print("SRS generation error:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )