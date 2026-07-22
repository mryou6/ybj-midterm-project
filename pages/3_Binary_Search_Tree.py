"""
Binary Search Tree 체험 페이지입니다.

학습 흐름
1. 이진 탐색 트리 개념 알아보기
2. 숫자 삽입 및 탐색 체험하기
3. 트리 순회 체험하기
4. 삽입 위치 예측하기
5. 학습 확인하기
"""

from html import escape

import streamlit as st

from components.bst_visualizer import (
    render_bst,
    render_bst_code,
    render_bst_status,
    render_operation_history,
    render_operation_message,
    render_traversal_result,
)
from modules.bst_logic import BinarySearchTree
from modules.common import (
    apply_common_style,
    initialize_session_state,
    render_concept_box,
    render_footer,
    render_html,
    render_message,
    render_page_header,
    render_section_title,
)


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="Binary Search Tree 체험",
    page_icon="🌳",
    layout="wide",
)

apply_common_style()


# ============================================================
# 2. Session State 초기화
# ============================================================

initialize_session_state(
    "bst_values",
    [],
)

initialize_session_state(
    "bst_last_result",
    None,
)

initialize_session_state(
    "bst_history",
    [],
)

initialize_session_state(
    "bst_highlighted_path",
    [],
)

initialize_session_state(
    "bst_found_value",
    None,
)

initialize_session_state(
    "bst_target_value",
    None,
)

initialize_session_state(
    "bst_traversal_name",
    None,
)

initialize_session_state(
    "bst_traversal_values",
    [],
)

initialize_session_state(
    "bst_quiz_score",
    0,
)

initialize_session_state(
    "bst_quiz_submitted",
    False,
)

initialize_session_state(
    "bst_prediction_submitted",
    False,
)

initialize_session_state(
    "bst_prediction_answer",
    None,
)


# ============================================================
# 3. 트리 복원
# ============================================================

tree = BinarySearchTree()

tree.load_values(
    st.session_state.bst_values
)


def save_tree_state() -> None:
    """
    현재 트리 값을 Session State에 저장합니다.
    """

    st.session_state.bst_values = tree.to_list()


def reset_visual_feedback() -> None:
    """
    이전 탐색·순회 강조 상태를 초기화합니다.
    """

    st.session_state.bst_highlighted_path = []
    st.session_state.bst_found_value = None
    st.session_state.bst_target_value = None
    st.session_state.bst_traversal_name = None
    st.session_state.bst_traversal_values = []


def reset_prediction() -> None:
    """
    트리 상태가 변경되면 예측 결과를 초기화합니다.
    """

    st.session_state.bst_prediction_submitted = False
    st.session_state.bst_prediction_answer = None

    if "bst_prediction_radio" in st.session_state:
        del st.session_state["bst_prediction_radio"]


def record_operation(
    result: dict,
    changes_tree: bool = False,
) -> None:
    """
    BST 연산 결과를 저장합니다.
    """

    st.session_state.bst_last_result = result
    st.session_state.bst_history.append(result)

    st.session_state.bst_highlighted_path = (
        result.get(
            "path",
            [],
        )
    )

    st.session_state.bst_target_value = (
        result.get(
            "value",
        )
    )

    if (
        result.get("action") == "search"
        and result.get("success")
    ):
        st.session_state.bst_found_value = (
            result.get("value")
        )
    else:
        st.session_state.bst_found_value = None

    save_tree_state()

    if changes_tree:
        reset_prediction()


# ============================================================
# 4. 페이지 상단
# ============================================================

render_page_header(
    title="Binary Search Tree 체험하기",
    description=(
        "숫자의 크기를 비교하여 왼쪽과 오른쪽으로 이동하며 "
        "노드를 삽입하고 탐색해 보세요."
    ),
    icon="🌳",
)


# ============================================================
# 5. 개념 설명
# ============================================================

render_section_title(
    "1. Binary Search Tree는 무엇인가요?"
)

