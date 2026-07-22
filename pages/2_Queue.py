"""
Queue 자료구조 체험 페이지입니다.

학습 흐름
1. Queue 개념 알아보기
2. Queue 직접 조작하기
3. 결과 예측하기
4. Stack과 Queue 비교하기
5. 학습 확인하기
"""

from html import escape

import streamlit as st

from components.queue_visualizer import (
    render_operation_history,
    render_operation_message,
    render_queue,
    render_queue_code,
    render_queue_slots,
    render_queue_status,
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
from modules.queue_logic import Queue


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="Queue 체험",
    page_icon="🚶",
    layout="wide"
)

apply_common_style()


# ============================================================
# 2. Session State 초기화
# ============================================================

initialize_session_state(
    "queue_items",
    []
)

initialize_session_state(
    "queue_max_size",
    5
)

initialize_session_state(
    "queue_last_result",
    None
)

initialize_session_state(
    "queue_history",
    []
)

initialize_session_state(
    "queue_quiz_score",
    0
)

initialize_session_state(
    "queue_quiz_submitted",
    False
)

initialize_session_state(
    "queue_prediction_submitted",
    False
)

initialize_session_state(
    "queue_prediction_answer",
    None
)


# ============================================================
# 3. Queue 객체 생성
# ============================================================

queue = Queue(
    max_size=st.session_state.queue_max_size
)

queue.load_items(
    st.session_state.queue_items
)


def save_queue_state() -> None:
    """
    Queue 객체의 현재 값을 Session State에 저장합니다.
    """

    st.session_state.queue_items = queue.to_list()


def reset_prediction() -> None:
    """
    Queue 상태가 변경되면 기존 예측 결과를 초기화합니다.
    """

    st.session_state.queue_prediction_submitted = False
    st.session_state.queue_prediction_answer = None

    if "queue_prediction_radio" in st.session_state:
        del st.session_state["queue_prediction_radio"]


def record_operation(
    result: dict,
    changes_queue: bool = False
) -> None:
    """
    연산 결과와 Queue 상태를 저장합니다.
    """

    st.session_state.queue_last_result = result
    st.session_state.queue_history.append(result)

    save_queue_state()

    if changes_queue:
        reset_prediction()


# ============================================================
# 4. 페이지 상단
# ============================================================

render_page_header(
    title="Queue 체험하기",
    description=(
        "대기줄에 차례대로 서는 것처럼 값을 직접 넣고 꺼내며 "
        "Queue의 원리를 알아보세요."
    ),
    icon="🚶"
)


# ============================================================
# 5. Queue 개념 알아보기
# ============================================================

render_section_title(
    "1. Queue는 무엇인가요?"
)

render_concept_box(
    title="놀이기구를 기다리는 대기줄을 떠올려 보세요.",
    text=(
        "대기줄에서는 먼저 도착한 사람이 가장 먼저 놀이기구를 "
        "이용합니다. Queue도 먼저 들어온 데이터를 먼저 처리하는 "
        "방식으로 데이터를 저장하고 꺼냅니다."
    )
)

concept_col1, concept_col2, concept_col3 = st.columns(3)

with concept_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🚶‍➡️</div>

            <div class="structure-card-title">
                Enqueue
            </div>

            <div class="structure-card-description">
                새로운 데이터를 Queue의 뒤쪽인 REAR에 추가합니다.
            </div>

            <span class="structure-card-keyword">
                줄의 뒤에 서기
            </span>
        </article>
        """
    )

with concept_col2:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🚪</div>

            <div class="structure-card-title">
                Dequeue
            </div>

            <div class="structure-card-description">
                Queue의 앞쪽인 FRONT 데이터를 꺼냅니다.
            </div>

            <span class="structure-card-keyword">
                맨 앞에서 나가기
            </span>
        </article>
        """
    )

