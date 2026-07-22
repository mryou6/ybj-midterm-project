"""
Binary Search Tree 시각화 모듈입니다.

주요 기능
- SVG 기반 이진 탐색 트리 시각화
- 노드와 간선 표시
- 삽입 및 탐색 경로 강조
- 트리 상태 표시
- 순회 결과 표시
- Python 코드 표시
- 연산 기록 표시
"""

from __future__ import annotations

import base64
from html import escape
from typing import Any

import streamlit as st

from modules.bst_logic import BinarySearchTree, Node
from modules.common import render_html


# ============================================================
# 1. 트리 좌표 계산
# ============================================================

def calculate_tree_positions(
    root: Node | None,
    width: int = 900,
    level_height: int = 120,
    top_margin: int = 65,
) -> dict[int, tuple[float, float]]:
    """
    각 노드가 화면에 표시될 좌표를 계산합니다.

    중위 순회 순서에 따라 X좌표를 배치하고,
    노드의 깊이에 따라 Y좌표를 배치합니다.

    Args:
        root: 트리의 ROOT 노드
        width: SVG 전체 너비
        level_height: 트리 단계별 세로 간격
        top_margin: SVG 위쪽 여백

    Returns:
        {노드값: (x좌표, y좌표)} 형태의 딕셔너리
    """

    if root is None:
        return {}

    ordered_nodes: list[tuple[Node, int]] = []

    def collect_inorder(
        node: Node | None,
        depth: int,
    ) -> None:
        if node is None:
            return

        collect_inorder(
            node.left,
            depth + 1,
        )

        ordered_nodes.append(
            (node, depth)
        )

        collect_inorder(
            node.right,
            depth + 1,
        )

    collect_inorder(
        root,
        0,
    )

    node_count = len(ordered_nodes)

    horizontal_margin = 80
    usable_width = width - horizontal_margin * 2

    positions: dict[int, tuple[float, float]] = {}

    for index, (node, depth) in enumerate(ordered_nodes):

        if node_count == 1:
            x = width / 2

        else:
            x = (
                horizontal_margin
                + usable_width
                * index
                / (node_count - 1)
            )

        y = top_margin + depth * level_height

        positions[node.value] = (
            x,
            y,
        )

    return positions


# ============================================================
# 2. 탐색 경로 간선 판단
# ============================================================

def is_path_edge(
    parent_value: int,
    child_value: int,
    highlighted_path: list[int],
) -> bool:
    """
    부모와 자식 사이의 간선이 현재 탐색 경로에 포함되는지 확인합니다.
    """

    if len(highlighted_path) < 2:
        return False

    for index in range(
        len(highlighted_path) - 1
    ):
        if (
            highlighted_path[index] == parent_value
            and highlighted_path[index + 1] == child_value
        ):
            return True

    return False


# ============================================================
# 3. 간선 SVG 생성
# ============================================================

def build_edge_svg(
    parent: Node,
    child: Node,
    positions: dict[int, tuple[float, float]],
    highlighted_path: list[int],
) -> str:
    """
    부모 노드와 자식 노드를 연결하는 간선을 생성합니다.
    """

    parent_x, parent_y = positions[parent.value]
    child_x, child_y = positions[child.value]

    highlighted = is_path_edge(
        parent.value,
        child.value,
        highlighted_path,
    )

    stroke_color = (
        "#e58a27"
        if highlighted
        else "#9aa8b6"
    )

    stroke_width = (
        5
        if highlighted
        else 3
    )

    return f"""
    <line
        x1="{parent_x}"
        y1="{parent_y + 31}"
        x2="{child_x}"
        y2="{child_y - 31}"
        stroke="{stroke_color}"
        stroke-width="{stroke_width}"
        stroke-linecap="round"
    />
    """


# ============================================================
# 4. 노드 SVG 생성
# ============================================================

