"""
Graph 자료구조의 핵심 로직을 구현하는 모듈입니다.

주요 기능
- 정점 추가
- 간선 추가
- 방향·무방향 그래프 지원
- DFS
- BFS
- 탐색 단계 기록
- 그래프 상태 저장 및 복원
"""

from __future__ import annotations

from collections import deque
from typing import Any


class Graph:
    """
    인접 리스트를 이용한 Graph 클래스입니다.

    directed가 False이면 무방향 그래프,
    True이면 방향 그래프로 동작합니다.
    """

    def __init__(self, directed: bool = False):
        self.directed = directed
        self.adjacency: dict[str, list[str]] = {}

    # ========================================================
    # 정점 및 간선
    # ========================================================

    def add_vertex(self, vertex: str) -> dict[str, Any]:
        """
        그래프에 정점을 추가합니다.
        """

        vertex = self.normalize_vertex(vertex)

        if not vertex:
            return {
                "success": False,
                "action": "add_vertex",
                "value": None,
                "message": "정점 이름을 입력해 주세요.",
                "concept": (
                    "정점은 그래프에서 하나의 지점이나 "
                    "대상을 나타냅니다."
                ),
            }

        if vertex in self.adjacency:
            return {
                "success": False,
                "action": "add_vertex",
                "value": vertex,
                "message": (
                    f"정점 {vertex}은(는) 이미 그래프에 존재합니다."
                ),
                "concept": (
                    "같은 이름의 정점은 한 번만 추가할 수 있습니다."
                ),
            }

        self.adjacency[vertex] = []

        return {
            "success": True,
            "action": "add_vertex",
            "value": vertex,
            "message": (
                f"정점 {vertex}을(를) 그래프에 추가했습니다."
            ),
            "concept": (
                "정점은 그래프를 구성하는 기본 요소입니다."
            ),
        }

    def add_edge(
        self,
        start: str,
        end: str,
    ) -> dict[str, Any]:
        """
        두 정점을 연결하는 간선을 추가합니다.
        """

        start = self.normalize_vertex(start)
        end = self.normalize_vertex(end)

        if not start or not end:
            return {
                "success": False,
                "action": "add_edge",
                "value": None,
                "message": "연결할 두 정점을 모두 입력해 주세요.",
                "concept": (
                    "간선은 두 정점 사이의 연결 관계를 나타냅니다."
                ),
            }

        if start == end:
            return {
                "success": False,
                "action": "add_edge",
                "value": (start, end),
                "message": (
                    "이번 학습용 그래프에서는 자기 자신을 연결하는 "
                    "간선을 추가하지 않습니다."
                ),
                "concept": (
                    "정점이 자기 자신과 연결된 간선을 "
                    "자기 루프라고 합니다."
                ),
            }

        # 정점이 없으면 자동으로 추가
        if start not in self.adjacency:
            self.adjacency[start] = []

        if end not in self.adjacency:
            self.adjacency[end] = []

        if end in self.adjacency[start]:
            return {
                "success": False,
                "action": "add_edge",
                "value": (start, end),
                "message": (
                    f"{start}와(과) {end}은(는) 이미 연결되어 있습니다."
                ),
                "concept": (
                    "같은 두 정점 사이의 간선은 한 번만 추가합니다."
                ),
            }

        self.adjacency[start].append(end)

        if not self.directed:
            self.adjacency[end].append(start)

        graph_type = (
            "방향 간선"
            if self.directed
            else "무방향 간선"
        )

        return {
            "success": True,
            "action": "add_edge",
            "value": (start, end),
            "message": (
                f"{start}와(과) {end} 사이에 "
                f"{graph_type}을(를) 추가했습니다."
            ),
            "concept": (
                "간선은 정점 사이의 연결 관계를 표현합니다."
            ),
        }

    # ========================================================
    # DFS
    # ========================================================

    def dfs(self, start: str) -> dict[str, Any]:
        """
        시작 정점에서 깊이 우선 탐색을 실행합니다.

        Stack을 이용하는 반복 방식으로 구현하며,
        각 단계의 Stack과 방문 상태를 기록합니다.
        """

        start = self.normalize_vertex(start)

        if start not in self.adjacency:
            return {
                "success": False,
                "action": "dfs",
                "value": start,
                "order": [],
                "steps": [],
                "message": (
                    f"시작 정점 {start}을(를) 찾을 수 없습니다."
                ),
                "concept": (
                    "DFS를 실행하려면 그래프에 존재하는 "
                    "시작 정점을 선택해야 합니다."
                ),
            }

        stack = [start]
        visited: list[str] = []
        visited_set: set[str] = set()
        steps: list[dict[str, Any]] = []

        steps.append(
            {
                "step": 0,
                "current": None,
                "visited": [],
                "container": stack.copy(),
                "added": [start],
                "description": (
                    f"시작 정점 {start}을(를) Stack에 넣습니다."
                ),
            }
        )

        while stack:
            current = stack.pop()

            if current in visited_set:
                continue

            visited_set.add(current)
            visited.append(current)

            # 인접 리스트의 앞쪽 정점을 먼저 방문하기 위해
            # Stack에는 역순으로 삽입
            unvisited_neighbors = [
                neighbor
                for neighbor in self.adjacency[current]
                if neighbor not in visited_set
            ]

            added_vertices = []

            for neighbor in reversed(unvisited_neighbors):
                if neighbor not in stack:
                    stack.append(neighbor)
                    added_vertices.append(neighbor)

            steps.append(
                {
                    "step": len(steps),
                    "current": current,
                    "visited": visited.copy(),
                    "container": stack.copy(),
                    "added": added_vertices.copy(),
                    "description": (
                        f"정점 {current}을(를) 방문하고, "
                        "아직 방문하지 않은 인접 정점을 Stack에 넣습니다."
                    ),
                }
            )

        return {
            "success": True,
            "action": "dfs",
            "value": start,
            "order": visited,
            "steps": steps,
            "message": (
                f"{start}에서 시작한 DFS를 완료했습니다."
            ),
            "concept": (
                "DFS는 한 방향을 가능한 깊이 탐색한 뒤 "
                "이전 갈림길로 돌아갑니다."
            ),
        }

    # ========================================================
    # BFS
    # ========================================================

    def bfs(self, start: str) -> dict[str, Any]:
        """
        시작 정점에서 너비 우선 탐색을 실행합니다.

        Queue를 이용하며 각 단계의 Queue와 방문 상태를 기록합니다.
        """

        start = self.normalize_vertex(start)

        if start not in self.adjacency:
            return {
                "success": False,
                "action": "bfs",
                "value": start,
                "order": [],
                "steps": [],
                "message": (
                    f"시작 정점 {start}을(를) 찾을 수 없습니다."
                ),
                "concept": (
                    "BFS를 실행하려면 그래프에 존재하는 "
                    "시작 정점을 선택해야 합니다."
                ),
            }

        queue = deque([start])
        discovered = {start}
        visited: list[str] = []
        steps: list[dict[str, Any]] = []

        steps.append(
            {
                "step": 0,
                "current": None,
                "visited": [],
                "container": list(queue),
                "added": [start],
                "description": (
                    f"시작 정점 {start}을(를) Queue에 넣습니다."
                ),
            }
        )

        while queue:
            current = queue.popleft()
            visited.append(current)

            added_vertices = []

            for neighbor in self.adjacency[current]:
                if neighbor not in discovered:
                    discovered.add(neighbor)
                    queue.append(neighbor)
                    added_vertices.append(neighbor)

            steps.append(
                {
                    "step": len(steps),
                    "current": current,
                    "visited": visited.copy(),
                    "container": list(queue),
                    "added": added_vertices.copy(),
                    "description": (
                        f"정점 {current}을(를) 방문하고, "
                        "새롭게 발견한 인접 정점을 Queue 뒤에 넣습니다."
                    ),
                }
            )

        return {
            "success": True,
            "action": "bfs",
            "value": start,
            "order": visited,
            "steps": steps,
            "message": (
                f"{start}에서 시작한 BFS를 완료했습니다."
            ),
            "concept": (
                "BFS는 시작 정점과 가까운 정점부터 "
                "차례대로 탐색합니다."
            ),
        }

    # ========================================================
    # 그래프 정보
    # ========================================================

    def vertices(self) -> list[str]:
        """
        모든 정점 목록을 반환합니다.
        """

        return list(self.adjacency.keys())

    def edges(self) -> list[tuple[str, str]]:
        """
        모든 간선 목록을 반환합니다.
        """

        result: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()

        for start, neighbors in self.adjacency.items():
            for end in neighbors:
                if self.directed:
                    result.append((start, end))
                else:
                    edge_key = tuple(
                        sorted((start, end))
                    )

                    if edge_key not in seen:
                        seen.add(edge_key)
                        result.append((start, end))

        return result

    def vertex_count(self) -> int:
        return len(self.adjacency)

    def edge_count(self) -> int:
        return len(self.edges())

    def degree(self, vertex: str) -> int:
        """
        무방향 그래프에서 정점의 차수를 반환합니다.
        방향 그래프에서는 나가는 간선 수를 반환합니다.
        """

        vertex = self.normalize_vertex(vertex)

        if vertex not in self.adjacency:
            return 0

        return len(self.adjacency[vertex])

    def is_empty(self) -> bool:
        return not self.adjacency

    # ========================================================
    # 저장·복원
    # ========================================================

    def clear(self) -> dict[str, Any]:
        """
        그래프의 모든 정점과 간선을 제거합니다.
        """

        vertex_count = self.vertex_count()
        edge_count = self.edge_count()

        self.adjacency.clear()

        return {
            "success": True,
            "action": "clear",
            "value": None,
            "message": (
                "그래프를 초기화했습니다. "
                f"정점 {vertex_count}개와 간선 {edge_count}개가 "
                "제거되었습니다."
            ),
            "concept": (
                "초기화하면 그래프는 정점과 간선이 없는 "
                "빈 상태가 됩니다."
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Session State에 저장할 수 있는 형태로 반환합니다.
        """

        return {
            "directed": self.directed,
            "adjacency": {
                vertex: neighbors.copy()
                for vertex, neighbors in self.adjacency.items()
            },
        }

    def load_dict(
        self,
        graph_data: dict[str, Any],
    ) -> None:
        """
        저장된 그래프 데이터를 복원합니다.
        """

        self.directed = bool(
            graph_data.get(
                "directed",
                False,
            )
        )

        adjacency_data = graph_data.get(
            "adjacency",
            {},
        )

        self.adjacency = {
            str(vertex): [
                str(neighbor)
                for neighbor in neighbors
            ]
            for vertex, neighbors in adjacency_data.items()
        }

    def load_example(
        self,
        nodes: list[str],
        edges: list[list[str]],
        directed: bool = False,
    ) -> None:
        """
        예제 정점과 간선으로 그래프를 구성합니다.
        """

        self.directed = directed
        self.adjacency = {}

        for node in nodes:
            normalized = self.normalize_vertex(node)

            if normalized:
                self.adjacency[normalized] = []

        for edge in edges:
            if len(edge) != 2:
                continue

            self.add_edge(
                edge[0],
                edge[1],
            )

    # ========================================================
    # 문자열 정리
    # ========================================================

    @staticmethod
    def normalize_vertex(vertex: str) -> str:
        """
        정점 이름을 공백 제거 및 대문자 형태로 정리합니다.
        """

        return str(vertex).strip().upper()