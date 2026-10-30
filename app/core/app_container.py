"""Lightweight dependency injection container for SecureVault Pro.

Provides a simple service locator pattern for managing application-wide
dependencies and their lifecycle. Services are registered by type and
resolved lazily on first access.
"""

from typing import Any


class ServiceContainer:
    """Simple dependency injection container.

    Supports singleton registration (factory function or instance)
    and lazy resolution by type. Thread-safe for read access.
    """

    def __init__(self) -> None:
        self._factories: dict[type, Any] = {}
        self._instances: dict[type, Any] = {}
        self._singletons: dict[type, bool] = {}

    def register(
        self,
        service_type: type,
        factory: Any,
        *,
        singleton: bool = True,
    ) -> None:
        """Register a service type with a factory function or instance.

        Args:
            service_type: The type/interface to register against.
            factory: Either a callable factory or an instance.
            singleton: If True, the factory is called once and cached.
        """
        self._factories[service_type] = factory
        self._singletons[service_type] = singleton

    def register_instance(self, service_type: type, instance: Any) -> None:
        """Register an already-created instance as a singleton.

        Args:
            service_type: The type/interface to register against.
            instance: The instance to store.
        """
        self._factories[service_type] = lambda: instance
        self._singletons[service_type] = True
        self._instances[service_type] = instance

    def resolve(self, service_type: type) -> Any:
        """Resolve a service by type.

        Args:
            service_type: The type to resolve.

        Returns:
            An instance of the requested type.

        Raises:
            KeyError: If the service type is not registered.
        """
        if service_type in self._instances:
            return self._instances[service_type]

        factory = self._factories.get(service_type)
        if factory is None:
            raise KeyError(f"Service not registered: {service_type.__name__}")

        instance = factory() if callable(factory) else factory

        if self._singletons.get(service_type, False):
            self._instances[service_type] = instance

        return instance

    def has(self, service_type: type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._factories

    def clear(self) -> None:
        """Clear all registered services and cached instances."""
        self._instances.clear()
        self._factories.clear()
        self._singletons.clear()

    def __contains__(self, service_type: type) -> bool:
        return self.has(service_type)


_container: ServiceContainer | None = None


def get_container() -> ServiceContainer:
    """Get the global service container."""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def reset_container() -> None:
    """Reset the global container (primarily for testing)."""
    global _container
    if _container is not None:
        _container.clear()
    _container = None
