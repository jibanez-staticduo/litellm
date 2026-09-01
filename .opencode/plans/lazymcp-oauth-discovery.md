# Corregir el discovery OAuth de LazyMCP

## Objetivo

Eliminar los `404` de discovery OAuth generados al conectar clientes MCP a LazyMCP y hacer que toda respuesta `WWW-Authenticate` apunte a metadata RFC 9728 cuyo campo `resource` coincida exactamente con el endpoint publico solicitado.

El cambio debe cubrir el gateway raiz, los endpoints LazyMCP con scope y los toolsets, sin cambiar permisos, seleccion de servidores, credenciales upstream ni el comportamiento del endpoint MCP existente.

## Problema verificado

- El cliente conecta a `/lazymcp` y prueba `/.well-known/oauth-protected-resource/lazymcp` y `/lazymcp/.well-known/oauth-protected-resource`; ambas rutas devuelven `404`
- El cliente termina usando `/.well-known/oauth-protected-resource`, que devuelve `200`, por lo que la conexion suele continuar
- LazyMCP reescribe internamente `/lazymcp...` a `/mcp...` antes de ejecutar la autenticacion en `litellm/proxy/_experimental/mcp_server/server.py`
- La autenticacion construye desafios para recursos `/mcp...` en `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py`, aunque el recurso publico solicitado sea `/lazymcp...`
- La metadata encontrada puede declarar `resource: .../mcp` o el origen, en vez del recurso real `.../lazymcp`; un cliente estricto puede rechazarla aunque los clientes actuales hagan fallback
- El problema pertenece a la superficie del gateway LazyMCP. No se genera una vez por cada MCP interno, sino en cada conexion o reconexion del cliente al endpoint LazyMCP

## Decisiones de diseno

- Tratar la URL publica de transporte como identidad RFC 9728. Nunca construir metadata desde la ruta interna reescrita
- Canonicalizar los aliases con barra final al recurso sin barra final
- Publicar como ruta principal la forma path-inserted de RFC 9728 y mantener la forma path-appended porque clientes MCP reales la prueban
- Reutilizar el authorization server gateway existente en `{base}/mcp`; no crear otro flujo OAuth, emisor, token endpoint ni registro dinamico para LazyMCP
- Servir metadata scoped generica sin revelar si el nombre corresponde a servidor, grupo, toolset oculto o nombre inexistente. La autorizacion real seguira ocurriendo despues de autenticar
- Mantener intacta la separacion entre autenticacion de entrada de LiteLLM y autenticacion upstream de cada MCP
- No limitar el arreglo a silenciar access logs. Las rutas deben existir y devolver documentos validos

## Matriz de recursos y discovery

`{base}` representa la URL externa calculada por `get_request_base_url()`. `{root}` representa `SERVER_ROOT_PATH` en las rutas well-known, siguiendo la convencion ya usada por LiteLLM.

| Recurso publico canonico | Discovery principal | Discovery compatible | `resource` |
|---|---|---|---|
| `/lazymcp` | `/.well-known/oauth-protected-resource{root}/lazymcp` | `{root}/lazymcp/.well-known/oauth-protected-resource` | `{base}/lazymcp` |
| `/lazymcp/{scope}` | `/.well-known/oauth-protected-resource{root}/lazymcp/{scope}` | `{root}/lazymcp/{scope}/.well-known/oauth-protected-resource` | `{base}/lazymcp/{scope}` |
| `/toolset/{name}/lazymcp` | `/.well-known/oauth-protected-resource{root}/toolset/{name}/lazymcp` | `{root}/toolset/{name}/lazymcp/.well-known/oauth-protected-resource` | `{base}/toolset/{name}/lazymcp` |

Cada documento devolvera como minimo:

```json
{
  "authorization_servers": ["{base}/mcp"],
  "resource": "{recurso publico canonico}",
  "scopes_supported": []
}
```

## Implementacion

### 1. Modelar la identidad publica de LazyMCP

- Añadir helpers pequenos y tipados en `litellm/proxy/_experimental/mcp_server/oauth_utils.py` para:
  - extraer y normalizar el recurso LazyMCP publico desde `scope["_original_path"]` o `scope["path"]`
  - eliminar solo la barra final del alias conocido, sin normalizar segmentos arbitrarios
  - construir la URL principal de protected-resource metadata respetando `PROXY_BASE_URL`, proxies confiables y `SERVER_ROOT_PATH`
- Reutilizar `get_request_base_url()` y `well_known_root_suffix()`; no duplicar logica de forwarded headers
- Rechazar rutas que no pertenezcan a una de las tres formas soportadas en vez de fabricar una URL generica

### 2. Preservar la ruta original antes de reescribir

- En `litellm/proxy/proxy_server.py`, guardar `scope["_original_path"]` antes de cambiar `scope["path"]` en:
  - `root_lazymcp_route()`
  - `dynamic_lazymcp_route()`
  - `toolset_lazymcp_route()`
  - la rama de `dynamic_lazymcp_route()` que resuelve un nombre como toolset
