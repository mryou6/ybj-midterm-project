"""
Data Structure Playground 메인 페이지입니다.

주요 기능
- 웹 애플리케이션 소개
- 자료구조별 체험 페이지 안내
- Stack, Queue, Binary Search Tree, Graph 페이지 이동
"""

import streamlit as st

from modules.common import (
    apply_common_style,
    render_concept_box,
    render_footer,
    render_html,
    render_page_header,
    render_section_title,
)


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="자료구조 놀이터",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_common_style()


# ============================================================
# 2. 페이지 이동 함수
# ============================================================

def move_to_page(page_path: str) -> None:
    """
    지정한 자료구조 페이지로 이동합니다.

    Args:
        page_path: streamlit_app.py를 기준으로 한 페이지 파일 경로
    """

    st.switch_page(page_path)


# ============================================================
# 3. 메인 소개
# ============================================================

render_page_header(
    title="자료구조 놀이터",
    description=(
        "Stack, Queue, Binary Search Tree, Graph를 직접 조작하고 "
        "시각적으로 체험하는 자료구조 학습 웹앱입니다."
    ),
    icon="🧩",
)

render_section_title(
    "누구나 쉽게 체험하는 자료구조"
)

render_concept_box(
    title="코드를 몰라도 괜찮습니다!",
    text=(
        "값을 직접 넣고 꺼내거나 탐색하면서 자료구조가 작동하는 "
        "과정을 시각적으로 확인해 보세요. 아래에서 체험하고 싶은 "
        "자료구조를 선택하면 해당 학습 페이지로 이동합니다."
    ),
)


# ============================================================
# 4. 자료구조 선택 카드
# ============================================================

render_section_title(
    "체험할 자료구조를 선택해 보세요"
)

first_row_col1, first_row_col2 = st.columns(2)

with first_row_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🥞</div>

            <div class="structure-card-title">
                Stack
            </div>

            <div class="structure-card-description">
                접시를 쌓는 것처럼 마지막에 들어온 데이터가
                가장 먼저 나오는 LIFO 구조를 체험합니다.
            </div>

            <span class="structure-card-keyword">
                Push · Pop · Peek
            </span>
        </article>
        """
    )

    if st.button(
        "🥞 Stack 체험하러 가기",
        key="go_to_stack",
        use_container_width=True,
        type="primary",
    ):
        move_to_page(
            "pages/1_Stack.py"
        )

with first_row_col2:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🚶</div>

            <div class="structure-card-title">
                Queue
            </div>

            <div class="structure-card-description">
                대기줄처럼 먼저 들어온 데이터가
                가장 먼저 나오는 FIFO 구조를 체험합니다.
            </div>

            <span class="structure-card-keyword">
                Enqueue · Dequeue
            </span>
        </article>
        """
    )

    if st.button(
        "🚶 Queue 체험하러 가기",
        key="go_to_queue",
        use_container_width=True,
    ):
        move_to_page(
            "pages/2_Queue.py"
        )


second_row_col1, second_row_col2 = st.columns(2)

with second_row_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🌳</div>

            <div class="structure-card-title">
                Binary Search Tree
            </div>

            <div class="structure-card-description">
                숫자의 크기를 비교하여 작은 값은 왼쪽,
                큰 값은 오른쪽에 배치하는 트리를 체험합니다.
            </div>

            <span class="structure-card-keyword">
                삽입 · 탐색 · 순회
            </span>
        </article>
        """
    )

    if st.button(
        "🌳 Binary Search Tree 체험하러 가기",
        key="go_to_bst",
        use_container_width=True,
    ):
        move_to_page(
            "pages/3_Binary_Search_Tree.py"
        )

with second_row_col2:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🕸️</div>

            <div class="structure-card-title">
                Graph
            </div>

            <div class="structure-card-description">
                정점과 간선을 직접 연결하고 DFS와 BFS의
                탐색 과정을 단계별로 체험합니다.
            </div>

            <span class="structure-card-keyword">
                Vertex · Edge · DFS · BFS
            </span>
        </article>
        """
    )

    if st.button(
        "🕸️ Graph 체험하러 가기",
        key="go_to_graph",
        use_container_width=True,
    ):
        move_to_page(
            "pages/4_Graph.py"
        )


# ============================================================
# 5. 추천 학습 순서
# ============================================================

render_section_title(
    "추천 학습 순서"
)

render_html(
    """
    <section class="step-panel">
        <div class="step-title">
            처음 자료구조를 학습한다면 다음 순서로 체험해 보세요.
        </div>

        <div class="visit-order">
            <span class="visit-node">1. Stack</span>
            <span class="visit-arrow">→</span>

            <span class="visit-node">2. Queue</span>
            <span class="visit-arrow">→</span>

            <span class="visit-node">3. Binary Search Tree</span>
            <span class="visit-arrow">→</span>

            <span class="visit-node">4. Graph</span>
        </div>
    </section>
    """
)


# ============================================================
# 6. 페이지 하단
# ============================================================

render_footer()