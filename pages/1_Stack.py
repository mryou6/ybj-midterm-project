"""
Stack 자료구조 체험 페이지입니다.

학습 흐름
1. Stack 개념 알아보기
2. Stack 직접 조작하기
3. 결과 예측하기
4. 학습 확인하기
"""

from html import escape

import streamlit as st

from components.stack_visualizer import (
    render_operation_history,
    render_operation_message,
    render_stack,
    render_stack_code,
    render_stack_slots,
    render_stack_status,
)
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
from modules.stack_logic import Stack


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="Stack 체험",
    page_icon="🥞",
    layout="wide",
)

apply_common_style()


# ============================================================
# 2. Session State 초기화
# ============================================================

initialize_session_state(
    "stack_items",
    [],
)

# Stack의 기본 최대 크기는 5입니다.
initialize_session_state(
    "stack_max_size",
    5,
)

initialize_session_state(
    "stack_last_result",
    None,
)

initialize_session_state(
    "stack_history",
    [],
)

initialize_session_state(
    "stack_quiz_score",
    0,
)

initialize_session_state(
    "stack_quiz_submitted",
    False,
)

initialize_session_state(
    "stack_prediction_submitted",
    False,
)

initialize_session_state(
    "stack_prediction_answer",
    None,
)


# ============================================================
# 3. Stack 객체 생성 및 상태 복원
# ============================================================

stack = Stack(
    max_size=st.session_state.stack_max_size,
)

stack.load_items(
    st.session_state.stack_items,
)


# ============================================================
# 4. 공통 함수
# ============================================================

def parse_stack_values(
    input_text: str,
) -> list[str]:
    """
    쉼표를 기준으로 여러 입력값을 분리합니다.

    예:
        "A, B, C" -> ["A", "B", "C"]
        "A,B,C"   -> ["A", "B", "C"]
        " A , B " -> ["A", "B"]

    빈 값과 앞뒤 공백은 제거합니다.
    """

    return [
        value.strip()
        for value in input_text.split(",")
        if value.strip()
    ]


def save_stack_state() -> None:
    """
    현재 Stack 상태를 Session State에 저장합니다.
    """

    st.session_state.stack_items = stack.to_list()


def reset_prediction() -> None:
    """
    Stack 상태가 변경되면 이전 예측 결과를 초기화합니다.
    """

    st.session_state.stack_prediction_submitted = False
    st.session_state.stack_prediction_answer = None

    if "stack_prediction_radio" in st.session_state:
        del st.session_state["stack_prediction_radio"]


def record_operation(
    result: dict,
    changes_stack: bool = False,
) -> None:
    """
    연산 결과와 Stack 상태를 저장합니다.

    Args:
        result: Stack 연산 결과
        changes_stack: Stack 내부 데이터가 변경됐는지 여부
    """

    st.session_state.stack_last_result = result
    st.session_state.stack_history.append(result)

    save_stack_state()

    if changes_stack:
        reset_prediction()


def create_resize_result(
    new_size: int,
    message: str,
    concept: str,
) -> dict:
    """
    Stack 크기 변경 결과 딕셔너리를 생성합니다.
    """

    return {
        "success": True,
        "action": "resize",
        "value": new_size,
        "values": [],
        "message": message,
        "concept": concept,
    }


# ============================================================
# 5. 페이지 상단
# ============================================================

render_page_header(
    title="Stack 체험하기",
    description=(
        "접시를 쌓고 꺼내는 것처럼 값을 직접 넣고 꺼내며 "
        "Stack의 원리를 알아보세요."
    ),
    icon="🥞",
)


# ============================================================
# 6. Stack 개념 알아보기
# ============================================================

render_section_title(
    "1. Stack은 무엇인가요?"
)

render_concept_box(
    title="접시를 쌓는 모습을 떠올려 보세요.",
    text=(
        "접시를 여러 장 쌓으면 가장 마지막에 올린 접시를 "
        "가장 먼저 꺼내야 합니다. Stack도 이와 같은 방식으로 "
        "데이터를 저장하고 꺼냅니다."
    ),
)

concept_col1, concept_col2, concept_col3 = st.columns(3)

