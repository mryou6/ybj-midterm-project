"""
원형 큐(Circular Queue)의 시각화 컴포넌트입니다.

주요 기능
- 원형 큐 배열 시각화
- front와 rear 위치 표시
- 실제 데이터 처리 순서 표시
- 현재 상태 표시
- Python 코드 표시
- 연산 결과 및 기록 표시
"""

from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from modules.circular_queue_logic import CircularQueue
from modules.common import render_html


# ============================================================
# 1. 연산 결과 표시
# ============================================================

def render_circular_operation_message(
    result: dict | None,
) -> None:
    """
    최근 원형 큐 연산 결과를 표시합니다.
    """

    if not result:
        return

    message = escape(
        str(result.get("message", ""))
    )

    concept = escape(
        str(result.get("concept", ""))
    )

    success = result.get(
        "success",
        False,
    )

    box_class = (
        "success-box"
        if success
        else "warning-box"
    )

    render_html(
        f"""
        <div class="{box_class}">
            <strong>{message}</strong>

            {
                f"<br><br>{concept}"
                if concept
                else ""
            }
        </div>
        """
    )


# ============================================================
# 2. 배열형 원형 큐 시각화
# ============================================================

def render_circular_queue(
    queue: CircularQueue,
) -> None:
    """
    원형 큐를 배열 형태로 시각화합니다.

    각 칸에 다음 정보를 표시합니다.
    - 배열 인덱스
    - 저장된 데이터
    - front 위치
    - rear 위치
    - 다음 삽입 위치
    """

    items = queue.items
    front = queue.front
    rear = queue.rear
    next_rear = queue.next_rear_index()
    next_front = queue.next_front_index()

    slot_blocks: list[str] = []

    for index, value in enumerate(items):
        labels: list[str] = []

        if index == front:
            labels.append(
                '<span class="circular-label front-label">front</span>'
            )

        if index == rear:
            labels.append(
                '<span class="circular-label rear-label">rear</span>'
            )

        if (
            index == next_front
            and not queue.is_empty()
        ):
            labels.append(
                '<span class="circular-label data-front-label">'
                '다음 삭제'
                '</span>'
            )

        if (
            index == next_rear
            and not queue.is_full()
        ):
            labels.append(
                '<span class="circular-label next-label">'
                '다음 삽입'
                '</span>'
            )

        labels_html = "".join(labels)

        if value is None:
            value_text = "빈 공간"
            value_class = "empty"
        else:
            value_text = escape(
                str(value)
            )
            value_class = "filled"

        slot_blocks.append(
            f"""
            <div class="circular-slot-wrapper">
                <div class="circular-index">
                    index {index}
                </div>

                <div class="circular-slot {value_class}">
                    {value_text}
                </div>

                <div class="circular-label-area">
                    {labels_html}
                </div>
            </div>
            """
        )

    data_values = queue.data_values()

    if data_values:
        order_text = " → ".join(
            escape(str(value))
            for value in data_values
        )
    else:
        order_text = "저장된 데이터 없음"

    state_text = (
        "공백 상태"
        if queue.is_empty()
        else (
            "포화 상태"
            if queue.is_full()
            else "데이터 저장 중"
        )
    )

    render_html(
        f"""
        <style>
            .circular-queue-panel {{
                padding: 24px;
                border: 1px solid #d5e0eb;
                border-radius: 16px;
                background: #f8fbfe;
                margin-bottom: 16px;
            }}

            .circular-array {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                align-items: flex-start;
                gap: 12px;
                margin: 14px 0 24px 0;
            }}

            .circular-slot-wrapper {{
                width: 112px;
                text-align: center;
            }}

            .circular-index {{
                margin-bottom: 7px;
                color: #6d7e90;
                font-size: 13px;
                font-weight: 600;
            }}

            .circular-slot {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 72px;
                padding: 8px;
                border: 2px solid #8eb4d8;
                border-radius: 14px;
                font-size: 20px;
                font-weight: 700;
                box-sizing: border-box;
            }}

            .circular-slot.filled {{
                background: #e8f3ff;
                color: #173d65;
            }}

            .circular-slot.empty {{
                background: #ffffff;
                color: #9aa8b6;
                border-style: dashed;
                font-size: 15px;
                font-weight: 500;
            }}

            .circular-label-area {{
                min-height: 60px;
                margin-top: 7px;
            }}

            .circular-label {{
                display: block;
                width: fit-content;
                margin: 3px auto;
                padding: 3px 8px;
                border-radius: 999px;
                font-size: 12px;
                font-weight: 700;
            }}

            .front-label {{
                background: #e7f5ed;
                color: #18723c;
            }}

            .rear-label {{
                background: #fff0ec;
                color: #b8412d;
            }}

            .data-front-label {{
                background: #fff7d9;
                color: #826200;
            }}

            .next-label {{
                background: #ebe8ff;
                color: #5741a7;
            }}

            .circular-summary {{
                padding: 17px 20px;
                border-radius: 12px;
                background: #ffffff;
                border: 1px solid #d9e3ec;
                line-height: 1.8;
                color: #28455f;
            }}

            .circular-summary strong {{
                color: #173d65;
            }}
        </style>

        <section class="circular-queue-panel">
            <div class="circular-array">
                {''.join(slot_blocks)}
            </div>

            <div class="circular-summary">
                <strong>실제 데이터 순서</strong><br>
                FRONT 방향 → {order_text} → REAR 방향

                <br><br>

                <strong>현재 상태</strong><br>
                {state_text}
            </div>
        </section>
        """
    )


