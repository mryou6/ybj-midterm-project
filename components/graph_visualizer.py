"""
Graph 자료구조 시각화 모듈입니다.

주요 기능
- SVG 기반 그래프 시각화
- 방향·무방향 간선 표시
- 현재 정점과 방문 정점 강조
- DFS Stack 및 BFS Queue 상태 표시
- 방문 순서 표시
- 코드 및 연산 기록 표시
"""

from __future__ import annotations

import base64
import math
from html import escape
from typing import Any

import streamlit as st

from modules.common import render_html
from modules.graph_logic import Graph


# ============================================================
# 1. 정점 좌표
# ============================================================

def calculate_graph_positions(
    vertices: list[str],
    width: int = 850,
    height: int = 500,
) -> dict[str, tuple[float, float]]:
    """
    정점을 원형으로 배치할 좌표를 계산합니다.
    """

    if not vertices:
        return {}

    center_x = width / 2
    center_y = height / 2

    radius = min(
        width,
        height,
    ) * 0.34

    positions: dict[str, tuple[float, float]] = {}

    if len(vertices) == 1:
        positions[vertices[0]] = (
            center_x,
            center_y,
        )

        return positions

    for index, vertex in enumerate(vertices):
        angle = (
            -math.pi / 2
            + 2 * math.pi * index / len(vertices)
        )

        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)

        positions[vertex] = (
            x,
            y,
        )

    return positions


# ============================================================
# 2. SVG Base64 변환
# ============================================================

def svg_to_data_uri(svg_text: str) -> str:
    encoded_svg = base64.b64encode(
        svg_text.encode("utf-8")
    ).decode("utf-8")

    return (
        "data:image/svg+xml;base64,"
        + encoded_svg
    )


# ============================================================
# 3. 간선 생성
# ============================================================

def build_edge_svg(
    start: str,
    end: str,
    positions: dict[str, tuple[float, float]],
    directed: bool,
    highlighted: bool,
) -> str:
    """
    두 정점을 연결하는 SVG 간선을 생성합니다.
    """

    start_x, start_y = positions[start]
    end_x, end_y = positions[end]

    dx = end_x - start_x
    dy = end_y - start_y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    if distance == 0:
        return ""

    node_radius = 31

    unit_x = dx / distance
    unit_y = dy / distance

    x1 = start_x + unit_x * node_radius
    y1 = start_y + unit_y * node_radius

    x2 = end_x - unit_x * node_radius
    y2 = end_y - unit_y * node_radius

    stroke = (
        "#e58a27"
        if highlighted
        else "#99a7b5"
    )

    stroke_width = (
        5
        if highlighted
        else 3
    )

    marker = (
        'marker-end="url(#arrowhead)"'
        if directed
        else ""
    )

    return f"""
    <line
        x1="{x1}"
        y1="{y1}"
        x2="{x2}"
        y2="{y2}"
        stroke="{stroke}"
        stroke-width="{stroke_width}"
        stroke-linecap="round"
        {marker}
    />
    """


# ============================================================
# 4. 노드 생성
# ============================================================

def build_node_svg(
    vertex: str,
    positions: dict[str, tuple[float, float]],
    visited: list[str],
    current: str | None,
    start_vertex: str | None,
) -> str:
    """
    그래프 정점을 원 모양으로 생성합니다.
    """

    x, y = positions[vertex]

    fill = "#eaf4fd"
    stroke = "#3478b8"
    text_color = "#23577f"
    stroke_width = 3

    if vertex == start_vertex:
        fill = "#fff1df"
        stroke = "#e08224"
        text_color = "#88460b"
        stroke_width = 5

    if vertex in visited:
        fill = "#e8f8ef"
        stroke = "#2c9a63"
        text_color = "#216240"
        stroke_width = 4

    if vertex == current:
        fill = "#f6eafd"
        stroke = "#ad56c7"
        text_color = "#6c2e7e"
        stroke_width = 6

    return f"""
    <g>
        <circle
            cx="{x}"
            cy="{y}"
            r="31"
            fill="{fill}"
            stroke="{stroke}"
            stroke-width="{stroke_width}"
        />

        <text
            x="{x}"
            y="{y + 7}"
            text-anchor="middle"
            font-family="Noto Sans KR, sans-serif"
            font-size="20"
            font-weight="800"
            fill="{text_color}"
        >
            {escape(vertex)}
        </text>
    </g>
    """