render_concept_box(
    title="숫자에 따라 갈림길을 선택하는 모습을 떠올려 보세요.",
    text=(
        "이진 탐색 트리에서는 현재 노드보다 작은 값은 왼쪽에, "
        "큰 값은 오른쪽에 저장합니다. 탐색할 때도 같은 규칙으로 "
        "이동하기 때문에 필요한 방향의 노드만 확인할 수 있습니다."
    ),
)

concept_col1, concept_col2, concept_col3 = st.columns(3)

with concept_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">⬅️</div>

            <div class="structure-card-title">
                작은 값
            </div>

            <div class="structure-card-description">
                현재 노드보다 작은 값은 왼쪽 자식 방향으로 이동합니다.
            </div>

            <span class="structure-card-keyword">
                LEFT
            </span>
        </article>
        """
    )

with concept_col2:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🌱</div>

            <div class="structure-card-title">
                ROOT
            </div>

            <div class="structure-card-description">
                트리에서 가장 처음 삽입된 값은 ROOT 노드가 됩니다.
            </div>

            <span class="structure-card-keyword">
                시작 노드
            </span>
        </article>
        """
    )

with concept_col3:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">➡️</div>

            <div class="structure-card-title">
                큰 값
            </div>

            <div class="structure-card-description">
                현재 노드보다 큰 값은 오른쪽 자식 방향으로 이동합니다.
            </div>

            <span class="structure-card-keyword">
                RIGHT
            </span>
        </article>
        """
    )

render_message(
    (
        "예를 들어 ROOT가 <strong>50</strong>일 때, "
        "<strong>30</strong>은 왼쪽으로, "
        "<strong>70</strong>은 오른쪽으로 이동합니다."
    ),
    message_type="info",
    allow_html=True,
)


# ============================================================
# 6. 삽입 및 탐색
# ============================================================

render_section_title(
    "2. 트리 직접 체험하기"
)

control_col, visual_col = st.columns(
    [1, 1.9]
)

with control_col:
    st.subheader(
        "트리 조작"
    )

    input_value = st.number_input(
        "삽입하거나 탐색할 정수",
        min_value=-999,
        max_value=999,
        value=50,
        step=1,
        key="bst_input_value",
    )

    button_col1, button_col2 = st.columns(2)

    with button_col1:
        insert_clicked = st.button(
            "🌱 숫자 삽입",
            use_container_width=True,
            type="primary",
        )

    with button_col2:
        search_clicked = st.button(
            "🔍 숫자 탐색",
            use_container_width=True,
        )

    sample_clicked = st.button(
        "🌳 예제 트리 만들기",
        use_container_width=True,
    )

    clear_clicked = st.button(
        "🔄 트리 초기화",
        use_container_width=True,
    )

    if insert_clicked:
        reset_visual_feedback()

        result = tree.insert(
            int(input_value)
        )

        record_operation(
            result,
            changes_tree=result["success"],
        )

        st.rerun()

    if search_clicked:
        reset_visual_feedback()

        result = tree.search(
            int(input_value)
        )

        record_operation(
            result,
            changes_tree=False,
        )

        st.rerun()

    if sample_clicked:
        example_values = [
            50,
            30,
            70,
            20,
            40,
            60,
            80,
        ]

        tree.clear()

        for value in example_values:
            tree.insert(value)

        result = {
            "success": True,
            "action": "insert",
            "value": None,
            "path": [],
            "message": (
                "50, 30, 70, 20, 40, 60, 80으로 "
                "예제 트리를 만들었습니다."
            ),
            "concept": (
                "각 값이 ROOT보다 작은지 또는 큰지에 따라 "
                "왼쪽과 오른쪽으로 배치됩니다."
            ),
        }

        record_operation(
            result,
            changes_tree=True,
        )

        reset_visual_feedback()

        st.rerun()

    if clear_clicked:
        result = tree.clear()

        record_operation(
            result,
            changes_tree=True,
        )

        reset_visual_feedback()

        st.session_state.bst_quiz_submitted = False

        st.rerun()

    render_operation_message(
        st.session_state.bst_last_result
    )


with visual_col:
    st.subheader(
        "Binary Search Tree 시각화"
    )

    render_bst(
        tree,
        highlighted_path=(
            st.session_state.bst_highlighted_path
        ),
        found_value=(
            st.session_state.bst_found_value
        ),
        target_value=(
            st.session_state.bst_target_value
        ),
    )


# ============================================================
# 7. 현재 상태와 코드
# ============================================================

status_col1, status_col2 = st.columns(2)

with status_col1:
    render_bst_status(
        tree
    )

with status_col2:
    active_operation = None

    if st.session_state.bst_last_result:
        active_operation = (
            st.session_state.bst_last_result.get(
                "action"
            )
        )

    render_bst_code(
        active_operation
    )


# ============================================================
# 8. 트리 순회
# ============================================================

render_section_title(
    "3. 트리 순회 체험하기"
)

render_concept_box(
    title="순회란 무엇인가요?",
    text=(
        "순회는 트리의 모든 노드를 정해진 순서에 따라 "
        "한 번씩 방문하는 과정입니다. ROOT를 언제 방문하는지에 따라 "
        "전위·중위·후위 순회로 구분됩니다."
    ),
)

traversal_col1, traversal_col2, traversal_col3 = st.columns(3)

with traversal_col1:
    preorder_clicked = st.button(
        "전위 순회\nROOT → LEFT → RIGHT",
        use_container_width=True,
    )

with traversal_col2:
    inorder_clicked = st.button(
        "중위 순회\nLEFT → ROOT → RIGHT",
        use_container_width=True,
    )

with traversal_col3:
    postorder_clicked = st.button(
        "후위 순회\nLEFT → RIGHT → ROOT",
        use_container_width=True,
    )

if preorder_clicked:
    values = tree.preorder()

    st.session_state.bst_traversal_name = "전위 순회"
    st.session_state.bst_traversal_values = values

    st.session_state.bst_last_result = {
        "success": bool(values),
        "action": "preorder",
        "value": None,
        "path": values,
        "message": "전위 순회를 실행했습니다.",
        "concept": "ROOT를 가장 먼저 방문합니다.",
    }

if inorder_clicked:
    values = tree.inorder()

    st.session_state.bst_traversal_name = "중위 순회"
    st.session_state.bst_traversal_values = values

    st.session_state.bst_last_result = {
        "success": bool(values),
        "action": "inorder",
        "value": None,
        "path": values,
        "message": "중위 순회를 실행했습니다.",
        "concept": (
            "이진 탐색 트리를 중위 순회하면 "
            "값이 오름차순으로 출력됩니다."
        ),
    }

if postorder_clicked:
    values = tree.postorder()

    st.session_state.bst_traversal_name = "후위 순회"
    st.session_state.bst_traversal_values = values

    st.session_state.bst_last_result = {
        "success": bool(values),
        "action": "postorder",
        "value": None,
        "path": values,
        "message": "후위 순회를 실행했습니다.",
        "concept": "ROOT를 가장 마지막에 방문합니다.",
    }

if st.session_state.bst_traversal_name:
    render_traversal_result(
        st.session_state.bst_traversal_name,
        st.session_state.bst_traversal_values,
    )


# ============================================================
# 9. 결과 예측
# ============================================================

render_section_title(
    "4. 삽입 위치 예측하기"
)

render_html(
    """
    <section class="quiz-box">
        <div class="quiz-title">
            새로운 값은 ROOT의 어느 방향으로 이동할까요?
        </div>

        <div class="quiz-question">
            현재 ROOT와 아래의 값을 비교하여,
            첫 번째 이동 방향을 예측해 보세요.
        </div>
    </section>
    """
)

if tree.root is None:
    st.info(
        "예측 활동을 하려면 먼저 트리에 값을 삽입해 주세요."
    )

else:
    prediction_value = st.number_input(
        "예측할 새로운 정수",
        min_value=-999,
        max_value=999,
        value=25,
        step=1,
        key="bst_prediction_value",
    )

    prediction = st.radio(
        "ROOT에서의 첫 이동 방향",
        [
            "왼쪽",
            "오른쪽",
            "이동하지 않음",
        ],
        index=None,
        key="bst_prediction_radio",
    )

    if st.button(
        "예측 결과 확인",
        key="check_bst_prediction",
    ):
        st.session_state.bst_prediction_submitted = True
        st.session_state.bst_prediction_answer = prediction

    if st.session_state.bst_prediction_submitted:
        root_value = tree.root.value

        if prediction_value < root_value:
            correct_answer = "왼쪽"
        elif prediction_value > root_value:
            correct_answer = "오른쪽"
        else:
            correct_answer = "이동하지 않음"

        selected_answer = (
            st.session_state.bst_prediction_answer
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
                    {escape(str(prediction_value))}과(와)
                    ROOT {escape(str(root_value))}을(를) 비교하면
                    첫 이동 방향은
                    <strong>{correct_answer}</strong>입니다.
                </div>
                """
            )

        else:
            render_html(
                f"""
                <div class="quiz-result-wrong">
                    다시 생각해 보세요.<br>
                    새로운 값이 ROOT보다 작으면 왼쪽,
                    크면 오른쪽으로 이동합니다.
                    정답은
                    <strong>{correct_answer}</strong>입니다.
                </div>
                """
            )


