import base64
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import (
    Final,
    cast,  # noqa: TID251  # SDK image union discriminates arrays and tuple file descriptors at runtime
)

from httpx._types import FileTypes as HTTPFileTypes
from httpx._types import RequestFiles
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from litellm.litellm_core_utils.get_provider_specific_headers import ProviderSpecificHeaderUtils
from litellm.llms.chatgpt.common_utils import (
    CHATGPT_API_BASE,
    chatgpt_client_api_base,
    get_chatgpt_client_credential,
    get_chatgpt_request_credential,
    is_chatgpt_oauth_key,
)
from litellm.types.utils import ProviderSpecificHeader
from staticduo_litellm.compatibility.provider_http import oauth_headers
from staticduo_litellm.compatibility.provider_providers_chatgpt_images import (
    AllMessageValues,
    FileTypes,
    GenericLiteLLMParams,
    GPTImageGenerationConfig,
    ImageEditRequestUtils,
    OpenAIImageEditConfig,
    without_oauth_identity_headers,
)
from staticduo_litellm.providers.chatgpt.authenticator import Authenticator


class ReferenceImage(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    image_url: str = Field(pattern=r"^(data:image/(png|jpeg|webp);base64,|https://)")


_PROVIDER_SPECIFIC_HEADERS: Final[TypeAdapter[ProviderSpecificHeader | Sequence[ProviderSpecificHeader] | None]] = (
    TypeAdapter(ProviderSpecificHeader | Sequence[ProviderSpecificHeader] | None)
)
_STRING_HEADERS: Final = TypeAdapter(Mapping[str, str])


def encode_reference(
    file: HTTPFileTypes | FileTypes,
) -> dict[str, str]:  # mutable-ok: image handler requires dictionaries
    content: Final = file[1] if isinstance(file, tuple) else file
    raw: Final = (
        Path(os.fsdecode(content)).read_bytes()
        if isinstance(content, os.PathLike)
        else content.encode()
        if isinstance(content, str)
        else content
        if isinstance(content, bytes)
        else content.read()
    )
    content_type: Final = (
        file[2]
        if isinstance(file, tuple) and len(file) >= 3 and file[2]
        else ImageEditRequestUtils.get_image_content_type(raw)
    )
    if content_type not in ("image/png", "image/jpeg", "image/webp"):
        raise ValueError("Reference images must be PNG, JPEG, or WEBP")
    return {"image_url": f"data:{content_type};base64," + base64.b64encode(raw).decode("ascii")}


def image_headers(
    headers: Mapping[str, object],
    model: str,
    params: Mapping[str, object],
    api_key: str | None = None,
    api_base: str | None = None,
) -> dict[str, object]:  # mutable-ok: image handler requires dictionaries
    normalized_params: Final = GenericLiteLLMParams.model_validate(params)
    raw_params: Final = TypeAdapter(Mapping[str, object]).validate_python(params)
    typed_headers: Final = TypeAdapter(Mapping[str, str]).validate_python(headers)
    scoped_headers: Final = ProviderSpecificHeaderUtils.get_provider_specific_headers(
        provider_specific_header=_PROVIDER_SPECIFIC_HEADERS.validate_python(
            raw_params.get("provider_specific_header")
        ),
        custom_llm_provider="chatgpt",
    )
    configured_headers: Final = _STRING_HEADERS.validate_python(raw_params.get("extra_headers") or {})
    client_credential_params: Final = raw_params
    client_credential: Final = get_chatgpt_client_credential(typed_headers) or get_chatgpt_request_credential(
        client_credential_params
    )
    client_api_key: Final = (
        api_key
        if isinstance(api_key, str)
        and is_chatgpt_oauth_key(api_key)
        and client_credential is None
        else None
    )
    explicit_account_id: Final = next(
        (
            value
            for key, value in {**scoped_headers, **configured_headers, **typed_headers}.items()
            if key.lower() == "chatgpt-account-id"
        ),
        None,
    )
    if client_credential is not None or client_api_key is not None:
        chatgpt_client_api_base(api_base or normalized_params.api_base or CHATGPT_API_BASE)
    identity_headers: Final = (
        {
            "Authorization": f"Bearer {client_credential.access_token}",
            **({"ChatGPT-Account-Id": client_credential.account_id} if client_credential.account_id else {}),
        }
        if client_credential is not None
        else {
            "Authorization": f"Bearer {client_api_key}",
            **({"ChatGPT-Account-Id": explicit_account_id} if explicit_account_id else {}),
        }
        if client_api_key is not None
        else {}
    )
    raw_auth_headers: Final = oauth_headers(
        normalized_params,
        model,
        headers=(identity_headers if client_credential is not None or client_api_key is not None else None),
    )
    validated_auth_headers: Final = _STRING_HEADERS.validate_python(raw_auth_headers)
    auth_headers: Final[Mapping[str, str]] = {
        **validated_auth_headers,
        **(
            {"ChatGPT-Account-Id": explicit_account_id}
            if explicit_account_id and (client_credential is not None or client_api_key is not None)
            else {}
        ),
    }
    return {
        **without_oauth_identity_headers(typed_headers),
        **auth_headers,
        **{
            key: value
            for key, value in typed_headers.items()
            if key.lower() not in ("cookie", "x-litellm-api-key", "authorization", "chatgpt-account-id")
        },
        "accept": "application/json",
    }


class ChatGPTImageGenerationConfig(GPTImageGenerationConfig):
    def validate_environment(
        self,
        headers: Mapping[str, object],
        model: str,
        messages: Sequence[AllMessageValues],
        optional_params: Mapping[str, object],
        litellm_params: Mapping[str, object],
        api_key: str | None = None,
        api_base: str | None = None,
    ) -> dict[str, object]:  # mutable-ok: image handler requires dictionaries
        return image_headers(headers, model, litellm_params, api_key=api_key, api_base=api_base)

    def get_complete_url(
        self,
        api_base: str | None,
        api_key: str | None,
        model: str,
        optional_params: Mapping[str, object],
        litellm_params: Mapping[str, object],
        stream: bool | None = None,
    ) -> str:
        return f"{(api_base or Authenticator.get_api_base()).rstrip('/')}/images/generations"

    def transform_image_generation_request(
        self,
        model: str,
        prompt: str,
        optional_params: Mapping[str, object],
        litellm_params: Mapping[str, object],
        headers: Mapping[str, object],
    ) -> dict[str, object]:  # mutable-ok: image handler requires dictionaries
        return {"model": model, "prompt": prompt, **optional_params}


class ChatGPTImageEditConfig(OpenAIImageEditConfig):
    def validate_environment(
        self,
        headers: Mapping[str, object],
        model: str,
        api_key: str | None = None,
        litellm_params: Mapping[str, object] | None = None,
        api_base: str | None = None,
    ) -> dict[str, object]:  # mutable-ok: image handler requires dictionaries
        return image_headers(
            headers,
            model,
            litellm_params or MappingProxyType({}),
            api_key=api_key,
            api_base=api_base,
        )

    def get_complete_url(self, model: str, api_base: str | None, litellm_params: Mapping[str, object]) -> str:
        return f"{(api_base or Authenticator.get_api_base()).rstrip('/')}/images/edits"

    def use_multipart_form_data(self) -> bool:
        return False

    def transform_image_edit_request(
        self,
        model: str,
        prompt: str | None,
        image: FileTypes | Sequence[FileTypes] | None,
        image_edit_optional_request_params: Mapping[str, object],
        litellm_params: GenericLiteLLMParams,
        headers: Mapping[str, object],
    ) -> tuple[dict[str, object], RequestFiles]:  # mutable-ok: image handler requires dictionaries
        if image_edit_optional_request_params.get("mask") is not None:
            raise ValueError("ChatGPT image editing does not support masks")
        references: Final = getattr(litellm_params, "images", None)
        if references is not None:
            if image:
                raise ValueError("Specify only one of image or images")
            validated: Final = TypeAdapter(tuple[ReferenceImage, ...]).validate_python(references)
            if not 1 <= len(validated) <= 5:
                raise ValueError("images must contain between 1 and 5 reference images")
            return {
                "prompt": prompt,
                **image_edit_optional_request_params,
                "model": model,  # the authenticated alias wins over passthrough fields
                "images": tuple(item.model_dump() for item in validated),
            }, ()

        inputs: Final = (
            cast(Sequence[FileTypes], tuple(image))  # cast-ok: SDK image arrays contain the declared file union
            if isinstance(image, list)
            else (cast(FileTypes, image),)  # cast-ok: a tuple is an SDK file descriptor
            if image is not None
            else ()
        )
        encoded: Final = tuple(encode_reference(file) for file in inputs)
        if not 1 <= len(encoded) <= 5:
            raise ValueError("images must contain between 1 and 5 reference images")
        return {
            "prompt": prompt,
            **image_edit_optional_request_params,
            "model": model,  # the authenticated alias wins over passthrough fields
            "images": encoded,
        }, ()
