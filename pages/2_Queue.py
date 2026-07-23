"""
Queue 자료구조 체험 페이지입니다.

지원하는 학습 모드
1. 선형 큐
   - Enqueue
   - 여러 값 일괄 Enqueue
   - Dequeue
   - FRONT와 REAR 확인

2. 원형 큐
   - 고정 크기 배열
   - front와 rear의 순환 이동
   - 한 칸을 비워 두는 포화 판별
   - 여러 값 일괄 Enqueue
"""

from html import escape

import streamlit as st

from components.circular_queue_visualizer import (
    render_circular_operation_history,
    render_circular_operation_message,
    render_circular_queue,
    render_circular_queue_code,
    render_circular_queue_status,
    render_pointer_information,
)
from components.queue_visualizer import (
    render_operation_history,
    render_operation_message,
    render_queue,
    render_queue_code,
    render_queue_slots,
    render_queue_status,
)
from modules.circular_queue_logic import CircularQueue
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
from modules.queue_logic import Queue


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="Queue 체험",
    page_icon="🚶",
    layout="wide",
)

apply_common_style()


# ============================================================
# 2. Session State 초기화
# ============================================================

# ------------------------------------------------------------
# Queue 모드
# ------------------------------------------------------------

initialize_session_state(
    "queue_learning_mode",
    "선형 큐",
)


# ------------------------------------------------------------
# 선형 큐
# ------------------------------------------------------------

initialize_session_state(
    "queue_items",
    [],
)

initialize_session_state(
    "queue_max_size",
    5,
)

initialize_session_state(
    "queue_last_result",
    None,
)

initialize_session_state(
    "queue_history",
    [],
)

initialize_session_state(
    "queue_prediction_submitted",
    False,
)

initialize_session_state(
    "queue_prediction_answer",
    None,
)

initialize_session_state(
    "queue_quiz_score",
    0,
)

initialize_session_state(
    "queue_quiz_submitted",
    False,
)


# ------------------------------------------------------------
# 원형 큐
# ------------------------------------------------------------

initialize_session_state(
    "circular_queue_items",
    [
        None,
        None,
        None,
        None,
        None,
    ],
)

initialize_session_state(
    "circular_queue_front",
    0,
)

initialize_session_state(
    "circular_queue_rear",
    0,
)

initialize_session_state(
    "circular_queue_last_result",
    None,
)

initialize_session_state(
    "circular_queue_history",
    [],
)

initialize_session_state(
    "circular_prediction_submitted",
    False,
)

initialize_session_state(
    "circular_prediction_answer",
    None,
)

initialize_session_state(
    "circular_queue_quiz_score",
    0,
)

initialize_session_state(
    "circular_queue_quiz_submitted",
    False,
)


# ============================================================
# 3. Queue 객체 생성
# ============================================================

linear_queue = Queue(
    max_size=st.session_state.queue_max_size
)

linear_queue.load_items(
    st.session_state.queue_items
)


circular_queue = CircularQueue(
    max_size=5
)

circular_queue.load_state(
    items=st.session_state.circular_queue_items,
    front=st.session_state.circular_queue_front,
    rear=st.session_state.circular_queue_rear,
)


# ============================================================
# 4. 공통 함수
# ============================================================

def parse_queue_values(
    input_text: str,
) -> list[str]:
    """
    쉼표를 기준으로 여러 입력값을 분리합니다.
    """

    return [
        value.strip()
        for value in input_text.split(",")
        if value.strip()
    ]


# ------------------------------------------------------------
# 선형 큐 상태 관리
# ------------------------------------------------------------

def save_linear_queue_state() -> None:
    st.session_state.queue_items = (
        linear_queue.to_list()
    )


def reset_linear_prediction() -> None:
    st.session_state.queue_prediction_submitted = False
    st.session_state.queue_prediction_answer = None

    if "queue_prediction_radio" in st.session_state:
        del st.session_state["queue_prediction_radio"]


def record_linear_operation(
    result: dict,
    changes_queue: bool = False,
) -> None:
    st.session_state.queue_last_result = result
    st.session_state.queue_history.append(result)

    save_linear_queue_state()

    if changes_queue:
        reset_linear_prediction()


# ------------------------------------------------------------
# 원형 큐 상태 관리
# ------------------------------------------------------------

def save_circular_queue_state() -> None:
    state = circular_queue.to_state()

    st.session_state.circular_queue_items = (
        state["items"]
    )

    st.session_state.circular_queue_front = (
        state["front"]
    )

    st.session_state.circular_queue_rear = (
        state["rear"]
    )


