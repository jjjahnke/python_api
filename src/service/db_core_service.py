import datetime
from typing import Union
from uuid import UUID

from pydantic import BaseModel

from model.db_core import DBCore
from utils.persistence_engine import InMemoryPersistenceEngine, PersistenceEngine


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class DBCoreService():
    
    def __init__(self,
                 model_type: type[BaseModel] = DBCore,
                 persistence_engine: PersistenceEngine = InMemoryPersistenceEngine()):
        self.model_type = model_type
        self.persistence_engine = persistence_engine

    def check_model_type(self, record):
        if record.__class__ != self.model_type:
            raise ValueError(f"Invalid model type: {record.__class__.__name__}")

    def get(self, uuid: UUID) -> DBCore:
        record = None
        try:
          record = self.persistence_engine.read_data(self.model_type.__name__, uuid)
        except KeyError:
          pass
        return record

    def create(self, record: DBCore) -> DBCore:
        self.check_model_type(record)
        
        if self.get(record.uuid):
            raise ValueError(f"Record already exists: {record.uuid}")
        
        record.created_at = utc_now()
        record.updated_at = utc_now()
        return self.persistence_engine.write_data(record)

    def update(self, record:DBCore, createOnUpdate:bool=False) -> DBCore:
        self.check_model_type(record)

        if not self.get(record.uuid):
            if createOnUpdate:
                return self.create(record)
            else:
                raise ValueError(f"Record does not exist: {record.uuid}")
        
        record.updated_at = utc_now()

        self.internal_store[record.uuid] = record
        if self.persistence_engine:
            self.persistence_engine.write_data(record)
        return record

    def delete(self, record:DBCore, hard_delete=False) -> DBCore:
        self.check_model_type(record)

        record.deleted_at = utc_now()
        record.is_deleted = True

        if hard_delete:
            del self.internal_store[record.uuid]
            if self.persistence_engine:
                self.persistence_engine.delete_data(record)
        else:
            return self.update(record)
        return record
    
    def filter(self, filter_func) -> list[DBCore]:
        return [record for record in self.internal_store.values() if filter_func(record)]
