"""
Stack 자료구조 체험 페이지입니다.

지원 기능
1. Stack 기본 개념
2. Push, Pop, Peek 직접 체험
3. 여러 값 일괄 Push
4. 다음 Pop 결과 예측
5. Stack 활용 사례
   - 괄호 검사
   - 후위 표기법 계산
6. 학습 확인
"""

from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from components.stack_application_visualizer import (
    render_bracket_check_visualization,
    render_bracket_guide,
    render_postfix_guide,
    render_postfix_visualization,
    render_stack_application_code,
)
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
from modules.stack_application_logic import (
    calculate_postfix,
    check_brackets,
)
from modules.stack_logic import Stack


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="Stack 체험",
    page_icon="📚",
    layout="wide",
)

apply_common_style()


# ============================================================
# 2. Session State 초기화
# ============================================================

# ------------------------------------------------------------
# 기본 Stack 상태
# ------------------------------------------------------------

initialize_session_state(
    "stack_items",
    [],
)

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
    "stack_prediction_submitted",
    False,
)

initialize_session_state(
    "stack_prediction_answer",
    None,
)

initialize_session_state(
    "stack_quiz_score",
    0,
)

initialize_session_state(
    "stack_quiz_submitted",
    False,
)


# ------------------------------------------------------------
# Stack 활용 기능 상태
# ------------------------------------------------------------

initialize_session_state(
    "stack_application_mode",
    "괄호 검사기",
)

initialize_session_state(
    "bracket_check_result",
    None,
)

initialize_session_state(
    "bracket_check_history",
    [],
)

initialize_session_state(
    "postfix_result",
    None,
)

initialize_session_state(
    "postfix_history",
    [],
)


# ------------------------------------------------------------
# 예제 입력과 초기화를 위한 플래그
# ------------------------------------------------------------

initialize_session_state(
    "load_bracket_sample",
    False,
)

initialize_session_state(
    "clear_bracket_input",
    False,
)

initialize_session_state(
    "load_postfix_sample",
    False,
)

initialize_session_state(
    "clear_postfix_input",
    False,
)


# ============================================================
# 3. Stack 객체 생성 및 상태 복원
# ============================================================

stack = Stack(
    max_size=st.session_state.stack_max_size
)

stack.load_items(
    st.session_state.stack_items
)


# ============================================================
# 4. 공통 함수
# ============================================================

def parse_stack_values(
    input_text: str,
) -> list[str]:
    """
    쉼표로 구분된 입력값을 Stack에 넣을 값 목록으로 변환합니다.

    예:
        A, B, C
        -> ["A", "B", "C"]
    """

    return [
        value.strip()
        for value in str(input_text).split(",")
        if value.strip()
    ]


def save_stack_state() -> None:
    """
    현재 Stack의 데이터를 Session State에 저장합니다.
    """

    st.session_state.stack_items = (
        stack.to_list()
    )


def reset_stack_prediction() -> None:
    """
    Stack 상태가 변경되면 이전 예측 결과를 초기화합니다.
    """

    st.session_state.stack_prediction_submitted = False
    st.session_state.stack_prediction_answer = None

    if "stack_prediction_radio" in st.session_state:
        del st.session_state["stack_prediction_radio"]


def record_stack_operation(
    result: dict[str, Any],
    changes_stack: bool = False,
) -> None:
    """
    Stack 연산 결과를 저장합니다.
    """

    st.session_state.stack_last_result = result
    st.session_state.stack_history.append(result)

    save_stack_state()

    if changes_stack:
        reset_stack_prediction()


def reset_application_step_state(
    key_prefix: str,
) -> None:
    """
    괄호 검사 또는 후위 표기법의 단계 탐색 위치를 초기화합니다.
    """

    step_index_key = (
        f"{key_prefix}_application_step_index"
    )

    signature_key = (
        f"{key_prefix}_application_result_signature"
    )

    if step_index_key in st.session_state:
        del st.session_state[step_index_key]

    if signature_key in st.session_state:
        del st.session_state[signature_key]


def create_empty_stack_result(
    action: str,
    message: str,
    concept: str,
) -> dict[str, Any]:
    """
    Stack 로직의 입력 오류를 공통 결과 형식으로 생성합니다.
    """

    return {
        "success": False,
        "action": action,
        "value": None,
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
        "Stack의 Push와 Pop을 직접 실행하고, "
        "괄호 검사와 후위 표기법 계산에 Stack이 "
        "어떻게 활용되는지 확인해 보세요."
    ),
    icon="📚",
)


