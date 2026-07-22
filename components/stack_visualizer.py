"""
Stack 자료구조를 HTML로 시각화하는 모듈입니다.

주요 기능
- Stack 블록 시각화
- TOP 표시
- 빈 공간 표시
- 현재 상태 정보 표시
- 연산 기록 표시
"""


from html import escape
from typing import Any

import streamlit as st


def format_value(value: Any) -> str:
    """
    HTML에 안전하게 표시할 수 있도록 값을 문자열로 변환합니다.
    """

    return escape(str(value))


def render_stack(
    items: list[Any],
    max_size: int
) -> None:
    """
    Stack의 현재 상태를 세로 블록 형태로 표시합니다.

    Args:
        items: Stack에 저장된 값
        max_size: Stack의 최대 크기
    """

    if max_size <= 0:
        st.error(
            "Stack의 최대 크기는 1 이상이어야 합니다."
        )
        return

    if not items:
        stack_content = """
        <div class="stack-empty">
            <div class="empty-state-icon">📭</div>
            Stack이 비어 있습니다.<br>
            값을 입력한 뒤 Push 버튼을 눌러 보세요.
        </div>
        """

    else:
        item_html = []

        for index, value in enumerate(items):
            is_top = index == len(items) - 1

            item_class = "stack-item"

            top_label = ""

            if is_top:
                item_class += " stack-item-top"

                top_label = """
                <div class="stack-label">
                    TOP · 가장 먼저 나올 데이터
                </div>
                """

            item_html.append(
                f"""
                <div class="{item_class}">
                    {top_label}
                    <div>{format_value(value)}</div>
                </div>
                """
            )

        stack_content = "\n".join(item_html)

    st.markdown(
        f"""
        <div class="stack-wrapper">
            {stack_content}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_stack_slots(
    items: list[Any],
    max_size: int
) -> None:
    """
    사용된 공간과 남은 공간을 슬롯 형태로 표시합니다.

    Args:
        items: Stack 데이터
        max_size: 최대 크기
    """

    used_count = len(items)
    empty_count = max_size - used_count

    slot_html = []

    for index in range(max_size - 1, -1, -1):
        if index < used_count:
            value = items[index]

            if index == used_count - 1:
                slot_class = "stack-item stack-item-top"
                label = (
                    '<div class="stack-label">TOP</div>'
                )
            else:
                slot_class = "stack-item"
                label = ""

            slot_html.append(
                f"""
                <div class="{slot_class}">
                    {label}
                    {format_value(value)}
                </div>
                """
            )

        else:
            slot_html.append(
                """
                <div
                    class="stack-item"
                    style="
                        border-style: dashed;
                        background-color: transparent;
                        color: #9aa8b5;
                    "
                >
                    빈 공간
                </div>
                """
            )

    st.markdown(
        f"""
        <div class="stack-wrapper">
            {''.join(slot_html)}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        f"사용 중인 공간: {used_count}칸 · "
        f"남은 공간: {empty_count}칸"
    )


def render_stack_status(
    items: list[Any],
    max_size: int
) -> None:
    """
    Stack의 주요 상태를 정보 패널로 표시합니다.
    """

    current_size = len(items)

    top_value = (
        format_value(items[-1])
        if items
        else "없음"
    )

    next_pop_value = (
        format_value(items[-1])
        if items
        else "없음"
    )

    remaining_space = max_size - current_size

    status_text = (
        "가득 참"
        if current_size >= max_size
        else "저장 가능"
    )

    st.markdown(
        f"""
        <div class="status-panel">
            <div class="status-title">
                현재 Stack 상태
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
                    현재 TOP
                </span>
                <span class="status-value">
                    {top_value}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    다음 Pop 값
                </span>
                <span class="status-value">
                    {next_pop_value}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    Stack 상태
                </span>
                <span class="status-value">
                    {status_text}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_operation_message(
    operation_result: dict | None
) -> None:
    """
    가장 최근에 실행한 Stack 연산 결과를 표시합니다.

    Args:
        operation_result: Stack 클래스의 연산 결과
    """

    if not operation_result:
        st.markdown(
            """
            <div class="info-box">
                아직 실행한 연산이 없습니다.
                값을 입력하고 Push 버튼을 눌러 보세요.
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    success = operation_result.get(
        "success",
        False
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

    st.markdown(
        f"""
        <div class="{box_class}">
            <strong>{message}</strong>
            <br>
            {concept}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_stack_code(
    active_operation: str | None = None
) -> None:
    """
    Stack 연산의 간단한 Python 코드를 표시합니다.

    Args:
        active_operation: 최근 실행한 연산
    """

    operation_names = {
        "push": "Push",
        "pop": "Pop",
        "peek": "Peek",
        "clear": "초기화",
    }

    active_name = operation_names.get(
        active_operation,
        "연산 없음"
    )

    st.markdown(
        f"""
        <div class="data-code">
            <div>
                # 현재 실행한 연산: {active_name}
            </div>
            <br>

            <div>
                def push(value):
            </div>
            <div>
                &nbsp;&nbsp;&nbsp;&nbsp;stack.append(value)
            </div>
            <br>

            <div>
                def pop():
            </div>
            <div>
                &nbsp;&nbsp;&nbsp;&nbsp;return stack.pop()
            </div>
            <br>

            <div>
                def peek():
            </div>
            <div>
                &nbsp;&nbsp;&nbsp;&nbsp;return stack[-1]
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_operation_history(
    history: list[dict]
) -> None:
    """
    사용자가 실행한 연산 기록을 표시합니다.

    Args:
        history: 연산 기록 목록
    """

    if not history:
        st.info(
            "아직 저장된 연산 기록이 없습니다."
        )
        return

    st.markdown(
        '<div class="step-panel">',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="step-title">
            최근 연산 기록
        </div>
        """,
        unsafe_allow_html=True
    )

    recent_history = history[-10:]

    for number, item in enumerate(
        reversed(recent_history),
        start=1
    ):
        action = item.get(
            "action",
            "-"
        )

        value = item.get(
            "value",
            "-"
        )

        message = item.get(
            "message",
            ""
        )

        st.markdown(
            f"""
            <div class="step-item">
                {number}. [{escape(str(action)).upper()}]
                {escape(str(message))}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )