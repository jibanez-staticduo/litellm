# Anthropic Subscription Implementation Plan

**Estado:** Completado y cerrado el 2026-10-01. El usuario confirma que ha funcionado y acepta la entrega de la fase 1

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking

**Goal:** Usar la suscripcion de Anthropic desde Claude Code a traves de LiteLLM y registrar el consumo con su valor equivalente a precios de API

**Architecture:** Claude Code conserva el login y la renovacion OAuth. LiteLLM autentica por separado al cliente con una virtual key y reenvia Messages al proveedor `anthropic`, usando el OAuth recibido. La custodia central de cuentas para otros clientes se evalua como una fase posterior

**Tech Stack:** LiteLLM Proxy, Anthropic Messages, OAuth del cliente Claude Code, SSE, virtual keys, PostgreSQL spend logs y el mapa de precios de LiteLLM

**Spec:** Peticion del usuario del 2026-10-01, corregida expresamente: la primera fase usa la suscripcion de Anthropic via LiteLLM. El pricing de API representa el consumo; no selecciona una credencial de API ni cambia la facturacion upstream

## Resultado de la investigacion

Revision local: `e3cb7c39cefd1e8b9bdc427b33f1d989cad50641`, igual a `origin/main` tras actualizar referencias el 2026-10-01. La investigacion inicial no incluia verificacion del runtime. La ejecucion posterior verificada del NAS se recoge al final de este documento; Fedora permanece fuera de este despliegue

