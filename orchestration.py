"""
Orchestration Workflow Engine
Auto-generated from visual design

This orchestration executes multiple agents in a coordinated workflow.
Agents are executed in topological order based on dependencies (edges).
"""

import sys
import os
import json
import logging
import importlib.util
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict, deque
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ── Design metadata ──────────────────────────────────────
DESIGN_NODES = [
    {
        "id": "node-1775037125467",
        "type": "agent",
        "data": {
            "label": "Ecommerce Attendance Tracker Agent edited Design",
            "agentId": "3ab14ae6-1f90-45e5-9d56-4264a6d73634",
            "agentName": "Ecommerce Attendance Tracker Agent edited Design",
            "config": {}
        },
        "position": {
            "x": 410.2264211997178,
            "y": 372.04603423256015
        }
    },
    {
        "id": "node-1775037126342",
        "type": "agent",
        "data": {
            "label": "Healthcare Employee Attendance Tracker Design",
            "agentId": "13f94957-4100-4972-a9e8-f0cfd561d4b9",
            "agentName": "Healthcare Employee Attendance Tracker Design",
            "config": {}
        },
        "position": {
            "x": 407.55171164887713,
            "y": 147.91888742744277
        }
    },
    {
        "id": "node-1775037126688",
        "type": "agent",
        "data": {
            "label": "Healthcare Employee Attendance Tracker Design",
            "agentId": "13f94957-4100-4972-a9e8-f0cfd561d4b9",
            "agentName": "Healthcare Employee Attendance Tracker Design",
            "config": {}
        },
        "position": {
            "x": -100.089893240361,
            "y": -299.72881670716646
        }
    }
]

DESIGN_EDGES = [
    {
        "id": "edge-node-1775037126688-node-1775037126342-1775037140208",
        "source": "node-1775037126688",
        "target": "node-1775037126342",
        "data": {
            "edgeStyle": "solid",
            "lineType": "smoothstep",
            "sourceHandlePosition": "bottom",
            "targetHandlePosition": "top"
        }
    },
    {
        "id": "edge-node-1775037126342-node-1775037125467-1775037143352",
        "source": "node-1775037126342",
        "target": "node-1775037125467",
        "data": {
            "edgeStyle": "solid",
            "lineType": "smoothstep",
            "sourceHandlePosition": "bottom",
            "targetHandlePosition": "top"
        }
    }
]


