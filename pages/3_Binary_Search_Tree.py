"""
Binary Search Tree 체험 페이지입니다.

학습 흐름
1. BST 개념 알아보기
2. 숫자 삽입 및 탐색
3. 트리 순회
4. 삽입 방향 예측
5. 학습 확인
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

initialize_session_state("bst_values", [])
initialize_session_state("bst_last_result", None)
initialize_session_state("bst_history", [])
initialize_session_state("bst_highlighted_path", [])
initialize_session_state("bst_found_value", None)
initialize_session_state("bst_target_value", None)
initialize_session_state("bst_traversal_name", None)
initialize_session_state("bst_traversal_values", [])
initialize_session_state("bst_quiz_score", 0)
initialize_session_state("bst_quiz_submitted", False)
initialize_session_state("bst_prediction_submitted", False)
initialize_session_state("bst_prediction_answer", None)


# ============================================================
# 3. 트리 복원
# ============================================================

tree = BinarySearchTree()

tree.load_values(
    st.session_state.bst_values
)


# ============================================================
# 4. 공통 함수
# ============================================================

def parse_bst_values(
    input_text: str,
) -> tuple[list[int], list[str]]:
    """
    쉼표로 구분된 문자열을 정수 목록으로 변환합니다.

    Returns:
        정상 숫자 목록, 잘못 입력된 값 목록
    """

    parsed_values: list[int] = []
    invalid_values: list[str] = []

    for raw_value in input_text.split(","):
        cleaned_value = raw_value.strip()

        if not cleaned_value:
            continue

        try:
            integer_value = int(cleaned_value)

            if integer_value not in parsed_values:
                parsed_values.append(integer_value)

        except ValueError:
            invalid_values.append(cleaned_value)

    return parsed_values, invalid_values


def save_tree_state() -> None:
    st.session_state.bst_values = tree.to_list()


def reset_visual_feedback() -> None:
    st.session_state.bst_highlighted_path = []
    st.session_state.bst_found_value = None
    st.session_state.bst_target_value = None
    st.session_state.bst_traversal_name = None
    st.session_state.bst_traversal_values = []


def reset_prediction() -> None:
    st.session_state.bst_prediction_submitted = False
    st.session_state.bst_prediction_answer = None

    if "bst_prediction_radio" in st.session_state:
        del st.session_state["bst_prediction_radio"]


def record_operation(
    result: dict,
    changes_tree: bool = False,
) -> None:
    st.session_state.bst_last_result = result
    st.session_state.bst_history.append(result)

    st.session_state.bst_highlighted_path = result.get(
        "path",
        [],
    )

    st.session_state.bst_target_value = result.get(
        "value"
    )

    if (
        result.get("action") == "search"
        and result.get("success")
    ):
        st.session_state.bst_found_value = result.get(
            "value"
        )
    else:
        st.session_state.bst_found_value = None

    save_tree_state()

    if changes_tree:
        reset_prediction()


# ============================================================
# 5. 페이지 상단
# ============================================================

render_page_header(
    title="Binary Search Tree 체험하기",
    description=(
        "여러 숫자를 입력 순서대로 삽입하고, "
        "크기를 비교하며 트리가 만들어지는 과정을 확인해 보세요."
    ),
    icon="🌳",
)


# ============================================================
# 6. 개념 설명
# ============================================================

render_section_title(
    "1. Binary Search Tree는 무엇인가요?"
)

render_concept_box(
    title="숫자에 따라 갈림길을 선택하는 모습을 떠올려 보세요.",
    text=(
        "현재 노드보다 작은 값은 왼쪽에, 큰 값은 오른쪽에 "
        "저장합니다. 숫자를 자동으로 정렬한 뒤 배치하는 것이 아니라 "
        "입력한 순서대로 하나씩 비교하여 위치를 결정합니다."
    ),
)

concept_col1, concept_col2, concept_col3 = st.columns(3)

with concept_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">⬅️</div>
            <div class="structure-card-title">작은 값</div>
            <div class="structure-card-description">
                현재 노드보다 작은 값은 왼쪽 자식 방향으로 이동합니다.
            </div>
            <span class="structure-card-keyword">LEFT</span>
        </article>
        """
    )