# ============================================================
# 3. front와 rear 이동 설명
# ============================================================

def render_pointer_information(
    queue: CircularQueue,
) -> None:
    """
    front와 rear의 현재 위치 및 다음 이동 위치를 표시합니다.
    """

    next_front = queue.next_front_index()
    next_rear = queue.next_rear_index()

    next_front_text = (
        str(next_front)
        if next_front is not None
        else "없음"
    )

    next_rear_text = (
        "삽입 불가"
        if queue.is_full()
        else str(next_rear)
    )

    render_html(
        f"""
        <section class="status-panel">
            <div class="status-title">
                front와 rear 위치
            </div>

            <div class="status-item">
                <span class="status-label">
                    front
                </span>

                <span class="status-value">
                    {queue.front}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    rear
                </span>

                <span class="status-value">
                    {queue.rear}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    다음 삭제 위치
                </span>

                <span class="status-value">
                    {next_front_text}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    다음 삽입 위치
                </span>

                <span class="status-value">
                    {next_rear_text}
                </span>
            </div>
        </section>
        """
    )


# ============================================================
# 4. 원형 큐 상태 표시
# ============================================================

def render_circular_queue_status(
    queue: CircularQueue,
) -> None:
    """
    원형 큐의 전체 상태를 표시합니다.
    """

    data_values = queue.data_values()

    if data_values:
        data_text = " → ".join(
            escape(str(value))
            for value in data_values
        )
    else:
        data_text = "없음"

    if queue.is_empty():
        status_text = "공백"
    elif queue.is_full():
        status_text = "포화"
    else:
        status_text = "저장 중"

    render_html(
        f"""
        <section class="status-panel">
            <div class="status-title">
                원형 큐 현재 상태
            </div>

            <div class="status-item">
                <span class="status-label">
                    배열 크기
                </span>

                <span class="status-value">
                    {queue.max_size}칸
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    실제 저장 용량
                </span>

                <span class="status-value">
                    {queue.capacity()}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    저장된 데이터
                </span>

                <span class="status-value">
                    {queue.size()}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    남은 공간
                </span>

                <span class="status-value">
                    {queue.remaining_space()}칸
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    현재 상태
                </span>

                <span class="status-value">
                    {status_text}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    처리 순서
                </span>

                <span class="status-value">
                    {data_text}
                </span>
            </div>
        </section>
        """
    )


# ============================================================
# 5. Python 코드 표시
# ============================================================

def render_circular_queue_code(
    active_operation: str | None = None,
) -> None:
    """
    원형 큐의 주요 Python 코드를 표시합니다.
    """

    enqueue_code = """
def enqueue(data):
    global rear

    if (rear + 1) % SIZE == front:
        print("원형 큐가 포화 상태입니다.")
        return

    rear = (rear + 1) % SIZE
    queue[rear] = data
"""

    dequeue_code = """
def dequeue():
    global front

    if front == rear:
        print("원형 큐가 공백 상태입니다.")
        return None

    front = (front + 1) % SIZE
    data = queue[front]
    queue[front] = None

    return data
"""

    empty_full_code = """
def is_empty():
    return front == rear


def is_full():
    return (rear + 1) % SIZE == front
"""

    initialize_code = """
SIZE = 5

queue = [
    None
    for _ in range(SIZE)
]

front = 0
rear = 0
"""

    st.markdown(
        "#### 원형 큐 Python 코드"
    )

    tabs = st.tabs(
        [
            "초기화",
            "Enqueue",
            "Dequeue",
            "공백·포화 확인",
        ]
    )

    with tabs[0]:
        st.code(
            initialize_code.strip(),
            language="python",
        )

    with tabs[1]:
        st.code(
            enqueue_code.strip(),
            language="python",
        )

        if active_operation in {
            "enqueue",
            "enqueue_many",
        }:
            st.caption(
                "현재 실행한 기능: 원형 큐 Enqueue"
            )

    with tabs[2]:
        st.code(
            dequeue_code.strip(),
            language="python",
        )

        if active_operation == "dequeue":
            st.caption(
                "현재 실행한 기능: 원형 큐 Dequeue"
            )

    with tabs[3]:
        st.code(
            empty_full_code.strip(),
            language="python",
        )


# ============================================================
# 6. 원형 큐 연산 기록
# ============================================================

def render_circular_operation_history(
    history: list[dict],
) -> None:
    """
    원형 큐의 연산 기록을 표시합니다.
    """

    if not history:
        st.info(
            "아직 실행한 원형 큐 연산이 없습니다."
        )
        return

    for index, result in enumerate(
        reversed(history),
        start=1,
    ):
        action = escape(
            str(result.get("action", "연산"))
        )

        message = escape(
            str(result.get("message", ""))
        )

        front = result.get(
            "front",
            "-"
        )

        rear = result.get(
            "rear",
            "-"
        )

        success_text = (
            "성공"
            if result.get("success")
            else "실패"
        )

        st.markdown(
            f"""
**{index}. {action} · {success_text}**

{message}

`front = {front}` · `rear = {rear}`
            """
        )

        st.divider()