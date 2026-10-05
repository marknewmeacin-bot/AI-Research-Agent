from ollama import Client
from config import OLLAMA_HOST, OLLAMA_MODEL
from tools import (
    add_research_note,
    clear_research_notes,
    get_research_notes,
    get_verified_research_notes,
    read_webpage,
    search_web,
    verify_finding,
)

ollama_client = Client(host=OLLAMA_HOST)
TARGET_VERIFIED_NOTES = 5

AVAILABLE_TOOLS = {
    "search_web": search_web,
    "read_webpage": read_webpage,
    "add_research_note": add_research_note,
    "get_research_notes": get_research_notes,
    "verify_finding": verify_finding,
}

TOOLS = [search_web, read_webpage, add_research_note, get_research_notes, verify_finding]


def generate_report(user_request: str, verified_notes: list) -> str:
    """Generates the final Markdown report from stored findings."""
    notes_summary = "\n\n".join(
        [f"Source: {n['source']}\nFinding: {n['finding']}\nEvidence: {n['evidence']}" for n in verified_notes]
    )

    response = ollama_client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a research analyst. Write a concise, professional research report in clean Markdown using headers and bullet points.",
            },
            {
                "role": "user",
                "content": f"Topic: {user_request}\n\nVerified Findings:\n{notes_summary}\n\nProduce a structured Markdown report.",
            },
        ],
    )
    return response.message.content


def research_agent(user_request: str, max_steps: int = 10, progress_callback=None):
    clear_research_notes()

    def emit(data):
        if progress_callback:
            progress_callback(data)

    emit({"type": "plan", "message": "Research plan created", "plan": "1. Search web\n2. Extract facts\n3. Synthesize report"})

    messages = [
        {
            "role": "system",
            "content": (
                "You are an automated research assistant. Follow this loop strictly:\n"
                "1. Call search_web\n"
                "2. Call read_webpage\n"
                "3. Call add_research_note with key facts.\n"
                "Do NOT read more than 2 pages without taking notes."
            ),
        },
        {"role": "user", "content": f"Research Topic: {user_request}"},
    ]

    for step in range(max_steps):
        verified = get_verified_research_notes()

        # Target met check: Stop execution early if target verified notes count is hit
        if len(verified) >= TARGET_VERIFIED_NOTES:
            emit({"type": "step", "step": step + 1, "message": "Target research findings met. Writing final report..."})
            report = generate_report(user_request, verified)
            emit({"type": "complete", "report": report})
            return report

        # Step cap fallback: Force finish if stuck beyond step 6 with at least 1 verified finding
        if step >= 6 and len(verified) >= 1:
            emit({"type": "step", "step": step + 1, "message": "Maximum research depth reached. Synthesizing available findings..."})
            report = generate_report(user_request, verified)
            emit({"type": "complete", "report": report})
            return report

        emit({"type": "step", "step": step + 1, "message": f"Agent step {step + 1}"})

        try:
            response = ollama_client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=TOOLS,
                options={"temperature": 0.1},
            )
        except Exception as err:
            emit({"type": "error", "message": f"Execution error: {str(err)}"})
            return None

        messages.append(response.message)

        # Handle turns where the model produces plain text instead of tool calls
        if not response.message.tool_calls:
            notes = get_research_notes()
            if notes:
                latest = notes[-1]
                verify_finding(latest["source"], latest["finding"], latest["evidence"])
                emit({"type": "verification", "message": "Verified recorded note automatically"})
            else:
                messages.append({"role": "user", "content": "Please invoke a tool to continue research."})
            continue

        # Execute returned tool calls
        for tool_call in response.message.tool_calls:
            t_name = tool_call.function.name
            t_args = tool_call.function.arguments or {}

            emit({"type": "tool", "tool": t_name, "message": f"Using tool: {t_name}"})
            t_func = AVAILABLE_TOOLS.get(t_name)

            if t_func:
                try:
                    res = t_func(**t_args)
                    emit({"type": "tool_complete", "tool": t_name, "message": f"Completed: {t_name}"})
                except Exception as e:
                    res = f"Error executing tool: {str(e)}"
            else:
                res = "Tool not found."

            # Hard truncation on long webpage outputs to protect context length
            if t_name == "read_webpage" and isinstance(res, str):
                truncated_res = res[:1200] + "\n...[Webpage truncated to preserve context buffer]"
            else:
                truncated_res = str(res)

            messages.append({"role": "tool", "content": truncated_res, "tool_name": t_name})

            # Auto-verify notes right after saving them
            if t_name == "add_research_note":
                notes = get_research_notes()
                if notes:
                    latest = notes[-1]
                    verify_finding(latest["source"], latest["finding"], latest["evidence"])
                    emit({"type": "verification", "message": "Verified recorded note automatically"})

    # Final sweep
    verified = get_verified_research_notes()
    if verified:
        report = generate_report(user_request, verified)
        emit({"type": "complete", "report": report})
        return report

    emit({"type": "error", "message": "Loop ended without sufficient findings."})
    return None


def run_agent(request: str) -> str:
    """Helper entry point for synchronous execution."""
    return research_agent(request, max_steps=10)