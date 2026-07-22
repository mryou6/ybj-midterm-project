"""
Queue 자료구조 시각화 모듈입니다.

주요 기능
- Queue 데이터 시각화
- FRONT와 REAR 표시
- 전체 저장 공간 표시
- 현재 상태 표시
- 연산 결과 표시
- Python 코드 표시
- 연산 기록 표시
"""

from html import escape
from typing import Any

import streamlit as st

from modules.common import render_html


# ============================================================
# 1. 값 변환
# ============================================================

def format_value(value: Any) -> str:
    """
    사용자 입력값을 HTML에 안전하게 표시합니다.
    """

    return escape(str(value))


# ============================================================
# 2. 현재 데이터 시각화
# ============================================================

def render_queue(
    items: list[Any],
    max_size: int
) -> None:
    """
    Queue 데이터를 왼쪽에서 오른쪽으로 표시합니다.

    왼쪽:
        FRONT, 다음에 나올 데이터

    오른쪽:
        REAR, 가장 최근에 들어온 데이터
    """

    if max_size <= 0:
        st.error(
            "Queue의 최대 크기는 1 이상이어야 합니다."
        )
        return

    if not items:
        render_html(
            """
            <div class="queue-wrapper">
                <div class="queue-empty">
                    <div class="empty-state-icon">🚏</div>
                    Queue가 비어 있습니다.<br>
                    값을 입력하고 Enqueue를 눌러 보세요.
                </div>
            </div>
            """
        )
        return

    blocks = []

    for index, value in enumerate(items):
        is_front = index == 0
        is_rear = index == len(items) - 1

        classes = ["queue-item"]
        marker_parts = []

        if is_front:
            classes.append("queue-item-front")
            marker_parts.append("FRONT")

        if is_rear:
            classes.append("queue-item-rear")
            marker_parts.append("REAR")

        class_name = " ".join(classes)

        marker_text = ""

        if marker_parts:
            marker_text = (
                '<div class="queue-marker">'
                + " · ".join(marker_parts)
                + "</div>"
            )

        blocks.append(
            f"""
            <div class="{class_name}">
                {marker_text}
                <div>{format_value(value)}</div>
            </div>
            """
        )

        if index < len(items) - 1:
            blocks.append(
                """
                <div class="queue-direction">
                    →
                </div>
                """
            )

    render_html(
        f"""
        <div style="
            margin-bottom: 0.5rem;
            color: #607386;
            font-weight: 600;
        ">
            데이터가 나가는 방향 →
        </div>

        <div class="queue-wrapper">
            {''.join(blocks)}
        </div>
        """
    )


# ============================================================
# 3. 전체 저장 공간 시각화
# ============================================================

def render_queue_slots(
    items: list[Any],
    max_size: int
) -> None:
    """
    Queue의 사용 중인 공간과 빈 공간을 함께 표시합니다.
    """

    if max_size <= 0:
        st.error(
            "Queue의 최대 크기는 1 이상이어야 합니다."
        )
        return

    used_count = len(items)
    empty_count = max_size - used_count

    blocks = []

    for index in range(max_size):
        if index < used_count:
            value = items[index]

            is_front = index == 0
            is_rear = index == used_count - 1

            classes = ["queue-item"]
            marker_parts = []

            if is_front:
                classes.append("queue-item-front")
                marker_parts.append("FRONT")

            if is_rear:
                classes.append("queue-item-rear")
                marker_parts.append("REAR")

            class_name = " ".join(classes)

            marker_text = ""

            if marker_parts:
                marker_text = (
                    '<div class="queue-marker">'
                    + " · ".join(marker_parts)
                    + "</div>"
                )

            blocks.append(
                f"""
                <div class="{class_name}">
                    {marker_text}
                    <div>{format_value(value)}</div>
                </div>
                """
            )

        else:
            blocks.append(
                """
                <div class="queue-item"
                     style="
                         border-style: dashed;
                         background-color: transparent;
                         color: #8a99a8;
                     ">
                    빈 공간
                </div>
                """
            )

        if index < max_size - 1:
            blocks.append(
                """
                <div class="queue-direction">
                    →
                </div>
                """
            )

    render_html(
        f"""
        <div style="
            margin-bottom: 0.5rem;
            color: #607386;
            font-weight: 600;
        ">
            FRONT에서 나가고 REAR로 들어옵니다.
        </div>

        <div class="queue-wrapper">
            {''.join(blocks)}
        </div>
        """
    )

    st.caption(
        f"사용 중인 공간: {used_count}칸 · "
        f"남은 공간: {empty_count}칸"
    )


