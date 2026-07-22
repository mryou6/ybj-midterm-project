"""
Graph 자료구조 체험 페이지입니다.

학습 흐름
1. Graph 개념 알아보기
2. 정점과 간선 구성하기
3. DFS·BFS 체험하기
4. 버튼으로 탐색 단계 확인하기
5. 다음 방문 정점 예측하기
6. 학습 확인하기
"""

import json
from html import escape

import streamlit as st

from components.graph_visualizer import (
    render_graph,
    render_graph_code,
    render_graph_status,
    render_operation_history,
    render_operation_message,
    render_traversal_step,
    render_visit_order,
)
from modules.common import (
    DATA_DIR,
    apply_common_style,
    initialize_session_state,
    render_concept_box,
    render_footer,
    render_html,
    render_message,
    render_page_header,
    render_section_title,
)
from modules.graph_logic import Graph


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="Graph 체험",
    page_icon="🕸️",
    layout="wide",
)

apply_common_style()


# ============================================================
# 2. 예제 그래프 읽기
# ============================================================

@st.cache_data
def load_example_graphs() -> dict:
    """
    data/example_graphs.json 파일을 읽습니다.
    """

    graph_file = (
        DATA_DIR
        / "example_graphs.json"
    )

    if not graph_file.exists():
        return {}

    try:
        return json.loads(
            graph_file.read_text(
                encoding="utf-8",
            )
        )

    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        return {}


example_graphs = load_example_graphs()


# ============================================================
# 3. Session State 초기화
# ============================================================

initialize_session_state(
    "graph_data",
    {
        "directed": False,
        "adjacency": {},
    },
)

initialize_session_state(
    "graph_last_result",
    None,
)

initialize_session_state(
    "graph_history",
    [],
)

initialize_session_state(
    "graph_algorithm",
    None,
)

initialize_session_state(
    "graph_traversal_order",
    [],
)

initialize_session_state(
    "graph_traversal_steps",
    [],
)

initialize_session_state(
    "graph_step_index",
    0,
)

initialize_session_state(
    "graph_start_vertex",
    None,
)

initialize_session_state(
    "graph_quiz_score",
    0,
)

initialize_session_state(
    "graph_quiz_submitted",
    False,
)

initialize_session_state(
    "graph_prediction_submitted",
    False,
)

initialize_session_state(
    "graph_prediction_answer",
    None,
)


# ============================================================
# 4. Graph 객체 복원
# ============================================================

graph = Graph()

graph.load_dict(
    st.session_state.graph_data
)


def save_graph_state() -> None:
    """
    Graph 객체를 Session State에 저장합니다.
    """

    st.session_state.graph_data = (
        graph.to_dict()
    )


def reset_traversal() -> None:
    """
    그래프 구조가 변경되면 기존 탐색 결과를 초기화합니다.
    """

    st.session_state.graph_algorithm = None
    st.session_state.graph_traversal_order = []
    st.session_state.graph_traversal_steps = []
    st.session_state.graph_step_index = 0
    st.session_state.graph_start_vertex = None
    st.session_state.graph_prediction_submitted = False
    st.session_state.graph_prediction_answer = None

    if "graph_prediction_radio" in st.session_state:
        del st.session_state["graph_prediction_radio"]


def reset_prediction() -> None:
    """
    탐색 단계가 변경되면 이전 예측 결과를 초기화합니다.
    """

    st.session_state.graph_prediction_submitted = False
    st.session_state.graph_prediction_answer = None

    if "graph_prediction_radio" in st.session_state:
        del st.session_state["graph_prediction_radio"]


def record_operation(
    result: dict,
    changes_graph: bool = False,
) -> None:
    """
    그래프 연산 결과를 기록합니다.
    """

    st.session_state.graph_last_result = result
    st.session_state.graph_history.append(result)

    save_graph_state()

    if changes_graph:
        reset_traversal()


def move_to_step(
    target_step: int,
) -> None:
    """
    탐색 단계를 지정한 번호로 이동합니다.
    """

    steps = st.session_state.graph_traversal_steps

    if not steps:
        return

    last_index = len(steps) - 1

    st.session_state.graph_step_index = max(
        0,
        min(
            target_step,
            last_index,
        ),
    )

    reset_prediction()