# ============================================================
# 5. 그래프 시각화
# ============================================================

def render_graph(
    graph: Graph,
    visited: list[str] | None = None,
    current: str | None = None,
    start_vertex: str | None = None,
) -> None:
    """
    현재 그래프를 SVG 이미지로 표시합니다.
    """

    visited = visited or []

    vertices = graph.vertices()

    if not vertices:
        render_html(
            """
            <div class="graph-canvas">
                <div class="empty-state">
                    <div class="empty-state-icon">🕸️</div>
                    그래프가 비어 있습니다.<br>
                    정점과 간선을 추가하거나 예제 그래프를 불러오세요.
                </div>
            </div>
            """
        )
        return

    canvas_width = max(
        850,
        len(vertices) * 110,
    )

    canvas_height = 520

    positions = calculate_graph_positions(
        vertices,
        width=canvas_width,
        height=canvas_height,
    )

    edge_elements = []

    for start, end in graph.edges():
        highlighted = (
            start in visited
            and end in visited
        )

        edge_elements.append(
            build_edge_svg(
                start,
                end,
                positions,
                graph.directed,
                highlighted,
            )
        )

    node_elements = [
        build_node_svg(
            vertex,
            positions,
            visited,
            current,
            start_vertex,
        )
        for vertex in vertices
    ]

    arrow_definition = ""

    if graph.directed:
        arrow_definition = """
        <defs>
            <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
            >
                <polygon
                    points="0 0, 10 3.5, 0 7"
                    fill="#7f8d9a"
                />
            </marker>
        </defs>
        """

    svg_text = f"""
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 {canvas_width} {canvas_height}"
        width="{canvas_width}"
        height="{canvas_height}"
    >
        <rect
            width="{canvas_width}"
            height="{canvas_height}"
            fill="#fafcfe"
        />

        {arrow_definition}
        {''.join(edge_elements)}
        {''.join(node_elements)}
    </svg>
    """

    image_uri = svg_to_data_uri(
        svg_text
    )

    render_html(
        f"""
        <div class="graph-canvas"
             style="
                 min-height: auto;
                 padding: 0.5rem;
                 overflow-x: auto;
             ">
            <img
                src="{image_uri}"
                alt="그래프 시각화"
                style="
                    display: block;
                    width: 100%;
                    min-width: 650px;
                    height: auto;
                    margin: 0 auto;
                "
            >
        </div>
        """
    )


# ============================================================
# 6. 그래프 상태
# ============================================================

def render_graph_status(
    graph: Graph,
) -> None:
    """
    그래프의 주요 상태를 표시합니다.
    """

    graph_type = (
        "방향 그래프"
        if graph.directed
        else "무방향 그래프"
    )

    vertex_text = (
        ", ".join(graph.vertices())
        if graph.vertices()
        else "없음"
    )

    render_html(
        f"""
        <section class="status-panel">
            <div class="status-title">
                현재 Graph 상태
            </div>

            <div class="status-item">
                <span class="status-label">그래프 유형</span>
                <span class="status-value">{graph_type}</span>
            </div>

            <div class="status-item">
                <span class="status-label">정점 수</span>
                <span class="status-value">
                    {graph.vertex_count()}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">간선 수</span>
                <span class="status-value">
                    {graph.edge_count()}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">정점 목록</span>
                <span class="status-value">
                    {escape(vertex_text)}
                </span>
            </div>
        </section>
        """
    )


# ============================================================
# 7. 탐색 단계
# ============================================================

