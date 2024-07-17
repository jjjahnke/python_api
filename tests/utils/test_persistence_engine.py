import json
import os
from uuid import uuid4
import pytest
from unittest.mock import mock_open, patch

from icecream import ic

from model.db_core import DBCore
from utils.persistence_engine import FilePersistenceEngine

class MockDBCore(DBCore):
    bogus_field: str

@pytest.fixture
def file_persistence_engine(tmp_path):
    return FilePersistenceEngine(base_path=str(tmp_path))

def test_check_file_creates_file_if_not_exists(file_persistence_engine, mocker):
    mocker.patch('os.path.exists', return_value=False)
    mocker.patch('os.makedirs')
    open_mock = mock_open()
    with patch('builtins.open', open_mock, create=True):
        file_persistence_engine.check_file("test_file")
    open_mock.assert_called_once_with(file_persistence_engine.base_path + "/test_file", 'w')

def test_write_data_writes_correct_data_to_file(file_persistence_engine, mocker):
    test_uuid = uuid4()  # Generate a UUID for testing
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    open_mock = mock_open()
    with patch('builtins.open', open_mock, create=True):
        file_persistence_engine.write_data(model_instance)
    
    # Assert open was called twice, once for checking the file and once for writing
    open_mock.call_count == 2

    # Assert the correct data was written to the file
    write_calls = open_mock().write.call_args_list
    assert write_calls[0][0][0] == "", "First write should be empty"
    written_data = write_calls[1][0][0]
    assert type(written_data) == str, "Written data should be a string"
    written_data = json.loads(written_data)
    assert written_data["__class__"] == "DBCore", "Class name should be DBCore"
    assert written_data["__module__"] == "model.db_core", "Module name should be model.db_core"
    assert f'"uuid":"{str(test_uuid)}"' in written_data["__attributes__"], "UUID should be in attributes"

def test_read_data_reads_and_reconstructs_model(file_persistence_engine, mocker):
    # Create a real instance of DBCore for testing
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    
    # Serialize the model instance to JSON
    data = {"__class__": model_instance.__class__.__name__,
          "__module__": model_instance.__module__, 
          "__attributes__": model_instance.model_dump_json()}
    model_json = json.dumps(data)    
    # Mock the open function to return the serialized model
    mocker.patch('builtins.open', mocker.mock_open(read_data=model_json))
    
    # Attempt to read and reconstruct the model from the mocked file
    reconstructed_model = file_persistence_engine.read_data(DBCore.__name__, str(test_uuid))
    
    # Assertions to verify the reconstructed model matches the original
    assert type(reconstructed_model) == DBCore
    assert reconstructed_model.uuid == test_uuid
    assert reconstructed_model.is_deleted == False