# ============================================================
# 10. 학습 확인
# ============================================================

render_section_title(
    "5. 학습 확인하기"
)

with st.form(
    "bst_quiz_form"
):
    question1 = st.radio(
        "1. 현재 노드보다 작은 값은 어느 방향에 저장되나요?",
        [
            "왼쪽",
            "오른쪽",
            "아무 위치",
        ],
        index=None,
    )

    question2 = st.radio(
        "2. 현재 노드보다 큰 값은 어느 방향에 저장되나요?",
        [
            "왼쪽",
            "오른쪽",
            "ROOT 위쪽",
        ],
        index=None,
    )

    question3 = st.radio(
        "3. 중위 순회의 방문 순서로 알맞은 것은?",
        [
            "ROOT → LEFT → RIGHT",
            "LEFT → ROOT → RIGHT",
            "LEFT → RIGHT → ROOT",
        ],
        index=None,
    )

    question4 = st.radio(
        "4. 이진 탐색 트리를 중위 순회한 결과의 특징은?",
        [
            "값이 오름차순으로 출력된다.",
            "ROOT만 출력된다.",
            "값이 무작위로 출력된다.",
        ],
        index=None,
    )

    quiz_submitted = st.form_submit_button(
        "학습 결과 확인"
    )

if quiz_submitted:
    score = 0

    if question1 == "왼쪽":
        score += 1

    if question2 == "오른쪽":
        score += 1

    if question3 == "LEFT → ROOT → RIGHT":
        score += 1

    if question4 == "값이 오름차순으로 출력된다.":
        score += 1

    st.session_state.bst_quiz_score = score
    st.session_state.bst_quiz_submitted = True

