"""Base repository with generic CRUD operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.base import Base


class BaseRepository[T: Base]:
    """Generic CRUD repository for SQLAlchemy models.

    Provides standard create, read, update, delete operations.
    All repositories inherit from this base.
    """

    def __init__(self, model: type[T], session: Session) -> None:
        self.model = model
        self.session = session

    def get_by_id(self, entity_id: str) -> T | None:
        """Get an entity by its primary key.

        Args:
            entity_id: The entity's primary key value.

        Returns:
            The entity if found, None otherwise.
        """
        return self.session.get(self.model, entity_id)

    def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Get all entities with pagination.

        Args:
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            List of entities.
        """
        stmt = select(self.model).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def count(self) -> int:
        """Count total entities of this type.

        Returns:
            Total count.
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        return self.session.execute(stmt).scalar() or 0

    def create(self, entity: T) -> T:
        """Add a new entity to the session.

        Args:
            entity: The entity to create.

        Returns:
            The created entity.
        """
        self.session.add(entity)
        self.session.flush()
        return entity

    def update(self, entity: T) -> T:
        """Update an existing entity.

        Args:
            entity: The entity with updated fields.

        Returns:
            The updated entity.
        """
        self.session.merge(entity)
        self.session.flush()
        return entity

    def delete(self, entity: T) -> None:
        """Delete an entity.

        Args:
            entity: The entity to delete.
        """
        self.session.delete(entity)
        self.session.flush()

    def delete_by_id(self, entity_id: str) -> bool:
        """Delete an entity by its primary key.

        Args:
            entity_id: The entity's primary key value.

        Returns:
            True if the entity was found and deleted, False otherwise.
        """
        entity = self.get_by_id(entity_id)
        if entity is None:
            return False
        self.delete(entity)
        return True

    def exists(self, entity_id: str) -> bool:
        """Check if an entity exists by its primary key.

        Args:
            entity_id: The entity's primary key value.

        Returns:
            True if the entity exists.
        """
        return self.get_by_id(entity_id) is not None