with concept_col2:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🌱</div>
            <div class="structure-card-title">ROOT</div>
            <div class="structure-card-description">
                가장 처음 삽입한 값이 트리의 ROOT가 됩니다.
            </div>
            <span class="structure-card-keyword">시작 노드</span>
        </article>
        """
    )

with concept_col3:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">➡️</div>
            <div class="structure-card-title">큰 값</div>
            <div class="structure-card-description">
                현재 노드보다 큰 값은 오른쪽 자식 방향으로 이동합니다.
            </div>
            <span class="structure-card-keyword">RIGHT</span>
        </article>
        """
    )

render_message(
    (
        "예: <strong>50, 30, 70</strong>을 입력하면 "
        "50이 ROOT, 30은 왼쪽, 70은 오른쪽에 배치됩니다."
    ),
    message_type="info",
    allow_html=True,
)


# ============================================================
# 7. 트리 직접 체험
# ============================================================

render_section_title(
    "2. 트리 직접 체험하기"
)

control_col, visual_col = st.columns(
    [1, 1.9]
)

with control_col:
    st.subheader("트리 조작")

    insert_text = st.text_input(
        "삽입할 정수",
        placeholder="예: 50 또는 50, 30, 70, 20",
        help=(
            "여러 숫자는 쉼표로 구분하세요. "
            "숫자는 입력한 순서대로 삽입됩니다."
        ),
        max_chars=200,
        key="bst_insert_text",
    )

    parsed_values, invalid_values = parse_bst_values(
        insert_text
    )

    if parsed_values:
        preview_text = " → ".join(
            str(value)
            for value in parsed_values
        )

        root_preview = (
            tree.root.value
            if tree.root is not None
            else parsed_values[0]
        )

        render_html(
            f"""
            <div class="info-box">
                <strong>삽입 순서</strong><br>
                {escape(preview_text)}<br><br>

                현재 트리가 비어 있다면
                <strong>{root_preview}</strong>이(가)
                ROOT가 됩니다.
            </div>
            """
        )

    if invalid_values:
        invalid_text = ", ".join(
            escape(value)
            for value in invalid_values
        )

        render_message(
            f"정수가 아닌 입력이 포함되어 있습니다: {invalid_text}",
            message_type="warning",
        )

    insert_clicked = st.button(
        "🌱 숫자 삽입",
        use_container_width=True,
        key="bst_insert_button",
    )

    st.markdown("#### 숫자 탐색")

    search_value = st.number_input(
        "탐색할 정수",
        min_value=-9999,
        max_value=9999,
        value=50,
        step=1,
        key="bst_search_value",
    )

    search_clicked = st.button(
        "🔍 숫자 탐색",
        use_container_width=True,
        key="bst_search_button",
    )

    sample_clicked = st.button(
        "🌳 예제 트리 만들기",
        use_container_width=True,
        key="bst_sample_button",
    )

    clear_clicked = st.button(
        "🔄 트리 초기화",
        use_container_width=True,
        key="bst_clear_button",
    )

    if insert_clicked:
        values, invalid = parse_bst_values(
            insert_text
        )

        if invalid:
            result = {
                "success": False,
                "action": "insert_many",
                "value": None,
                "values": [],
                "path": [],
                "message": (
                    "정수가 아닌 값이 포함되어 삽입을 취소했습니다."
                ),
                "concept": (
                    "쉼표 사이에는 정수만 입력해 주세요."
                ),
            }

        elif not values:
            result = {
                "success": False,
                "action": "insert",
                "value": None,
                "values": [],
                "path": [],
                "message": "삽입할 정수를 입력해 주세요.",
                "concept": (
                    "여러 숫자는 쉼표로 구분하여 입력할 수 있습니다."
                ),
            }

        elif len(values) == 1:
            result = tree.insert(
                values[0]
            )

        else:
            result = tree.insert_many(
                values
            )

        record_operation(
            result,
            changes_tree=result["success"],
        )

        st.rerun()

    if search_clicked:
        reset_visual_feedback()

        result = tree.search(
            int(search_value)
        )

        record_operation(
            result,
            changes_tree=False,
        )

        st.rerun()

    if sample_clicked:
        tree.clear()

        example_values = [
            50,
            30,
            70,
            20,
            40,
            60,
            80,
        ]

        result = tree.insert_many(
            example_values
        )

        result["message"] = (
            "50, 30, 70, 20, 40, 60, 80으로 "
            "예제 트리를 만들었습니다."
        )

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
# 8. 상태와 코드
# ============================================================