# ============================================================
# 6. Stack 개념
# ============================================================

render_section_title(
    "1. Stack은 무엇인가요?"
)

render_concept_box(
    title="가장 나중에 들어온 데이터가 가장 먼저 나옵니다.",
    text=(
        "Stack은 한쪽 끝에서만 데이터의 삽입과 삭제가 "
        "이루어지는 자료구조입니다. 새로운 데이터는 TOP에 "
        "쌓이고, 데이터를 꺼낼 때도 TOP부터 제거됩니다."
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
                새로운 데이터를 Stack의 TOP에 추가합니다.
            </div>

            <span class="structure-card-keyword">
                삽입
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
                Stack의 TOP에 있는 데이터를 제거합니다.
            </div>

            <span class="structure-card-keyword">
                삭제
            </span>
        </article>
        """
    )

with concept_col3:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">
                🔝
            </div>

            <div class="structure-card-title">
                LIFO
            </div>

            <div class="structure-card-description">
                가장 나중에 삽입된 데이터가 가장 먼저 제거됩니다.
            </div>

            <span class="structure-card-keyword">
                Last In First Out
            </span>
        </article>
        """
    )

render_message(
    (
        "책을 차곡차곡 쌓은 뒤 가장 위의 책부터 꺼내는 모습이 "
        "Stack의 동작과 비슷합니다."
    ),
    message_type="info",
)


# ============================================================
# 7. Stack 직접 체험
# ============================================================

render_section_title(
    "2. Stack 직접 체험하기"
)

control_col, visual_col = st.columns(
    [1, 1.8]
)

with control_col:
    st.subheader(
        "Stack 조작"
    )

    # --------------------------------------------------------
    # Stack 크기 조절
    # --------------------------------------------------------

    st.markdown(
        "#### Stack 크기"
    )

    size_col1, size_col2, size_col3 = st.columns(
        [1, 1.4, 1]
    )

    with size_col1:
        decrease_size_clicked = st.button(
            "➖ 감소",
            use_container_width=True,
            key="decrease_stack_size",
            disabled=(
                st.session_state.stack_max_size <= 3
                or bool(st.session_state.stack_items)
            ),
        )

    with size_col2:
        reset_size_clicked = st.button(
            f"크기 {st.session_state.stack_max_size}",
            use_container_width=True,
            key="reset_stack_size",
            disabled=bool(
                st.session_state.stack_items
            ),
        )

    with size_col3:
        increase_size_clicked = st.button(
            "➕ 증가",
            use_container_width=True,
            key="increase_stack_size",
            disabled=(
                st.session_state.stack_max_size >= 10
                or bool(st.session_state.stack_items)
            ),
        )

    if decrease_size_clicked:
        st.session_state.stack_max_size = max(
            3,
            st.session_state.stack_max_size - 1,
        )

        st.session_state.stack_items = []
        st.session_state.stack_last_result = None
        reset_stack_prediction()

        st.rerun()

    if reset_size_clicked:
        st.session_state.stack_max_size = 5
        st.session_state.stack_items = []
        st.session_state.stack_last_result = None
        reset_stack_prediction()

        st.rerun()

    if increase_size_clicked:
        st.session_state.stack_max_size = min(
            10,
            st.session_state.stack_max_size + 1,
        )

        st.session_state.stack_items = []
        st.session_state.stack_last_result = None
        reset_stack_prediction()

        st.rerun()

    if st.session_state.stack_items:
        st.caption(
            "Stack에 데이터가 있는 동안에는 크기를 변경할 수 없습니다."
        )

    # --------------------------------------------------------
    # 값 입력
    # --------------------------------------------------------

    stack_input_text = st.text_input(
        "Stack에 넣을 값",
        placeholder="예: A 또는 A, B, C",
        help=(
            "여러 값은 쉼표로 구분하세요. "
            "왼쪽 값부터 차례대로 Push됩니다."
        ),
        max_chars=200,
        key="stack_input_text",
    )

    parsed_values = parse_stack_values(
        stack_input_text
    )

    if parsed_values:
        preview_text = " → ".join(
            escape(value)
            for value in parsed_values
        )

        render_html(
            f"""
            <div class="info-box">
                <strong>Push 순서</strong><br>
                {preview_text}<br><br>

                남은 공간:
                <strong>{stack.remaining_space()}칸</strong>
            </div>
            """
        )

    # --------------------------------------------------------
    # 조작 버튼
    # --------------------------------------------------------

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        push_clicked = st.button(
            "📥 Push",
            use_container_width=True,
            key="stack_push_button",
        )

    with action_col2:
        pop_clicked = st.button(
            "📤 Pop",
            use_container_width=True,
            key="stack_pop_button",
        )

    peek_clicked = st.button(
        "🔍 TOP 확인",
        use_container_width=True,
        key="stack_peek_button",
    )

    sample_clicked = st.button(
        "📚 예제 Stack 만들기",
        use_container_width=True,
        key="stack_sample_button",
    )

    clear_clicked = st.button(
        "🔄 Stack 초기화",
        use_container_width=True,
        key="stack_clear_button",
    )

    # --------------------------------------------------------
    # Push
    # --------------------------------------------------------

    if push_clicked:
        values = parse_stack_values(
            stack_input_text
        )

        if not values:
            result = create_empty_stack_result(
                action="push",
                message="Stack에 넣을 값을 입력해 주세요.",
                concept=(
                    "여러 값은 쉼표로 구분하여 한 번에 "
                    "Push할 수 있습니다."
                ),
            )

        elif len(values) == 1:
            result = stack.push(
                values[0]
            )

        else:
            result = stack.push_many(
                values
            )

        record_stack_operation(
            result,
            changes_stack=bool(
                result.get("success")
            ),
        )

        st.rerun()

    # --------------------------------------------------------
    # Pop
    # --------------------------------------------------------

    if pop_clicked:
        result = stack.pop()

        record_stack_operation(
            result,
            changes_stack=bool(
                result.get("success")
            ),
        )

        st.rerun()

    # --------------------------------------------------------
    # Peek
    # --------------------------------------------------------

    if peek_clicked:
        result = stack.peek()

        record_stack_operation(
            result,
            changes_stack=False,
        )

        st.rerun()

    # --------------------------------------------------------
    # 예제 Stack
    # --------------------------------------------------------

    if sample_clicked:
        stack.clear()

        sample_values = [
            "A",
            "B",
            "C",
        ]

        result = stack.push_many(
            sample_values
        )

        result["message"] = (
            "A, B, C를 차례대로 Push하여 "
            "예제 Stack을 만들었습니다."
        )

        record_stack_operation(
            result,
            changes_stack=True,
        )

        st.rerun()

    # --------------------------------------------------------
    # 초기화
    # --------------------------------------------------------

    if clear_clicked:
        result = stack.clear()

        record_stack_operation(
            result,
            changes_stack=True,
        )

        st.session_state.stack_items = []
        st.session_state.stack_quiz_submitted = False

        st.rerun()

    render_operation_message(
        st.session_state.stack_last_result
    )


with visual_col:
    st.subheader(
        "Stack 시각화"
    )

    stack_display_mode = st.radio(
        "표시 방식",
        [
            "현재 데이터만 보기",
            "전체 저장 공간 보기",
        ],
        horizontal=True,
        key="stack_display_mode",
    )

    if stack_display_mode == "현재 데이터만 보기":
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
# 8. Stack 상태와 코드
# ============================================================

status_col, code_col = st.columns(2)

with status_col:
    render_stack_status(
        st.session_state.stack_items,
        st.session_state.stack_max_size,
    )

with code_col:
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
# 9. 다음 Pop 결과 예측
# ============================================================

render_section_title(
    "3. 다음 Pop 결과 예측하기"
)

if stack.is_empty():
    st.info(
        "예측 활동을 하려면 먼저 Stack에 값을 Push해 주세요."
    )

else:
    current_values = stack.to_list()

    prediction_options = list(
        reversed(current_values)
    )

    prediction = st.radio(
        "다음 Pop 연산에서 제거될 값은 무엇인가요?",
        options=prediction_options,
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
        correct_answer = current_values[-1]

        selected_answer = (
            st.session_state.stack_prediction_answer
        )

        if selected_answer is None:
            render_message(
                "답을 선택한 뒤 결과를 확인해 주세요.",
                message_type="warning",
            )

        elif selected_answer == correct_answer:
            render_message(
                (
                    f"정답입니다! 현재 TOP은 {correct_answer}이므로 "
                    "다음 Pop에서 가장 먼저 제거됩니다."
                ),
                message_type="success",
            )

        else:
            render_message(
                (
                    f"정답은 {correct_answer}입니다. "
                    "Stack의 가장 위에 있는 TOP을 확인해 보세요."
                ),
                message_type="warning",
            )


# ============================================================
# 10. Stack 활용 체험
# ============================================================

render_section_title(
    "4. Stack 활용 체험하기"
)

render_concept_box(
    title="Stack은 최근에 저장한 정보를 먼저 확인할 때 활용됩니다.",
    text=(
        "프로그램의 괄호 검사, 수식 계산, 실행 취소, "
        "웹 브라우저의 뒤로 가기 등에는 Stack의 "
        "LIFO 구조가 활용됩니다."
    ),
)

application_mode = st.radio(
    "체험할 Stack 활용 기능",
    [
        "괄호 검사기",
        "후위 표기법 계산기",
    ],
    horizontal=True,
    key="stack_application_mode",
)


# ============================================================
# 10-1. 괄호 검사기
# ============================================================

if application_mode == "괄호 검사기":

    render_bracket_guide()

    bracket_input_example = "({[]})"

    # 위젯이 생성되기 전에 예제 또는 초기화 상태를 적용합니다.
    if st.session_state.load_bracket_sample:
        st.session_state.bracket_expression = (
            bracket_input_example
        )

        st.session_state.load_bracket_sample = False

    if st.session_state.clear_bracket_input:
        st.session_state.bracket_expression = ""
        st.session_state.clear_bracket_input = False

    bracket_control_col, bracket_visual_col = st.columns(
        [1, 1.8]
    )

    with bracket_control_col:
        st.subheader(
            "괄호식 입력"
        )

        bracket_expression = st.text_area(
            "검사할 문자열",
            placeholder=bracket_input_example,
            height=150,
            help=(
                "소괄호 (), 중괄호 {}, 대괄호 []를 "
                "함께 사용할 수 있습니다. 괄호가 아닌 문자는 "
                "기본적으로 검사에서 제외됩니다."
            ),
            key="bracket_expression",
        )

        ignore_non_brackets = st.checkbox(
            "괄호가 아닌 문자는 검사에서 제외",
            value=True,
            key="ignore_non_brackets",
        )

        render_html(
            """
            <div class="info-box">
                <strong>입력 예시</strong><br><br>

                올바른 식: ({[]})<br>
                잘못된 식: ([)]<br>
                닫히지 않은 식: (()   
            </div>
            """
        )

        bracket_button_col1, bracket_button_col2 = st.columns(2)

        with bracket_button_col1:
            check_bracket_clicked = st.button(
                "✅ 괄호 검사",
                use_container_width=True,
                key="check_bracket_button",
            )

        with bracket_button_col2:
            load_bracket_sample_clicked = st.button(
                "📘 예제 불러오기",
                use_container_width=True,
                key="load_bracket_sample_button",
            )

        clear_bracket_clicked = st.button(
            "🔄 괄호 검사 초기화",
            use_container_width=True,
            key="clear_bracket_button",
        )

        if check_bracket_clicked:
            bracket_result = check_brackets(
                expression=bracket_expression,
                ignore_non_brackets=ignore_non_brackets,
            )

            st.session_state.bracket_check_result = (
                bracket_result
            )

            st.session_state.bracket_check_history.append(
                {
                    "expression": bracket_expression,
                    "result": bracket_result,
                }
            )

            reset_application_step_state(
                "bracket"
            )

            st.rerun()

        if load_bracket_sample_clicked:
            bracket_result = check_brackets(
                expression=bracket_input_example,
                ignore_non_brackets=True,
            )

            st.session_state.bracket_check_result = (
                bracket_result
            )

            st.session_state.bracket_check_history.append(
                {
                    "expression": bracket_input_example,
                    "result": bracket_result,
                }
            )

            st.session_state.load_bracket_sample = True

            reset_application_step_state(
                "bracket"
            )

            st.rerun()

        if clear_bracket_clicked:
            st.session_state.bracket_check_result = None
            st.session_state.clear_bracket_input = True

            reset_application_step_state(
                "bracket"
            )

            st.rerun()

        st.markdown(
            "#### 핵심 코드"
        )

        render_stack_application_code(
            "bracket"
        )

    with bracket_visual_col:
        st.subheader(
            "괄호 검사 과정"
        )

        render_bracket_check_visualization(
            st.session_state.bracket_check_result,
            key_prefix="bracket",
        )

    # --------------------------------------------------------
    # 괄호 검사 기록
    # --------------------------------------------------------

    with st.expander(
        "괄호 검사 기록 보기",
        expanded=False,
    ):
        bracket_history = (
            st.session_state.bracket_check_history
        )

        if not bracket_history:
            st.info(
                "아직 괄호 검사를 실행하지 않았습니다."
            )

        else:
            for history_index, history_item in enumerate(
                reversed(bracket_history),
                start=1,
            ):
                expression_text = escape(
                    str(
                        history_item.get(
                            "expression",
                            "",
                        )
                    )
                )

                history_result = history_item.get(
                    "result",
                    {},
                )

                success_text = (
                    "올바른 괄호식"
                    if history_result.get("success")
                    else "잘못된 괄호식"
                )

                message_text = escape(
                    str(
                        history_result.get(
                            "message",
                            "",
                        )
                    )
                )

                st.markdown(
                    f"""
**{history_index}. `{expression_text}` — {success_text}**

{message_text}
                    """
                )

                st.divider()

            if st.button(
                "괄호 검사 기록 삭제",
                key="clear_bracket_history",
            ):
                st.session_state.bracket_check_history = []
                st.rerun()


# ============================================================
# 10-2. 후위 표기법 계산기
# ============================================================

else:

    render_postfix_guide()

    postfix_input_example = "3 5 + 2 *"

    # 위젯이 생성되기 전에 예제 또는 초기화 상태를 적용합니다.
    if st.session_state.load_postfix_sample:
        st.session_state.postfix_expression = (
            postfix_input_example
        )

        st.session_state.load_postfix_sample = False

    if st.session_state.clear_postfix_input:
        st.session_state.postfix_expression = ""
        st.session_state.clear_postfix_input = False

    postfix_control_col, postfix_visual_col = st.columns(
        [1, 1.8]
    )

    with postfix_control_col:
        st.subheader(
            "후위 표기법 입력"
        )

        postfix_expression = st.text_input(
            "계산할 후위 표기법",
            placeholder=postfix_input_example,
            help=(
                "여러 자리 숫자, 음수, 실수는 공백으로 "
                "구분해 주세요. 지원 연산자는 "
                "+, -, *, /, %, ^입니다."
            ),
            key="postfix_expression",
        )

        render_html(
            """
            <div class="info-box">
                <strong>입력 예시</strong><br><br>

                3 5 + 2 * → 16<br>
                8 2 - → 6<br>
                10 4 2 * + → 18<br>
                2 3 ^ → 8
            </div>
            """
        )

        postfix_button_col1, postfix_button_col2 = st.columns(2)

        with postfix_button_col1:
            calculate_postfix_clicked = st.button(
                "🧮 계산하기",
                use_container_width=True,
                key="calculate_postfix_button",
            )

        with postfix_button_col2:
            load_postfix_sample_clicked = st.button(
                "📘 예제 불러오기",
                use_container_width=True,
                key="load_postfix_sample_button",
            )

        clear_postfix_clicked = st.button(
            "🔄 계산기 초기화",
            use_container_width=True,
            key="clear_postfix_button",
        )

        if calculate_postfix_clicked:
            postfix_calculation_result = calculate_postfix(
                postfix_expression
            )

            st.session_state.postfix_result = (
                postfix_calculation_result
            )

            st.session_state.postfix_history.append(
                {
                    "expression": postfix_expression,
                    "result": postfix_calculation_result,
                }
            )

            reset_application_step_state(
                "postfix"
            )

            st.rerun()

        if load_postfix_sample_clicked:
            postfix_calculation_result = calculate_postfix(
                postfix_input_example
            )

            st.session_state.postfix_result = (
                postfix_calculation_result
            )

            st.session_state.postfix_history.append(
                {
                    "expression": postfix_input_example,
                    "result": postfix_calculation_result,
                }
            )

            st.session_state.load_postfix_sample = True

            reset_application_step_state(
                "postfix"
            )

            st.rerun()

        if clear_postfix_clicked:
            st.session_state.postfix_result = None
            st.session_state.clear_postfix_input = True

            reset_application_step_state(
                "postfix"
            )

            st.rerun()

        st.markdown(
            "#### 핵심 코드"
        )

        render_stack_application_code(
            "postfix"
        )

    with postfix_visual_col:
        st.subheader(
            "후위 표기법 계산 과정"
        )

        render_postfix_visualization(
            st.session_state.postfix_result,
            key_prefix="postfix",
        )

    # --------------------------------------------------------
    # 후위 표기법 계산 기록
    # --------------------------------------------------------

    with st.expander(
        "후위 표기법 계산 기록 보기",
        expanded=False,
    ):
        postfix_history = (
            st.session_state.postfix_history
        )

        if not postfix_history:
            st.info(
                "아직 후위 표기법 계산을 실행하지 않았습니다."
            )

        else:
            for history_index, history_item in enumerate(
                reversed(postfix_history),
                start=1,
            ):
                expression_text = escape(
                    str(
                        history_item.get(
                            "expression",
                            "",
                        )
                    )
                )

                history_result = history_item.get(
                    "result",
                    {},
                )

                if history_result.get("success"):
                    result_text = escape(
                        str(
                            history_result.get(
                                "result",
                                "",
                            )
                        )
                    )

                    summary_text = (
                        f"계산 결과: {result_text}"
                    )

                else:
                    summary_text = escape(
                        str(
                            history_result.get(
                                "message",
                                "계산 실패",
                            )
                        )
                    )

                st.markdown(
                    f"""
**{history_index}. `{expression_text}`**

{summary_text}
                    """
                )

                st.divider()

            if st.button(
                "후위 표기법 기록 삭제",
                key="clear_postfix_history",
            ):
                st.session_state.postfix_history = []
                st.rerun()


# ============================================================
# 11. 학습 확인
# ============================================================

render_section_title(
    "5. 학습 확인하기"
)

with st.form(
    "stack_quiz_form"
):
    stack_question1 = st.radio(
        "1. Stack의 데이터 처리 방식은?",
        [
            "FIFO",
            "LIFO",
            "무작위 처리",
        ],
        index=None,
    )

    stack_question2 = st.radio(
        "2. Stack에 데이터를 추가하는 연산은?",
        [
            "Push",
            "Pop",
            "Dequeue",
        ],
        index=None,
    )

    stack_question3 = st.radio(
        "3. Stack에서 데이터를 제거하는 위치는?",
        [
            "BOTTOM",
            "가운데",
            "TOP",
        ],
        index=None,
    )

    stack_question4 = st.radio(
        "4. 괄호 검사에서 여는 괄호를 만나면 수행하는 연산은?",
        [
            "Push",
            "Pop",
            "정렬",
        ],
        index=None,
    )

    stack_question5 = st.radio(
        "5. 후위 표기법에서 연산자를 만나면 가장 먼저 하는 일은?",
        [
            "피연산자 두 개를 Pop한다.",
            "연산자를 Stack에 Push한다.",
            "모든 숫자를 삭제한다.",
        ],
        index=None,
    )

    stack_quiz_submitted = st.form_submit_button(
        "학습 결과 확인"
    )

if stack_quiz_submitted:
    score = 0

    if stack_question1 == "LIFO":
        score += 1

    if stack_question2 == "Push":
        score += 1

    if stack_question3 == "TOP":
        score += 1

    if stack_question4 == "Push":
        score += 1

    if (
        stack_question5
        == "피연산자 두 개를 Pop한다."
    ):
        score += 1

    st.session_state.stack_quiz_score = score
    st.session_state.stack_quiz_submitted = True

if st.session_state.stack_quiz_submitted:
    score = st.session_state.stack_quiz_score

    if score == 5:
        render_message(
            (
                "5문제를 모두 맞혔습니다! "
                "Stack의 기본 연산과 활용 원리를 잘 이해했습니다."
            ),
            message_type="success",
        )

    elif score >= 3:
        render_message(
            (
                f"5문제 중 {score}문제를 맞혔습니다. "
                "틀린 문항과 관련된 Stack 동작을 다시 체험해 보세요."
            ),
            message_type="warning",
        )

    else:
        render_message(
            (
                f"5문제 중 {score}문제를 맞혔습니다. "
                "Push, Pop, TOP과 LIFO 개념부터 다시 확인해 보세요."
            ),
            message_type="warning",
        )


# ============================================================
# 12. 기본 Stack 연산 기록
# ============================================================

with st.expander(
    "기본 Stack 연산 기록 보기",
    expanded=False,
):
    render_operation_history(
        st.session_state.stack_history
    )

    if st.session_state.stack_history:
        if st.button(
            "기본 Stack 연산 기록 삭제",
            key="clear_stack_history",
        ):
            st.session_state.stack_history = []
            st.rerun()


# ============================================================
# 13. 페이지 하단
# ============================================================

render_footer()