with concept_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                📥
            </div>

            <div class="structure-card-title">
                Push
            </div>

            <div class="structure-card-description">
                새로운 데이터를 Stack의 가장 위에 추가합니다.
            </div>

            <span class="structure-card-keyword">
                데이터 넣기
            </span>
        </article>
        """
    )

with concept_col2:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                📤
            </div>

            <div class="structure-card-title">
                Pop
            </div>

            <div class="structure-card-description">
                Stack의 가장 위에 있는 데이터를 꺼냅니다.
            </div>

            <span class="structure-card-keyword">
                데이터 꺼내기
            </span>
        </article>
        """
    )

with concept_col3:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                👀
            </div>

            <div class="structure-card-title">
                Peek
            </div>

            <div class="structure-card-description">
                데이터를 꺼내지 않고 가장 위의 값만 확인합니다.
            </div>

            <span class="structure-card-keyword">
                TOP 확인하기
            </span>
        </article>
        """
    )

render_message(
    (
        "<strong>LIFO</strong>는 Last In, First Out의 약자로, "
        "마지막에 들어온 데이터가 가장 먼저 나오는 방식을 뜻합니다."
    ),
    message_type="info",
    allow_html=True,
)


# ============================================================
# 7. Stack 직접 체험하기
# ============================================================

render_section_title(
    "2. Stack 직접 체험하기"
)


# ------------------------------------------------------------
# Stack 최대 크기 설정
# ------------------------------------------------------------

with st.expander(
    "Stack 최대 크기 설정",
    expanded=False,
):
    current_max_size = st.session_state.stack_max_size
    current_item_count = len(
        st.session_state.stack_items
    )

    st.markdown(
        f"현재 Stack 최대 크기: **{current_max_size}칸**"
    )

    size_col1, size_col2, size_col3 = st.columns(3)

    with size_col1:
        decrease_clicked = st.button(
            "➖ 1칸 줄이기",
            key="decrease_stack_size",
            use_container_width=True,
            disabled=(
                current_max_size <= 3
                or current_max_size - 1 < current_item_count
            ),
        )

    with size_col2:
        reset_size_clicked = st.button(
            "5️⃣ 기본 크기 5",
            key="reset_stack_size",
            use_container_width=True,
            disabled=(
                current_max_size == 5
                or current_item_count > 5
            ),
        )

    with size_col3:
        increase_clicked = st.button(
            "➕ 1칸 늘리기",
            key="increase_stack_size",
            use_container_width=True,
            disabled=current_max_size >= 15,
        )

    if decrease_clicked:
        new_size = current_max_size - 1

        st.session_state.stack_max_size = new_size

        st.session_state.stack_last_result = (
            create_resize_result(
                new_size=new_size,
                message=(
                    f"Stack 최대 크기를 {new_size}칸으로 줄였습니다."
                ),
                concept=(
                    "현재 저장된 데이터 수보다 작은 크기로는 "
                    "줄일 수 없습니다."
                ),
            )
        )

        st.rerun()

    if reset_size_clicked:
        st.session_state.stack_max_size = 5

        st.session_state.stack_last_result = (
            create_resize_result(
                new_size=5,
                message=(
                    "Stack 최대 크기를 기본값인 5칸으로 변경했습니다."
                ),
                concept=(
                    "이 웹앱의 기본 Stack 크기는 5칸입니다."
                ),
            )
        )

        st.rerun()

    if increase_clicked:
        new_size = current_max_size + 1

        st.session_state.stack_max_size = new_size

        st.session_state.stack_last_result = (
            create_resize_result(
                new_size=new_size,
                message=(
                    f"Stack 최대 크기를 {new_size}칸으로 늘렸습니다."
                ),
                concept=(
                    "Stack에 데이터를 저장할 수 있는 공간이 "
                    "1칸 증가했습니다."
                ),
            )
        )

        st.rerun()

    render_html(
        f"""
        <div class="info-box">
            기본 크기는 <strong>5칸</strong>이며,
            현재 최대 크기는
            <strong>{current_max_size}칸</strong>입니다.<br>

            현재 Stack에는
            <strong>{current_item_count}개</strong>의 데이터가
            저장되어 있습니다.
        </div>
        """
    )


# ------------------------------------------------------------
# Stack 조작 및 시각화
# ------------------------------------------------------------

control_col, visual_col = st.columns(
    [1, 1.6]
)

with control_col:
    st.subheader(
        "Stack 조작"
    )

    input_text = st.text_input(
        "Stack에 넣을 값",
        placeholder="예: A 또는 A, B, C",
        help=(
            "여러 값은 쉼표로 구분하세요. "
            "입력한 순서대로 Push되며 앞뒤 공백은 자동으로 제거됩니다."
        ),
        max_chars=150,
        key="stack_input_value",
    )

    parsed_values = parse_stack_values(
        input_text
    )

    if parsed_values:
        input_preview = " → ".join(
            escape(value)
            for value in parsed_values
        )

        top_preview = escape(
            parsed_values[-1]
        )

        render_html(
            f"""
            <div class="info-box">
                <strong>입력 순서</strong><br>
                {input_preview}

                <br><br>

                마지막 값
                <strong>{top_preview}</strong>이(가)
                TOP이 됩니다.
            </div>
            """
        )

    button_col1, button_col2 = st.columns(2)

    with button_col1:
        push_clicked = st.button(
            "📥 Push: 넣기",
            use_container_width=True,
            key="stack_push_button",
        )

    with button_col2:
        pop_clicked = st.button(
            "📤 Pop: 꺼내기",
            use_container_width=True,
            key="stack_pop_button",
        )

    button_col3, button_col4 = st.columns(2)

    with button_col3:
        peek_clicked = st.button(
            "👀 Peek: 확인",
            use_container_width=True,
            key="stack_peek_button",
        )

    with button_col4:
        clear_clicked = st.button(
            "🔄 초기화",
            use_container_width=True,
            key="stack_clear_button",
        )

    # --------------------------------------------------------
    # Push 실행
    # --------------------------------------------------------

    if push_clicked:
        values = parse_stack_values(
            input_text
        )

        if not values:
            result = {
                "success": False,
                "action": "push",
                "value": None,
                "values": [],
                "message": (
                    "Stack에 넣을 값을 입력해 주세요."
                ),
                "concept": (
                    "여러 값은 쉼표로 구분하여 입력할 수 있습니다."
                ),
            }

        elif len(values) == 1:
            result = stack.push(
                values[0]
            )

        else:
            result = stack.push_many(
                values
            )

        record_operation(
            result,
            changes_stack=result["success"],
        )

        st.rerun()

    # --------------------------------------------------------
    # Pop 실행
    # --------------------------------------------------------

    if pop_clicked:
        result = stack.pop()

        record_operation(
            result,
            changes_stack=result["success"],
        )

        st.rerun()

    # --------------------------------------------------------
    # Peek 실행
    # --------------------------------------------------------

    if peek_clicked:
        result = stack.peek()

        record_operation(
            result,
            changes_stack=False,
        )

        st.rerun()

    # --------------------------------------------------------
    # 초기화 실행
    # --------------------------------------------------------

    if clear_clicked:
        result = stack.clear()

        record_operation(
            result,
            changes_stack=True,
        )

        st.session_state.stack_quiz_submitted = False

        st.rerun()

    render_operation_message(
        st.session_state.stack_last_result
    )


with visual_col:
    st.subheader(
        "Stack 시각화"
    )

    display_mode = st.radio(
        "표시 방식",
        [
            "현재 데이터만 보기",
            "전체 저장 공간 보기",
        ],
        horizontal=True,
        key="stack_display_mode",
    )

    if display_mode == "현재 데이터만 보기":
        render_stack(
            st.session_state.stack_items,
            st.session_state.stack_max_size,
        )

    else:
        render_stack_slots(
            st.session_state.stack_items,
            st.session_state.stack_max_size,
        )


# ============================================================
# 8. 현재 상태와 Python 코드
# ============================================================

status_col1, status_col2 = st.columns(2)

with status_col1:
    render_stack_status(
        st.session_state.stack_items,
        st.session_state.stack_max_size,
    )

with status_col2:
    active_operation = None

    if st.session_state.stack_last_result:
        active_operation = (
            st.session_state.stack_last_result.get(
                "action"
            )
        )

    render_stack_code(
        active_operation
    )


# ============================================================
# 9. 결과 예측하기
# ============================================================

render_section_title(
    "3. 결과 예측하기"
)

render_html(
    """
    <section class="quiz-box">
        <div class="quiz-title">
            Pop을 실행하면 어떤 값이 나올까요?
        </div>

        <div class="quiz-question">
            현재 Stack의 상태를 살펴보고,
            다음 Pop 연산으로 제거될 값을 예측해 보세요.
        </div>
    </section>
    """
)

current_items = st.session_state.stack_items

if not current_items:
    st.info(
        "예측 활동을 하려면 Stack에 값을 1개 이상 넣어 주세요."
    )

else:
    # 같은 값이 여러 번 들어 있어도 선택지에는 한 번만 표시합니다.
    unique_options = list(
        dict.fromkeys(current_items)
    )

    prediction = st.radio(
        "다음에 나올 값 선택",
        options=unique_options,
        index=None,
        key="stack_prediction_radio",
    )

    if st.button(
        "예측 결과 확인",
        key="check_stack_prediction",
    ):
        st.session_state.stack_prediction_submitted = True
        st.session_state.stack_prediction_answer = prediction

    if st.session_state.stack_prediction_submitted:
        correct_answer = current_items[-1]

        selected_answer = (
            st.session_state.stack_prediction_answer
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

                    현재 TOP은
                    <strong>
                        {escape(str(correct_answer))}
                    </strong>이며,

                    Pop을 실행하면 이 값이 가장 먼저 나옵니다.
                </div>
                """
            )

        else:
            render_html(
                f"""
                <div class="quiz-result-wrong">
                    다시 생각해 보세요.<br>

                    Stack은 마지막에 들어온 값이 먼저 나옵니다.

                    현재 TOP은
                    <strong>
                        {escape(str(correct_answer))}
                    </strong>입니다.
                </div>
                """
            )


