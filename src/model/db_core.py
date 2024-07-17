import datetime
from typing import Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class DBCore(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    parent_uuid: Union[UUID, None] = None

    created_at: Union[datetime.datetime, None] = Field(
        default_factory=datetime.datetime.now
    )
    updated_at: Union[datetime.datetime, None] = Field(
        default_factory=datetime.datetime.now
    )
    deleted_at: Union[datetime.datetime, None] = None
    is_deleted: Union[bool, None] = False

    def link_to_parent(self, parent: "DBCore"):
        self.parent_uuid = parent.uuid

    def unlink_from_parent(self):
        self.parent_uuid = None

    def create(self):
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

    def update(self):
        self.updated_at = datetime.datetime.now()

    def delete(self):
        self.deleted_at = datetime.datetime.now()
        self.is_deleted = True
