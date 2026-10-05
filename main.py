import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from agent import generate_report, research_agent, run_agent
from schemas import ChatRequest, ChatResponse
from tools import get_verified_research_notes


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Research AI server")
    yield
    print("Shutting down Research AI server")


app = FastAPI(
    title="Research AI Agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def home():
    return FileResponse("frontend/index.html")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        result = await run_in_threadpool(run_agent, request.message)
        return ChatResponse(response=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/research")
async def research(topic: str):
    if not topic.strip():
        raise HTTPException(status_code=400, detail="Topic parameter is required.")

    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()

    def progress_callback(event):
        loop.call_soon_threadsafe(queue.put_nowait, event)

    def run_pipeline():
        research_agent(user_request=topic, max_steps=15, progress_callback=progress_callback)
        notes = get_verified_research_notes()
        if not notes:
            raise ValueError("No verified findings collected during research.")
        
        progress_callback({"type": "step", "message": "Synthesizing final Markdown report..."})
        return generate_report(user_request=topic, verified_notes=notes)

    async def event_stream():
        task = asyncio.create_task(asyncio.to_thread(run_pipeline))

        while True:
            if task.done() and queue.empty():
                break

            try:
                event = await asyncio.wait_for(queue.get(), timeout=0.5)
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                continue

        try:
            report_content = await task
            yield f"data: {json.dumps({'type': 'complete', 'report': report_content})}\n\n"
        except Exception as err:
            yield f"data: {json.dumps({'type': 'error', 'message': str(err)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")