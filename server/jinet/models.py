"""Database tables."""

from typing import List, Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, LargeBinary, UniqueConstraint
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB


class UserBase(SQLModel):
    created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column("created", type_=TIMESTAMP(timezone=True), nullable=False),
    )
    username: Optional[str] = Field(nullable=True, default=None)
    role: str = Field(nullable=False)
    picture: str = Field(nullable=False)
    sub: str = Field(nullable=False, index=True)
    can_upload: bool = Field(default=False, nullable=False)


class User(UserBase, table=True):
    id: int = Field(nullable=False, primary_key=True)
    packages: List["Package"] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"lazy": "selectin"}
    )
    sample_data: List["SampleData"] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"lazy": "selectin"}
    )
    permission_requests: List["PermissionRequest"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )


class PackageBase(SQLModel):
    name: str
    data: bytes = Field(sa_column=Column("data", LargeBinary))
    published: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            "published",
            type_=TIMESTAMP(timezone=True),
            nullable=False,
        ),
    )
    description: Optional[str] = Field(default=None)
    version: int
    runtime: str
    interface: dict = Field(sa_column=Column("interface", JSONB, nullable=False))
    reviewed: bool = Field(default=False)


class Package(PackageBase, table=True):
    id: int = Field(nullable=False, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(
        back_populates="packages", sa_relationship_kwargs={"lazy": "selectin"}
    )
    tags: List["Tag"] = Relationship(
        back_populates="package", sa_relationship_kwargs={"lazy": "selectin"}
    )
    ratings: List["Rating"] = Relationship(
        back_populates="package", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Tag(SQLModel, table=True):
    name: str = Field(nullable=False, primary_key=True)
    package_id: int = Field(foreign_key="package.id", primary_key=True)
    package: Package = Relationship(
        back_populates="tags", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Rating(SQLModel, table=True):
    id: int = Field(nullable=False, primary_key=True)
    package_id: int = Field(foreign_key="package.id")
    package: Package = Relationship(
        back_populates="ratings", sa_relationship_kwargs={"lazy": "selectin"}
    )
    rating: int = Field(nullable=False)


class SampleData(SQLModel, table=True):
    id: int = Field(nullable=False, primary_key=True)
    data: bytes = Field(sa_column=Column("data", LargeBinary, nullable=False))
    name: str = Field(nullable=False)
    mime: str = Field(nullable=False)
    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(
        back_populates="sample_data", sa_relationship_kwargs={"lazy": "selectin"}
    )


class PermissionRequest(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("permission", "user_id"),)

    id: int = Field(nullable=False, primary_key=True)
    permission: str = Field(nullable=False)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(
        back_populates="permission_requests",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
