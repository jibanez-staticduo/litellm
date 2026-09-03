import json
import os
import time
import uuid

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, StreamingResponse
from starlette.routing import Route

UPSTREAM_AUTH = os.environ.get("SYNTHETIC_UPSTREAM_AUTH", "")


def authorized(request):
    return request.headers.get("authorization") == UPSTREAM_AUTH


def usage():
    return {"prompt_tokens": 20, "completion_tokens": 20, "total_tokens": 40}


def chat_body(model):
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "synthetic chat ok"}, "finish_reason": "stop"}],
        "usage": usage(),
    }


async def chat(request: Request):
    if not authorized(request):
        return JSONResponse({"error": {"message": "upstream authentication failed"}}, status_code=401)
    body = await request.json()
    response = chat_body(body.get("model", "synthetic"))
    if not body.get("stream"):
        return JSONResponse(response)

    async def events():
        yield f"data: {json.dumps(response | {'object': 'chat.completion.chunk', 'choices': [{'index': 0, 'delta': {'role': 'assistant', 'content': 'synthetic chat ok'}, 'finish_reason': None}]})}\n\n"
        yield f"data: {json.dumps(response | {'object': 'chat.completion.chunk', 'choices': [], 'usage': usage()})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


def responses_body(model):
    return {
        "id": f"resp_{uuid.uuid4().hex[:24]}",
        "object": "response",
        "created_at": int(time.time()),
        "status": "completed",
        "model": model,
        "output": [{"type": "message", "id": f"msg_{uuid.uuid4().hex[:16]}", "status": "completed", "role": "assistant", "content": [{"type": "output_text", "text": "synthetic responses ok", "annotations": []}]}],
        "parallel_tool_calls": True,
        "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30, "output_tokens_details": {"reasoning_tokens": 0}},
        "text": {"format": {"type": "text"}},
        "error": None,
        "incomplete_details": None,
        "instructions": None,
        "metadata": {},
        "temperature": 1.0,
        "tool_choice": "auto",
        "tools": [],
        "top_p": 1.0,
        "max_output_tokens": None,
        "previous_response_id": None,
        "reasoning": {"effort": None, "summary": None},
        "truncation": "disabled",
        "user": None,
    }


async def responses(request: Request):
    if not authorized(request):
        return JSONResponse({"error": {"message": "upstream authentication failed"}}, status_code=401)
    body = await request.json()
    response = responses_body(body.get("model", "synthetic"))
    if not body.get("stream"):
        return JSONResponse(response)

    async def events():
        yield f"event: response.created\ndata: {json.dumps({'type': 'response.created', 'sequence_number': 0, 'response': response | {'status': 'in_progress', 'output': []}})}\n\n"
        yield f"event: response.completed\ndata: {json.dumps({'type': 'response.completed', 'sequence_number': 1, 'response': response})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


async def health(_request: Request):
    return PlainTextResponse("ok")


app = Starlette(routes=[
    Route("/health", health, methods=["GET"]),
    Route("/v1/chat/completions", chat, methods=["POST"]),
    Route("/v1/responses", responses, methods=["POST"]),
])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8190)
