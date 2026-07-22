"""
Binary Search Tree 시각화 모듈입니다.

주요 기능
- SVG 기반 트리 시각화
- 노드와 간선 표시
- 탐색 및 삽입 경로 강조
- 현재 상태 표시
- 순회 결과 표시
- Python 코드 표시
- 연산 기록 표시
"""

from __future__ import annotations

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
    level_height: int = 110,
    top_margin: int = 55,
) -> dict[int, tuple[float, float]]:
    """
    각 노드의 SVG 좌표를 계산합니다.

    중위 순회 순서대로 X좌표를 배치하여
    부모·자식 노드가 겹치지 않도록 합니다.
    """

    if root is None:
        return {}

    ordered_nodes: list[tuple[Node, int]] = []

    def inorder_collect(
        node: Node | None,
        depth: int,
    ) -> None:
        if node is None:
            return

        inorder_collect(node.left, depth + 1)
        ordered_nodes.append((node, depth))
        inorder_collect(node.right, depth + 1)

    inorder_collect(root, 0)

    node_count = len(ordered_nodes)
    horizontal_margin = 65

    usable_width = width - (horizontal_margin * 2)

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

        positions[node.value] = (x, y)

    return positions


# ============================================================
# 2. SVG 요소 생성
# ============================================================

def build_edge_svg(
    parent: Node,
    child: Node,
    positions: dict[int, tuple[float, float]],
    highlighted_path: list[int],
) -> str:
    """
    부모와 자식 노드를 연결하는 선을 생성합니다.
    """

    parent_x, parent_y = positions[parent.value]
    child_x, child_y = positions[child.value]

    is_highlighted = False

    if parent.value in highlighted_path:
        parent_index = highlighted_path.index(parent.value)

        if parent_index + 1 < len(highlighted_path):
            is_highlighted = (
                highlighted_path[parent_index + 1]
                == child.value
            )

    stroke = "#e38a2d" if is_highlighted else "#9aa8b6"
    stroke_width = 5 if is_highlighted else 3

    return (
        f'<line x1="{parent_x}" y1="{parent_y + 28}" '
        f'x2="{child_x}" y2="{child_y - 28}" '
        f'stroke="{stroke}" '
        f'stroke-width="{stroke_width}" '
        f'stroke-linecap="round" />'
    )


def build_node_svg(
    node: Node,
    positions: dict[int, tuple[float, float]],
    highlighted_path: list[int],
    found_value: int | None,
    target_value: int | None,
) -> str:
    """
    하나의 트리 노드를 SVG로 생성합니다.
    """

    x, y = positions[node.value]

    fill = "#eef0ff"
    stroke = "#6a75c9"
    text_color = "#353d83"
    stroke_width = 3

    if node.value in highlighted_path:
        fill = "#fff1df"
        stroke = "#e58a27"
        text_color = "#8c4a0b"
        stroke_width = 5

    if (
        found_value is not None
        and node.value == found_value
    ):
        fill = "#e8f8ef"
        stroke = "#2c9b63"
        text_color = "#216341"
        stroke_width = 5

    elif (
        target_value is not None
        and node.value == target_value
        and node.value == highlighted_path[-1]
        if highlighted_path
        else False
    ):
        fill = "#fff1df"
        stroke = "#e58a27"

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
            font-size="19"
            font-weight="800"
            fill="{text_color}"
            font-family="Noto Sans KR, sans-serif"
        >
            {escape(str(node.value))}
        </text>
    </g>
    """


# ============================================================
# 3. 트리 시각화
# ============================================================

def render_bst(
    tree: BinarySearchTree,
    highlighted_path: list[int] | None = None,
    found_value: int | None = None,
    target_value: int | None = None,
) -> None:
    """
    이진 탐색 트리를 SVG로 표시합니다.

    Args:
        tree: 표시할 BinarySearchTree
        highlighted_path: 삽입 또는 탐색 과정의 방문 경로
        found_value: 탐색에 성공한 값
        target_value: 현재 삽입·탐색 대상 값
    """

    highlighted_path = highlighted_path or []

    if tree.root is None:
        render_html(
            """
            <div class="tree-canvas">
                <div class="empty-state">
                    <div class="empty-state-icon">🌱</div>
                    트리가 비어 있습니다.<br>
                    숫자를 입력하고 삽입 버튼을 눌러 보세요.
                </div>
            </div>
            """
        )
        return

    tree_height = tree.height()

    canvas_width = max(
        900,
        tree.size() * 115,
    )

    canvas_height = max(
        380,
        100 + tree_height * 115,
    )

    positions = calculate_tree_positions(
        tree.root,
        width=canvas_width,
        level_height=110,
        top_margin=55,
    )

    edge_elements: list[str] = []
    node_elements: list[str] = []

    def collect_elements(node: Node | None) -> None:
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

        collect_elements(node.left)
        collect_elements(node.right)

        node_elements.append(
            build_node_svg(
                node,
                positions,
                highlighted_path,
                found_value,
                target_value,
            )
        )

    collect_elements(tree.root)

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
            <strong>{escape(path_text)}</strong>
        </div>
        """

    render_html(
        f"""
        {path_description}

        <div class="tree-canvas">
            <svg
                viewBox="0 0 {canvas_width} {canvas_height}"
                width="100%"
                height="{canvas_height}"
                role="img"
                aria-label="이진 탐색 트리"
            >
                {''.join(edge_elements)}
                {''.join(node_elements)}
            </svg>
        </div>
        """
    )