def reset_circular_prediction() -> None:
    st.session_state.circular_prediction_submitted = False
    st.session_state.circular_prediction_answer = None

    if "circular_prediction_radio" in st.session_state:
        del st.session_state["circular_prediction_radio"]


def record_circular_operation(
    result: dict,
    changes_queue: bool = False,
) -> None:
    st.session_state.circular_queue_last_result = result
    st.session_state.circular_queue_history.append(result)

    save_circular_queue_state()

    if changes_queue:
        reset_circular_prediction()


# ============================================================
# 5. 페이지 상단
# ============================================================

render_page_header(
    title="Queue 체험하기",
    description=(
        "선형 큐와 원형 큐를 직접 조작하며 "
        "두 자료구조의 차이를 확인해 보세요."
    ),
    icon="🚶",
)


# ============================================================
# 6. Queue 유형 선택
# ============================================================

render_section_title(
    "학습할 Queue 유형 선택"
)

queue_mode = st.radio(
    "Queue 유형",
    [
        "선형 큐",
        "원형 큐",
    ],
    horizontal=True,
    key="queue_learning_mode",
)

if queue_mode == "선형 큐":
    render_message(
        (
            "선형 큐는 배열의 앞쪽 공간이 비어도 "
            "rear가 마지막 인덱스에 도달하면 "
            "더 이상 삽입할 수 있습니다."
        ),
        message_type="info",
    )

else:
    render_message(
        (
            "원형 큐는 배열의 마지막 다음 위치를 "
            "다시 처음 위치와 연결하여 빈 공간을 재사용합니다."
        ),
        message_type="info",
    )


# ============================================================
# 7. 선형 큐 모드
# ============================================================