# ============================================================
# 5. 페이지 상단
# ============================================================

render_page_header(
    title="Graph 체험하기",
    description=(
        "정점과 간선을 연결하고 DFS와 BFS를 실행하며 "
        "그래프 탐색 과정을 직접 관찰해 보세요."
    ),
    icon="🕸️",
)


# ============================================================
# 6. Graph 개념 설명
# ============================================================

render_section_title(
    "1. Graph는 무엇인가요?"
)

render_concept_box(
    title="지하철 노선도나 친구 관계를 떠올려 보세요.",
    text=(
        "그래프는 여러 대상과 그 대상 사이의 연결 관계를 "
        "표현하는 자료구조입니다. 각각의 대상을 정점이라고 하고, "
        "정점을 연결하는 선을 간선이라고 합니다."
    ),
)

concept_col1, concept_col2, concept_col3 = st.columns(3)

with concept_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                🔵
            </div>

            <div class="structure-card-title">
                정점 Vertex
            </div>

            <div class="structure-card-description">
                사람, 장소, 컴퓨터 등 하나의 대상을 나타냅니다.
            </div>

            <span class="structure-card-keyword">
                대상
            </span>
        </article>
        """
    )

with concept_col2:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                ➖
            </div>

            <div class="structure-card-title">
                간선 Edge
            </div>

            <div class="structure-card-description">
                두 정점 사이의 연결 관계를 나타냅니다.
            </div>

            <span class="structure-card-keyword">
                연결
            </span>
        </article>
        """
    )