def build_node_svg(
    node: Node,
    positions: dict[int, tuple[float, float]],
    highlighted_path: list[int],
    found_value: int | None,
) -> str:
    """
    하나의 트리 노드를 원 모양의 SVG 요소로 생성합니다.
    """

    x, y = positions[node.value]

    fill_color = "#eef0ff"
    stroke_color = "#6874c7"
    text_color = "#353d83"
    stroke_width = 3

    # 탐색 또는 삽입 경로에 포함된 노드
    if node.value in highlighted_path:
        fill_color = "#fff1df"
        stroke_color = "#e58a27"
        text_color = "#8c4a0b"
        stroke_width = 5

    # 탐색에 성공한 노드
    if (
        found_value is not None
        and node.value == found_value
    ):
        fill_color = "#e8f8ef"
        stroke_color = "#2c9b63"
        text_color = "#216341"
        stroke_width = 5

    return f"""
    <g>
        <circle
            cx="{x}"
            cy="{y}"
            r="32"
            fill="{fill_color}"
            stroke="{stroke_color}"
            stroke-width="{stroke_width}"
        />

        <text
            x="{x}"
            y="{y + 7}"
            text-anchor="middle"
            font-family="Noto Sans KR, sans-serif"
            font-size="19"
            font-weight="800"
            fill="{text_color}"
        >
            {escape(str(node.value))}
        </text>
    </g>
    """


# ============================================================
# 5. SVG를 Base64 이미지로 변환
# ============================================================

def svg_to_data_uri(
    svg_text: str,
) -> str:
    """
    SVG 문자열을 브라우저에서 표시할 수 있는
    Base64 데이터 주소로 변환합니다.
    """

    encoded_svg = base64.b64encode(
        svg_text.encode("utf-8")
    ).decode("utf-8")

    return (
        "data:image/svg+xml;base64,"
        + encoded_svg
    )


# ============================================================
# 6. 트리 시각화
# ============================================================

