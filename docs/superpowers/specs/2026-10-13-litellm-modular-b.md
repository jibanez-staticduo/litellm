# Propuesta para modularizar el fork LiteLLM

Fecha: 2026-10-13. Estado: analisis y opciones, pendiente de elegir alcance. No se ha implementado ni desplegado el refactor

## Objetivo y limites

Reducir el trabajo y el riesgo de integrar BerriAI upstream, manteniendo las funciones propias y las interfaces que usan Codex, OpenCode, Claude y los MCP actuales

La unidad de exito es una actualizacion de upstream con menos modificaciones en archivos compartidos, menos conflictos funcionales y los mismos contratos de autenticacion, Responses/SSE, herramientas, routing y gasto. Mover archivos sin reducir esos puntos de contacto no satisface el objetivo

Se conserva main como fuente de las releases, publicacion previa en docker.staticduo.com, validacion en Fedora antes de NAS y configuracion especifica de cada host. No se cambia el cliente Codex ni se exige un servicio externo nuevo para la primera etapa

## Base comprobada

- Main publicado y confirmado en remoto: f5eaab5396f957c5529456bbb545e52ce0b48c46
- Upstream incorporado en ese main: 541e3ed5305a530ebef74d5684d3aca2632c1009
- Fuente de lectura: /home/staticduo/.codex/worktrees/litellm-nightly-20261011, limpio al inspeccionarlo
- El checkout original conserva sus modificaciones locales y su referencia antigua; no se ha usado como candidato de refactor
- Delta bajo litellm/, excluidos codemap.yml y el snapshot OpenAPI generado: 196 archivos modificados y 25 nuevos. Incluye diferencias de estilo/tipos y documentos; no equivale a 221 funciones privadas
- merge.log de las noches 9, 10 y 11 de octubre registra 21, 35 y 14 conflictos. Son 70 entradas de conflicto, no 70 funcionalidades distintas
- Los dos JSON de precios aparecen en los tres merges. server.py y operations.py de MCP aparecen en los dos ultimos. Schema UI generado tambien produjo conflictos

No se compara main con un upstream posterior aun no incorporado. Un diff contra ese tip mezclaria novedades pendientes con personalizaciones del fork

## Hallazgos

LazyMCP es la extraccion con mayor concentracion de logica propia: server.py pasa de 3015 a 4245 lineas, con +1253/-23. Se mezclan fachada describe/call/status, discovery, cache, schemas, transporte y registro con infraestructura upstream

El upstream ya ofrece admision, autoridad, permisos, rate limits, preparacion de credenciales, snapshots de catalogo y sesiones. Esas funciones no deben copiarse a un motor de autorizacion privado. El manager apenas cambia de tamano; entre los puntos propios esta la invalidacion de cache Lazy importada desde server.py

Portable Codex tiene 421 lineas propias y ya implementa CustomLogger con hooks de request, respuesta y streaming. Es el mejor primer piloto de extraccion a un paquete cargable

Headroom ya tiene una frontera de guardrail y cliente de compresion, pero la manipulacion de bloques nativos y retrieval necesita adaptadores especificos. Un pre-hook generico no reproduce todo el flujo

ChatGPT/Anthropic tienen modulos propios de perfiles, OAuth, politica y transporte. Parte de su identidad tambien aparece en seleccion de deployment, retries, fallbacks y cache. Sacar el storage de credenciales es mas sencillo que sacar toda la politica de cuentas

El bridge Responses contiene cambios de razonamiento, herramientas y eventos SSE en transformation.py y streaming_iterator.py. Un hook posterior no recupera datos descartados por la transformacion ni puede corregir cualquier orden de eventos

CustomLLM, en el snapshot analizado, no ofrece metodos Responses ni un registro que cubra su ruta nativa. No permite convertir todas estas personalizaciones en proveedores externos sin ampliar una interfaz

context_compaction.py y reasoning_items.py ya existen en la base upstream sin delta funcional relevante. native_compaction.py solo presenta un cambio de estilo 21/21. No se extraen como si toda esa funcionalidad fuera privada

La politica memory_luna_pricing tiene 97 lineas propias y usa precios canonicos de GPT-6 Luna para el alias de memoria. Es una politica distinta de cobrar siempre el backend efectivo. Debe conservarse explicitamente; no se cambia aprovechando el refactor