with concept_col3:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🔍</div>

            <div class="structure-card-title">
                FRONT와 REAR
            </div>

            <div class="structure-card-description">
                FRONT는 다음에 나갈 위치이고 REAR는 새 값이 들어오는 위치입니다.
            </div>

            <span class="structure-card-keyword">
                앞과 뒤 확인하기
            </span>
        </article>
        """
    )

render_message(
    (
        "<strong>FIFO</strong>는 First In, First Out의 약자로, "
        "먼저 들어온 데이터가 가장 먼저 나오는 방식을 뜻합니다."
    ),
    message_type="info",
    allow_html=True
)


# ============================================================
# 6. Queue 직접 체험
# ============================================================

render_section_title(
    "2. Queue 직접 체험하기"
)

with st.expander(
    "Queue 최대 크기 설정",
    expanded=False
):
    selected_max_size = st.slider(
        "Queue에 저장할 수 있는 최대 데이터 수",
        min_value=3,
        max_value=10,
        value=st.session_state.queue_max_size,
        step=1
    )

    if selected_max_size != st.session_state.queue_max_size:
        current_count = len(
            st.session_state.queue_items
        )

        if current_count > selected_max_size:
            st.warning(
                "현재 저장된 데이터 수보다 작은 크기로는 "
                "변경할 수 없습니다."
            )

        else:
            st.session_state.queue_max_size = selected_max_size
            queue.max_size = selected_max_size

            st.success(
                f"Queue 최대 크기를 {selected_max_size}로 변경했습니다."
            )


control_col, visual_col = st.columns(
    [1, 1.8]
)

with control_col:
    st.subheader(
        "Queue 조작"
    )

    input_value = st.text_input(
        "Queue에 넣을 값",
        placeholder="예: 10, 사과, A",
        max_chars=20,
        key="queue_input_value"
    )

    button_col1, button_col2 = st.columns(2)

    with button_col1:
        enqueue_clicked = st.button(
            "🚶 Enqueue: 넣기",
            use_container_width=True,
            type="primary"
        )

    with button_col2:
        dequeue_clicked = st.button(
            "🚪 Dequeue: 꺼내기",
            use_container_width=True
        )

    button_col3, button_col4 = st.columns(2)

    with button_col3:
        front_clicked = st.button(
            "🔍 FRONT 확인",
            use_container_width=True
        )

    with button_col4:
        rear_clicked = st.button(
            "🔎 REAR 확인",
            use_container_width=True
        )

    clear_clicked = st.button(
        "🔄 Queue 초기화",
        use_container_width=True
    )

    if enqueue_clicked:
        cleaned_value = input_value.strip()

        if not cleaned_value:
            result = {
                "success": False,
                "action": "enqueue",
                "value": None,
                "message": "Queue에 넣을 값을 입력해 주세요.",
                "concept": (
                    "Enqueue 연산을 실행하려면 먼저 데이터가 필요합니다."
                ),
            }

            st.session_state.queue_last_result = result

        else:
            result = queue.enqueue(
                cleaned_value
            )

            record_operation(
                result,
                changes_queue=result["success"]
            )

            st.rerun()

    if dequeue_clicked:
        result = queue.dequeue()

        record_operation(
            result,
            changes_queue=result["success"]
        )

        st.rerun()

    if front_clicked:
        result = queue.front()

        record_operation(
            result,
            changes_queue=False
        )

        st.rerun()

    if rear_clicked:
        result = queue.rear()

        record_operation(
            result,
            changes_queue=False
        )

        st.rerun()

    if clear_clicked:
        result = queue.clear()

        record_operation(
            result,
            changes_queue=True
        )

        st.session_state.queue_quiz_submitted = False

        st.rerun()

    render_operation_message(
        st.session_state.queue_last_result
    )


with visual_col:
    st.subheader(
        "Queue 시각화"
    )

    display_mode = st.radio(
        "표시 방식",
        [
            "현재 데이터만 보기",
            "전체 저장 공간 보기"
        ],
        horizontal=True,
        key="queue_display_mode"
    )

    if display_mode == "현재 데이터만 보기":
        render_queue(
            st.session_state.queue_items,
            st.session_state.queue_max_size
        )

    else:
        render_queue_slots(
            st.session_state.queue_items,
            st.session_state.queue_max_size
        )


# ============================================================
# 7. 현재 상태와 코드
# ============================================================

status_col1, status_col2 = st.columns(2)

with status_col1:
    render_queue_status(
        st.session_state.queue_items,
        st.session_state.queue_max_size
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


# ============================================================
# 8. 결과 예측
# ============================================================

render_section_title(
    "3. 결과 예측하기"
)

render_html(
    """
    <section class="quiz-box">
        <div class="quiz-title">
            Dequeue를 실행하면 어떤 값이 나올까요?
        </div>

        <div class="quiz-question">
            현재 Queue의 FRONT를 확인하고,
            다음 Dequeue 연산으로 제거될 값을 예측해 보세요.
        </div>
    </section>
    """
)

current_items = st.session_state.queue_items

if not current_items:
    st.info(
        "예측 활동을 하려면 Queue에 값을 1개 이상 넣어 주세요."
    )

else:
    unique_options = list(
        dict.fromkeys(current_items)
    )

    prediction = st.radio(
        "다음에 나올 값 선택",
        options=unique_options,
        index=None,
        key="queue_prediction_radio"
    )

    if st.button(
        "예측 결과 확인",
        key="check_queue_prediction"
    ):
        st.session_state.queue_prediction_submitted = True
        st.session_state.queue_prediction_answer = prediction

    if st.session_state.queue_prediction_submitted:
        correct_answer = current_items[0]

        selected_answer = (
            st.session_state.queue_prediction_answer
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
                    현재 FRONT는
                    <strong>{escape(str(correct_answer))}</strong>이며,
                    Dequeue를 실행하면 이 값이 먼저 나옵니다.
                </div>
                """
            )

        else:
            render_html(
                f"""
                <div class="quiz-result-wrong">
                    다시 생각해 보세요.<br>
                    Queue는 먼저 들어온 값이 먼저 나옵니다.
                    현재 FRONT는
                    <strong>{escape(str(correct_answer))}</strong>입니다.
                </div>
                """
            )


