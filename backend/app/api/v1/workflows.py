import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.langgraph.factory import ServiceFactory
from app.langgraph.graph import workflow_app
from app.core.logger import logger, update_log_context

router = APIRouter()

@router.get("/{thread_id}")
def get_workflow_summary(thread_id: str, db: Session = Depends(get_db)):
    """
    Reads the LangGraph checkpoint state and returns a summary of the workflow.
    """
    factory = ServiceFactory(db)
    config = {
        "configurable": {
            "thread_id": thread_id,
            "db": db,
            "factory": factory
        }
    }
    
    snapshot = workflow_app.get_state(config)
    if not snapshot or not snapshot.values:
        # Return empty/uninitialized state rather than 404
        # so the frontend knows the workflow hasn't started yet
        return {
            "success": True,
            "data": {
                "thread_id": thread_id,
                "current_stage": None,
                "next": [],
                "values": {
                    "user_id": None,
                    "goal_id": None,
                    "goal_title": None,
                    "current_stage": None,
                    "error": None
                }
            }
        }
        
    return {
        "success": True,
        "data": {
            "thread_id": thread_id,
            "current_stage": snapshot.values.get("current_stage"),
            "next": list(snapshot.next) if snapshot.next else [],
            "values": {
                "user_id": snapshot.values.get("user_id"),
                "goal_id": snapshot.values.get("goal_id"),
                "goal_title": snapshot.values.get("goal_title"),
                "current_stage": snapshot.values.get("current_stage"),
                "error": snapshot.values.get("error")
            }
        }
    }

@router.get("/{thread_id}/state")
def get_workflow_state(thread_id: str, db: Session = Depends(get_db)):
    """
    Returns the full state values dictionary from the LangGraph checkpoint.
    """
    factory = ServiceFactory(db)
    config = {
        "configurable": {
            "thread_id": thread_id,
            "db": db,
            "factory": factory
        }
    }
    
    snapshot = workflow_app.get_state(config)
    if not snapshot or not snapshot.values:
        # Return empty state instead of 404 so frontend can show "processing" state
        return {
            "success": True,
            "data": {
                "current_stage": None,
                "error": None,
                "strategies": [],
                "readiness": None,
            }
        }
        
    return {
        "success": True,
        "data": snapshot.values
    }

@router.get("/{thread_id}/history")
def get_workflow_history(thread_id: str, db: Session = Depends(get_db)):
    """
    Chronologically traces checkpoint history to visualize stage progression.
    """
    factory = ServiceFactory(db)
    config = {
        "configurable": {
            "thread_id": thread_id,
            "db": db,
            "factory": factory
        }
    }
    
    stages = []
    try:
        # get_state_history yields checkpoints from newest to oldest
        for state in workflow_app.get_state_history(config):
            stage = state.values.get("current_stage")
            if stage and stage not in stages:
                stages.append(stage)
                
        # Reverse history to obtain oldest-to-newest chronological ordering
        stages.reverse()
    except Exception as e:
        logger.error(f"Failed to retrieve workflow history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch state history: {e}"
        )
        
    return {
        "stages": stages
    }

@router.post("/{thread_id}/resume")
def resume_workflow(thread_id: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Resumes or initializes a workflow, injecting updates and streaming until next pause or completion.
    """
    factory = ServiceFactory(db)
    config = {
        "configurable": {
            "thread_id": thread_id,
            "db": db,
            "factory": factory
        }
    }
    
    snapshot = workflow_app.get_state(config)
    
    # Check if workflow is not initialized yet
    if not snapshot or not snapshot.values:
        user_id = payload.get("user_id")
        goal_id = payload.get("goal_id")
        goal_title = payload.get("goal_title", "Unassigned Goal")
        
        if not user_id or not goal_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow is not initialized. Please provide user_id and goal_id in payload to initialize."
            )
            
        initial_state = {
            "user_id": str(user_id),
            "goal_id": str(goal_id),
            "goal_title": goal_title,
            "thread_id": thread_id,
            "current_stage": "",
            "error": None
        }
        
        try:
            update_log_context({
                "thread_id": thread_id,
                "event": "workflow_initialize"
            })
            logger.info(f"Initializing new workflow thread {thread_id}")
            
            # Start graph from entry point
            for event in workflow_app.stream(initial_state, config):
                node_name = list(event.keys())[0]
                logger.info(f"LangGraph executed initial node: {node_name}")
                
        except Exception as e:
            logger.error(f"Error initializing workflow: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Execution error initializing workflow: {e}"
            )
    else:
        # Resume existing workflow from paused node
        as_node = None
        if snapshot.next:
            next_nodes = list(snapshot.next) if isinstance(snapshot.next, (list, tuple)) else [snapshot.next]
            if next_nodes:
                as_node = next_nodes[0]
                
        try:
            update_log_context({
                "thread_id": thread_id,
                "event": "workflow_resume",
                "as_node": as_node
            })
            logger.info(f"Resuming workflow thread {thread_id} at node: {as_node}")
            
            # Apply state updates
            workflow_app.update_state(config, payload, as_node=as_node)
            
            # Resume graph execution
            for event in workflow_app.stream(None, config):
                node_name = list(event.keys())[0]
                logger.info(f"LangGraph executed node: {node_name}")
                
        except Exception as e:
            logger.error(f"Error resuming workflow execution: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Execution error resuming workflow: {e}"
            )
        
    new_snapshot = workflow_app.get_state(config)
    return {
        "success": True,
        "data": {
            "thread_id": thread_id,
            "current_stage": new_snapshot.values.get("current_stage"),
            "next": list(new_snapshot.next) if new_snapshot.next else [],
            "values": {
                "user_id": new_snapshot.values.get("user_id"),
                "goal_id": new_snapshot.values.get("goal_id"),
                "goal_title": new_snapshot.values.get("goal_title"),
                "current_stage": new_snapshot.values.get("current_stage"),
                "error": new_snapshot.values.get("error")
            }
        }
    }