def render_bst(
    tree: BinarySearchTree,
    highlighted_path: list[int] | None = None,
    found_value: int | None = None,
    target_value: int | None = None,
) -> None:
    """
    이진 탐색 트리를 SVG 이미지로 시각화합니다.

    Args:
        tree: 출력할 이진 탐색 트리
        highlighted_path: 삽입 또는 탐색 과정에서 방문한 노드
        found_value: 탐색에 성공한 노드
        target_value: 삽입 또는 탐색 대상 값
    """

    del target_value  # 현재 버전에서는 별도로 사용하지 않음

    highlighted_path = (
        highlighted_path or []
    )

    if tree.root is None:
        render_html(
            """
            <div class="tree-canvas">
                <div class="empty-state">
                    <div class="empty-state-icon">
                        🌱
                    </div>

                    트리가 비어 있습니다.<br>
                    숫자를 입력하고 삽입 버튼을 눌러 보세요.
                </div>
            </div>
            """
        )
        return

    node_count = tree.size()
    tree_height = tree.height()

    canvas_width = max(
        900,
        node_count * 125,
    )

    canvas_height = max(
        360,
        110 + tree_height * 125,
    )

    positions = calculate_tree_positions(
        tree.root,
        width=canvas_width,
        level_height=120,
        top_margin=65,
    )

    edge_elements: list[str] = []
    node_elements: list[str] = []

    def collect_elements(
        node: Node | None,
    ) -> None:
        if node is None:
            return

        if node.left is not None:
            edge_elements.append(
                build_edge_svg(
                    node,
                    node.left,
                    positions,
                    highlighted_path,
                )
            )

        if node.right is not None:
            edge_elements.append(
                build_edge_svg(
                    node,
                    node.right,
                    positions,
                    highlighted_path,
                )
            )

        collect_elements(
            node.left
        )

        collect_elements(
            node.right
        )

        node_elements.append(
            build_node_svg(
                node,
                positions,
                highlighted_path,
                found_value,
            )
        )

    collect_elements(
        tree.root
    )

    svg_text = f"""
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 {canvas_width} {canvas_height}"
        width="{canvas_width}"
        height="{canvas_height}"
    >
        <rect
            x="0"
            y="0"
            width="{canvas_width}"
            height="{canvas_height}"
            fill="#fafcfe"
        />

        {''.join(edge_elements)}

        {''.join(node_elements)}
    </svg>
    """

    image_uri = svg_to_data_uri(
        svg_text
    )

    path_description = ""

    if highlighted_path:
        path_text = " → ".join(
            str(value)
            for value in highlighted_path
        )

        path_description = f"""
        <div style="
            margin-bottom: 0.8rem;
            color: #5f7285;
            font-weight: 650;
        ">
            비교·이동 경로:
            <strong>
                {escape(path_text)}
            </strong>
        </div>
        """

    render_html(
        f"""
        {path_description}

        <div class="tree-canvas"
             style="
                 min-height: auto;
                 padding: 0.5rem;
                 overflow-x: auto;
             ">

            <img
                src="{image_uri}"
                alt="이진 탐색 트리 시각화"
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
# 7. 트리 상태 표시
# ============================================================

def render_bst_status(
    tree: BinarySearchTree,
) -> None:
    """
    이진 탐색 트리의 주요 상태를 표시합니다.
    """

    root_value = (
        tree.root.value
        if tree.root is not None
        else "없음"
    )

    minimum_value = tree.minimum()
    maximum_value = tree.maximum()

    minimum_text = (
        minimum_value
        if minimum_value is not None
        else "없음"
    )

    maximum_text = (
        maximum_value
        if maximum_value is not None
        else "없음"
    )

    render_html(
        f"""
        <section class="status-panel">
            <div class="status-title">
                현재 Binary Search Tree 상태
            </div>

            <div class="status-item">
                <span class="status-label">
                    노드 수
                </span>

                <span class="status-value">
                    {tree.size()}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    트리 높이
                </span>

                <span class="status-value">
                    {tree.height()}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    ROOT
                </span>

                <span class="status-value">
                    {root_value}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    가장 작은 값
                </span>

                <span class="status-value">
                    {minimum_text}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    가장 큰 값
                </span>

                <span class="status-value">
                    {maximum_text}
                </span>
            </div>
        </section>
        """
    )


# ============================================================
# 8. 연산 결과 메시지
# ============================================================

def render_operation_message(
    operation_result: dict[str, Any] | None,
) -> None:
    """
    가장 최근에 실행한 트리 연산 결과를 표시합니다.
    """

    if not operation_result:
        render_html(
            """
            <div class="info-box">
                아직 실행한 연산이 없습니다.<br>
                숫자를 입력한 뒤 삽입 또는 탐색을 실행해 보세요.
            </div>
            """
        )
        return

    success = bool(
        operation_result.get(
            "success",
            False,
        )
    )

    message = escape(
        str(
            operation_result.get(
                "message",
                "",
            )
        )
    )

    concept = escape(
        str(
            operation_result.get(
                "concept",
                "",
            )
        )
    )

    box_class = (
        "success-box"
        if success
        else "warning-box"
    )

    render_html(
        f"""
        <div class="{box_class}">
            <strong>
                {message}
            </strong>

            <br>

            {concept}
        </div>
        """
    )


# ============================================================
# 9. 순회 결과 표시
# ============================================================

def render_traversal_result(
    traversal_name: str,
    values: list[int],
) -> None:
    """
    전위·중위·후위 순회 결과를 표시합니다.
    """

    if not values:
        st.info(
            "트리가 비어 있어 순회할 수 없습니다."
        )
        return

    elements = []

    for index, value in enumerate(values):
        elements.append(
            f"""
            <span class="visit-node">
                {escape(str(value))}
            </span>
            """
        )

        if index < len(values) - 1:
            elements.append(
                """
                <span class="visit-arrow">
                    →
                </span>
                """
            )

    render_html(
        f"""
        <section class="step-panel">
            <div class="step-title">
                {escape(traversal_name)} 결과
            </div>

            <div class="visit-order">
                {''.join(elements)}
            </div>
        </section>
        """
    )


# ============================================================
# 10. Python 코드 표시
# ============================================================

def render_bst_code(
    active_operation: str | None = None,
) -> None:
    """
    이진 탐색 트리의 핵심 코드를 표시합니다.
    """

    operation_names = {
        "insert": "삽입",
        "search": "탐색",
        "preorder": "전위 순회",
        "inorder": "중위 순회",
        "postorder": "후위 순회",
        "clear": "초기화",
    }

    active_name = operation_names.get(
        active_operation,
        "연산 없음",
    )

    st.markdown(
        f"**현재 실행한 연산: `{active_name}`**"
    )

    code_text = """def insert(node, value):
    if node is None:
        return Node(value)

    if value < node.value:
        node.left = insert(node.left, value)
    elif value > node.value:
        node.right = insert(node.right, value)

    return node


def search(node, value):
    if node is None or node.value == value:
        return node

    if value < node.value:
        return search(node.left, value)

    return search(node.right, value)
"""

    st.code(
        code_text,
        language="python",
        line_numbers=True,
    )


# ============================================================
# 11. 연산 기록 표시
# ============================================================

def render_operation_history(
    history: list[dict[str, Any]],
) -> None:
    """
    최근 BST 연산 기록을 표시합니다.
    """

    if not history:
        st.info(
            "아직 저장된 연산 기록이 없습니다."
        )
        return

    history_elements = []

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

        history_elements.append(
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
                최근 연산 기록
            </div>

            {''.join(history_elements)}
        </section>
        """
    )