class OrchestrationEngine:
    """
    Orchestration engine that executes agents following the
    dependency graph defined in the visual designer.

    Features:
        - Topological sort for correct execution order
        - Dynamic agent loading from build artefacts
        - Data-flow routing between nodes via edges
        - Per-node error isolation with detailed logging
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Args:
            base_path: Root directory that contains the agent build
                       folders. Defaults to the directory of this file.
        """
        self.base_path = base_path or os.path.dirname(os.path.abspath(__file__))
        self.nodes: Dict[str, Dict] = {n["id"]: n for n in DESIGN_NODES}
        self.edges: List[Dict] = DESIGN_EDGES

        # Adjacency helpers
        self.successors: Dict[str, List[str]] = defaultdict(list)
        self.predecessors: Dict[str, List[str]] = defaultdict(list)
        for edge in self.edges:
            src, tgt = edge["source"], edge["target"]
            self.successors[src].append(tgt)
            self.predecessors[tgt].append(src)

        logger.info(
            "OrchestrationEngine initialised – %d node(s), %d edge(s)",
            len(self.nodes), len(self.edges),
        )

    def _topological_sort(self) -> List[str]:
        """Return node IDs in a valid execution order (Kahn's algorithm)."""
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}
        for edge in self.edges:
            in_degree[edge["target"]] += 1

        queue: deque = deque(nid for nid, d in in_degree.items() if d == 0)
        order: List[str] = []

        while queue:
            nid = queue.popleft()
            order.append(nid)
            for succ in self.successors.get(nid, []):
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)

        if len(order) != len(self.nodes):
            raise RuntimeError(
                "Cycle detected in orchestration graph – cannot determine execution order"
            )
        return order

    def _load_agent(self, node_id: str):
        """Dynamically load an agent module for *node_id*."""
        node = self.nodes.get(node_id)
        if not node:
            logger.error("Node not found: %s", node_id)
            return None

        node_data = node.get("data", {})
        agent_name = node_data.get("agentName", "Agent")

        # Determine agent module path
        if node_id == 'node-1775037125467':
            module_path = os.path.join(self.base_path, 'ecommerce_attendance_tracker_agent_edited_design', 'agent.py')
            config_path = os.path.join(self.base_path, 'ecommerce_attendance_tracker_agent_edited_design', 'config.py')
        elif node_id == 'node-1775037126342':
            module_path = os.path.join(self.base_path, 'healthcare_employee_attendance_tracker_design', 'agent.py')
            config_path = os.path.join(self.base_path, 'healthcare_employee_attendance_tracker_design', 'config.py')
        elif node_id == 'node-1775037126688':
            module_path = os.path.join(self.base_path, 'healthcare_employee_attendance_tracker_design', 'agent.py')
            config_path = os.path.join(self.base_path, 'healthcare_employee_attendance_tracker_design', 'config.py')
        else:
            logger.warning("Unknown node: %s", node_id)
            return None

        try:
            # Load agent module
            if not os.path.exists(module_path):
                logger.error("Agent file not found: %s", module_path)
                return None

            # Load config if exists
            config = None
            if os.path.exists(config_path):
                spec = importlib.util.spec_from_file_location("config", config_path)
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)
                config = {
                    k: getattr(config_module, k)
                    for k in dir(config_module)
                    if not k.startswith("_")
                }

            # Load agent module
            spec = importlib.util.spec_from_file_location("agent", module_path)
            agent_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(agent_module)

            return {"module": agent_module, "config": config}

        except Exception as exc:
            logger.error("Failed to load agent for node %s: %s", node_id, exc)
            return None

    def _get_node_inputs(
        self, node_id: str, results: Dict[str, Any], initial_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather inputs for *node_id* from upstream results and edges."""
        preds = self.predecessors.get(node_id, [])

        if not preds:
            return dict(initial_input)

        merged: Dict[str, Any] = {}
        for edge in self.edges:
            if edge["target"] != node_id:
                continue
            src_id = edge["source"]
            edge_data = edge.get("data", {})
            src_output_key = edge_data.get("sourceOutput", edge_data.get("source_output", "output"))
            tgt_input_key = edge_data.get("targetInput", edge_data.get("target_input", "input"))

            src_result = results.get(src_id, {})
            if isinstance(src_result, dict):
                value = src_result.get(src_output_key, src_result.get("output", src_result))
            else:
                value = src_result
            merged[tgt_input_key] = value

        return merged

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the full orchestration.

        Args:
            input_data: Initial payload passed to root nodes.

        Returns:
            Dict with per-node results, final output, and status.
        """
        execution_order = self._topological_sort()
        logger.info("Execution order: %s", execution_order)

        results: Dict[str, Any] = {}
        errors: Dict[str, str] = {}

        for node_id in execution_order:
            node = self.nodes[node_id]
            node_label = node.get("data", {}).get("label", node_id)
            logger.info("── Executing node: %s (%s)", node_id, node_label)

            try:
                agent_info = self._load_agent(node_id)

                node_input = self._get_node_inputs(node_id, results, input_data)
                logger.info("   Input keys: %s", list(node_input.keys()))

                if agent_info and agent_info["module"]:
                    module = agent_info["module"]
                    config = agent_info.get("config")

                    # Try common entry-point patterns
                    if hasattr(module, "run"):
                        result = module.run(node_input, config=config)
                    elif hasattr(module, "execute"):
                        result = module.execute(node_input, config=config)
                    elif hasattr(module, "main"):
                        result = module.main(node_input)
                    elif hasattr(module, "Agent"):
                        agent_instance = module.Agent(config=config) if config else module.Agent()
                        result = agent_instance.run(node_input) if hasattr(agent_instance, "run") else agent_instance.execute(node_input)
                    else:
                        logger.warning("No entry point found for node %s – passing input through", node_id)
                        result = node_input
                else:
                    logger.warning("Agent not loaded for node %s – passing input through", node_id)
                    result = node_input

                results[node_id] = result
                logger.info("   ✅ Node %s completed", node_id)

            except Exception as exc:
                error_msg = f"Error in node {node_id} ({node_label}): {exc}"
                logger.error("   ❌ %s", error_msg)
                errors[node_id] = str(exc)
                results[node_id] = {"error": str(exc)}

        # Determine final output from the last node(s)
        final_node = execution_order[-1] if execution_order else None
        final_output = results.get(final_node, {}) if final_node else {}

        status = "completed_with_errors" if errors else "success"
        logger.info("Orchestration finished – status: %s", status)

        return {
            "status": status,
            "execution_order": execution_order,
            "results": results,
            "errors": errors,
            "final_output": final_output,
        }


def main():
    """CLI entry-point for standalone execution."""
    orchestration = OrchestrationEngine()

    # Default test input – replace with real data as needed
    input_data = {
        "message": "Hello from orchestration",
        "user_id": "test_user",
        "timestamp": "2026-04-01T09:53:07.009701+00:00"
    }

    # Execute workflow
    result = orchestration.execute(input_data)

    # Print results
    print("\n" + "="*80)
    print("ORCHESTRATION RESULTS")
    print("="*80)
    print(json.dumps(result, indent=2))
    print("="*80 + "\n")

    return result


if __name__ == "__main__":
    main()