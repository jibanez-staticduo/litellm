# Anthropic Subscription Implementation Plan

**Estado:** En ejecucion. La fase 1 nativa esta entregada y el candidato HTTP gestionado paso sus gates y se retiro. El motor SDK nativo supera el rechazo HTTP de OpenCode en probes reales. Se implementan broker, transporte y QA antes de promover a Fedora y despues NAS

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking

**Goal:** Usar suscripciones Anthropic a traves de LiteLLM, registrar el consumo con su valor equivalente a precios de API y completar la gestion de varias cuentas y el acceso desde otros clientes

**Architecture:** Claude Code conserva el login y la renovacion OAuth. LiteLLM autentica por separado al cliente con una virtual key y reenvia Messages al proveedor `anthropic`, usando el OAuth recibido. La fase 2 implementa perfiles OAuth gestionados con seleccion explicita y refresh serializado. Codex pasa en aislamiento; OpenCode recibe un rechazo por extra usage. La promocion gestionada permanece bloqueada

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

## Fase 2: Varias cuentas y otros clientes

La fase 1 quedo aceptada en el piloto y la ruta compartida completa herramientas y continuacion desde Claude Code. La publicacion de modelos en el NAS compartido esta verificada. El candidato gestionado sigue aislado y no se promueve a Fedora ni NAS por el bloqueo externo de OpenCode subscription-only

### Decision de ejecucion de la fase 2

La prueba diferencial inicial confirmo HTTP 429 para un cuerpo generico y HTTP 200 al incluir un bloque `x-anthropic-billing-header`, con el mismo OAuth y un User-Agent propio de LiteLLM. El motor SDK exige un bridge con estado para herramientas e historial y se descarto como transporte de esta entrega. Se implemento compatibilidad HTTP experimental, seleccionada por el administrador con `anthropic_oauth_compatibility: claude_code`, version 2.1.286, manteniendo prompts y nombres de herramientas del cliente

Los deployments centrales usan `use_anthropic_oauth: true`, `anthropic_auth_profile` y `anthropic_token_dir`. `AnthropicAuthenticator` importa explicitamente una autorizacion dedicada, conserva cada perfil con custodia exclusiva, serializa refresh y persiste tokens rotados atomicamente con permisos 0600. El directorio privado usa 0700. Router fija politica, perfil y destino desde el deployment y desactiva fallbacks para los aliases gestionados. Chat, Messages, Responses mediante el bridge comun y count_tokens usan la misma cuenta sin consultar credenciales API globales

Los aliases por perfil permiten seleccion explicita de cuentas. No hay rotacion automatica ni planificacion por cuota. NAS y Fedora disponen de autorizaciones independientes, y Claude CLI no debe seguir renovando la autorizacion importada que custodia LiteLLM

### Trabajo pendiente y criterios de cierre

- [x] Publicar los aliases nativos de fase 1 en `https://litellm.staticduo.com` para el equipo `49cfd117-ef74-4eec-b26e-2d2ff083f5be`, verificar catalogo autenticado y llamada real desde Claude Code
- [x] Implementar perfiles gestionados, seleccion explicita y refresh serializado. Verificar refresh real con rotacion en el candidato aislado y autorizaciones NAS/Fedora independientes
- [x] Implementar politica de deployment que impide cambiar cuenta, destino, credencial o fallback desde el request, con pruebas focalizadas
- [x] Reparar replay firmado de thinking en Responses y verificar herramienta con continuacion en el candidato aislado
- [x] Probar candidato 04 aislado: Messages con los tres modelos, Chat Completions, Responses, dos rutas de count_tokens y replay firmado con herramientas
- [x] Validar Codex 0.159.2 real con herramientas, archivo y resume en aislamiento, con 207 reasoning tokens y sin inventar catalogo nativo Anthropic
- [ ] Completar OpenCode subscription-only. OpenCode 2.0.20 recibe HTTP 400 por extra usage en Messages y Responses, tambien tras reintentar con `drop_params: true` solo en el piloto para `prompt_cache_key`
- [x] Verificar ledger gestionado: cinco registros exitosos conservan `used_client_oauth_token=false`, `used_server_oauth_token=true`, `anthropic_auth_profile=default` y la virtual key esperada. Sus costes coinciden con el calculador desplegado
- [x] Ejecutar gate final del candidato: `make check` pasa con tipos API regenerados, lint y presupuestos sin modificarlos
- [x] Retirar los temporales anteriores de fase 1, conservando datos y archivos privados
- [x] Parar y eliminar el piloto gestionado despues de QA contable, conservando DB y volumenes. Verificar ausencia de ambos contenedores con `docker ps -a` y salud del proxy nativo compartido
- [ ] Promover primero a Fedora y luego a NAS solo cuando el alcance subscription-only cumpla aceptacion. No promover el candidato gestionado con el bloqueo actual

### Bloqueo externo comprobado

Anthropic devolvio HTTP 400 a OpenCode 2.0.20 en ambos transportes con este mensaje:

> Third-party apps now draw from your extra usage, not your plan limits. Add more at claude.ai/settings/usage and keep going

La consulta OAuth `GET /api/oauth/usage` confirma `extra_usage.is_enabled=false` y `credits_ever_enabled=false`. No se habilita extra usage para sortear el rechazo. La prueba inicial de cuerpo generico HTTP 429 no explicaba por si sola este bloqueo. El requisito de OpenCode subscription-only no esta satisfecho aunque Codex funcione en aislamiento

La investigacion del SDK oficial encontro perfiles independientes y streaming, pero no un proveedor stateless equivalente para herramientas de Codex/OpenCode, historial assistant y thinking firmado. El candidato usa el proveedor Anthropic existente y el bridge comun Responses. Su compatibilidad experimental no demuestra habilitacion general de clientes por parte del proveedor

### Motor nativo, reapertura comprobada

El bloqueo corresponde al transporte HTTP directo. El SDK oficial 0.3.287 completo una prueba real con el prompt original de OpenCode, identidad propia del puente y extra usage desactivado. Otra prueba devolvio tres herramientas en un mensaje, incluidas dos con argumentos identicos. Sus handlers quedaron suspendidos mientras el caller devolvia resultados en orden inverso. El motor mantuvo la asociacion correcta, thinking firmado y otro turno user en la misma sesion. Descartar el SDK por complejidad no demostraba imposibilidad

Se implementara un broker interno Messages/SSE con sesiones nativas, manteniendo el proveedor Anthropic y el bridge Responses existentes. El modo `anthropic_execution_mode: native_sdk` sera exclusivo del deployment. URL y credencial del servicio permaneceran separadas del OAuth Anthropic. El broker fijara perfil, identidad autenticada, deployment y modelo de cada sesion, validara el historial y los IDs pendientes y traducira los nombres MCP de forma reversible, conservando nombres HTTP y firmas originales

Cada perfil nativo tendra un `CLAUDE_CONFIG_DIR` dedicado con autorizacion propia y renovacion por Claude Code original. El access token en ENV solo demuestra el probe: no se usara como fuente de produccion para un Query largo. No se compartiran refresh tokens con el autenticador HTTP ni se usara SessionStore para copiar credenciales. La custodia HTTP anterior permanece separada para rollback

El contador debe contar el cuerpo solicitado con la misma cuenta del engine, sin inferencia auxiliar de pago, sin aproximaciones presentadas como conteo exacto y sin exponer credenciales al proxy o cliente. La prueba nativa de renovacion forzo la caducidad del perfil dedicado, invoco `getContextUsage({detail: "full"})` sin prompt y verifico rotacion por el motor. El SDK oficial de API conto dos cuerpos arbitrarios con el acceso propio del engine: 8 y 208 tokens, sin inferencia. NAS y Fedora tienen autorizaciones nativas independientes con directorios 0700 y credenciales 0600 Se verificara la renovacion nativa antes de aceptar produccion. Los controles de API sin equivalencia documentada se rechazaran, y los cambios de historial que el motor no pueda importar no se sintetizaran dentro de prompts

- [x] Probar SDK nativo con prompt OpenCode original, herramientas paralelas y repetidas, resultados externos en orden inverso, thinking firmado y otro turno
- [x] Implementar broker tipado con autenticacion privada, aislamiento de sesiones, streaming, cancelacion y pruebas funcionales con SDK inyectado
- [ ] Integrar el modo nativo trusted en Chat, Messages, Responses y ambos contadores, preservando politica de cuentas y contabilidad
- [x] Verificar autorizaciones nativas independientes, refresh, parametros efectivos y conteo exacto sin cargos auxiliares
- [ ] Validar OpenCode y Codex reales en aislamiento, eliminar todos los contenedores temporales y conservar datos
- [ ] Probar el mismo candidato en Fedora y solo despues promover a NAS, con modelos visibles y consumo atribuible

### Resultado del cliente OpenCode con motor nativo

El request completo del agente OpenCode 2.0.20, con doce herramientas, falla antes de `message_start`. La captura del cuerpo y su ejecucion directa con Agent SDK 0.3.287 y el mismo perfil nativo reproducen HTTP 400 de Anthropic con el requisito de extra usage. El resultado SDK contiene `is_error=true` y el mismo mensaje de facturacion observado en HTTP directo. El parser SSE de OpenCode completa la llamada auxiliar de titulo, que no lleva herramientas; ese probe no demuestra que el agente completo pueda consumir los limites del plan

