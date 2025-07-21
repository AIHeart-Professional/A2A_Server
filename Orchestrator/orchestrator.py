from asyncio import tasks
from json import tool
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import functools
import requests
from config.logging_config import setup_logging
import logging
from Agents.app import execute_agent

setup_logging()
logger = logging.getLogger(__name__)

class OrchestratorState(TypedDict):
    tasks: List[dict]
    intent: str
    original_request: dict
    current_step: int
    results: Annotated[List[dict], lambda x, y: x + y]
    context: dict

async def run_orchestrator(request: dict, details: dict):
    """
    Runs the orchestrator with a given request.
    `request` is the plan from the planner.
    `details` is the formatted request from the intent handler.
    """
    initial_state = {
        "tasks": details.get("tasks", []),
        "intent": details.get("intent"),
        "original_request": request.get("initial_request"),
        "current_step": 0,
        "results": [],
        "context": {},
    }
    app_graph = await define_nodes(initial_state["tasks"])
    return await app_graph.ainvoke(initial_state)

async def define_nodes(tasks):
    """
    Dynamically defines nodes in the workflow for each step in the tasks,
    linking each node to the next.
    Returns a compiled StateGraph.
    """
    workflow = StateGraph(OrchestratorState)
    num_steps = len(tasks)
    step_name = []
    # Add a node for each step
    for idx, step in enumerate(tasks.values()):
        node_name = step["tool"]["name"]
        step_name.append(node_name)
        workflow.add_node(node_name, functools.partial(run_step, step_idx=idx))

    # Link each node to the next, last node goes to END
    for idx in range(num_steps):
        node_name = step_name[idx]
        if idx == num_steps - 1:
            workflow.add_conditional_edges(
                node_name, 
                should_continue, 
                {
                    "END": END
                    }
                )
        else:
            next_node = step_name[idx + 1]
        #    workflow.add_edge(node_name, next_node)
            workflow.add_conditional_edges(
                node_name, 
                should_continue, 
                {
                    "CONTINUE": next_node, 
                    "END": END
                    }
                )
    # Set entry point to the first step
    workflow.set_entry_point(step_name[0])

    return workflow.compile()

async def run_step(state, step_idx):
    step = state["tasks"]["task_" + str(step_idx + 1)]
    context = state.get("context", {})
    if isinstance(step, dict):
        tool = step.get("tool", {})
        action = tool.get("name")
        agent = step.get("agent")
        if not agent or not action:
            logger.error(f"Invalid step format: {step}")
            return {**state, "current_step": state["current_step"] + 1, "results": state["results"] + [f"Invalid step format: {step}"]}
        step_name = f"{agent}/{action}"
    else:
        step_name = step
    logger.info(f"Executing step: {step_name} by calling {agent}.")
    result = await call_agent(agent, action, step["tool"].get("fields", {}), context)
    
    if isinstance(result, dict):
        # If the tool name isn't in the context, add it with a list for results
        if action not in context:
            context[action] = []
        # Append the new result to the list for that tool
        context[action].append(result)
        
    new_results = state["results"] + [result]
    # If error occurs, return the error message and stop
    if isinstance(result, dict) and "error" in result:
        logger.error(f"Error occurred: {result['error']}. Ending workflow.")
        return {**state, "current_step": state["current_step"] + 1, "results": new_results, "context": context}
    return {**state, "current_step": state["current_step"] + 1, "results": new_results, "context": context}

async def call_agent(agent: str, action: str, fields: dict, context: dict):
    """Generic function to call an agent."""
    try:
        response = await execute_agent(agent, action, fields, context)
        return response
    except Exception as e:
        logging.error(f"Error calling agent {agent} with action {action}: {e}")
        return {"error": str(e)}

async def should_continue(state: OrchestratorState):
    """
    Determines whether to continue to the next step or end.
    Checks for errors and if we're on the last step.
    """
    # Check if there was an error in the last result
    last_result = state["results"][-1] if state["results"] else {}
    if isinstance(last_result, dict) and "error" in last_result:
        return "END"
    
    # Check if we've completed all tasks
    total_tasks = len(state["tasks"])
    if state["current_step"] >= total_tasks:
        return "END"
    
    return "CONTINUE"