with concept_col3:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                🧭
            </div>

            <div class="structure-card-title">
                그래프 탐색
            </div>

            <div class="structure-card-description">
                DFS와 BFS를 이용해 연결된 정점을 방문합니다.
            </div>

            <span class="structure-card-keyword">
                방문 순서
            </span>
        </article>
        """
    )

render_message(
    (
        "<strong>DFS</strong>는 Stack을 활용해 깊이 탐색하고, "
        "<strong>BFS</strong>는 Queue를 활용해 "
        "가까운 정점부터 탐색합니다."
    ),
    message_type="info",
    allow_html=True,
)


# ============================================================
# 7. 그래프 구성
# ============================================================

render_section_title(
    "2. 그래프 구성하기"
)

control_col, visual_col = st.columns(
    [1, 1.9]
)

with control_col:
    st.subheader(
        "정점과 간선 추가"
    )

    directed_option = st.radio(
        "그래프 유형",
        [
            "무방향 그래프",
            "방향 그래프",
        ],
        index=(
            1
            if graph.directed
            else 0
        ),
        horizontal=True,
        key="graph_type_radio",
    )

    selected_directed = (
        directed_option
        == "방향 그래프"
    )

    if selected_directed != graph.directed:
        graph.directed = selected_directed
        graph.adjacency = {}

        result = {
            "success": True,
            "action": "change_type",
            "value": selected_directed,
            "message": (
                f"{directed_option}로 변경했습니다."
            ),
            "concept": (
                "그래프 유형을 변경하면 "
                "기존 연결 관계를 초기화합니다."
            ),
        }

        record_operation(
            result,
            changes_graph=True,
        )

        st.rerun()

    vertex_names = st.text_input(
        "추가할 정점 이름",
        placeholder="예: A, B, C, D",
        help=(
            "여러 정점은 쉼표로 구분하세요. "
            "입력값의 앞뒤 공백은 자동으로 제거됩니다."
        ),
        max_chars=100,
        key="graph_vertex_names",
    )

    if st.button(
        "🔵 정점 추가",
        use_container_width=True,
        type="primary",
    ):
        result = graph.add_vertices(
            vertex_names
        )

        record_operation(
            result,
            changes_graph=result["success"],
        )

        st.rerun()

    vertices = graph.vertices()

    if len(vertices) >= 2:
        edge_col1, edge_col2 = st.columns(2)

        with edge_col1:
            edge_start = st.selectbox(
                "시작 정점",
                vertices,
                key="graph_edge_start",
            )

        with edge_col2:
            available_end_indices = list(
                range(len(vertices))
            )

            default_end_index = (
                1
                if len(vertices) > 1
                else 0
            )

            edge_end = st.selectbox(
                "도착 정점",
                vertices,
                index=default_end_index,
                key="graph_edge_end",
            )

        if st.button(
            "➖ 간선 추가",
            use_container_width=True,
        ):
            result = graph.add_edge(
                edge_start,
                edge_end,
            )

            record_operation(
                result,
                changes_graph=result["success"],
            )

            st.rerun()

    else:
        st.caption(
            "간선을 추가하려면 정점을 2개 이상 만들어 주세요."
        )

    if example_graphs:
        st.markdown(
            "#### 예제 그래프"
        )

        example_name = st.selectbox(
            "불러올 예제",
            list(example_graphs.keys()),
            key="graph_example_name",
        )

        selected_example = (
            example_graphs[example_name]
        )

        st.caption(
            selected_example.get(
                "description",
                "",
            )
        )

        if st.button(
            "📂 예제 그래프 불러오기",
            use_container_width=True,
        ):
            graph.load_example(
                nodes=selected_example.get(
                    "nodes",
                    [],
                ),
                edges=selected_example.get(
                    "edges",
                    [],
                ),
                directed=selected_example.get(
                    "directed",
                    False,
                ),
            )

            result = {
                "success": True,
                "action": "load_example",
                "value": example_name,
                "message": (
                    f"'{example_name}'을(를) 불러왔습니다."
                ),
                "concept": (
                    "시작 정점을 선택하고 "
                    "DFS와 BFS의 방문 순서를 비교해 보세요."
                ),
            }

            record_operation(
                result,
                changes_graph=True,
            )

            st.rerun()

    if st.button(
        "🔄 그래프 초기화",
        use_container_width=True,
    ):
        result = graph.clear()

        record_operation(
            result,
            changes_graph=True,
        )

        st.session_state.graph_quiz_submitted = False

        st.rerun()

    render_operation_message(
        st.session_state.graph_last_result
    )


with visual_col:
    st.subheader(
        "Graph 시각화"
    )

    current_step = None

    if st.session_state.graph_traversal_steps:
        current_index = min(
            st.session_state.graph_step_index,
            len(
                st.session_state.graph_traversal_steps
            ) - 1,
        )

        current_step = (
            st.session_state.graph_traversal_steps[
                current_index
            ]
        )

    render_graph(
        graph,
        visited=(
            current_step.get(
                "visited",
                [],
            )
            if current_step
            else []
        ),
        current=(
            current_step.get(
                "current"
            )
            if current_step
            else None
        ),
        start_vertex=(
            st.session_state.graph_start_vertex
        ),
    )


# ============================================================
# 8. 그래프 상태와 코드
# ============================================================

status_col1, status_col2 = st.columns(2)

with status_col1:
    render_graph_status(
        graph
    )

with status_col2:
    render_graph_code(
        st.session_state.graph_algorithm
    )


# ============================================================
# 9. DFS·BFS 실행
# ============================================================

render_section_title(
    "3. DFS와 BFS 체험하기"
)

if graph.is_empty():
    st.info(
        "탐색을 실행하려면 먼저 그래프를 구성해 주세요."
    )

else:
    start_vertex = st.selectbox(
        "탐색 시작 정점",
        graph.vertices(),
        key="graph_search_start",
    )

    search_col1, search_col2 = st.columns(2)

    with search_col1:
        dfs_clicked = st.button(
            "🔍 DFS 실행",
            use_container_width=True,
            type="primary",
        )

    with search_col2:
        bfs_clicked = st.button(
            "🌊 BFS 실행",
            use_container_width=True,
        )

    if dfs_clicked:
        result = graph.dfs(
            start_vertex
        )

        st.session_state.graph_algorithm = "DFS"
        st.session_state.graph_traversal_order = (
            result.get(
                "order",
                [],
            )
        )
        st.session_state.graph_traversal_steps = (
            result.get(
                "steps",
                [],
            )
        )
        st.session_state.graph_step_index = 0
        st.session_state.graph_start_vertex = (
            start_vertex
        )
        st.session_state.graph_last_result = result
        st.session_state.graph_history.append(
            result
        )

        reset_prediction()

        st.rerun()

    if bfs_clicked:
        result = graph.bfs(
            start_vertex
        )

        st.session_state.graph_algorithm = "BFS"
        st.session_state.graph_traversal_order = (
            result.get(
                "order",
                [],
            )
        )
        st.session_state.graph_traversal_steps = (
            result.get(
                "steps",
                [],
            )
        )
        st.session_state.graph_step_index = 0
        st.session_state.graph_start_vertex = (
            start_vertex
        )
        st.session_state.graph_last_result = result
        st.session_state.graph_history.append(
            result
        )

        reset_prediction()

        st.rerun()


# ============================================================
# 10. 버튼으로 탐색 단계 이동
# ============================================================

steps = st.session_state.graph_traversal_steps

if steps:
    current_index = min(
        st.session_state.graph_step_index,
        len(steps) - 1,
    )

    last_index = len(steps) - 1

    render_html(
        f"""
        <section class="status-panel">
            <div class="status-title">
                {escape(str(st.session_state.graph_algorithm))}
                탐색 단계 조작
            </div>

            <div class="status-item">
                <span class="status-label">
                    현재 단계
                </span>

                <span class="status-value">
                    {current_index} / {last_index}
                </span>
            </div>
        </section>
        """
    )

    step_col1, step_col2, step_col3, step_col4 = (
        st.columns(4)
    )

    with step_col1:
        first_clicked = st.button(
            "⏮ 처음",
            use_container_width=True,
            disabled=current_index == 0,
        )

    with step_col2:
        previous_clicked = st.button(
            "◀ 이전",
            use_container_width=True,
            disabled=current_index == 0,
        )

    with step_col3:
        next_clicked = st.button(
            "다음 ▶",
            use_container_width=True,
            type=(
                "primary"
                if current_index < last_index
                else "secondary"
            ),
            disabled=current_index >= last_index,
        )

    with step_col4:
        last_clicked = st.button(
            "마지막 ⏭",
            use_container_width=True,
            disabled=current_index >= last_index,
        )

    if first_clicked:
        move_to_step(0)
        st.rerun()

    if previous_clicked:
        move_to_step(
            current_index - 1
        )
        st.rerun()

    if next_clicked:
        move_to_step(
            current_index + 1
        )
        st.rerun()

    if last_clicked:
        move_to_step(
            last_index
        )
        st.rerun()

    current_step = steps[
        st.session_state.graph_step_index
    ]

    render_traversal_step(
        st.session_state.graph_algorithm,
        current_step,
        len(steps),
    )

    render_visit_order(
        st.session_state.graph_algorithm,
        st.session_state.graph_traversal_order,
    )


# ============================================================
# 11. 다음 방문 정점 예측
# ============================================================

render_section_title(
    "4. 다음 방문 정점 예측하기"
)

steps = st.session_state.graph_traversal_steps

if len(steps) < 2:
    st.info(
        "DFS 또는 BFS를 실행한 뒤 탐색 과정을 예측해 보세요."
    )

else:
    current_index = min(
        st.session_state.graph_step_index,
        len(steps) - 1,
    )

    if current_index >= len(steps) - 1:
        render_message(
            (
                "현재 마지막 단계입니다. "
                "이전 버튼을 눌러 중간 단계로 이동한 뒤 "
                "다음 정점을 예측해 보세요."
            ),
            message_type="info",
        )

    else:
        next_step = steps[
            current_index + 1
        ]

        render_html(
            f"""
            <section class="quiz-box">
                <div class="quiz-title">
                    현재 단계 다음에는 어떤 정점을 방문할까요?
                </div>

                <div class="quiz-question">
                    현재
                    {escape(str(st.session_state.graph_algorithm))}의
                    Stack 또는 Queue 상태를 살펴보고
                    다음 방문 정점을 예측해 보세요.
                </div>
            </section>
            """
        )

        prediction = st.radio(
            "다음 방문 정점",
            graph.vertices(),
            index=None,
            key="graph_prediction_radio",
        )

        if st.button(
            "예측 결과 확인",
            key="check_graph_prediction",
        ):
            st.session_state.graph_prediction_submitted = True
            st.session_state.graph_prediction_answer = (
                prediction
            )

        if st.session_state.graph_prediction_submitted:
            correct_answer = next_step.get(
                "current"
            )

            selected_answer = (
                st.session_state.graph_prediction_answer
            )

            if selected_answer is None:
                st.warning(
                    "답을 선택한 뒤 결과를 확인해 주세요."
                )

            elif selected_answer == correct_answer:
                render_html(
                    f"""
                    <div class="quiz-result-correct">
                        정답입니다!<br>
                        다음에 방문할 정점은
                        <strong>
                            {escape(str(correct_answer))}
                        </strong>입니다.
                    </div>
                    """
                )

            else:
                render_html(
                    f"""
                    <div class="quiz-result-wrong">
                        다시 생각해 보세요.<br>
                        다음에 방문할 정점은
                        <strong>
                            {escape(str(correct_answer))}
                        </strong>입니다.
                    </div>
                    """
                )


# ============================================================
# 12. 학습 확인
# ============================================================

render_section_title(
    "5. 학습 확인하기"
)

with st.form(
    "graph_quiz_form"
):
    question1 = st.radio(
        "1. 그래프에서 하나의 대상을 나타내는 요소는?",
        [
            "정점",
            "간선",
            "배열",
        ],
        index=None,
    )

    question2 = st.radio(
        "2. 두 정점 사이의 연결 관계를 나타내는 요소는?",
        [
            "정점",
            "간선",
            "ROOT",
        ],
        index=None,
    )

    question3 = st.radio(
        "3. DFS에서 주로 사용하는 자료구조는?",
        [
            "Stack",
            "Queue",
            "Heap",
        ],
        index=None,
    )

    question4 = st.radio(
        "4. BFS에서 주로 사용하는 자료구조는?",
        [
            "Stack",
            "Queue",
            "Tree",
        ],
        index=None,
    )

    quiz_submitted = st.form_submit_button(
        "학습 결과 확인"
    )

if quiz_submitted:
    score = 0

    if question1 == "정점":
        score += 1

    if question2 == "간선":
        score += 1

    if question3 == "Stack":
        score += 1

    if question4 == "Queue":
        score += 1

    st.session_state.graph_quiz_score = score
    st.session_state.graph_quiz_submitted = True

if st.session_state.graph_quiz_submitted:
    score = st.session_state.graph_quiz_score

    if score == 4:
        render_html(
            """
            <div class="quiz-result-correct">
                4문제를 모두 맞혔습니다!<br>
                Graph와 DFS·BFS의 기본 원리를 잘 이해했습니다.
            </div>
            """
        )

    elif score >= 2:
        render_html(
            f"""
            <div class="warning-box">
                4문제 중 {score}문제를 맞혔습니다.<br>
                정점·간선과 DFS·BFS의 차이를
                한 번 더 확인해 보세요.
            </div>
            """
        )

    else:
        render_html(
            f"""
            <div class="quiz-result-wrong">
                4문제 중 {score}문제를 맞혔습니다.<br>
                예제 그래프를 불러와 DFS와 BFS를
                다시 실행해 보세요.
            </div>
            """
        )


# ============================================================
# 13. 연산 기록
# ============================================================

with st.expander(
    "내가 실행한 Graph 연산 기록 보기",
    expanded=False,
):
    render_operation_history(
        st.session_state.graph_history
    )

    if st.session_state.graph_history:
        if st.button(
            "연산 기록 삭제",
            key="clear_graph_history",
        ):
            st.session_state.graph_history = []
            st.rerun()


# ============================================================
# 14. 페이지 하단
# ============================================================

render_footer()