# ============================================================
# 4. 트리 상태
# ============================================================

def render_bst_status(
    tree: BinarySearchTree,
) -> None:
    """
    이진 탐색 트리의 현재 상태를 표시합니다.
    """

    root_value = (
        tree.root.value
        if tree.root is not None
        else "없음"
    )

    minimum = (
        tree.minimum()
        if tree.minimum() is not None
        else "없음"
    )

    maximum = (
        tree.maximum()
        if tree.maximum() is not None
        else "없음"
    )

    render_html(
        f"""
        <section class="status-panel">
            <div class="status-title">
                현재 Binary Search Tree 상태
            </div>

            <div class="status-item">
                <span class="status-label">노드 수</span>
                <span class="status-value">{tree.size()}개</span>
            </div>

            <div class="status-item">
                <span class="status-label">트리 높이</span>
                <span class="status-value">{tree.height()}</span>
            </div>

            <div class="status-item">
                <span class="status-label">ROOT</span>
                <span class="status-value">{root_value}</span>
            </div>

            <div class="status-item">
                <span class="status-label">가장 작은 값</span>
                <span class="status-value">{minimum}</span>
            </div>

            <div class="status-item">
                <span class="status-label">가장 큰 값</span>
                <span class="status-value">{maximum}</span>
            </div>
        </section>
        """
    )


# ============================================================
# 5. 연산 메시지
# ============================================================

def render_operation_message(
    operation_result: dict[str, Any] | None,
) -> None:
    """
    가장 최근의 BST 연산 결과를 표시합니다.
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
            <strong>{message}</strong><br>
            {concept}
        </div>
        """
    )


# ============================================================
# 6. 순회 결과
# ============================================================

def render_traversal_result(
    traversal_name: str,
    values: list[int],
) -> None:
    """
    트리 순회 결과를 노드와 화살표로 표시합니다.
    """

    if not values:
        st.info(
            "트리가 비어 있어 순회할 수 없습니다."
        )
        return

    node_elements = []

    for index, value in enumerate(values):
        node_elements.append(
            f"""
            <span class="visit-node">
                {escape(str(value))}
            </span>
            """
        )

        if index < len(values) - 1:
            node_elements.append(
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
                {''.join(node_elements)}
            </div>
        </section>
        """
    )


# ============================================================
# 7. Python 코드
# ============================================================

def render_bst_code(
    active_operation: str | None = None,
) -> None:
    """
    BST의 핵심 Python 코드를 표시합니다.
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
# 8. 연산 기록
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