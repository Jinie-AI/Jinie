import asyncio
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from srs.pipeline import run_srs_pipeline
from component_generator.router import router as components_router


app = FastAPI(title="Jinie Backend")


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stage 5 — Component Generator, exposed at POST /api/components/generate
app.include_router(components_router)


# =========================================================
# REQUEST MODEL
# =========================================================

class SRSRequest(BaseModel):
    prompt: str


# =========================================================
# ROOT TEST
# =========================================================

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "Jinie Backend is working!"
    }


# =========================================================
# NORMAL SRS GENERATION
# =========================================================

@app.post("/api/srs/generate")
def generate_srs(request: SRSRequest):

    print("\n========================================")
    print("SRS GENERATION REQUEST RECEIVED")
    print("========================================")
    print("Prompt:", request.prompt)

    if not request.prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty"
        )

    try:

        print("Starting SRS pipeline...")

        result = run_srs_pipeline(
            request.prompt
        )

        print("SRS PIPELINE FINISHED SUCCESSFULLY")

        return result.model_dump(mode="json")

    except Exception as e:

        print("SRS GENERATION ERROR:")
        print(repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# STREAMING SRS GENERATION
# =========================================================

@app.post("/api/srs/generate-stream")
async def generate_srs_stream(request: SRSRequest):

    print("\n========================================")
    print("SRS STREAM REQUEST RECEIVED")
    print("========================================")
    print("Prompt:", request.prompt)

    if not request.prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty"
        )

    async def event_generator():

        progress_queue = asyncio.Queue()

        loop = asyncio.get_running_loop()

        # -------------------------------------------------
        # Progress callback
        # -------------------------------------------------

        def progress_callback(progress):

            print("PROGRESS:", progress)

            asyncio.run_coroutine_threadsafe(
                progress_queue.put(progress),
                loop
            )

        # -------------------------------------------------
        # Run pipeline in background thread
        # -------------------------------------------------

        async def run_pipeline():

            try:

                print("Starting pipeline thread...")

                result = await asyncio.to_thread(
                    run_srs_pipeline,
                    request.prompt,
                    None,
                    progress_callback
                )

                print("PIPELINE FINISHED SUCCESSFULLY")

                await progress_queue.put({
                    "type": "complete",
                    "progress": 100,
                    "stage": "complete",
                    "message": "SRS generation complete",
                    "result": result.model_dump(mode="json")
                })

            except Exception as e:

                print("PIPELINE ERROR:")
                print(repr(e))

                await progress_queue.put({
                    "type": "error",
                    "progress": 0,
                    "stage": "error",
                    "message": str(e)
                })

        # -------------------------------------------------
        # Start pipeline
        # -------------------------------------------------

        task = asyncio.create_task(
            run_pipeline()
        )

        try:

            while True:

                data = await progress_queue.get()

                print(
                    "SENDING EVENT:",
                    data.get("type"),
                    data.get("stage"),
                    data.get("progress")
                )

                yield (
                    f"data: {json.dumps(data)}\n\n"
                )

                if data["type"] in [
                    "complete",
                    "error"
                ]:
                    break

        finally:

            if not task.done():

                task.cancel()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )