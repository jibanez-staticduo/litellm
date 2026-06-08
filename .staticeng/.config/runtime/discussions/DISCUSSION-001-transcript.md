---
id: DISCUSSION-001
title: Fix LiteLLM MCP edit and spend logs timeout
status: active
agent: product_manager
session_id: ses_16b5c8a69ffeUKSyBcP79vCvvl
appended_message_ids:
  - msg_e964857520011q90v8zYtD56zd
  - msg_ea7a19472001bFLc7aW3LDcyOy
  - msg_ea7a37a2e001ixUeTxCbBihHMO
  - msg_ea7a6782c001XYfJTahcmuSF4l
  - msg_ea7ab5d080015p5aeL0Bf4zl4M
  - msg_ea7ad1115001mE4Sclh1przF0S
---

# Discussion: Fix LiteLLM MCP edit and spend logs timeout

## Messages

**product_manager**
Paro aquí: el git no está limpio como esperaba.

Después del switch, `git status` en `/home/staticduo/git/litellm` muestra:

- rama: `staticduo-production-main`
- pero hay deletes en `evidences/...` y `tasks/todo/...`
- `.staticeng/` aparece untracked

Esto contradice el handoff anterior que decía “limpio”. No voy a seguir tocando repo ni mezclar estados hasta que me digas qué prefieres.

Lo que sí vi en read-only antes de parar:

- LiteLLM desplegado: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260601`
- container `litellm`: `Up 2 days (healthy)`
- admin health: `healthy`, DB `connected`
- recursos ahora: LiteLLM bajo CPU (~0.2%) pero alto RAM (~4.66 GiB); PostgreSQL ~5.6% CPU, ~986 MiB

Dime cómo procedo con el estado git:

1. restaurar el stash anterior para recuperar los deletes/untracked y revisar
2. dejar el repo como está y seguir solo con diagnóstico Docker/logs read-only
3. limpiar/normalizar el workspace principal en `staticduo-production-main` sin perder nada, revisando primero qué hay en stash y en `.staticeng/`

**User**
esto es el nuevo procedimiento de staticeng que ha evolucionado de nomadworks commitea y pushea los cambios

**product_manager**
Hecho: commiteado y pusheado a `fork/main`.

- Rama local: `staticduo-production-main`
- Commit: `ad926e49c9 chore: migrate NomadWorks artifacts to StaticEng`
- Push: `staticduo-production-main -> fork/main`
- Verificado: `HEAD` y `fork/main` apuntan ambos a `ad926e49c9`
- Estado final: limpio

El commit mueve artifacts de `tasks/` y `evidences/` a `.staticeng/` y añade scaffolding/config de StaticEng.

**User**
perfecto, ahora quiero que investiges un problema que tengo en producción con litellm. Esta desplegado ya sabes lo que despliega el script de deploy de litellm que obtiene el último litellm, mergea la rama de litellm-production-main y lo pone en producción. Pues cuando edito un mcp en producción peta y cuando los cargos creo que da timeout. Porque pasa?

**product_manager**
Parece que son dos problemas separados.

El fallo al editar/listar MCPs está bastante claro: el backend revienta con objetos cacheados como `dict`.

Evidencia live últimos 2h:
- `AttributeError: 'dict' object has no attribute 'teams'`: 269 veces.
- HTTP 500:
  - `GET /v1/mcp/server/health`: 77
  - `GET /v1/mcp/server`: 10
  - `PUT /v1/mcp/server`: 2
- Stack apunta a:
  - `mcp_management_endpoints.py:1022`
  - `ui_session_utils.py:79`
  - `ui_session_utils.py:64`
- Línea problemática actual: `if user_obj is None or not user_obj.teams:` y luego `for team_id in user_obj.teams:`.

Causa: `get_user_object()` a veces devuelve un dict desde cache/DB serialization, pero el código MCP UI session asume objeto con atributo `.teams`. Es la misma familia que ya arreglamos para `user_role`, `tpm_limit`, `rpm_limit`, `spend`, etc., pero faltó este path nuevo de MCP UI session.

Por eso “editar un MCP” peta: aunque el `PUT /v1/mcp/server` actualiza DB, después llama a reload/health/listado, y esas rutas construyen contextos efectivos con equipos del usuario. Ahí cae con `.teams`.

El timeout de cargos/costes también está claro:
- `/global/spend` responde OK.
- `/spend/logs` sin filtros sigue dando timeout.
- DB: `LiteLLM_SpendLogs` pesa `56 GB`, ~724k filas.
- El endpoint legacy `/spend/logs` está marcado en código como deprecated/no paginado y si no hay filtro hace `get_data(table_name="spend", query_type="find_all")`, o sea intenta traer todo.
- Hay índices por `startTime`, `request_id`, `end_user`, `session_id`, pero eso no salva el caso sin filtros porque no pagina y además las filas tienen columnas pesadas (`messages`, `response`, `proxy_server_request`).

Conclusión:
- MCP edit/list/health falla por bug real de código: acceso `.teams` no dict-safe en `ui_session_utils.py`.
- Cargos timeout pasa porque la UI/admin/MCP probablemente está llamando al endpoint legacy `/spend/logs` sin rango/paginación. Con esa tabla de 56GB es esperable que timeoutee. Hay que usar `/spend/logs/v2` o `/spend/logs/ui` con `start_date`, `end_date`, `page`, `page_size`.

Seguro ahora:
- Evitar `/spend/logs` legacy sin filtros.
- Para consultar cargos, usar `/global/spend` o `/spend/logs/v2?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&page=1&page_size=50`.
- Evitar editar MCPs desde UI hasta parchear el `.teams`.

Requiere fix + deploy:
- Parchear `litellm/proxy/_experimental/mcp_server/ui_session_utils.py` para usar acceso dict/object seguro:
  - si `user_obj` es dict, leer `user_obj.get("teams")`
  - si es objeto, leer `getattr(user_obj, "teams", None)`
- Añadir test de regresión para UI session token con `user_obj` dict.
- Opcional: hacer que el admin MCP no use `/spend/logs` legacy; cambiarlo a `/spend/logs/v2` con rango obligatorio o exponer una herramienta paginada.

**User**
hay que arreglar ambos, el de costes puede ser porque guarda el "contenido" de cada llamada?
