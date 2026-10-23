"""
Dependency Injection container for RatTeil application.

This module provides a simple DI container for managing application dependencies.
"""

from typing import Dict, Type, Any, Callable, Optional, TypeVar, Generic
from functools import lru_cache
import asyncio

from ratteil.config.settings import Settings, get_settings
from ratteil.repositories.surah_repository import SurahRepository
from ratteil.repositories.reciter_repository import ReciterRepository


T = TypeVar('T')


class Container:
    """
    Simple dependency injection container.
    
    This container manages singleton instances of services and repositories,
    making it easy to share dependencies across the application.
    """
    
    def __init__(self):
        """Initialize the container."""
        self._instances: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, bool] = {}
    
    def register(self, interface: Type[T], implementation: Type[T], singleton: bool = True) -> None:
        """
        Register a dependency.
        
        Args:
            interface: The interface/type to register
            implementation: The concrete implementation
            singleton: Whether to treat as singleton
        """
        self._factories[interface] = implementation
        self._singletons[interface] = singleton
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register a pre-created instance.
        
        Args:
            interface: The interface/type to register
            instance: The instance to use
        """
        self._instances[interface] = instance
        self._singletons[interface] = True
    
    def resolve(self, interface: Type[T]) -> T:
        """
        Resolve a dependency.
        
        Args:
            interface: The interface/type to resolve
            
        Returns:
            The resolved instance
        """
        # Check if we have a cached instance
        if interface in self._instances:
            return self._instances[interface]
        
        # Check if we have a factory
        if interface in self._factories:
            implementation = self._factories[interface]
            instance = implementation()
            
            # Cache if singleton
            if self._singletons.get(interface, True):
                self._instances[interface] = instance
            
            return instance
        
        # Try to instantiate directly
        try:
            instance = interface()
            self._instances[interface] = instance
            return instance
        except Exception:
            raise ValueError(f"Cannot resolve dependency: {interface}")
    
    def reset(self, interface: Optional[Type[T]] = None) -> None:
        """
        Reset cached instances.
        
        Args:
            interface: Specific interface to reset, or None for all
        """
        if interface:
            self._instances.pop(interface, None)
        else:
            self._instances.clear()
    
    def clear(self) -> None:
        """Clear all registrations and instances."""
        self._instances.clear()
        self._factories.clear()
        self._singletons.clear()


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = Container()
        _initialize_container(_container)
    return _container


def reset_container() -> None:
    """Reset the global container."""
    global _container
    if _container is not None:
        _container.clear()
    _container = None


def _initialize_container(container: Container) -> None:
    """
    Initialize the container with default dependencies.
    
    Args:
        container: The container to initialize
    """
    # Register settings
    container.register_instance(Settings, get_settings())
    
    # Register repositories
    
    container.register(
        SurahRepository,
        lambda: SurahRepository(surahs_db)
    )
    container.register(
        ReciterRepository,
        lambda: ReciterRepository(reciters_db)
    )
    
    # Register services (will be added as they are created)
    


class AsyncContainer:
    """
    Async dependency injection container.
    
    This container supports async initialization of dependencies.
    """
    
    def __init__(self):
        """Initialize the async container."""
        self._instances: Dict[Type, Any] = {}
        self._async_factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, bool] = {}
    
    def register_async(self, interface: Type[T], factory: Callable[[], Any], singleton: bool = True) -> None:
        """
        Register an async dependency factory.
        
        Args:
            interface: The interface/type to register
            factory: Async factory function
            singleton: Whether to treat as singleton
        """
        self._async_factories[interface] = factory
        self._singletons[interface] = singleton
    
    async def resolve_async(self, interface: Type[T]) -> T:
        """
        Resolve an async dependency.
        
        Args:
            interface: The interface/type to resolve
            
        Returns:
            The resolved instance
        """
        # Check if we have a cached instance
        if interface in self._instances:
            return self._instances[interface]
        
        # Check if we have an async factory
        if interface in self._async_factories:
            factory = self._async_factories[interface]
            instance = await factory()
            
            # Cache if singleton
            if self._singletons.get(interface, True):
                self._instances[interface] = instance
            
            return instance
        
        # Try to instantiate directly
        try:
            instance = interface()
            self._instances[interface] = instance
            return instance
        except Exception:
            raise ValueError(f"Cannot resolve async dependency: {interface}")
    
    def reset(self, interface: Optional[Type[T]] = None) -> None:
        """Reset cached instances."""
        if interface:
            self._instances.pop(interface, None)
        else:
            self._instances.clear()
    
    def clear(self) -> None:
        """Clear all registrations and instances."""
        self._instances.clear()
        self._async_factories.clear()
        self._singletons.clear()


# Context manager for dependency injection
def dependency_scope():
    """
    Create a dependency scope context manager.
    
    This allows for scoped dependencies that are cleaned up after use.
    """
    class DependencyScope:
        def __init__(self):
            self.container = Container()
        
        def __enter__(self):
            return self.container
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.container.clear()
    
    return DependencyScope()


# Decorator for injectable classes
def injectable(cls: Type[T]) -> Type[T]:
    """
    Decorator to mark a class as injectable.
    
    This registers the class with the global container.
    """
    container = get_container()
    container.register(cls, cls)
    return cls


# Decorator for injectable functions
def inject(*dependencies: Type):
    """
    Decorator to inject dependencies into a function.
    
    Args:
        *dependencies: Dependency types to inject
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            container = get_container()
            injected_args = [container.resolve(dep) for dep in dependencies]
            return func(*injected_args, *args, **kwargs)
        return wrapper
    return decorator


# Async version of inject decorator
def async_inject(*dependencies: Type):
    """
    Decorator to inject dependencies into an async function.
    
    Args:
        *dependencies: Dependency types to inject
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            container = get_container()
            async_container = AsyncContainer()
            injected_args = [await async_container.resolve_async(dep) for dep in dependencies]
            return await func(*injected_args, *args, **kwargs)
        return wrapper
    return decorator