# ============================================================
# 10. 학습 확인하기
# ============================================================

render_section_title(
    "4. 학습 확인하기"
)

with st.form(
    "stack_quiz_form"
):
    question1 = st.radio(
        "1. Stack의 데이터 처리 방식으로 알맞은 것은?",
        [
            "먼저 들어온 데이터가 먼저 나온다.",
            "마지막에 들어온 데이터가 먼저 나온다.",
            "중간에 있는 데이터가 먼저 나온다.",
        ],
        index=None,
    )

    question2 = st.radio(
        "2. Stack에 데이터를 추가하는 연산은?",
        [
            "Push",
            "Pop",
            "Peek",
        ],
        index=None,
    )

    question3 = st.radio(
        "3. 가장 위의 값을 제거하지 않고 확인하는 연산은?",
        [
            "Push",
            "Pop",
            "Peek",
        ],
        index=None,
    )

    quiz_submitted = st.form_submit_button(
        "학습 결과 확인"
    )

if quiz_submitted:
    score = 0

    if question1 == "마지막에 들어온 데이터가 먼저 나온다.":
        score += 1

    if question2 == "Push":
        score += 1

    if question3 == "Peek":
        score += 1

    st.session_state.stack_quiz_score = score
    st.session_state.stack_quiz_submitted = True


