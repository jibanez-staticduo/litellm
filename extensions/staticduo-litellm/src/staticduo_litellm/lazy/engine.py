from __future__ import annotations

from .cache import CacheService
from .catalog import CatalogService
from .ports import MCPPorts
from .resolver import ResolverService
from .service import ServiceService


class LazyMCPService(CacheService, CatalogService, ResolverService, ServiceService):
    def __init__(self, ports: MCPPorts) -> None:
        self.ports = ports