if queue_mode == "선형 큐":

    # --------------------------------------------------------
    # 개념
    # --------------------------------------------------------

    render_section_title(
        "1. 선형 Queue는 무엇인가요?"
    )

    render_concept_box(
        title="먼저 줄을 선 사람이 먼저 나갑니다.",
        text=(
            "선형 Queue는 먼저 들어온 데이터가 먼저 나오는 "
            "FIFO 구조입니다. 데이터는 REAR에서 삽입하고 "
            "FRONT에서 삭제합니다."
        ),
    )

    concept_col1, concept_col2, concept_col3 = st.columns(3)

    with concept_col1:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">🚶</div>
                <div class="structure-card-title">Enqueue</div>
                <div class="structure-card-description">
                    새로운 데이터를 Queue의 뒤쪽에 추가합니다.
                </div>
                <span class="structure-card-keyword">REAR</span>
            </article>
            """
        )

    with concept_col2:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">🚪</div>
                <div class="structure-card-title">Dequeue</div>
                <div class="structure-card-description">
                    Queue의 가장 앞에 있는 데이터를 제거합니다.
                </div>
                <span class="structure-card-keyword">FRONT</span>
            </article>
            """
        )

    with concept_col3:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">➡️</div>
                <div class="structure-card-title">FIFO</div>
                <div class="structure-card-description">
                    먼저 삽입된 데이터가 가장 먼저 제거됩니다.
                </div>
                <span class="structure-card-keyword">
                    First In First Out
                </span>
            </article>
            """
        )


    # --------------------------------------------------------
    # 직접 체험
    # --------------------------------------------------------

    render_section_title(
        "2. 선형 Queue 직접 체험하기"
    )

    control_col, visual_col = st.columns(
        [1, 1.8]
    )

    with control_col:
        st.subheader(
            "선형 Queue 조작"
        )

        input_text = st.text_input(
            "Queue에 넣을 값",
            placeholder="예: A 또는 A, B, C",
            help=(
                "여러 값은 쉼표로 구분하세요. "
                "입력 순서대로 Enqueue됩니다."
            ),
            key="linear_queue_input",
        )

        parsed_values = parse_queue_values(
            input_text
        )

        if parsed_values:
            preview_text = " → ".join(
                escape(value)
                for value in parsed_values
            )

            render_html(
                f"""
                <div class="info-box">
                    <strong>입력 순서</strong><br>
                    {preview_text}
                </div>
                """
            )

        button_col1, button_col2 = st.columns(2)

        with button_col1:
            enqueue_clicked = st.button(
                "🚶 Enqueue",
                use_container_width=True,
                key="linear_enqueue",
            )

        with button_col2:
            dequeue_clicked = st.button(
                "🚪 Dequeue",
                use_container_width=True,
                key="linear_dequeue",
            )

        button_col3, button_col4 = st.columns(2)

        with button_col3:
            front_clicked = st.button(
                "🔍 FRONT 확인",
                use_container_width=True,
                key="linear_front",
            )

        with button_col4:
            rear_clicked = st.button(
                "🔎 REAR 확인",
                use_container_width=True,
                key="linear_rear",
            )

        clear_clicked = st.button(
            "🔄 선형 Queue 초기화",
            use_container_width=True,
            key="linear_queue_clear",
        )

        if enqueue_clicked:
            values = parse_queue_values(
                input_text
            )

            if not values:
                result = {
                    "success": False,
                    "action": "enqueue",
                    "value": None,
                    "values": [],
                    "message": (
                        "Queue에 넣을 값을 입력해 주세요."
                    ),
                    "concept": (
                        "여러 값은 쉼표로 구분할 수 있습니다."
                    ),
                }

            elif len(values) == 1:
                result = linear_queue.enqueue(
                    values[0]
                )

            else:
                result = linear_queue.enqueue_many(
                    values
                )

            record_linear_operation(
                result,
                changes_queue=result["success"],
            )

            st.rerun()

        if dequeue_clicked:
            result = linear_queue.dequeue()

            record_linear_operation(
                result,
                changes_queue=result["success"],
            )

            st.rerun()

        if front_clicked:
            result = linear_queue.front()

            record_linear_operation(
                result,
                changes_queue=False,
            )

            st.rerun()

        if rear_clicked:
            result = linear_queue.rear()

            record_linear_operation(
                result,
                changes_queue=False,
            )

            st.rerun()

        if clear_clicked:
            result = linear_queue.clear()

            record_linear_operation(
                result,
                changes_queue=True,
            )

            st.session_state.queue_quiz_submitted = False

            st.rerun()

        render_operation_message(
            st.session_state.queue_last_result
        )

    with visual_col:
        st.subheader(
            "선형 Queue 시각화"
        )

        display_mode = st.radio(
            "표시 방식",
            [
                "현재 데이터만 보기",
                "전체 저장 공간 보기",
            ],
            horizontal=True,
            key="linear_queue_display_mode",
        )

        if display_mode == "현재 데이터만 보기":
            render_queue(
                st.session_state.queue_items,
                st.session_state.queue_max_size,
            )

        else:
            render_queue_slots(
                st.session_state.queue_items,
                st.session_state.queue_max_size,
            )


    # --------------------------------------------------------
    # 상태와 코드
    # --------------------------------------------------------

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        render_queue_status(
            st.session_state.queue_items,
            st.session_state.queue_max_size,
        )

    with status_col2:
        active_operation = None

        if st.session_state.queue_last_result:
            active_operation = (
                st.session_state.queue_last_result.get(
                    "action"
                )
            )

        render_queue_code(
            active_operation
        )


    # --------------------------------------------------------
    # 연산 기록
    # --------------------------------------------------------

    with st.expander(
        "선형 Queue 연산 기록 보기",
        expanded=False,
    ):
        render_operation_history(
            st.session_state.queue_history
        )

        if st.session_state.queue_history:
            if st.button(
                "선형 Queue 연산 기록 삭제",
                key="clear_linear_queue_history",
            ):
                st.session_state.queue_history = []
                st.rerun()


# ============================================================
# 8. 원형 큐 모드
# ============================================================

else:

    # --------------------------------------------------------
    # 개념
    # --------------------------------------------------------

    render_section_title(
        "1. 원형 Queue는 무엇인가요?"
    )

    render_concept_box(
        title="배열의 마지막과 처음을 연결합니다.",
        text=(
            "원형 Queue는 rear 또는 front가 배열의 마지막에 "
            "도달하면 다시 0번 인덱스로 이동합니다. "
            "이 덕분에 앞쪽의 빈 공간을 다시 사용할 수 있습니다."
        ),
    )

    concept_col1, concept_col2, concept_col3 = st.columns(3)

    with concept_col1:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">🔄</div>
                <div class="structure-card-title">순환 이동</div>
                <div class="structure-card-description">
                    마지막 인덱스 다음에는 다시 0번으로 이동합니다.
                </div>
                <span class="structure-card-keyword">
                    % SIZE
                </span>
            </article>
            """
        )

    with concept_col2:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">⬜</div>
                <div class="structure-card-title">한 칸 비우기</div>
                <div class="structure-card-description">
                    공백과 포화 상태를 구분하기 위해 한 칸을 비웁니다.
                </div>
                <span class="structure-card-keyword">
                    SIZE - 1
                </span>
            </article>
            """
        )

    with concept_col3:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">♻️</div>
                <div class="structure-card-title">공간 재사용</div>
                <div class="structure-card-description">
                    Dequeue로 생긴 앞쪽 공간을 다시 사용할 수 있습니다.
                </div>
                <span class="structure-card-keyword">
                    효율적인 공간 사용
                </span>
            </article>
            """
        )

    render_message(
        (
            "기본 배열 크기는 <strong>5칸</strong>이지만, "
            "한 칸을 비워 두므로 실제 데이터는 "
            "<strong>4개</strong>까지 저장할 수 있습니다."
        ),
        message_type="info",
        allow_html=True,
    )


    # --------------------------------------------------------
    # 직접 체험
    # --------------------------------------------------------

    render_section_title(
        "2. 원형 Queue 직접 체험하기"
    )

    control_col, visual_col = st.columns(
        [1, 1.9]
    )

    with control_col:
        st.subheader(
            "원형 Queue 조작"
        )

        circular_input = st.text_input(
            "원형 Queue에 넣을 값",
            placeholder="예: A 또는 A, B, C, D",
            help=(
                "여러 값은 쉼표로 구분하세요. "
                "기본 크기 5에서 최대 4개까지 저장할 수 있습니다."
            ),
            key="circular_queue_input",
        )

        parsed_values = parse_queue_values(
            circular_input
        )

        if parsed_values:
            preview_text = " → ".join(
                escape(value)
                for value in parsed_values
            )

            render_html(
                f"""
                <div class="info-box">
                    <strong>입력 순서</strong><br>
                    {preview_text}<br><br>

                    현재 남은 공간:
                    <strong>
                        {circular_queue.remaining_space()}칸
                    </strong>
                </div>
                """
            )

        button_col1, button_col2 = st.columns(2)

        with button_col1:
            circular_enqueue_clicked = st.button(
                "🔄 Enqueue",
                use_container_width=True,
                key="circular_enqueue",
            )

        with button_col2:
            circular_dequeue_clicked = st.button(
                "🚪 Dequeue",
                use_container_width=True,
                key="circular_dequeue",
            )

        button_col3, button_col4 = st.columns(2)

        with button_col3:
            circular_front_clicked = st.button(
                "🔍 FRONT 확인",
                use_container_width=True,
                key="circular_front",
            )

        with button_col4:
            circular_rear_clicked = st.button(
                "🔎 REAR 확인",
                use_container_width=True,
                key="circular_rear",
            )

        circular_clear_clicked = st.button(
            "🔄 원형 Queue 초기화",
            use_container_width=True,
            key="circular_clear",
        )

        if circular_enqueue_clicked:
            values = parse_queue_values(
                circular_input
            )

            if not values:
                result = {
                    "success": False,
                    "action": "enqueue",
                    "value": None,
                    "values": [],
                    "message": (
                        "원형 Queue에 넣을 값을 입력해 주세요."
                    ),
                    "concept": (
                        "여러 값은 쉼표로 구분할 수 있습니다."
                    ),
                    "front": circular_queue.front,
                    "rear": circular_queue.rear,
                }

            elif len(values) == 1:
                result = circular_queue.enqueue(
                    values[0]
                )

            else:
                result = circular_queue.enqueue_many(
                    values
                )

            record_circular_operation(
                result,
                changes_queue=result["success"],
            )

            st.rerun()

        if circular_dequeue_clicked:
            result = circular_queue.dequeue()

            record_circular_operation(
                result,
                changes_queue=result["success"],
            )

            st.rerun()

        if circular_front_clicked:
            result = circular_queue.peek_front()

            record_circular_operation(
                result,
                changes_queue=False,
            )

            st.rerun()

        if circular_rear_clicked:
            result = circular_queue.peek_rear()

            record_circular_operation(
                result,
                changes_queue=False,
            )

            st.rerun()

        if circular_clear_clicked:
            result = circular_queue.clear()

            record_circular_operation(
                result,
                changes_queue=True,
            )

            st.session_state.circular_queue_quiz_submitted = False

            st.rerun()

        render_circular_operation_message(
            st.session_state.circular_queue_last_result
        )

    with visual_col:
        st.subheader(
            "원형 Queue 시각화"
        )

        render_circular_queue(
            circular_queue
        )

        render_pointer_information(
            circular_queue
        )


    # --------------------------------------------------------
    # 상태와 코드
    # --------------------------------------------------------

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        render_circular_queue_status(
            circular_queue
        )

    with status_col2:
        active_operation = None

        if st.session_state.circular_queue_last_result:
            active_operation = (
                st.session_state
                .circular_queue_last_result
                .get("action")
            )

        render_circular_queue_code(
            active_operation
        )


    # --------------------------------------------------------
    # 결과 예측
    # --------------------------------------------------------

    render_section_title(
        "3. 다음 Dequeue 결과 예측하기"
    )

    data_values = circular_queue.data_values()

    if not data_values:
        st.info(
            "예측 활동을 하려면 원형 Queue에 값을 넣어 주세요."
        )

    else:
        prediction = st.radio(
            "다음 Dequeue에서 나올 값",
            options=list(
                dict.fromkeys(data_values)
            ),
            index=None,
            key="circular_prediction_radio",
        )

        if st.button(
            "예측 결과 확인",
            key="check_circular_prediction",
        ):
            st.session_state.circular_prediction_submitted = True
            st.session_state.circular_prediction_answer = prediction

        if st.session_state.circular_prediction_submitted:
            correct_answer = data_values[0]
            selected_answer = (
                st.session_state.circular_prediction_answer
            )

            if selected_answer is None:
                render_message(
                    "답을 선택해 주세요.",
                    message_type="warning",
                )

            elif selected_answer == correct_answer:
                render_message(
                    (
                        f"정답입니다! 다음에 나올 값은 "
                        f"{correct_answer}입니다."
                    ),
                    message_type="success",
                )

            else:
                render_message(
                    (
                        f"정답은 {correct_answer}입니다. "
                        "front의 다음 위치를 확인해 보세요."
                    ),
                    message_type="warning",
                )


    # --------------------------------------------------------
    # 학습 확인
    # --------------------------------------------------------

    render_section_title(
        "4. 원형 Queue 학습 확인하기"
    )

    with st.form(
        "circular_queue_quiz_form"
    ):
        circular_question1 = st.radio(
            "1. 원형 Queue가 공백인 조건은?",
            [
                "front == rear",
                "rear == SIZE - 1",
                "front == 0",
            ],
            index=None,
        )

        circular_question2 = st.radio(
            "2. 원형 Queue가 포화인 조건은?",
            [
                "(rear + 1) % SIZE == front",
                "rear == front",
                "rear == SIZE",
            ],
            index=None,
        )

        circular_question3 = st.radio(
            "3. 배열의 마지막 다음 위치를 구하는 방법은?",
            [
                "(index + 1) % SIZE",
                "index + SIZE",
                "index - 1",
            ],
            index=None,
        )

        circular_question4 = st.radio(
            "4. 크기가 5인 원형 Queue의 실제 저장 용량은?",
            [
                "3개",
                "4개",
                "5개",
            ],
            index=None,
        )

        circular_quiz_submitted = st.form_submit_button(
            "학습 결과 확인"
        )

    if circular_quiz_submitted:
        score = 0

        if circular_question1 == "front == rear":
            score += 1

        if (
            circular_question2
            == "(rear + 1) % SIZE == front"
        ):
            score += 1

        if circular_question3 == "(index + 1) % SIZE":
            score += 1

        if circular_question4 == "4개":
            score += 1

        st.session_state.circular_queue_quiz_score = score
        st.session_state.circular_queue_quiz_submitted = True

    if st.session_state.circular_queue_quiz_submitted:
        score = (
            st.session_state.circular_queue_quiz_score
        )

        if score == 4:
            render_message(
                (
                    "4문제를 모두 맞혔습니다! "
                    "원형 Queue의 원리를 잘 이해했습니다."
                ),
                message_type="success",
            )

        else:
            render_message(
                (
                    f"4문제 중 {score}문제를 맞혔습니다. "
                    "front와 rear의 이동 규칙을 다시 확인해 보세요."
                ),
                message_type="warning",
            )


    # --------------------------------------------------------
    # 연산 기록
    # --------------------------------------------------------

    with st.expander(
        "원형 Queue 연산 기록 보기",
        expanded=False,
    ):
        render_circular_operation_history(
            st.session_state.circular_queue_history
        )

        if st.session_state.circular_queue_history:
            if st.button(
                "원형 Queue 연산 기록 삭제",
                key="clear_circular_queue_history",
            ):
                st.session_state.circular_queue_history = []
                st.rerun()


# ============================================================
# 9. 페이지 하단
# ============================================================

render_footer()