La consulta OAuth de uso del perfil nativo devuelve HTTP 200 y `extra_usage.is_enabled=false`. No se habilita extra usage ni se cambia la identidad de la aplicacion para evitar el rechazo. El criterio subscription-only de OpenCode sigue incumplido y bloquea la promocion ordenada a Fedora y NAS

El piloto nativo pasa los tres modelos en Messages, Chat, Responses, ambos contadores y replay firmado de una herramienta. Cinco registros nativos conservan servidor OAuth, perfil default y la virtual key esperada; el coste coincide con el calculador desplegado. Las correcciones de thinking vacio firmado y herramientas `type: custom` disponen de regresiones. El gate `make check` pasa sobre el candidato Python anterior a la correccion posterior de caller en Responses

La pagina real del Admin UI del NAS con el filtro de equipo solicitado muestra los tres aliases canonicos de fase 1. Los aliases gestionados `-subscription` no se han publicado en los proxies compartidos

## Fuentes verificadas el 2026-10-01

[LiteLLM Max subscription](https://docs.litellm.ai/docs/tutorials/claude_code_max_subscription), [BYOK](https://docs.litellm.ai/docs/tutorials/claude_code_byok) y [forwarding por grupo](https://docs.litellm.ai/docs/proxy/forward_client_headers)

[Anthropic gateways](https://code.claude.com/docs/en/gateways), [suscripciones](https://code.claude.com/docs/en/llm-gateway#subscriptions-and-gateways), [precedencia de credenciales](https://code.claude.com/docs/en/llm-gateway-connect), [compatibilidad](https://code.claude.com/docs/en/llm-gateway-protocol) y [restricciones de autenticacion](https://code.claude.com/docs/en/legal-and-compliance)

[OpenCode Anthropic](https://opencode.ai/docs/providers/#anthropic), [retirada de OAuth](https://github.com/anomalyco/opencode/pull/18186) y [artefacto historico 0.0.13](https://unpkg.com/opencode-anthropic-auth@0.0.13/index.mjs)

Se consultaron Hindsight compartido, sus paginas pertinentes, Kindly y Context7. Las referencias historicas sirvieron para localizar componentes y decisiones; las afirmaciones tecnicas de este plan se contrastaron con el codigo o las fuentes actuales citadas

## Ejecucion verificada, 2026-10-01

### Piloto inicial

El piloto aislado del NAS, endpoint `http://127.0.0.1:14001`, demostro el transporte nativo con PostgreSQL independiente. Claude Code 2.1.285 completo streaming, Read, segundo turno, thinking y `/context` conservando su login Pro y refresh. Opus y Haiku tambien respondieron desde el cliente nativo. El contador nativo devolvio HTTP 200 y las solicitudes con OAuth invalido o sin OAuth devolvieron HTTP 401

Tres spend logs de esa conversacion registraron `used_client_oauth_token=true` y coincidieron con el calculador de costes desplegado, incluyendo cache de una hora, cache read y reasoning. Los importes equivalentes fueron USD 0.018318, 0.0015432 y 0.0022766. No se encontraron credenciales raw en los logs del contenedor ni las filas de consumo inspeccionadas

### Promocion al NAS compartido

Los aliases `claude-sonnet-5-5`, `claude-opus-5-5` y `claude-haiku-4-5` estan publicados en `https://litellm.staticduo.com`. El catalogo autenticado de la virtual key contiene los tres aliases y `/model/info` contiene los tres deployments para el equipo `49cfd117-ef74-4eec-b26e-2d2ff083f5be`, con acceso `all-proxy-models`

El template `docker/anthropic-subscription/shared-models.json` usa el sentinel invalido `sk-ant-oat01-client-oauth-required` y metadatos descriptivos. Esas flags no son una politica servidor inmutable. La configuracion efectiva inspeccionada carece de credenciales Anthropic API globales y de fallbacks para los aliases actuales, con forwarding de headers limitado a los grupos correspondientes. El rechazo sin OAuth se ha probado en esta configuracion, sin atribuir a los metadatos una garantia que no implementan

La imagen desplegada es `sha256:e941ad3d6c58aa1f7a136a0a21e542eef3a96bc911ab5e672efdf40ad2cf6316`, overlay del contador `d17375a5a9` y Responses `cb61cd4156` sobre la base `sha256:7263f32613a930e539792b7a1613a02eef617846d8e8ae493ab779a475af9fba`. El contexto de build incluye tambien `streaming_iterator.py`. Se activo mediante `LITELLM_IMAGE` en `/volume2/docker/litellm/.env`, con backup privado en `/volume2/docker/litellm/anthropic-subscription/environment.before-overlay`. Compose recreo solo `litellm` con `up -d --no-deps --pull never`. El contenedor compartido permanece healthy y readiness devolvio HTTP 200

El launcher fuente y `~/.local/bin/claude-litellm` del NAS apuntan a la URL HTTPS compartida y leen por defecto `/volume2/docker/litellm/anthropic-subscription/claude-code-key`. Claude Code conserva login y refresh propios. El comando ordinario `claude` conserva la ruta directa para rollback del cliente

La prueba final desde el launcher uso Read y devolvio `SUBSCRIPTION_TOOL_OK`. La continuacion mediante `--resume` devolvio `FINAL_ROUTE_817`, exit code 0 e `is_error=false`. El contador compartido devolvio HTTP 200 con `input_tokens=11`, OAuth invalido devolvio HTTP 401 y sin OAuth devolvio HTTP 401. La QA previa del candidato tambien completo Read y continuacion, con contador HTTP 200 e invalid/sin OAuth HTTP 401

La API compartida `/spend/logs/ui` devolvio HTTP 200 al filtrar `key_alias=claude-subscription`, `model_group=claude-sonnet-5-5` e intervalo UTC `2026-10-01 17:27:36` a `2026-10-02 00:00:00`. Los ultimos cuatro registros nativos exitosos tienen `used_client_oauth_token=true` e importes equivalentes USD 0.0080198, 0.0103398, 0.0112836 y 0.0779932. La solicitud sin OAuth registra spend 0. La comparacion con el calculador se verifico en el piloto y no se repitio para estos registros compartidos

El parche Responses pasa 112 tests focalizados, el contador pasa 48 y `make check` pasa sobre el parche Responses. Los hallazgos de review independiente se corrigieron. Estas comprobaciones corresponden al parche previo de fase 1 y no sustituyen el gate final del candidato gestionado

### Retirada de temporales y limites pendientes

Se pararon y eliminaron `litellm-anthropic-qa`, `litellm-anthropic-subscription-proxy-1` y `litellm-anthropic-subscription-postgres-1`, sin `-v`. Su ausencia se verifico con `docker ps -a`. Se conservaron `postgresql-data` y los archivos privados. El directorio privado del piloto tiene permisos 700 y sus archivos de key, config, credentials e image tienen permisos 600 tras corregir permisos heredados por ACL. El `litellm` compartido nativo sigue healthy con la imagen verificada de fase 1. Esta retirada corresponde a los temporales anteriores, no al piloto gestionado actual

No se ha forzado agotamiento real de cuota ni interrupcion durante generacion. El consumo del piloto inicial se comprobo en la base de datos y en `/spend/logs/ui` con HTTP 200, sin captura visual del dashboard. Esa evidencia usa OAuth del cliente y no demuestra la atribucion server/profile del candidato gestionado

### Candidato gestionado aislado

El candidato 04 paso Messages para los tres modelos, Chat Completions, Responses, ambas rutas probadas de count_tokens y continuacion de herramienta con thinking firmado. La autorizacion dedicada NAS conserva directorio 0700 y credenciales 0600. El refresh real roto la credencial correctamente. Fedora tiene otra autorizacion importada y no se ha desplegado el candidato alli

Codex 0.159.2 completo herramientas, archivo y resume con 207 reasoning tokens. OpenCode 2.0.20 fallo por extra usage en Messages y Responses. Los indicadores de usage confirman extra usage desactivado y creditos nunca habilitados. La fase 1 nativa NAS permanece saludable y los aliases anteriores siguen publicados

El candidato final 05, `sha256:875fba7af1d4cdec0f0967e73f9016688f2b1fd563a81ffc597603f711e114fa`, repite las pruebas API y replay tras corregir la atribucion contable. Sus 21 archivos fuente overlay coinciden byte a byte con el checkout. Cinco registros exitosos conservan OAuth de servidor, perfil default, OAuth de cliente false y la virtual key esperada. Los cinco importes coinciden con el calculador desplegado

La regresion contable pasa 47 tests focalizados de logging y 27 de spend. La review independiente no encontro defectos bloqueantes y otros 13 tests focalizados de propagacion pasan. El gate final `make check` pasa, incluyendo lint, presupuestos y sincronizacion del schema del dashboard. Se pararon y eliminaron los dos contenedores del piloto gestionado y su red con Compose down sin `-v`. `docker ps -a` no devuelve esos contenedores en NAS ni otros temporales Anthropic en Fedora, `postgresql-data` sigue presente y ambos proxies compartidos permanecen healthy. La fase 2 sigue bloqueada por OpenCode subscription-only y no se ha promovido a Fedora ni NAS
