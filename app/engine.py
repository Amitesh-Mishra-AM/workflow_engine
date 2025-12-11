from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from pydantic import BaseModel
from .models import RunStatus
from .registries import NODE_REGISTRY, NodeFunc
import asyncio
State=Dict[str, Any]

class Graph(BaseModel):
    id:str
    nodes:List[str]
    edges:Dict[str, str]
    start_node:str

class RunRecord(BaseModel):
    id:str
    graph_id:str
    state:State
    log:List[str]
    status:RunStatus
    error:Optional[str]=None
class GraphEngine:
    def __init__(self):
        self.graphs:Dict[str, Graph]={}
        self.runs:Dict[str, RunRecord]={}

    def create_graph(self, nodes:List[str], edges:Dict[str, str], start_node:str) -> str:

        if start_node not in nodes:
            raise ValueError("start_node must be in nodes")

        for src, dst in edges.items():
            if src not in nodes or dst not in nodes:
                raise ValueError("edges must connect defined nodes")

        graph_id=str(uuid4())
        graph=Graph(
            id=graph_id,
            nodes=nodes,
            edges=edges,
            start_node=start_node,
        )
        self.graphs[graph_id]=graph
        return graph_id

    def _call_node(self, node_name:str, state:State) -> Tuple[State, Optional[str]]:
        if node_name not in NODE_REGISTRY:
            raise ValueError(f"Unknown node:{node_name}")

        func:NodeFunc=NODE_REGISTRY[node_name]
        result=func(state)

        if isinstance(result, tuple) and len(result) == 2:
            new_state, next_node=result
            return new_state, next_node
        else:
            return result, None
    def run_graph(self, graph_id:str, initial_state:State) -> RunRecord:
        if graph_id not in self.graphs:
            raise ValueError("Graph not found")

        graph=self.graphs[graph_id]
        run_id=str(uuid4())
        state:State=dict(initial_state) 
        log:List[str]=[]

        run=RunRecord(
            id=run_id,
            graph_id=graph_id,
            state=state,
            log=log,
            status=RunStatus.running,
        )
        self.runs[run_id]=run
        current_node=graph.start_node
        max_steps=100 
        try:
            for _ in range(max_steps):
                log.append(current_node)
                state, override_next=self._call_node(current_node, state)
                run.state=state 
                if override_next is not None:
                    next_node=override_next
                else:
                    next_node=graph.edges.get(current_node)
                if not next_node:
                    break

                current_node=next_node

            run.status=RunStatus.completed
        except Exception as e:
            run.status=RunStatus.failed
            run.error=str(e)

        self.runs[run_id]=run
        return run
    
    async def run_graph_async(self, graph_id:str, initial_state:State) -> RunRecord:
        return await asyncio.to_thread(self.run_graph, graph_id, initial_state)

    def get_run(self, run_id:str) -> Optional[RunRecord]:
        return self.runs.get(run_id)
