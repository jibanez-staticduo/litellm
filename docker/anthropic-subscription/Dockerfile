FROM docker.staticduo.com/litellm@sha256:7263f32613a930e539792b7a1613a02eef617846d8e8ae493ab779a475af9fba
COPY endpoints.py /app/.venv/lib/python3.13/site-packages/litellm/proxy/anthropic_endpoints/endpoints.py
COPY handler.py /app/.venv/lib/python3.13/site-packages/litellm/llms/anthropic/count_tokens/handler.py
COPY streaming_iterator.py /app/.venv/lib/python3.13/site-packages/litellm/responses/litellm_completion_transformation/streaming_iterator.py
COPY model_prices_and_context_window.json /app/.venv/lib/python3.13/site-packages/litellm/model_prices_and_context_window_backup.json
