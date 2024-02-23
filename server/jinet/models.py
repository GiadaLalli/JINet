"""Database tables."""

from typing import List, Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, JSON, Relationship
from sqlalchemy import Column, LargeBinary
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


class User(UserBase, table=True):
    id: int = Field(nullable=False, primary_key=True)
    packages: List["Package"] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"lazy": "selectin"}
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
