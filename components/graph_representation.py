"""
Graph의 인접 행렬과 인접 리스트를 생성하고 표시하는 모듈입니다.

주요 기능
- 인접 행렬 자동 생성
- 인접 리스트 자동 생성
- 무방향 그래프의 대칭성 확인
- 정점별 차수 표시
- 방향 그래프의 진입 차수와 진출 차수 표시
"""

from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from modules.common import render_html
from modules.graph_logic import Graph


# ============================================================
# 1. 인접 행렬 생성
# ============================================================

def create_adjacency_matrix(
    graph: Graph,
) -> pd.DataFrame:
    """
    현재 Graph를 인접 행렬 형태의 DataFrame으로 변환합니다.

    행:
        출발 정점

    열:
        도착 정점

    연결된 경우:
        1

    연결되지 않은 경우:
        0
    """

    vertices = graph.vertices()

    matrix_data = {
        destination: [
            (
                1
                if destination in graph.adjacency[source]
                else 0
            )
            for source in vertices
        ]
        for destination in vertices
    }

    return pd.DataFrame(
        matrix_data,
        index=vertices,
    )


# ============================================================
# 2. 인접 리스트 생성
# ============================================================

def create_adjacency_list(
    graph: Graph,
) -> dict[str, list[str]]:
    """
    현재 Graph의 인접 리스트 복사본을 반환합니다.
    """

    return {
        vertex: neighbors.copy()
        for vertex, neighbors in graph.adjacency.items()
    }


# ============================================================
# 3. 방향 그래프 차수 계산
# ============================================================

def calculate_indegree(
    graph: Graph,
    vertex: str,
) -> int:
    """
    방향 그래프에서 특정 정점의 진입 차수를 계산합니다.

    진입 차수:
        해당 정점으로 들어오는 간선의 수
    """

    indegree = 0

    for neighbors in graph.adjacency.values():
        if vertex in neighbors:
            indegree += 1

    return indegree


def calculate_outdegree(
    graph: Graph,
    vertex: str,
) -> int:
    """
    방향 그래프에서 특정 정점의 진출 차수를 계산합니다.

    진출 차수:
        해당 정점에서 나가는 간선의 수
    """

    return len(
        graph.adjacency.get(
            vertex,
            [],
        )
    )


# ============================================================
# 4. 행렬 대칭성 확인
# ============================================================

def is_symmetric_matrix(
    matrix: pd.DataFrame,
) -> bool:
    """
    인접 행렬이 대칭 행렬인지 확인합니다.
    """

    if matrix.empty:
        return True

    return matrix.equals(
        matrix.T
    )


# ============================================================
# 5. 인접 행렬 표시
# ============================================================

def render_adjacency_matrix(
    graph: Graph,
) -> None:
    """
    현재 Graph의 인접 행렬을 표시합니다.
    """

    if graph.is_empty():
        st.info(
            "인접 행렬을 만들려면 먼저 정점을 추가해 주세요."
        )
        return

    matrix_df = create_adjacency_matrix(
        graph
    )

    render_html(
        """
        <section class="concept-box">
            <div class="concept-title">
                인접 행렬
            </div>

            <div class="concept-text">
                두 정점이 간선으로 연결되어 있으면 1,
                연결되어 있지 않으면 0으로 표현합니다.
            </div>
        </section>
        """
    )

    graph_type_text = (
        "방향 그래프"
        if graph.directed
        else "무방향 그래프"
    )

    st.caption(
        f"현재 그래프 유형: {graph_type_text} · "
        "행은 출발 정점, 열은 도착 정점을 나타냅니다."
    )

    st.dataframe(
        matrix_df,
        width="stretch",
        height=min(
            100 + len(matrix_df) * 38,
            520,
        ),
        column_config={
            vertex: st.column_config.NumberColumn(
                vertex,
                width="small",
                format="%d",
            )
            for vertex in matrix_df.columns
        },
    )

    if graph.directed:
        render_html(
            """
            <div class="info-box">
                <strong>방향 그래프 확인</strong><br>
                행의 정점에서 열의 정점으로 이동할 수 있을 때
                해당 칸이 1이 됩니다.<br>
                따라서 행렬이 반드시 대칭일 필요는 없습니다.
            </div>
            """
        )

    elif is_symmetric_matrix(matrix_df):
        render_html(
            """
            <div class="success-box">
                <strong>대칭 행렬입니다.</strong><br>
                무방향 그래프에서는 A와 B가 연결되어 있으면
                B와 A도 연결되어 있으므로 인접 행렬이
                주대각선을 기준으로 대칭이 됩니다.
            </div>
            """
        )

    else:
        render_html(
            """
            <div class="warning-box">
                현재 무방향 그래프의 인접 행렬이
                대칭 형태가 아닙니다.<br>
                그래프의 간선 저장 상태를 확인해 주세요.
            </div>
            """
        )