# ============================================================
# 9. Stack과 Queue 비교
# ============================================================

render_section_title(
    "4. Stack과 Queue 비교하기"
)

comparison_col1, comparison_col2 = st.columns(2)

with comparison_col1:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🥞</div>

            <div class="structure-card-title">
                Stack
            </div>

            <div class="structure-card-description">
                마지막에 들어온 데이터가 먼저 나옵니다.
                접시를 쌓는 모습과 비슷합니다.
            </div>

            <span class="structure-card-keyword">
                LIFO
            </span>
        </article>
        """
    )

with comparison_col2:
    render_html(
        """
        <article class="structure-card">
            <div class="structure-card-icon">🚶</div>

            <div class="structure-card-title">
                Queue
            </div>

            <div class="structure-card-description">
                먼저 들어온 데이터가 먼저 나옵니다.
                대기줄을 서는 모습과 비슷합니다.
            </div>

            <span class="structure-card-keyword">
                FIFO
            </span>
        </article>
        """
    )


# ============================================================
# 10. 학습 확인 문제
# ============================================================

render_section_title(
    "5. 학습 확인하기"
)

with st.form(
    "queue_quiz_form"
):
    question1 = st.radio(
        "1. Queue의 데이터 처리 방식으로 알맞은 것은?",
        [
            "먼저 들어온 데이터가 먼저 나온다.",
            "마지막에 들어온 데이터가 먼저 나온다.",
            "임의의 데이터가 먼저 나온다."
        ],
        index=None
    )

    question2 = st.radio(
        "2. Queue에 데이터를 추가하는 연산은?",
        [
            "Enqueue",
            "Dequeue",
            "Front"
        ],
        index=None
    )

    question3 = st.radio(
        "3. Queue에서 다음에 제거될 데이터의 위치는?",
        [
            "FRONT",
            "REAR",
            "TOP"
        ],
        index=None
    )

    question4 = st.radio(
        "4. Queue와 가장 비슷한 일상생활 사례는?",
        [
            "접시 쌓기",
            "대기줄 서기",
            "책상 위에 책 펼치기"
        ],
        index=None
    )

    quiz_submitted = st.form_submit_button(
        "학습 결과 확인"
    )

if quiz_submitted:
    score = 0

    if question1 == "먼저 들어온 데이터가 먼저 나온다.":
        score += 1

    if question2 == "Enqueue":
        score += 1

    if question3 == "FRONT":
        score += 1

    if question4 == "대기줄 서기":
        score += 1

    st.session_state.queue_quiz_score = score
    st.session_state.queue_quiz_submitted = True

if st.session_state.queue_quiz_submitted:
    score = st.session_state.queue_quiz_score

    if score == 4:
        render_html(
            """
            <div class="quiz-result-correct">
                4문제를 모두 맞혔습니다!<br>
                Queue의 기본 원리를 잘 이해했습니다.
            </div>
            """
        )

    elif score >= 2:
        render_html(
            f"""
            <div class="warning-box">
                4문제 중 {score}문제를 맞혔습니다.<br>
                FRONT, REAR, Enqueue, Dequeue의 차이를
                한 번 더 확인해 보세요.
            </div>
            """
        )

    else:
        render_html(
            f"""
            <div class="quiz-result-wrong">
                4문제 중 {score}문제를 맞혔습니다.<br>
                Queue 시각화를 다시 조작하며
                FIFO 원리를 확인해 보세요.
            </div>
            """
        )


# ============================================================
# 11. 연산 기록
# ============================================================

with st.expander(
    "내가 실행한 Queue 연산 기록 보기",
    expanded=False
):
    render_operation_history(
        st.session_state.queue_history
    )

    if st.session_state.queue_history:
        if st.button(
            "연산 기록 삭제",
            key="clear_queue_history"
        ):
            st.session_state.queue_history = []
            st.rerun()


# ============================================================
# 12. 페이지 하단
# ============================================================

render_footer()