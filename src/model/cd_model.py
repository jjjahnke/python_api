from typing import List
from uuid import UUID
from pydantic import BaseModel

from model.db_core import DBCore


class User(DBCore):
    username: str
    email: str


class UserResponse(BaseModel):
    uuid: UUID
    username: str
    email: str

    def newResponse(user: User):
        return UserResponse(uuid=user.uuid, username=user.username, email=user.email)


class OpsInfo(BaseModel):
    name: str
    version: str
    description: str
    repo: str
    branch: str
    version: str


class Cluster(BaseModel):
    cluster_id: str
    name: str
    description: str
    opsInfo: OpsInfo
    ppp_namespace: str
    owner_id: str


class Environment(BaseModel):
    environment_id: str
    name: str
    description: str
    clusters: List[str]


class Deployable(BaseModel):
    deployable_id: str
    name: str
    description: str
    type: str
    url: str
    owner: str
    status: str
    created_at: str
    updated_at: str


class microAG(BaseModel):
    name: str
    version: str
    description: str
    repo: str
    branch: str
    version: str
    opsInfo: OpsInfo
    environment: Environment
    deployables: Deployable


class DeploymentRequest(BaseModel):
    envionment: str
    deployables: List[Deployable]
