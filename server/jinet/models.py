"""Database tables."""
from typing import List, Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, LargeBinary


class UserBase(SQLModel):
    created: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )
    first_name: Optional[str]
    last_name: Optional[str]
    role: str = Field(nullable=False)
    picture: bytes = Field(sa_column=Column("picture", LargeBinary))


class User(UserBase, table=True):
    id: int = Field(nullable=False, primary_key=True)
    packages: List["Package"] = Relationship(back_populates="owner")


class PackageBase(SQLModel):
    name: str
    data: bytes = Field(sa_column=Column("data", LargeBinary))
    published: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )
    description: Optional[str]
    version: int
    runtime: str
    rating: float


class Package(PackageBase, table=True):
    id: int = Field(nullable=False, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="packages")
    tags: List["Tag"] = Relationship(back_populates="package")


class Tag(SQLModel, table=True):
    name: str = Field(nullable=False, primary_key=True)
    package_id: int = Field(foreign_key="package.id", primary_key=True)
    package: Package = Relationship(back_populates="tags")