def test_delete_data_deletes_file(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    
    mocker.patch('os.path.exists', return_value=True)
    with patch('os.remove') as mock_remove:
        file_persistence_engine.delete_data(model_instance)
        mock_remove.assert_called_once_with(model_location)

def test_list_data_returns_list_of_models(file_persistence_engine, mocker):
    test_uuid1 = uuid4()
    test_uuid2 = uuid4()
    model_instance1 = DBCore(uuid=test_uuid1, parent_uuid=None, is_deleted=False)
    model_instance2 = DBCore(uuid=test_uuid2, parent_uuid=None, is_deleted=False)

    file_persistence_engine.write_data(model_instance1)
    file_persistence_engine.write_data(model_instance2)
    model_list = file_persistence_engine.list_data(model_instance1.__class__.__name__)

    assert len(model_list) == 2
    assert model_list.count(model_instance1) == 1
    assert model_list.count(model_instance2) == 1

def test_list_data_returns_empty_list_if_no_models(file_persistence_engine, mocker):
    test_uuid1 = uuid4()
    test_uuid2 = uuid4()
    model_instance1 = DBCore(uuid=test_uuid1, parent_uuid=None, is_deleted=False)
    model_instance2 = DBCore(uuid=test_uuid2, parent_uuid=None, is_deleted=False)

    file_persistence_engine.write_data(model_instance1)
    file_persistence_engine.write_data(model_instance2)
    model_list = file_persistence_engine.list_data(MockDBCore.__name__)
    assert len(model_list) == 0

def test_make_file_path_returns_correct_path(file_persistence_engine):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    file_path = file_persistence_engine.make_file_path(model_instance)
    assert file_path == f'{model_instance.__class__.__name__}+{str(test_uuid)}'

def test_read_file_reads_file(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    data = {"__class__": model_instance.__class__.__name__,
          "__module__": model_instance.__module__, 
          "__attributes__": model_instance.model_dump_json()}
    model_json = json.dumps(data)    
    mocker.patch('builtins.open', mocker.mock_open(read_data=model_json))
    reconstructed_model = file_persistence_engine.read_file(model_location)
    assert type(reconstructed_model) == DBCore
    assert reconstructed_model.uuid == test_uuid
    assert reconstructed_model.is_deleted == False
    assert reconstructed_model.parent_uuid == None
    assert reconstructed_model.created_at == model_instance.created_at
    assert reconstructed_model.updated_at == model_instance.updated_at
    assert reconstructed_model.deleted_at == None
    assert reconstructed_model.is_deleted == False

def test_read_file_throws_exception_if_file_does_not_exist(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    mocker.patch('os.path.exists', return_value=False)
    with pytest.raises(FileNotFoundError):
      reconstructed_model = file_persistence_engine.read_file(model_location)

def test_read_file_throws_exception_if_file_is_empty(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data=""))
    with pytest.raises(json.JSONDecodeError):
      reconstructed_model = file_persistence_engine.read_file(model_location)

def test_read_file_throws_exception_if_file_is_invalid_json(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mocker.mock_open(read_data="invalid_json"))
    with pytest.raises(json.JSONDecodeError):
      reconstructed_model = file_persistence_engine.read_file(model_location)

def test_read_file_throws_exception_if_file_is_missing_attributes(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    data = {"__class__": model_instance.__class__.__name__,
          "__module__": model_instance.__module__}
    model_json = json.dumps(data)    
    mocker.patch('builtins.open', mocker.mock_open(read_data=model_json))
    with pytest.raises(KeyError):
      reconstructed_model = file_persistence_engine.read_file(model_location)

def test_read_file_throws_exception_if_file_is_missing_classname(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    data = {"__module__": model_instance.__module__,
          "__attributes__": model_instance.model_dump_json()}
    model_json = json.dumps(data)    
    mocker.patch('builtins.open', mocker.mock_open(read_data=model_json))
    with pytest.raises(KeyError):
      reconstructed_model = file_persistence_engine.read_file(model_location)

def test_read_file_throws_exception_if_file_is_missing_modulename(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    data = {"__class__": model_instance.__class__.__name__,
          "__attributes__": model_instance.model_dump_json()}
    model_json = json.dumps(data)    
    mocker.patch('builtins.open', mocker.mock_open(read_data=model_json))
    with pytest.raises(KeyError):
      reconstructed_model = file_persistence_engine.read_file(model_location)

def test_read_file_throws_exception_if_file_is_missing_module_and_classname(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    data = {"__attributes__": model_instance.model_dump_json()}
    model_json = json.dumps(data)    
    mocker.patch('builtins.open', mocker.mock_open(read_data=model_json))
    with pytest.raises(KeyError):
      reconstructed_model = file_persistence_engine.read_file(model_location)

def test_read_file_throws_exception_if_file_is_missing_attributes(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    data = {"__class__": model_instance.__class__.__name__,
          "__module__": model_instance.__module__}
    model_json = json.dumps(data)    
    mocker.patch('builtins.open', mocker.mock_open(read_data=model_json))
    with pytest.raises(KeyError):
      reconstructed_model = file_persistence_engine.read_file(model_location)


def test_read_file_throws_exception_if_file_is_missing_attributes(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    data = {"__class__": model_instance.__class__.__name__,
          "__module__": model_instance.__module__}
    model_json = json.dumps(data)    
    mocker.patch('builtins.open', mocker.mock_open(read_data=model_json))
    with pytest.raises(KeyError):
      reconstructed_model = file_persistence_engine.read_file(model_location)

def test_read_file_throws_exception_if_file_is_missing_attributes(file_persistence_engine, mocker):
    test_uuid = uuid4()
    model_instance = DBCore(uuid=test_uuid, parent_uuid=None, is_deleted=False)
    model_location = os.path.join(file_persistence_engine.base_path, f"{model_instance.__class__.__name__}+{str(test_uuid)}")
    data = {"__class__": model_instance.__class__.__name__,
          "__module__": model_instance.__module__}
    model_json = json.dumps(data)    
    mocker.patch('builtins.open', mocker.mock_open(read_data=model_json))
    with pytest.raises(KeyError):
      reconstructed_model = file_persistence_engine.read_file(model_location)

def test_read_model_returns_correct_model(file_persistence_engine, mocker):
    test_uuid1 = uuid4()
    test_uuid2 = uuid4()
    model_instance1 = DBCore(uuid=test_uuid1, parent_uuid=None, is_deleted=False)
    model_instance2 = DBCore(uuid=test_uuid2, parent_uuid=None, is_deleted=False)

    file_persistence_engine.write_data(model_instance1)
    file_persistence_engine.write_data(model_instance2)

    reconstructed_model1 = file_persistence_engine.read_model(model_instance1)
    reconstructed_model2 = file_persistence_engine.read_model(model_instance2)

    assert reconstructed_model1 == model_instance1
    assert reconstructed_model2 == model_instance2

