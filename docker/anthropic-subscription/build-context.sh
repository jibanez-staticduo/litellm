#!/bin/sh
set -eu

destination=${1:?Supply an empty build-context directory}
source_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
mkdir -p "$destination"
if [ -n "$(ls -A -- "$destination")" ]; then
    printf '%s\n' 'The build-context directory must be empty' >&2
    exit 1
fi

for relative in \
    litellm/main.py \
    litellm/caching/caching_handler.py \
    litellm/router.py \
    litellm/router_utils/fallback_event_handlers.py \
    litellm/types/litellm_params.py \
    litellm/types/router.py \
    litellm/types/utils.py \
    litellm/litellm_core_utils/core_helpers.py \
    litellm/litellm_core_utils/get_litellm_params.py \
    litellm/litellm_core_utils/health_check_helpers.py \
    litellm/litellm_core_utils/litellm_logging.py \
    litellm/litellm_core_utils/memory_luna_pricing.py \
    litellm/litellm_core_utils/prompt_templates/factory.py \
    litellm/litellm_core_utils/prompt_templates/common_utils.py \
    litellm/llms/anthropic/authenticator.py \
    litellm/llms/anthropic/oauth_policy.py \
    litellm/llms/anthropic/native_transport.py \
    litellm/llms/anthropic/common_utils.py \
    litellm/llms/anthropic/chat/transformation.py \
    litellm/llms/anthropic/chat/handler.py \
    litellm/llms/anthropic/chat/guardrail_translation/handler.py \
    litellm/llms/openai/chat/guardrail_translation/handler.py \
    litellm/llms/openai/responses/guardrail_translation/handler.py \
    litellm/llms/anthropic/pass_through/messages/transformation.py \
    litellm/llms/anthropic/pass_through/messages/handler.py \
    litellm/llms/anthropic/count_tokens/handler.py \
    litellm/llms/anthropic/count_tokens/token_counter.py \
    litellm/proxy/anthropic_endpoints/endpoints.py \
    litellm/proxy/proxy_server.py \
    litellm/proxy/litellm_pre_call_utils.py \
    litellm/proxy/health_check.py \
    litellm/proxy/_types.py \
    litellm/proxy/guardrails/guardrail_hooks/headroom/headroom.py \
    litellm/proxy/guardrails/guardrail_hooks/headroom/native_text.py \
    litellm/proxy/spend_tracking/spend_tracking_utils.py \
    litellm/responses/litellm_completion_transformation/streaming_iterator.py
do
    mkdir -p "$destination/$(dirname -- "$relative")"
    cp "$source_root/$relative" "$destination/$relative"
done

cp "$source_root/docker/anthropic-subscription/Dockerfile" "$destination/Dockerfile"
cp "$source_root/model_prices_and_context_window.json" "$destination/model_prices_and_context_window.json"
