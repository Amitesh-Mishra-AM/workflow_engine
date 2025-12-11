from typing import Any, Dict, List
from enum import Enum
from pydantic import BaseModel

class RunStatus(str, Enum):
    running="running"
    completed="completed"
    failed="failed"

class GraphCreateRequest(BaseModel):
    nodes:List[str]              
    edges:Dict[str, str]         
    start_node:str               

class GraphCreateResponse(BaseModel):
    graph_id:str

class GraphRunRequest(BaseModel):
    graph_id:str
    initial_state:Dict[str, Any]={}

class GraphRunResponse(BaseModel):
    run_id:str
    final_state:Dict[str, Any]
    log:List[str]
    status:RunStatus
class GraphStateResponse(BaseModel):
    run_id:str
    state:Dict[str, Any]
    log:List[str]
    status:RunStatus