- En `handle_streamable_http_lazymcp()` de `litellm/proxy/_experimental/mcp_server/server.py`, conservar `_original_path` si ya existe y establecerlo desde la ruta recibida solo cuando falte
- Mantener la reescritura a `/mcp` exclusivamente para reutilizar resolucion, permisos y ejecucion internos

### 3. Añadir metadata RFC 9728 para LazyMCP

- En `litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py`, añadir un builder dedicado que reciba el recurso publico ya validado y devuelva metadata del gateway
- Registrar primero las rutas exactas y mas especificas para evitar capturas de Starlette:
  1. aggregate `/lazymcp`
  2. `/toolset/{name}/lazymcp`
  3. `/lazymcp/{scope}`
  4. sus formas path-appended compatibles
  5. conservar despues las rutas existentes de `/mcp`
- No reutilizar directamente `_build_oauth_protected_resource_response()` para scopes LazyMCP: ese builder presupone un unico servidor MCP y puede filtrar existencia o devolver metadata upstream incompatible con un grupo/toolset
- No consultar PostgreSQL ni el registro MCP desde estas rutas publicas. El documento describe el gateway; no valida acceso ni existencia del scope
- Seguir usando `well_known_root_suffix()` en los decorators y probar el comportamiento con root path vacio y `/litellm`

### 4. Emitir desafios correctos desde LazyMCP

- En `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py`, hacer que `_gateway_dcr_challenge()` seleccione metadata a partir de la ruta publica preservada
- Para peticiones LazyMCP, emitir una URL absoluta a la ruta path-inserted correspondiente, por ejemplo:

```http
WWW-Authenticate: Bearer resource_metadata="https://host/.well-known/oauth-protected-resource/lazymcp"
```

- Conservar `error="invalid_token"` cuando el cliente presento un bearer invalido o expirado
- Mantener los desafios actuales de `/mcp`, OAuth pass-through y servidores upstream sin cambios
- Asegurar que una cabecera `x-mcp-servers` no sustituya la identidad del recurso publico `/lazymcp`; limita el contenido de la peticion, no cambia su audience

### 5. Alinear el flujo DCR con los recursos LazyMCP

- Extender `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py` para reconocer:
  - `/lazymcp` como recurso aggregate
  - `/lazymcp/{scope}` como recurso scoped
  - `/toolset/{name}/lazymcp` como recurso scoped de toolset
- Preservar la identidad completa del recurso en autorizacion, codigo y token para que el token emitido no cambie silenciosamente de `/lazymcp` a `/mcp`
- Definir y comprobar la politica de audience:
  - el token debe ser valido para el recurso LazyMCP que inicio el flujo
  - un token scoped no debe ampliar acceso al aggregate ni a otro scope
  - el mismo usuario puede autorizar recursos distintos mediante sesiones distintas
- No interpretar un access group como un servidor individual durante DCR. El scope se resolvera mediante el mismo pipeline de permisos usado en la peticion autenticada

### 6. Mantener ownership y despliegues divididos

- Revisar `gateway/routes/allowlist.py`, `backend/routes/allowlist.py` y `tests/test_litellm/proxy/test_component_allowlists.py`
- Garantizar que el componente que atiende `/lazymcp` pueda servir o enrutar todas sus rutas well-known
- Evitar prefijos excesivamente amplios si basta con rutas explicitas para `/.well-known/oauth-protected-resource...`
- Confirmar que reverse proxies publican transport y metadata bajo el mismo host externo

## Pruebas de regresion

### Metadata y orden de rutas

Extender `tests/test_litellm/proxy/_experimental/mcp_server/test_discoverable_endpoints.py` para comprobar:

- `200` en las seis formas de discovery de la matriz
- igualdad de cuerpo entre la forma principal y compatible
- `resource` exacto para raiz, scope y toolset
- canonicalizacion consistente de endpoints de transporte con `/` final
- `authorization_servers == ["{base}/mcp"]`
- funcionamiento con `SERVER_ROOT_PATH` vacio y `/litellm`
- ausencia de colisiones con nombres `mcp`, `lazymcp`, `toolset` y `.well-known`
- metadata generica e indistinguible para scope existente, oculto y desconocido
- conservacion de las rutas `/mcp` existentes

### Ruta publica y reescritura

Extender `tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py` para comprobar:

- `_original_path` se conserva para raiz, scope y toolset
- la ruta interna sigue llegando como `/mcp` o `/mcp/{scope}`
- las variantes con barra final producen la misma identidad canonica
- la resolucion y permisos LazyMCP actuales no cambian

### Desafios de autenticacion

Extender `tests/test_litellm/proxy/_experimental/mcp_server/auth/test_user_api_key_auth_mcp.py` para comprobar:

- una peticion sin credenciales recibe `401` con el `resource_metadata` LazyMCP exacto
- bearer invalido conserva `error="invalid_token"`
- raiz, scope y toolset reciben desafios distintos
- `/mcp` sigue anunciando metadata `/mcp`
- OAuth pass-through, delegated OAuth, OBO y cabeceras upstream mantienen su comportamiento
- `PROXY_BASE_URL`, forwarded headers confiables y root path no generan rutas duplicadas ni URLs controlables por Host no confiable