# ============================================================
# 6. 인접 리스트 표시
# ============================================================

def render_adjacency_list(
    graph: Graph,
) -> None:
    """
    현재 Graph의 인접 리스트를 표시합니다.
    """

    if graph.is_empty():
        st.info(
            "인접 리스트를 만들려면 먼저 정점을 추가해 주세요."
        )
        return

    adjacency_list = create_adjacency_list(
        graph
    )

    render_html(
        """
        <section class="concept-box">
            <div class="concept-title">
                인접 리스트
            </div>

            <div class="concept-text">
                각 정점마다 직접 연결된 인접 정점만
                목록으로 저장합니다.
            </div>
        </section>
        """
    )

    list_blocks: list[str] = []

    for vertex, neighbors in adjacency_list.items():
        if neighbors:
            neighbor_nodes = []

            for index, neighbor in enumerate(neighbors):
                neighbor_nodes.append(
                    f"""
                    <span class="visit-node">
                        {escape(str(neighbor))}
                    </span>
                    """
                )

                if index < len(neighbors) - 1:
                    neighbor_nodes.append(
                        """
                        <span class="visit-arrow">
                            →
                        </span>
                        """
                    )

            neighbors_html = "".join(
                neighbor_nodes
            )

        else:
            neighbors_html = (
                '<span style="color: #8795a5;">'
                '연결된 정점 없음'
                '</span>'
            )

        list_blocks.append(
            f"""
            <div class="status-item">
                <span class="status-label">
                    {escape(str(vertex))}
                </span>

                <span class="status-value">
                    {neighbors_html}
                </span>
            </div>
            """
        )

    render_html(
        f"""
        <section class="status-panel">
            <div class="status-title">
                정점별 인접 정점
            </div>

            {''.join(list_blocks)}
        </section>
        """
    )


# ============================================================
# 7. 차수 정보 표시
# ============================================================

def render_degree_information(
    graph: Graph,
) -> None:
    """
    정점별 차수 정보를 표시합니다.

    무방향 그래프:
        정점의 차수

    방향 그래프:
        진입 차수와 진출 차수
    """

    if graph.is_empty():
        return

    vertices = graph.vertices()

    if graph.directed:
        degree_df = pd.DataFrame(
            {
                "정점": vertices,
                "진입 차수": [
                    calculate_indegree(
                        graph,
                        vertex,
                    )
                    for vertex in vertices
                ],
                "진출 차수": [
                    calculate_outdegree(
                        graph,
                        vertex,
                    )
                    for vertex in vertices
                ],
            }
        )

        title = "정점별 진입·진출 차수"

    else:
        degree_df = pd.DataFrame(
            {
                "정점": vertices,
                "차수": [
                    graph.degree(vertex)
                    for vertex in vertices
                ],
            }
        )

        title = "정점별 차수"

    st.markdown(
        f"#### {title}"
    )

    st.dataframe(
        degree_df,
        width="stretch",
        hide_index=True,
        column_config={
            "정점": st.column_config.TextColumn(
                "정점",
                width="medium",
            ),
        },
    )


# ============================================================
# 8. 표현 방식 전체 출력
# ============================================================

def render_graph_representations(
    graph: Graph,
) -> None:
    """
    인접 행렬과 인접 리스트를 하나의 학습 영역으로 표시합니다.
    """

    if graph.is_empty():
        st.info(
            "그래프를 구성하면 인접 행렬과 인접 리스트가 "
            "자동으로 생성됩니다."
        )
        return

    representation_mode = st.radio(
        "그래프 표현 방식",
        [
            "인접 행렬",
            "인접 리스트",
            "두 표현 함께 보기",
        ],
        horizontal=True,
        key="graph_representation_mode",
    )

    if representation_mode == "인접 행렬":
        render_adjacency_matrix(
            graph
        )

    elif representation_mode == "인접 리스트":
        render_adjacency_list(
            graph
        )

    else:
        matrix_col, list_col = st.columns(
            [1.15, 1]
        )

        with matrix_col:
            render_adjacency_matrix(
                graph
            )

        with list_col:
            render_adjacency_list(
                graph
            )

    st.divider()

    render_degree_information(
        graph
    )