Docker, brokers/clientes nativos y el controlador de cuotas tienen otro ciclo de release. deploy/quota-sidecar contiene patches sobre fuentes instaladas del controlador, no necesariamente sobre el core LiteLLM. Conviene convertirlos en releases mantenidas, con fuente y manifest propios, sin reaplicar parches historicos indefinidamente

## Opciones

| Opcion | Forma | Beneficio | Coste y riesgo |
| --- | --- | --- | --- |
| A. Modularizar dentro del fork | Modulos propios y adaptadores pequenos en el mismo repositorio | Mejora temprana, menos bloques en archivos calientes, misma imagen y frontera de seguridad | Esfuerzo menor; sigue existiendo dependencia del fork y de sus puntos de conexion |
| B. Extension versionada en el mismo proceso | Primero A, luego paquete staticduo_litellm separado del namespace litellm, con adaptadores compatibles | Separa releases y tests propios, facilita actualizar core sin resolver conflictos dentro de cada feature | Esfuerzo medio/alto; necesita versionar contratos y comprobar compatibilidad con cada actualizacion |
| C. Gateway o fachada externa | Servicio separado delante o detras de LiteLLM upstream | Puede reducir mucho el fork si las interfaces externas cubren todas las funciones | Esfuerzo y riesgo mayores: identidades delegadas, revocacion, streaming, WebSocket, errores y accounting distribuidos |

Recomendacion: B de forma gradual, empezando por A. No crear todos los servicios externos ni prometer upstream puro de inmediato

El paquete puede comenzar en el mismo repositorio para evitar coordinar dos publicaciones en el primer piloto. Una vez estabilizado, se puede separar. Aislar imports y contratos importa mas que el numero de repositorios

## Arquitectura propuesta

LiteLLM conserva routing, autenticacion y permisos upstream, presupuestos, cache general, gestion de modelos y persistencia principal

La extension concentra politica propia. Una distribucion posible, ajustable segun el inventario final:

```text
staticduo_litellm/
  codex/          portable agents y politicas/codec propios
  providers/      perfiles OAuth, transporte y summary auxiliar
  lazy/           schema, resolver, catalogo/cache, servicio y transporte
  compression/    cliente Headroom y transformaciones nativas
  pricing/        overrides y politica memory-model
  compatibility/ adaptadores al snapshot/API de LiteLLM
```

No es un framework generico de plugins. Se definen interfaces solo para las dependencias existentes que hoy obligan a modificar upstream

Los adaptadores de compatibilidad contienen los imports privados inevitables. El motor propio no importa proxy_server, Prisma o managers privados directamente. Las rutas y hooks existentes delegan en servicios propios mediante dependencias explicitas

Para MCP, el adaptador entrega un contexto autenticado vigente, seleccion autorizada, snapshot, ejecucion upstream e invalidacion. La extension no decide permisos leyendo metadata suministrada por el cliente, ni ejecuta todos los MCP con una credencial administrativa compartida

Para proveedores, se separan CredentialStore, selector de perfil y transporte, conservando la admision y binding de identidad. Los hooks posteriores a seleccion existen, pero hay que verificar que cubran cache, retries y fallbacks antes de retirar un punto de enforcement

Para Responses, se separan politicas/codec mientras el automata SSE permanece inicialmente en LiteLLM. La interfaz debe cubrir indices y orden de items, deltas, finalizacion, uso, errores y cancelacion. Realtime/Live queda en una entrega posterior

No se usa monkeypatching global ni sustitucion textual de funciones como mecanismo normal de extension. Donde no existe un hook suficiente, queda un patch pequeno, identificado y probado, hasta poder incorporarlo a upstream o mejorar la interfaz

## Plan gradual

### 0. Inventario y contratos

Crear un manifest de personalizaciones: feature, proposito, modulos, inserciones core, responsable, pruebas, dependencia de version y posible equivalente upstream. Separar logica, correcciones publicables, configuracion, artefactos generados y diferencias mecanicas de tipos/estilo

Registrar el baseline de conflictos y archivos compartidos. Identificar lo ya resuelto por upstream mediante pruebas de comportamiento. No borrar diferencias porque se parezcan ni mantener una copia de una funcion equivalente sin motivo

Salida: inventario revisable y matriz de contratos. No hay despliegue

### 1. Primera extraccion: Portable Codex