if st.session_state.bst_quiz_submitted:
    score = st.session_state.bst_quiz_score

    if score == 4:
        render_html(
            """
            <div class="quiz-result-correct">
                4문제를 모두 맞혔습니다!<br>
                이진 탐색 트리의 기본 원리를 잘 이해했습니다.
            </div>
            """
        )

    elif score >= 2:
        render_html(
            f"""
            <div class="warning-box">
                4문제 중 {score}문제를 맞혔습니다.<br>
                왼쪽·오른쪽 배치 규칙과 순회 순서를
                한 번 더 확인해 보세요.
            </div>
            """
        )

    else:
        render_html(
            f"""
            <div class="quiz-result-wrong">
                4문제 중 {score}문제를 맞혔습니다.<br>
                예제 트리를 직접 만들고 탐색하면서
                값의 이동 방향을 다시 확인해 보세요.
            </div>
            """
        )


# ============================================================
# 11. 연산 기록
# ============================================================

with st.expander(
    "내가 실행한 Tree 연산 기록 보기",
    expanded=False,
):
    render_operation_history(
        st.session_state.bst_history
    )

    if st.session_state.bst_history:
        if st.button(
            "연산 기록 삭제",
            key="clear_bst_history",
        ):
            st.session_state.bst_history = []
            st.rerun()


# ============================================================
# 12. 페이지 하단
# ============================================================

render_footer()