if st.session_state.stack_quiz_submitted:
    score = st.session_state.stack_quiz_score

    if score == 3:
        render_html(
            """
            <div class="quiz-result-correct">
                3문제를 모두 맞혔습니다!<br>
                Stack의 기본 원리를 잘 이해했습니다.
            </div>
            """
        )

    elif score == 2:
        render_html(
            """
            <div class="warning-box">
                3문제 중 2문제를 맞혔습니다.<br>
                Push, Pop, Peek의 차이를 한 번 더 확인해 보세요.
            </div>
            """
        )

    else:
        render_html(
            f"""
            <div class="quiz-result-wrong">
                3문제 중 {score}문제를 맞혔습니다.<br>
                시각화를 다시 조작하며 LIFO 원리를 확인해 보세요.
            </div>
            """
        )


# ============================================================
# 11. 연산 기록
# ============================================================

with st.expander(
    "내가 실행한 Stack 연산 기록 보기",
    expanded=False,
):
    render_operation_history(
        st.session_state.stack_history
    )

    if st.session_state.stack_history:
        if st.button(
            "연산 기록 삭제",
            key="clear_stack_history",
        ):
            st.session_state.stack_history = []
            st.rerun()


# ============================================================
# 12. 페이지 하단
# ============================================================

render_footer()