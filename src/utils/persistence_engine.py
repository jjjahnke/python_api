from abc import ABC, abstractmethod
from importlib import import_module
import json
import os
import uuid

from model.db_core import DBCore


class PersistenceEngine(ABC):

    @abstractmethod
    def read_model(self, model: DBCore) -> DBCore:
        pass  # pragma: no cover

    @abstractmethod
    def read_data(self, model_type: str, uuid: uuid) -> DBCore:
        pass  # pragma: no cover

    @abstractmethod
    def write_data(self, model: DBCore) -> DBCore:
        pass  # pragma: no cover

    @abstractmethod
    def delete_data(self, model: DBCore) -> DBCore:
        pass  # pragma: no cover

    @abstractmethod
    def list_data(self, model_type: str) -> list[DBCore]:
        pass  # pragma: no cover


class FilePersistenceEngine(PersistenceEngine):
    def __init__(self, base_path: str):
        self.base_path = base_path

    def make_file_path(self, model: DBCore):
        return f"{model.__class__.__name__}+{model.uuid}"

    def check_file(self, file_name: str):
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        file_path = os.path.join(self.base_path, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("")

        return file_path

    def write_data(self, model: DBCore) -> DBCore:
        file_path = self.check_file(self.make_file_path(model))

        data = json.dumps(
            {
                "__class__": model.__class__.__name__,
                "__module__": model.__module__,
                "__attributes__": model.model_dump_json(),
            }
        )

        with open(file_path, "w") as f:
            f.write(data)

        return model

    def read_model(self, model: DBCore) -> DBCore:
        return self.read_data(model.__class__.__name__, model.uuid)

    def read_data(self, model_type: str, uuid: uuid) -> DBCore:
        file_path = self.check_file(f"{model_type}+{uuid}")

        return self.read_file(file_path)

    def read_file(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            module = import_module(data["__module__"])
            cls = getattr(module, data["__class__"])
            return cls.model_validate(json.loads(data["__attributes__"]))

    def delete_data(self, model: DBCore) -> DBCore:
        file_path = self.check_file(self.make_file_path(model))
        os.remove(file_path)
        return model

    def list_data(self, model_type: str) -> list[DBCore]:
        files = os.listdir(self.base_path)
        models = []
        for file in files:
            if str(file).startswith(model_type):
                file_path = self.check_file(file)
                models.append(self.read_file(file_path))
        return models