status_col1, status_col2 = st.columns(2)

with status_col1:
    render_bst_status(tree)

with status_col2:
    active_operation = None

    if st.session_state.bst_last_result:
        active_operation = (
            st.session_state.bst_last_result.get(
                "action"
            )
        )

    render_bst_code(active_operation)


# ============================================================
# 9. 트리 순회
# ============================================================

render_section_title(
    "3. 트리 순회 체험하기"
)

render_concept_box(
    title="ROOT를 언제 방문하느냐에 따라 순회 방법이 달라집니다.",
    text=(
        "전위 순회는 ROOT를 먼저, 중위 순회는 ROOT를 가운데, "
        "후위 순회는 ROOT를 마지막에 방문합니다."
    ),
)

traversal_col1, traversal_col2, traversal_col3 = st.columns(3)

with traversal_col1:
    preorder_clicked = st.button(
        "전위 순회",
        use_container_width=True,
    )

with traversal_col2:
    inorder_clicked = st.button(
        "중위 순회",
        use_container_width=True,
    )

with traversal_col3:
    postorder_clicked = st.button(
        "후위 순회",
        use_container_width=True,
    )

if preorder_clicked:
    st.session_state.bst_traversal_name = "전위 순회"
    st.session_state.bst_traversal_values = tree.preorder()

if inorder_clicked:
    st.session_state.bst_traversal_name = "중위 순회"
    st.session_state.bst_traversal_values = tree.inorder()

if postorder_clicked:
    st.session_state.bst_traversal_name = "후위 순회"
    st.session_state.bst_traversal_values = tree.postorder()

if st.session_state.bst_traversal_name:
    render_traversal_result(
        st.session_state.bst_traversal_name,
        st.session_state.bst_traversal_values,
    )


# ============================================================
# 10. 삽입 방향 예측
# ============================================================

render_section_title(
    "4. 삽입 방향 예측하기"
)

if tree.root is None:
    st.info(
        "예측 활동을 하려면 먼저 숫자를 삽입해 주세요."
    )

else:
    prediction_value = st.number_input(
        "예측할 새로운 정수",
        min_value=-9999,
        max_value=9999,
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

        if st.session_state.bst_prediction_answer == correct_answer:
            render_message(
                f"정답입니다! 첫 이동 방향은 {correct_answer}입니다.",
                message_type="success",
            )
        else:
            render_message(
                f"정답은 {correct_answer}입니다.",
                message_type="warning",
            )


# ============================================================
# 11. 학습 확인
# ============================================================

render_section_title(
    "5. 학습 확인하기"
)

with st.form("bst_quiz_form"):
    question1 = st.radio(
        "1. 현재 노드보다 작은 값은 어느 방향에 저장되나요?",
        ["왼쪽", "오른쪽", "아무 위치"],
        index=None,
    )

    question2 = st.radio(
        "2. 현재 노드보다 큰 값은 어느 방향에 저장되나요?",
        ["왼쪽", "오른쪽", "ROOT 위쪽"],
        index=None,
    )

    question3 = st.radio(
        "3. 중위 순회의 방문 순서는?",
        [
            "ROOT → LEFT → RIGHT",
            "LEFT → ROOT → RIGHT",
            "LEFT → RIGHT → ROOT",
        ],
        index=None,
    )

    question4 = st.radio(
        "4. BST의 중위 순회 결과는?",
        [
            "오름차순",
            "ROOT만 출력",
            "무작위 순서",
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
    if question4 == "오름차순":
        score += 1

    st.session_state.bst_quiz_score = score
    st.session_state.bst_quiz_submitted = True

if st.session_state.bst_quiz_submitted:
    score = st.session_state.bst_quiz_score

    render_message(
        f"4문제 중 {score}문제를 맞혔습니다.",
        message_type=(
            "success"
            if score == 4
            else "warning"
        ),
    )


# ============================================================
# 12. 연산 기록
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
# 13. 하단
# ============================================================

render_footer()