# ============================================================
# 4. Queue 상태 표시
# ============================================================

def render_queue_status(
    items: list[Any],
    max_size: int
) -> None:
    """
    Queue의 주요 상태를 정보 패널로 표시합니다.
    """

    current_size = len(items)
    remaining_space = max_size - current_size

    front_value = (
        format_value(items[0])
        if items
        else "없음"
    )

    rear_value = (
        format_value(items[-1])
        if items
        else "없음"
    )

    state_text = (
        "가득 참"
        if current_size >= max_size
        else "저장 가능"
    )

    render_html(
        f"""
        <section class="status-panel">
            <div class="status-title">
                현재 Queue 상태
            </div>

            <div class="status-item">
                <span class="status-label">
                    저장된 데이터 수
                </span>
                <span class="status-value">
                    {current_size}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    최대 저장 가능 수
                </span>
                <span class="status-value">
                    {max_size}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    남은 공간
                </span>
                <span class="status-value">
                    {remaining_space}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    현재 FRONT
                </span>
                <span class="status-value">
                    {front_value}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    현재 REAR
                </span>
                <span class="status-value">
                    {rear_value}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    다음 Dequeue 값
                </span>
                <span class="status-value">
                    {front_value}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    현재 상태
                </span>
                <span class="status-value">
                    {state_text}
                </span>
            </div>
        </section>
        """
    )


# ============================================================
# 5. 최근 연산 메시지
# ============================================================

def render_operation_message(
    operation_result: dict | None
) -> None:
    """
    가장 최근에 실행한 Queue 연산 결과를 표시합니다.
    """

    if not operation_result:
        render_html(
            """
            <div class="info-box">
                아직 실행한 연산이 없습니다.<br>
                값을 입력하고 Enqueue 버튼을 눌러 보세요.
            </div>
            """
        )
        return

    success = bool(
        operation_result.get(
            "success",
            False
        )
    )

    message = escape(
        str(
            operation_result.get(
                "message",
                ""
            )
        )
    )

    concept = escape(
        str(
            operation_result.get(
                "concept",
                ""
            )
        )
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
            <br>
            {concept}
        </div>
        """
    )


# ============================================================
# 6. Python 코드 표시
# ============================================================

def render_queue_code(
    active_operation: str | None = None
) -> None:
    """
    Queue의 핵심 Python 코드를 표시합니다.
    """

    operation_names = {
        "enqueue": "Enqueue",
        "dequeue": "Dequeue",
        "front": "Front",
        "rear": "Rear",
        "clear": "초기화",
    }

    active_name = operation_names.get(
        active_operation,
        "연산 없음"
    )

    st.markdown(
        f"**현재 실행한 연산: `{active_name}`**"
    )

    code_text = """def enqueue(value):
    queue.append(value)

def dequeue():
    return queue.pop(0)

def front():
    return queue[0]

def rear():
    return queue[-1]
"""

    st.code(
        code_text,
        language="python",
        line_numbers=True
    )


# ============================================================
# 7. 연산 기록 표시
# ============================================================

def render_operation_history(
    history: list[dict]
) -> None:
    """
    최근 Queue 연산 기록을 표시합니다.
    """

    if not history:
        st.info(
            "아직 저장된 연산 기록이 없습니다."
        )
        return

    history_blocks = []

    for number, item in enumerate(
        reversed(history[-10:]),
        start=1
    ):
        action = escape(
            str(
                item.get(
                    "action",
                    "-"
                )
            ).upper()
        )

        message = escape(
            str(
                item.get(
                    "message",
                    ""
                )
            )
        )

        history_blocks.append(
            f"""
            <div class="step-item">
                {number}. [{action}] {message}
            </div>
            """
        )

    render_html(
        f"""
        <section class="step-panel">
            <div class="step-title">
                최근 연산 기록
            </div>

            {''.join(history_blocks)}
        </section>
        """
    )