from fastapi import FastAPI, HTTPException

from .engine import GraphEngine
from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    GraphStateResponse,
)

app=FastAPI(title="Mini Workflow Engine")
engine=GraphEngine()

@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(req: GraphCreateRequest):
    try:
        graph_id=engine.create_graph(
            nodes=req.nodes,
            edges=req.edges,
            start_node=req.start_node,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return GraphCreateResponse(graph_id=graph_id)


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(req: GraphRunRequest):
    try:
        run=engine.run_graph(
            graph_id=req.graph_id,
            initial_state=req.initial_state,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return GraphRunResponse(
        run_id=run.id,
        final_state=run.state,
        log=run.log,
        status=run.status,
    )


@app.get("/graph/state/{run_id}", response_model=GraphStateResponse)
async def get_graph_state(run_id: str):
    run=engine.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return GraphStateResponse(
        run_id=run.id,
        state=run.state,
        log=run.log,
        status=run.status,
    )

@app.post("/graph/run_async", response_model=GraphRunResponse)
async def run_graph_async(req: GraphRunRequest):
    try:
        run=await engine.run_graph_async(
            graph_id=req.graph_id,
            initial_state=req.initial_state,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return GraphRunResponse(
        run_id=run.id,
        final_state=run.state,
        log=run.log,
        status=run.status,
        error=run.error,
    )
