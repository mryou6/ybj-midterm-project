"""
Data Structure Playground 메인 페이지입니다.

주요 기능
- 웹 애플리케이션 소개
- 자료구조별 체험 페이지 안내
- Stack, Queue, Binary Search Tree, Graph 페이지 이동
- 자료구조 종합 형성평가 페이지 이동
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

def move_to_page(
    page_path: str,
) -> None:
    """
    지정한 자료구조 페이지로 이동합니다.

    Args:
        page_path:
            streamlit_app.py를 기준으로 한 페이지 파일 경로
    """

    st.switch_page(
        page_path
    )


# ============================================================
# 3. 메인 소개
# ============================================================

render_page_header(
    title="자료구조 놀이터",
    description=(
        "Stack, Queue, Binary Search Tree, Graph를 직접 조작하고 "
        "시각적으로 체험한 뒤 종합 형성평가로 학습 내용을 "
        "확인하는 자료구조 학습 웹앱입니다."
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
        "과정을 시각적으로 확인해 보세요. 각 자료구조의 개념과 "
        "동작을 체험한 뒤 종합 형성평가를 통해 자신의 학습 상태도 "
        "점검할 수 있습니다."
    ),
)


# ============================================================
# 4. 자료구조 선택 카드
# ============================================================

render_section_title(
    "체험할 자료구조를 선택해 보세요"
)


# ------------------------------------------------------------
# 4-1. Stack / Queue
# ------------------------------------------------------------

first_row_col1, first_row_col2 = st.columns(
    2
)

with first_row_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                🥞
            </div>

            <div class="structure-card-title">
                Stack
            </div>

            <div class="structure-card-description">
                접시를 쌓는 것처럼 마지막에 들어온 데이터가
                가장 먼저 나오는 LIFO 구조를 체험합니다.
                괄호 검사와 후위 표기법 계산도 확인할 수 있습니다.
            </div>

            <span class="structure-card-keyword">
                Push · Pop · Peek · LIFO
            </span>
        </article>
        """
    )

    if st.button(
        "🥞 Stack 체험하러 가기",
        key="go_to_stack",
        use_container_width=True,
    ):
        move_to_page(
            "pages/1_Stack.py"
        )

with first_row_col2:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                🚶
            </div>

            <div class="structure-card-title">
                Queue
            </div>

            <div class="structure-card-description">
                대기줄처럼 먼저 들어온 데이터가
                가장 먼저 나오는 FIFO 구조를 체험합니다.
                선형 Queue와 원형 Queue의 차이도 확인할 수 있습니다.
            </div>

            <span class="structure-card-keyword">
                Enqueue · Dequeue · FIFO
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


# ------------------------------------------------------------
# 4-2. Binary Search Tree / Graph
# ------------------------------------------------------------

second_row_col1, second_row_col2 = st.columns(
    2
)

with second_row_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                🌳
            </div>

            <div class="structure-card-title">
                Binary Search Tree
            </div>

            <div class="structure-card-description">
                숫자의 크기를 비교하여 작은 값은 왼쪽,
                큰 값은 오른쪽에 배치하는 트리를 체험합니다.
                일반 이진 트리와 순회 방법도 학습할 수 있습니다.
            </div>

            <span class="structure-card-keyword">
                삽입 · 탐색 · 전위 · 중위 · 후위
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
            <div class="structure-card-icon">
                🕸️
            </div>

            <div class="structure-card-title">
                Graph
            </div>

            <div class="structure-card-description">
                정점과 간선을 직접 연결하고 DFS와 BFS의
                탐색 과정을 단계별로 체험합니다.
                인접 행렬과 인접 리스트도 비교할 수 있습니다.
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
# 5. 종합 형성평가
# ============================================================

render_section_title(
    "학습 내용을 확인해 보세요"
)

assessment_left_space, assessment_col, assessment_right_space = (
    st.columns(
        [0.35, 1.3, 0.35]
    )
)

with assessment_col:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                📝
            </div>

            <div class="structure-card-title">
                자료구조 종합 형성평가
            </div>

            <div class="structure-card-description">
                Stack, Queue, Tree, Graph에서 무작위로 출제되는
                12문항을 풀고 전체 점수와 영역별 학습 상태를
                확인합니다. 오답 개념 분석과 다시 풀기도 지원합니다.
            </div>

            <span class="structure-card-keyword">
                12문항 · 영역별 분석 · 오답 다시 풀기
            </span>
        </article>
        """
    )

    if st.button(
        "📝 종합 형성평가 시작하기",
        key="go_to_formative_assessment",
        use_container_width=True,
        type="primary",
    ):
        move_to_page(
            "pages/5_Formative_Assessment.py"
        )


# ============================================================
# 6. 추천 학습 순서
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
            <span class="visit-node">
                1. Stack
            </span>

            <span class="visit-arrow">
                →
            </span>

            <span class="visit-node">
                2. Queue
            </span>

            <span class="visit-arrow">
                →
            </span>

            <span class="visit-node">
                3. Binary Search Tree
            </span>

            <span class="visit-arrow">
                →
            </span>

            <span class="visit-node">
                4. Graph
            </span>

            <span class="visit-arrow">
                →
            </span>

            <span class="visit-node">
                5. 종합 형성평가
            </span>
        </div>
    </section>
    """
)


# ============================================================
# 7. 학습 방법 안내
# ============================================================

render_section_title(
    "자료구조 놀이터 활용 방법"
)

guide_col1, guide_col2, guide_col3 = st.columns(
    3
)

with guide_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                👀
            </div>

            <div class="structure-card-title">
                개념 확인
            </div>

            <div class="structure-card-description">
                각 자료구조의 특징과 핵심 용어를 먼저 확인합니다.
            </div>

            <span class="structure-card-keyword">
                개념 이해
            </span>
        </article>
        """
    )

with guide_col2:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                🖱️
            </div>

            <div class="structure-card-title">
                직접 체험
            </div>

            <div class="structure-card-description">
                값을 삽입하고 삭제하며 자료구조의 변화를 관찰합니다.
            </div>

            <span class="structure-card-keyword">
                조작 · 예측
            </span>
        </article>
        """
    )

with guide_col3:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                ✅
            </div>

            <div class="structure-card-title">
                학습 점검
            </div>

            <div class="structure-card-description">
                종합 형성평가를 통해 이해한 내용과 보완할 개념을 확인합니다.
            </div>

            <span class="structure-card-keyword">
                평가 · 피드백
            </span>
        </article>
        """
    )

render_section_title(
    "교사용 메뉴"
)

if st.button(
    "📊 형성평가 결과 대시보드",
    key="go_to_assessment_dashboard",
    use_container_width=True,
):
    move_to_page(
        "pages/6_Assessment_Dashboard.py"
    )

# ============================================================
# 8. 페이지 하단
# ============================================================

render_footer()