Mover callback y politicas puras a un modulo con dependencias explicitas; mantener temporalmente el import anterior como adaptador compatible. Conservar configuracion publica, replay por propietario, Redis, seleccion portable/legacy y metadata autenticada

El piloto debe demostrar que la logica propia deja de vivir en archivos upstream y que el callback se carga de forma declarativa. Si depende de imports privados, quedan concentrados en compatibility, no repartidos por el paquete

Riesgo comprobado por review: proxy/utils.py:2929 detecta algunos hooks mediante type(callback).__dict__, sin recorrer toda la herencia. Una subclase vacia de compatibilidad puede desactivar pre-call o transformacion streaming silenciosamente. El import antiguo debe reexportar la clase/instancia concreta o declarar wrappers explicitos; la prueba debe cubrir carga por config, deteccion y ejecucion real hasta response.completed

Salida: candidato con paridad de contratos, validado de manera aislada y posteriormente en Fedora

### 2. Catalogo, generados y release operacional

Mover overrides realmente propios a un overlay versionado de datos y generar el catalogo derivado en build. El overlay debe expresar altas, cambios y eliminaciones de campos; register_model no se da por equivalente a eliminar un campo del catalogo

Probar recarga de precios, retirada/cambio de deployments y ausencia de registros obsoletos. Mantener la politica canonica de memory-model y contabilizacion anterior

Riesgo comprobado por review: litellm_logging.py:1980 aplica memory_luna durante el calculo de coste y sustituye hints monetarios del proveedor. No mover esa politica a un callback posterior al logging. Conservar un punto anterior al registro de gasto y presupuestos, manteniendo separadas la identidad real del backend y la referencia monetaria canonica GPT-6 Luna

El generador debe reconstruir desde una base upstream fresca y expresar eliminaciones, con resultado idempotente. Para el delta actual de solo +14/-8 en cada JSON no hace falta un framework general de catalogos

Regenerar snapshot OpenAPI y tipos UI desde la fuente final validada, sin resolver sus conflictos a mano. Conservar las pruebas del esquema generado y los gates existentes

Separar los scripts/controladores/brokers de su instalacion concreta: fuente mantenida, release versionada y manifest de core, extension, dependencias y artefactos nativos. Mantener publicacion en docker.staticduo.com antes de cada despliegue

Salida: retirar ediciones privadas directas de los JSON de catalogo cuando el overlay demuestre equivalencia, y dejar generados reproducibles

### 3. LazyMCP

Separar schema/resolver, cache/catalogo, servicio describe/call/status y transporte. Extraer tambien el componente UI LazyMCP Connect y el hook loopback, conservando las pequenas inserciones en pantallas y rutas upstream

Reutilizar OperationContext/catalog_operation, autoridad actual y operaciones upstream. Mantener challenges/resource/audience, credenciales por usuario, filtros de toolset, rate admission, revocacion en siguiente operacion y lifespan

Salida: server.py conserva registro y lifecycle mas delegacion, sin el bloque principal de logica Lazy. Esto no promete eliminar todos los cambios de auth/manager/UI

### 4. Headroom y politicas OAuth

Extraer cliente de compresion, manipulado/restauracion de contenido nativo y store de perfiles. Mantener adaptadores de guardrail/provider donde se validan identidad, cache, deployment y fallback

LiteLLM sigue siendo responsable del coste y no se introduce pricing/OAuth monetario dentro de Headroom. Conservar timeouts, fail-open y roundtrip multimodal/herramientas

Salida: politicas y storage privados encapsulados, con lista explicita de puntos core que siguen siendo necesarios

### 5. Responses, summary y rutas auxiliares

Extraer el summary auxiliar hosted_vllm_codex y codecs de reasoning/tool-search. No sustituir Responses por CustomLLM mientras el registro no soporte la superficie requerida

Tratar sync/async, streaming/nonstream, replay, ids, razonamiento cifrado, usage de llamadas auxiliares y cancelacion como contratos. Realtime/Live se extrae despues del bridge HTTP; no se mezcla con el primer piloto

Salida: menos branches propios en transformation/main/router, preservando las interfaces que no tienen alternativa suficiente

### 6. Extension versionada y mantenimiento nocturno

Una vez estabilizados los limites, publicar el paquete con version y compatibilidad declarada. La imagen fija core, extension y dependencias nativas; la prueba de compatibilidad forma parte del candidato nocturno

