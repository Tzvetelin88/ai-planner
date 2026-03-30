from __future__ import annotations

from collections import defaultdict, deque

from src.models.schemas import PlanTask, TaskDependency

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    nx = None


def validate_dependencies(tasks: list[PlanTask], dependencies: list[TaskDependency]) -> None:
    task_ids = {task.id for task in tasks}
    for dependency in dependencies:
        if dependency.task_id not in task_ids:
            raise ValueError(f"Unknown task id: {dependency.task_id}")
        if dependency.depends_on not in task_ids:
            raise ValueError(f"Unknown dependency id: {dependency.depends_on}")

    if nx is not None:
        graph = nx.DiGraph()
        graph.add_nodes_from(task_ids)
        graph.add_edges_from((dep.depends_on, dep.task_id) for dep in dependencies)
        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Task dependency graph must be acyclic")
        return

    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {task_id: 0 for task_id in task_ids}
    for dep in dependencies:
        adjacency[dep.depends_on].append(dep.task_id)
        indegree[dep.task_id] += 1

    queue = deque(task_id for task_id, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        current = queue.popleft()
        visited += 1
        for next_task in adjacency[current]:
            indegree[next_task] -= 1
            if indegree[next_task] == 0:
                queue.append(next_task)

    if visited != len(task_ids):
        raise ValueError("Task dependency graph must be acyclic")


def topological_task_ids(tasks: list[PlanTask], dependencies: list[TaskDependency]) -> list[str]:
    validate_dependencies(tasks, dependencies)
    task_ids = {task.id for task in tasks}

    if nx is not None:
        graph = nx.DiGraph()
        graph.add_nodes_from(task_ids)
        graph.add_edges_from((dep.depends_on, dep.task_id) for dep in dependencies)
        return list(nx.topological_sort(graph))

    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree = {task_id: 0 for task_id in task_ids}
    for dep in dependencies:
        adjacency[dep.depends_on].append(dep.task_id)
        indegree[dep.task_id] += 1

    queue = deque(sorted(task_id for task_id, degree in indegree.items() if degree == 0))
    ordered: list[str] = []
    while queue:
        current = queue.popleft()
        ordered.append(current)
        for next_task in sorted(adjacency[current]):
            indegree[next_task] -= 1
            if indegree[next_task] == 0:
                queue.append(next_task)

    return ordered