### DCR y aislamiento de recursos

Extender `tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py` para comprobar:

- autorizacion completa para los tres tipos de recurso LazyMCP
- audience/resource exacto dentro del codigo y token
- rechazo de replay entre `/lazymcp/{scope-a}`, `/lazymcp/{scope-b}`, aggregate y toolsets
- access groups y toolsets no se convierten por error en servidores individuales

### Componentes y seguridad

Extender `tests/test_litellm/proxy/test_component_allowlists.py` y, si aplica, `test_mcp_toolset_scope.py` para comprobar:

- ownership correcto de todas las rutas nuevas
- ninguna ruta well-known requiere autenticacion previa
- las rutas de transporte siguen aplicando permisos de key, equipo, grupo y toolset
- un nombre desconocido nunca abre el catalogo completo como fallback

## Validacion

Ejecutar primero pruebas focalizadas:

```bash
uv run --no-sync pytest -q tests/test_litellm/proxy/_experimental/mcp_server/test_discoverable_endpoints.py -k 'lazymcp or protected_resource or root_suffix'
uv run --no-sync pytest -q tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py -k 'lazymcp and (route or probe or toolset or auth)'
uv run --no-sync pytest -q tests/test_litellm/proxy/_experimental/mcp_server/auth/test_user_api_key_auth_mcp.py -k 'challenge or resource_metadata or lazymcp'
uv run --no-sync pytest -q tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py -k 'resource or scoped or lazymcp'
uv run --no-sync pytest -q tests/test_litellm/proxy/test_component_allowlists.py -k 'lazymcp or well_known'
```

Despues ejecutar el conjunto mapeado completo:

```bash
uv run --no-sync pytest -q \
  tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py \
  tests/test_litellm/proxy/_experimental/mcp_server/test_discoverable_endpoints.py \
  tests/test_litellm/proxy/_experimental/mcp_server/auth/test_user_api_key_auth_mcp.py \
  tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py \
  tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_toolset_scope.py \
  tests/test_litellm/proxy/test_component_allowlists.py
```

Ejecutar lint y type checking solo sobre los archivos tocados segun los comandos disponibles del repositorio. Si se reducen presupuestos estrictos, ejecutar `make lint-budget-update` con un working tree que contenga exclusivamente este arreglo.

## Prueba en Docker

Construir una imagen candidata y desplegarla primero en el entorno de menor riesgo. No modificar directamente el contenedor actual.

Verificar con peticiones sin secretos visibles:

```bash
curl -i https://host/.well-known/oauth-protected-resource/lazymcp
curl -i https://host/lazymcp/.well-known/oauth-protected-resource
curl -i https://host/lazymcp
```

Comprobar:

- ambas rutas metadata devuelven `200`
- ambas declaran exactamente `resource: https://host/lazymcp`
- la peticion no autenticada a `/lazymcp` devuelve un desafio con la ruta principal
- un cliente MCP puede inicializar, listar `mcp_describe` e invocar una herramienta autorizada
- no aparecen nuevos `404` para las dos rutas de discovery durante varias reconexiones
- `/health/readiness`, `/mcp`, MCP REST y los MCP internos permanecen saludables

## Rollout y rollback

- Capturar antes del despliegue el digest actual, estado de salud y conteo de errores de discovery
- Desplegar una imagen inmutable con tag y digest nuevos sin cambiar la base de datos
- Validar primero metadata, despues autenticacion, despues una llamada LazyMCP real
- Observar logs durante reconexiones reales y comparar `401`, `404` y errores MCP con la linea base
- Promover al segundo entorno solo si todos los gates pasan
- Ante cualquier regresion de autenticacion, aislamiento de scopes, toolsets o MCP existente, restaurar el digest anterior; el cambio no requiere migraciones ni rollback de datos

## Criterios de aceptacion

- Cero `404` en las rutas de discovery OAuth que un cliente prueba al conectar a `/lazymcp`
- Toda metadata devuelve un `resource` exactamente igual al endpoint publico canonico
- Todo desafio LazyMCP anuncia la metadata correspondiente al recurso solicitado
- `/lazymcp`, `/lazymcp/{scope}` y `/toolset/{name}/lazymcp` funcionan con discovery y DCR
- Tokens y permisos no se amplian entre aggregate, scopes o toolsets
- No cambia el comportamiento observable de `/mcp`, MCP REST ni autenticacion upstream
- Las pruebas mapeadas, lint, type checking y smoke test Docker pasan

## Fuera de alcance

- Cambiar fallbacks de modelos LLM, incluidos DeepSeek o Qwen
- Renovar tokens de proveedores de modelos
- Rediseñar el catalogo o las tres herramientas compactas de LazyMCP
- Cambiar configuraciones o credenciales de los MCP internos
- Ocultar access logs sin corregir las rutas