La tarea nocturna registra cuantos archivos upstream y adaptadores siguen modificados, conflictos por feature y resultados de contratos. Integra solo los cambios nuevos del core; no reaplica fuentes privadas mediante parches textuales opacos

Si una interfaz rompe, el candidato se bloquea antes de promocion. No se hace downgrade silencioso de una feature ni se elimina una comprobacion para aprobar el merge

## Validacion y salida de cada entrega

Las pruebas verifican comportamiento, no solo estructura de directorios:

- Misma respuesta normal, secuencia SSE y manejo de errores/cancelacion, sin perder razonamiento ni herramientas
- Mismo propietario, cuenta seleccionada y rechazo de cambio de perfil no autorizado, incluyendo retries/cache/fallbacks
- Misma visibilidad MCP; scope vacio no amplia permisos; revocacion y cambios de catalogo se reflejan; credenciales de gateway y upstream no se mezclan
- Mismo call-id y criterio de coste, sin dobles filas, cambios de grupo ni gasto auxiliar oculto
- Cambios de pricing y cache reload no recuperan deployments eliminados ni metadatos retirados
- Import/config de extension probado con la version real Python, SDK y puente nativo del candidato
- Gates de lint/tipos/coverage sin rebajar umbrales. Review proporcional al modulo cambiado
- QA real Qwen, ChatGPT Responses/SSE y LazyMCP, preservacion de inventario/montajes/migraciones y estabilidad. Claude sigue siendo diagnostico informativo para promocion; sus contratos afectados si se refactoriza se prueban sin exigir un proveedor disponible

Cada entrega usa un candidato completo publicado y validado en Fedora. Solo despues se promueve el mismo digest al NAS. El rollback consiste inicialmente en volver a la imagen previa compatible; no se introducen migraciones de datos en este refactor ni se considera que una imagen revierte automaticamente un esquema

## Como medir si mejora

Medir numero de archivos upstream modificados y puntos de conexion necesarios, conflictos funcionales por merge, tiempo activo de resolucion, duracion de validacion y resultados de paridad

Comparar varios merges reales posteriores con el baseline; los recuentos dependen del contenido de upstream. No prometer un porcentaje de reduccion ni cero conflictos a partir de mover modulos

No comparar el tiempo total de build con solo el tiempo del merge: compilar Rust/UI y copiar bases de datos puede seguir dominando la ejecucion aunque disminuyan los conflictos

## Recomendacion para decidir

Elegir B como objetivo y autorizar primero una entrega concreta: inventario final mas piloto Portable Codex. Revisar su resultado antes de extraer MCP/auth/Responses. Si el piloto no elimina puntos de acoplamiento reales o exige mas parche que el actual, corregir el limite antes de continuar

Elegir A si se busca un cambio menor sin gestionar todavia otra distribucion. Elegir C solo si se acepta un nuevo componente operacional y un proyecto especifico de autenticacion delegada y streaming

## Evidencia consultada

- Comparacion git del upstream integrado y main publicado; remoto main verificado con git ls-remote
- /home/staticduo/.local/state/litellm-nightly/20261009T020000Z-iDyQLw/merge.log
- /home/staticduo/.local/state/litellm-nightly/20261010T020000Z-gUkfeS/merge.log
- /home/staticduo/.local/state/litellm-nightly/20261011T020000Z-ahLqCH/merge.log
- server.py, operations.py, catalog.py y auth/user_api_key_auth_mcp.py del snapshot
- integrations/custom_logger.py, llms/custom_llm.py y hooks/portable_codex_agents.py del snapshot
- Proveedores ChatGPT/Anthropic, bridge Responses, native compaction y Headroom del snapshot
- Dockerfile, pyproject.toml, deploy/quota-sidecar y fuentes de brokers nativos
- Documentacion de hooks: https://docs.litellm.ai/docs/proxy/call_hooks
- Context7 de LiteLLM consultado; validacion de contratos concretos contra el snapshot local

Review arquitectonica independiente: la opcion B como evolucion de A es viable, con correcciones sobre deteccion de hooks, fase de pricing, contratos y ABI de extension, autoridad MCP por operacion y overlays con eliminaciones. Esas correcciones estan incorporadas en esta propuesta

No se han ejecutado tests ni benchmarks para este plan. La evidencia de paridad y de reduccion de conflictos se obtendra con cada candidato de implementacion
