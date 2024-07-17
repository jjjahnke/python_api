import datetime
from typing import Union
from uuid import UUID

from pydantic import BaseModel

from model.db_core import DBCore
from utils.persistence_engine import PersistenceEngine


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class DBCoreService:

    def __init__(
        self,
        internal_store: dict[UUID, DBCore],
        model_type: type[BaseModel] = DBCore,
        persistence_name: Union[str, None] = None,
        persistence_engine: Union[PersistenceEngine, None] = None,
    ):
        pass

    def link_to_parent(self, parent, child):
        child.parent_uuid = parent.uuid

    def unlink_from_parent(self, child):
        child.parent_uuid = None

    def create(self, child):
        child.created_at = utc_now()
        child.updated_at = utc_now()

    def update(self, child):
        child.updated_at = utc_now()

    def delete(self, child):
        child.deleted_at = utc_now()
        child.is_deleted = True