LiteLLM ya documenta la primera fase en [Using Claude Code Max Subscription](https://docs.litellm.ai/docs/tutorials/claude_code_max_subscription). Anthropic confirma que configurar solo la URL del gateway, conservando el login claude.ai como credencial activa, mantiene los limites y la facturacion de la suscripcion en [Subscriptions and gateways](https://code.claude.com/docs/en/llm-gateway#subscriptions-and-gateways)

La autenticacion doble usa `x-litellm-api-key` para el proxy y `Authorization: Bearer <OAuth>` para Anthropic. No hace falta crear otro proveedor para este caso. La implementacion local reconoce `sk-ant-oat*`, prepara los headers OAuth y puede recibirlos por el endpoint nativo `/v1/messages`

Hay dos huecos comprobados que impiden entregar la fase 1 como un cambio ciego de configuracion. El contador `/v1/messages/count_tokens` no transmite el OAuth del cliente y puede contar localmente o usar una clave API del servidor. Ademas, omitir `api_key` no evita resolver una credencial global. La lista de forwarding por grupos limita algunos headers, pero el OAuth tiene un camino independiente que se aplica a cualquier deployment Anthropic autorizado

OpenCode local, `/home/staticduo/git/opencode`, revision `0112a92c416f5ad833d96e7a8308441f0a875d94`, paquete `1.18.34`, ya no incluye OAuth Anthropic. La retirada consta en [PR #18186](https://github.com/anomalyco/opencode/pull/18186) y [su documentacion](https://opencode.ai/docs/providers/#anthropic). Su plugin historico `opencode-anthropic-auth@0.0.13` hacia PKCE, intercambio y refresh directamente por HTTP, e inferencia en Messages. Tambien alteraba prompt, nombres de herramientas y User-Agent para presentarse como Claude Code. No es una base adecuada para el cliente nativo ni prueba soporte actual para OpenCode

## Que tenemos y que podemos reutilizar

| Componente | Comportamiento comprobado | Aplicacion a Anthropic |
| --- | --- | --- |
| `litellm/llms/chatgpt/authenticator.py` | Perfil o archivo por deployment, locks de hilo/proceso, refresh y escritura atomica con permisos restrictivos | Patron para una posible custodia futura, sin copiar endpoints, claims ni flujo OAuth OpenAI |
| `litellm/llms/chatgpt/responses/transformation.py` | Backend Codex Responses, `store=False`, SSE y replay de reasoning cifrado | Demuestra la separacion entre transporte, autenticar cuenta y adaptar protocolo |
| `litellm/router_utils/fallback_event_handlers.py` | Fallback general y protecciones especificas para perfiles ChatGPT | El fallback general es reutilizable; las protecciones ChatGPT no cubren cuentas Anthropic |
| `litellm/llms/hosted_vllm_codex/chat/transformation.py` | Proveedor del fork que hereda el transporte vLLM | No se necesita para Claude Code, que ya habla Messages |
| `litellm/responses/litellm_completion_transformation/transformation.py` | Bridge de Responses a Chat Completions, herramientas y reasoning | Relevante al evaluar despues Claude desde Codex |
| `litellm/responses/litellm_completion_transformation/hosted_vllm_codex_summary.py` | Resume reasoning de Qwen con inferencia auxiliar cuando Codex pide summary | Es adaptacion de presentacion para Codex, no autenticacion ni parte del flujo Anthropic inicial |
| `litellm/llms/anthropic/common_utils.py` | Detecta OAuth, prepara Bearer/beta, limita la credencial reenviada al proveedor Anthropic | Base existente para la fase 1 |
| `litellm/proxy/litellm_pre_call_utils.py` | Separa headers de credenciales y logging, reenvio por proveedor y `used_client_oauth_token` | Reutilizar y verificar en la release que se despliegue |
| `litellm/llms/anthropic/cost_calculation.py` | Precios del modelo y tratamiento de cache, tier y multiplicadores | Valoracion API sin cambiar la credencial upstream |

Qwen3.8 funciona con Codex mediante un alias especifico `hosted_vllm_codex`, el bridge Responses y metadatos del catalogo del cliente. El resumen auxiliar conserva el reasoning original y limita esperas/buffers. Al cambiar despues a ChatGPT, su transformacion descarta reasoning plano incompatible y conserva el cifrado. Para Anthropic desde Codex habria que comprobar replay de bloques firmados y herramientas, no bastaria cambiar el nombre del proveedor

La configuracion, login y cuota de NAS y Fedora son independientes. Los hechos historicos de cuentas concretas no sustituyen el inventario efectivo antes de ejecutar este plan

## Global Constraints

La fase 1 conserva las credenciales y el refresh en Claude Code. No importa tokens del cliente al almacenamiento de LiteLLM

No configurar la clave LiteLLM como `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_API_KEY` ni `apiKeyHelper`: desplazan el login de suscripcion. Revisar tambien configuracion heredada y managed settings antes del piloto

Los deployments de suscripcion no deben terminar usando una clave API del servidor, un fallback API, Bedrock, Vertex ni otra cuenta cuando falta o falla el OAuth. El piloto debe usar un entorno sin credenciales Anthropic de API y sin fallback de esos aliases. La promocion al proxy compartido exige comprobar la misma propiedad, no asumir que omitir `api_key` elimina una variable global

Reutilizar el soporte `anthropic` existente. No implementar otro OAuth, prefijos `mcp_`, prompts que suplanten clientes ni un nuevo tipo de proveedor para la fase 1

Resolver modelos disponibles para la suscripcion en el momento del piloto y precios desde el mapa efectivo de LiteLLM. No fijar precios externos como literales en los tests

Los secretos no aparecen en logs, capturas, documentos, commits ni comandos compartidos. Usar referencias de entorno o almacenamiento existente y consultas filtradas

Aplicar cambios a una instancia piloto primero. Antes de promocionar, identificar por separado host, release, Compose/mounts y fuente efectiva de configuracion. No convertir este plan en un despliegue simultaneo de la flota

## Review Focus

La credencial OAuth debe llegar solo a Anthropic, y la clave LiteLLM nunca debe llegar upstream

Una solicitud sin OAuth o con OAuth caducado debe fallar sin producir consumo de API por una credencial global o fallback

Los turnos posteriores deben conservar firmas thinking, herramientas, cache y metadatos nativos de Claude Code

El consumo SSE debe quedar registrado, incluyendo desconexion con uso conocido, sin duplicar filas ni costes

El modelo facturado debe ser el realmente servido y el importe debe ser valor equivalente de API, distinguible mediante `used_client_oauth_token`

## Fase 1: Claude Code con su propia suscripcion

### Task 1: Piloto de autenticacion y transporte nativo

**Files:** Configuracion privada efectiva de la instancia piloto y entorno/settings del perfil Claude Code de prueba, descubiertos antes de editar. Referencias de codigo: `litellm/proxy/auth/user_api_key_auth.py`, `litellm/proxy/litellm_pre_call_utils.py`, `litellm/llms/anthropic/common_utils.py`, `litellm/llms/anthropic/pass_through/messages/transformation.py`

**Interfaces:** El cliente envia su OAuth en `Authorization`, mas su virtual key en `x-litellm-api-key`. El proxy responde por `/v1/messages` con Messages/SSE nativo. El refresh sigue siendo responsabilidad del cliente

- [x] Identificar la version efectiva de Claude Code y LiteLLM, los aliases existentes, las credenciales de API globales y los fallbacks aplicables, sin mostrar secretos
- [x] Preparar un proxy piloto sin credenciales Anthropic de API ni fallbacks de los aliases de suscripcion, con la misma release candidata a promocion
- [x] Registrar aliases separados para Sonnet, Opus y Haiku y restringir una virtual key de prueba a esos aliases
- [x] Conservar el forwarding que necesite Claude Code, limitado a estos grupos. Probar OAuth, beta y cuerpo nativo por la ruta seleccionada antes de ampliar forwarding global
- [x] Conectar un perfil Claude Code que tenga login de suscripcion propio y verificar que sigue activo al apuntar a la URL del piloto
- [x] Desde Claude Code, probar texto con streaming, una herramienta y su resultado en el turno siguiente, thinking cuando el modelo lo permita y el contador de tokens que use el cliente
- [x] Confirmar que un error OAuth no produce fallback ni sustituye la credencial, y que los logs no contienen ninguna de las dos claves

Configuracion orientativa de modelos. Los nombres upstream son los presentes en el mapa local consultado; confirmar acceso real y catalogo al ejecutar

```yaml
model_list:
  - model_name: claude-sonnet-5-5
    litellm_params:
      model: anthropic/claude-sonnet-5-5
  - model_name: claude-opus-5-5
    litellm_params:
      model: anthropic/claude-opus-5-5
  - model_name: claude-haiku-4-5
    litellm_params:
      model: anthropic/claude-haiku-4-5
litellm_settings:
  model_group_settings:
    forward_client_headers_to_llm_api:
      - claude-sonnet-5-5
      - claude-opus-5-5
      - claude-haiku-4-5
```

El OAuth tiene un camino especifico por proveedor en este fork. El forwarding por grupo complementa los headers del cliente. No es necesario activar `forward_llm_provider_auth_headers`, que corresponde al caso BYOK con claves API

Esta lista no es una frontera para el OAuth entre aliases Anthropic. El aislamiento del piloto proviene de la instancia sin otras credenciales, su catalogo limitado y el acceso por virtual key

Configuracion del cliente, con `LITELLM_CLAUDE_KEY` obtenido de forma privada y `CLAUDE_PROXY_URL` apuntando a la raiz del proxy, sin anadir `/v1`

```bash
export ANTHROPIC_BASE_URL="$CLAUDE_PROXY_URL"
export ANTHROPIC_CUSTOM_HEADERS="x-litellm-api-key: Bearer $LITELLM_CLAUDE_KEY"
export ANTHROPIC_MODEL=claude-sonnet-5-5
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-5-5
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-5-5
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5
claude
```

El entorno dedicado del piloto debe carecer de `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` y `apiKeyHelper`. No borrar credenciales de perfiles compartidos para conseguirlo. El login nuevo, si hace falta, se completa en el flujo nativo del cliente con el usuario

### Task 2: Reparar count_tokens para el OAuth del cliente

**Files:** Modificar `litellm/proxy/anthropic_endpoints/endpoints.py`, y `litellm/llms/anthropic/count_tokens/handler.py` si necesita recibir los headers nativos. Tests existentes: `tests/test_litellm/proxy/anthropic_endpoints/test_endpoints.py` y `tests/unit/llms/anthropic/test_count_tokens_oauth.py`. Referencias: `litellm/proxy/proxy_server.py` y `litellm/llms/anthropic/count_tokens/token_counter.py`

**Interfaces:** La peticion HTTP autenticada es la fuente confiable del OAuth; el cuerpo del usuario no puede introducir una credencial interna. El branch OAuth del endpoint nativo resuelve un deployment Anthropic autorizado y llama al handler CountTokens existente con ese token. El contador generico conserva su comportamiento para peticiones sin OAuth y otros proveedores

- [x] Extender `test_endpoints.py` con una regresion que envie OAuth y virtual key separados, use un alias y compruebe que la llamada nativa recibe el OAuth y el modelo resuelto, aunque exista una clave API de servidor distinta
- [x] Confirmar que falla con este HEAD: `TokenCountRequest` se construye sin credencial y `internal_token_counter` solo puede buscar la clave del deployment o del entorno
- [x] Implementar un branch interno para las solicitudes OAuth en el endpoint nativo, conservando la autorizacion del alias y sin mutar un deployment compartido ni exponer secretos en `TokenCountRequest`
- [x] Reutilizar `AnthropicCountTokensHandler.handle_count_tokens_request` y su preparacion OAuth. Si se necesitan betas adicionales del cliente, anadir `extra_headers: Mapping[str, str] | None = None` al handler y combinar exclusivamente headers permitidos, preservando la credencial seleccionada
- [x] Comprobar en la regresion que beta/cuerpo soportado llegan upstream, la clave LiteLLM no sale del proxy y un destino no Anthropic no recibe OAuth
- [x] Anadir la regresion de error: un rechazo upstream del contador OAuth conserva su status/error Anthropic y no se convierte en conteo local exitoso ni consulta otra credencial
- [x] Ejecutar los tests afectados y el caso existente de contador sin OAuth. Repetir despues un conteo real desde el perfil Claude Code del piloto y conservar la evidencia sin tokens

El CountTokens handler sabe usar OAuth cuando recibe el token. El fallo esta en el recorrido desde el endpoint, no en la deteccion del prefijo. Esta reparacion no debe sustituirse por un token fijo en configuracion

### Task 3: Contabilidad equivalente a API y pruebas de aislamiento

**Files:** Configuracion/model metadata del piloto, `model_prices_and_context_window.json` como fuente existente. Revisar `litellm/llms/anthropic/cost_calculation.py`, `litellm/proxy/spend_tracking/spend_tracking_utils.py` y `litellm/proxy/hooks/proxy_track_cost_callback.py`. No modificar el mapa de precios salvo discrepancia demostrada

**Interfaces:** Logs contienen modelo servido, usage completo, virtual key y `used_client_oauth_token=true`. `spend` es el valor equivalente de API que solicita el usuario, no una factura de Anthropic

- [x] Comprobar que los aliases resuelven al modelo real y al precio vigente de su deployment, incluyendo entrada, salida, cache read y cache creation/TTL disponibles
- [x] Hacer dos turnos comparables con un prefijo reutilizable y comprobar los contadores cache realmente devueltos. La prueba no presume que todo turno tendra cache hit
- [x] Comparar el coste del spend log con el calculador existente usando el usage y metadata del mismo request. No sumar dos veces tokens cache a los tokens de entrada
- [x] Confirmar `used_client_oauth_token=true` para las solicitudes Anthropic OAuth y atribucion a la virtual key esperada
- [x] Revisar comportamiento de cuota, errores y desconexion de stream. Registrar el uso conocido y distinguir cualquier dato que el proveedor no entregue (errores y uso verificados; ruta de desconexion revisada en common_request_processing.py, sin corte forzado en vivo)
- [x] Verificar que el piloto consumio suscripcion y que no utilizo una credencial de API. La presencia del flag OAuth por si sola no demuestra el tipo de cargo upstream
- [x] Si aparece un defecto, extender el test mapeado correspondiente y escribir la correccion minima. Reproducir el fallo antes de corregir y repetir la verificacion despues

Los tests existentes a revisar y extender solo cuando haya un defecto concreto son `tests/test_litellm/proxy/test_litellm_pre_call_utils.py` para credenciales/logging, `tests/unit/llms/anthropic/test_count_tokens_oauth.py` para count_tokens, `tests/unit/llms/anthropic/pass_through/messages/test_anthropic_experimental_pass_through_messages_handler.py` para Messages y `tests/test_litellm/proxy/spend_tracking/test_spend_tracking_utils.py` para atribucion. Localizar el test de coste ya mapeado dentro de `tests/unit/llms/anthropic/` al corregir contabilidad

Si un proxy compartido permite caer en una clave API global, elegir aislamiento de la instancia de suscripcion para el primer despliegue. Una alternativa posterior es una politica explicita de credencial OAuth obligatoria por deployment, con tests que prueben rechazo antes del envio upstream. No inventar que esa politica existe hoy

### Task 4: Promocion y evidencia desde Claude Code

**Files:** Solo fuentes de configuracion y cliente del host que se haya seleccionado para la primera entrega. El piloto aislado puede ser el endpoint inicial de produccion si la instancia compartida no cumple el aislamiento de credenciales

**Interfaces:** El mismo perfil Claude Code conserva su suscripcion y utiliza la URL seleccionada. El dashboard y spend logs muestran los requests atribuibles a su virtual key

- [x] Registrar la configuracion exacta candidata, el mecanismo de activacion existente y un backup seguro de los campos afectados
- [x] Hacer review proporcional de autenticacion doble, destinos, fallbacks y coste. Si se cambia codigo, ejecutar los tests afectados y los gates exigidos por el repositorio
- [x] Aplicar el cambio mediante el mecanismo del host cuando se ejecute el plan, respetando procesos/turnos activos y las autorizaciones de reinicio vigentes
- [x] Repetir la prueba completa desde Claude Code en el endpoint final y esperar a que el consumo aparezca en el dashboard y spend logs
- [x] Capturar comando/configuracion sin secretos, salida real de Claude Code y evidencia del dashboard. Los tests unitarios no se presentan como prueba de uso real (evidencia del dashboard por su API, sin captura visual)
- [x] Comprobar rollback: restaurar los campos del cliente que cambian la URL y los aliases, conservando su login. Desactivar solo los deployments/virtual key creados por esta entrega

**Aceptacion de fase 1:** Claude Code completa una conversacion con herramientas y streaming pasando por LiteLLM, usa la credencial de suscripcion, conserva el login/refresh nativo, obtiene conteo nativo con la misma credencial, no puede caer en API de pago por el proxy y registra consumo/coste equivalente a API con atribucion correcta. El soporte de codigo/documentacion no sustituye esta prueba real

## Seguimiento fuera de este plan: Varias cuentas y otros clientes

La fase 1 queda aceptada y no tiene trabajo pendiente. La rotacion central y el acceso desde otros clientes requieren un plan separado

El passthrough inicial permite varios clientes Claude Code autenticados con sus propias cuentas. Cada cliente envia su propio OAuth y tiene su virtual key. No proporciona rotacion central de cuentas ni una suscripcion disponible para Codex/OpenCode mediante una sola clave LiteLLM

Un proveedor equivalente a `chatgpt` necesita custodia por perfil, login, refresh, aislamiento concurrente, identidad verificable de cuenta, routing explicito, cuota/cooldown y politica de fallback. No se encontro un autenticador Anthropic integrado que proporcione ese conjunto en el codigo revisado. Detectar un token OAuth en `api_key` no implementa su ciclo de vida

Antes de especificar ese desarrollo, resolver la viabilidad del uso de suscripcion desde otros clientes. [Authentication and credential use](https://code.claude.com/docs/en/legal-and-compliance) restringe OAuth a aplicaciones nativas y no permite que productos de terceros ofrezcan login claude.ai o custodien credenciales de sus usuarios. La retirada del plugin OpenCode hace que no podamos tratarlo como soporte mantenido

Si existe un mecanismo permitido y probado para el uso concreto, elaborar otro plan con un autenticador Anthropic separado. Reutilizar patrones de archivos, locks y escrituras atomicas de ChatGPT, sin generalizar ese autenticador ni copiar su OAuth. Resolver antes de implementar las diferencias de refresh, identificacion, caducidad y cuota; no aplicar umbrales ni endpoints ChatGPT a Anthropic

Para clientes Responses como Codex, evaluar el bridge comun `litellm/responses/litellm_completion_transformation/` y los adaptadores existentes `litellm/llms/anthropic/pass_through/responses_adapters/` con mensajes, herramientas y replay de thinking firmado. Para OpenCode, seleccionar transporte Messages cuando corresponda. Esa compatibilidad no demuestra que las credenciales de suscripcion esten habilitadas para esos clientes

## Fuentes verificadas el 2026-10-01

[LiteLLM Max subscription](https://docs.litellm.ai/docs/tutorials/claude_code_max_subscription), [BYOK](https://docs.litellm.ai/docs/tutorials/claude_code_byok) y [forwarding por grupo](https://docs.litellm.ai/docs/proxy/forward_client_headers)

[Anthropic gateways](https://code.claude.com/docs/en/gateways), [suscripciones](https://code.claude.com/docs/en/llm-gateway#subscriptions-and-gateways), [precedencia de credenciales](https://code.claude.com/docs/en/llm-gateway-connect), [compatibilidad](https://code.claude.com/docs/en/llm-gateway-protocol) y [restricciones de autenticacion](https://code.claude.com/docs/en/legal-and-compliance)

[OpenCode Anthropic](https://opencode.ai/docs/providers/#anthropic), [retirada de OAuth](https://github.com/anomalyco/opencode/pull/18186) y [artefacto historico 0.0.13](https://unpkg.com/opencode-anthropic-auth@0.0.13/index.mjs)

Se consultaron Hindsight compartido, sus paginas pertinentes, Kindly y Context7. Las referencias historicas sirvieron para localizar componentes y decisiones; las afirmaciones tecnicas de este plan se contrastaron con el codigo o las fuentes actuales citadas

## Ejecucion verificada, 2026-10-01

La fase 1 esta activa en NAS, endpoint `http://127.0.0.1:14001`, instancia `litellm-anthropic-subscription` con PostgreSQL independiente. Claude Code conserva su login Pro y su refresh. El lanzador permanente `~/.local/bin/claude-litellm` selecciona el gateway, una virtual key restringida y los modelos canonicos `claude-sonnet-5-5`, `claude-opus-5-5` y `claude-haiku-4-5`. El comando ordinario `claude` conserva la ruta directa y sirve como rollback del cliente

El fix del contador esta en `d17375a5a9`. La imagen candidata desplegada es `sha256:1262f02dcc48bbc4cc9728a03a51a75661845b42000ca8c81df87157d70e28d8`, construida sobre la release NAS 1.105.0 fijada por digest. El proxy compartido existente no fue reiniciado. Los servicios del piloto tienen politica manual `restart: no`

La prueba interactiva desde Claude Code 2.1.285 completo streaming, Read, segundo turno, thinking y `/context`. El contador nativo devolvio HTTP 200 con el OAuth del cliente. Las solicitudes con OAuth invalido o sin OAuth devolvieron HTTP 401, sin credencial alternativa. Opus y Haiku tambien respondieron desde el cliente nativo

Tres spend logs de la conversacion registraron `used_client_oauth_token=true` y coincidieron con el calculador de costes desplegado, incluyendo cache de una hora, cache read y reasoning. Los importes equivalentes fueron USD 0.018318, 0.0015432 y 0.0022766. No se encontraron credenciales raw en los logs del contenedor ni las filas de consumo inspeccionadas

Los tests focalizados pasan 48 casos y el gate integrado `make check` pasa. Una review independiente no encontro defectos bloqueantes. Los errores no JSON del proveedor conservan el status y se normalizan al formato Anthropic. La evidencia reproducible y los comandos operativos estan en `docker/anthropic-subscription/README.md`

No se ha forzado agotamiento real de cuota ni interrupcion durante generacion. Los errores 401/429 y la ausencia de fallback local se verifican en las regresiones. El consumo se ha comprobado en la base de datos y en `/spend/logs/ui` con HTTP 200; no se ha capturado una pantalla del dashboard. Estos limites no cambian la evidencia real de la suscripcion ni la aceptacion del transporte nativo