def render_traversal_step(
    algorithm: str,
    step_data: dict[str, Any],
    total_steps: int,
) -> None:
    """
    DFS 또는 BFS의 현재 탐색 단계를 표시합니다.
    """

    container_name = (
        "Stack"
        if algorithm == "DFS"
        else "Queue"
    )

    current = (
        step_data.get("current")
        or "아직 방문 전"
    )

    visited = step_data.get(
        "visited",
        [],
    )

    container = step_data.get(
        "container",
        [],
    )

    visited_text = (
        " → ".join(visited)
        if visited
        else "없음"
    )

    container_text = (
        ", ".join(container)
        if container
        else "비어 있음"
    )

    description = escape(
        str(
            step_data.get(
                "description",
                "",
            )
        )
    )

    render_html(
        f"""
        <section class="step-panel">
            <div class="step-title">
                {algorithm} 탐색 단계
                {step_data.get("step", 0)} / {total_steps - 1}
            </div>

            <div class="status-item">
                <span class="status-label">현재 정점</span>
                <span class="status-value">
                    {escape(str(current))}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">방문 완료</span>
                <span class="status-value">
                    {escape(visited_text)}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    현재 {container_name}
                </span>
                <span class="status-value">
                    [{escape(container_text)}]
                </span>
            </div>

            <div class="info-box">
                {description}
            </div>
        </section>
        """
    )


# ============================================================
# 8. 방문 순서
# ============================================================

def render_visit_order(
    algorithm: str,
    order: list[str],
) -> None:
    """
    전체 방문 순서를 표시합니다.
    """

    if not order:
        return

    elements = []

    for index, vertex in enumerate(order):
        elements.append(
            f"""
            <span class="visit-node">
                {escape(vertex)}
            </span>
            """
        )

        if index < len(order) - 1:
            elements.append(
                """
                <span class="visit-arrow">→</span>
                """
            )

    render_html(
        f"""
        <section class="step-panel">
            <div class="step-title">
                {algorithm} 전체 방문 순서
            </div>

            <div class="visit-order">
                {''.join(elements)}
            </div>
        </section>
        """
    )


# ============================================================
# 9. 연산 메시지
# ============================================================

def render_operation_message(
    result: dict[str, Any] | None,
) -> None:
    """
    가장 최근 연산 결과를 표시합니다.
    """

    if not result:
        render_html(
            """
            <div class="info-box">
                아직 실행한 연산이 없습니다.<br>
                그래프에 정점과 간선을 추가해 보세요.
            </div>
            """
        )
        return

    box_class = (
        "success-box"
        if result.get("success")
        else "warning-box"
    )

    message = escape(
        str(result.get("message", ""))
    )

    concept = escape(
        str(result.get("concept", ""))
    )

    render_html(
        f"""
        <div class="{box_class}">
            <strong>{message}</strong><br>
            {concept}
        </div>
        """
    )


# ============================================================
# 10. Python 코드
# ============================================================

def render_graph_code(
    active_algorithm: str | None = None,
) -> None:
    """
    DFS와 BFS의 핵심 Python 코드를 표시합니다.
    """

    active_name = (
        active_algorithm
        if active_algorithm
        else "연산 없음"
    )

    st.markdown(
        f"**현재 실행한 탐색: `{active_name}`**"
    )

    code_text = """def dfs(graph, start):
    visited = []
    stack = [start]

    while stack:
        current = stack.pop()

        if current not in visited:
            visited.append(current)

            for neighbor in reversed(graph[current]):
                stack.append(neighbor)

    return visited


def bfs(graph, start):
    visited = []
    queue = [start]

    while queue:
        current = queue.pop(0)

        if current not in visited:
            visited.append(current)

            for neighbor in graph[current]:
                queue.append(neighbor)

    return visited
"""

    st.code(
        code_text,
        language="python",
        line_numbers=True,
    )


# ============================================================
# 11. 연산 기록
# ============================================================

def render_operation_history(
    history: list[dict[str, Any]],
) -> None:
    """
    최근 Graph 연산 기록을 표시합니다.
    """

    if not history:
        st.info(
            "아직 저장된 연산 기록이 없습니다."
        )
        return

    elements = []

    for number, item in enumerate(
        reversed(history[-10:]),
        start=1,
    ):
        action = escape(
            str(
                item.get(
                    "action",
                    "-",
                )
            ).upper()
        )

        message = escape(
            str(
                item.get(
                    "message",
                    "",
                )
            )
        )

        elements.append(
            f"""
            <div class="step-item">
                {number}. [{action}] {message}
            </div>
            """
        )

    render_html(
        f"""
        <section class="step-panel">
            <div class="step-title">
                최근 Graph 연산 기록
            </div>

            {''.join(elements)}
        </section>
        """
    )