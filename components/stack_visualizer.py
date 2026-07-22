"""
Stack 자료구조를 HTML로 시각화하는 모듈입니다.

주요 기능
- Stack 블록 시각화
- TOP 표시
- 빈 공간 표시
- 현재 상태 표시
- 연산 결과 및 기록 표시
"""

from html import escape
from typing import Any

import streamlit as st

from modules.common import render_html


# ============================================================
# 1. 값 출력 형식
# ============================================================

def format_value(value: Any) -> str:
    """
    값을 HTML에 안전하게 표시할 수 있도록 변환합니다.
    """

    return escape(str(value))


# ============================================================
# 2. 현재 데이터만 시각화
# ============================================================

def render_stack(
    items: list[Any],
    max_size: int
) -> None:
    """
    현재 Stack 데이터를 세로 구조로 표시합니다.

    가장 최근에 들어온 값이 화면의 가장 위에 표시됩니다.
    """

    if max_size <= 0:
        st.error(
            "Stack의 최대 크기는 1 이상이어야 합니다."
        )
        return

    if not items:
        render_html(
            """
            <div class="stack-wrapper"
                 style="flex-direction: column;">
                <div class="stack-empty">
                    <div class="empty-state-icon">📭</div>
                    Stack이 비어 있습니다.<br>
                    값을 입력한 뒤 Push 버튼을 눌러 보세요.
                </div>
            </div>
            """
        )
        return

    item_blocks = []

    # 가장 최근에 삽입된 값부터 화면 위에 표시
    reversed_items = list(reversed(items))

    for display_index, value in enumerate(reversed_items):
        is_top = display_index == 0

        item_class = "stack-item"
        top_label = ""

        if is_top:
            item_class += " stack-item-top"

            top_label = (
                '<div class="stack-label">'
                'TOP · 가장 먼저 나올 데이터'
                '</div>'
            )

        item_blocks.append(
            f"""
            <div class="{item_class}">
                {top_label}
                <div>{format_value(value)}</div>
            </div>
            """
        )

    stack_content = "\n".join(item_blocks)

    render_html(
        f"""
        <div class="stack-wrapper"
             style="flex-direction: column;">
            {stack_content}
        </div>
        """
    )


# ============================================================
# 3. 전체 저장 공간 시각화
# ============================================================

def render_stack_slots(
    items: list[Any],
    max_size: int
) -> None:
    """
    사용 중인 공간과 빈 공간을 함께 표시합니다.
    """

    if max_size <= 0:
        st.error(
            "Stack의 최대 크기는 1 이상이어야 합니다."
        )
        return

    used_count = len(items)
    empty_count = max_size - used_count

    slot_blocks = []

    # 화면 위쪽부터 TOP → 하단 순서로 표시
    for stack_index in range(max_size - 1, -1, -1):
        if stack_index < used_count:
            value = items[stack_index]
            is_top = stack_index == used_count - 1

            item_class = "stack-item"
            label = ""

            if is_top:
                item_class += " stack-item-top"
                label = (
                    '<div class="stack-label">'
                    'TOP'
                    '</div>'
                )

            slot_blocks.append(
                f"""
                <div class="{item_class}">
                    {label}
                    <div>{format_value(value)}</div>
                </div>
                """
            )

        else:
            slot_blocks.append(
                """
                <div class="stack-item"
                     style="
                         border-style: dashed;
                         background-color: transparent;
                         color: #9aa8b5;
                     ">
                    빈 공간
                </div>
                """
            )

    slots_html = "\n".join(slot_blocks)

    render_html(
        f"""
        <div class="stack-wrapper"
             style="flex-direction: column;">
            {slots_html}
        </div>
        """
    )

    st.caption(
        f"사용 중인 공간: {used_count}칸 · "
        f"남은 공간: {empty_count}칸"
    )


# ============================================================
# 4. Stack 상태 표시
# ============================================================

def render_stack_status(
    items: list[Any],
    max_size: int
) -> None:
    """
    Stack의 주요 상태를 정보 패널로 표시합니다.
    """

    current_size = len(items)
    remaining_space = max_size - current_size

    top_value = (
        format_value(items[-1])
        if items
        else "없음"
    )

    stack_status = (
        "가득 참"
        if current_size >= max_size
        else "저장 가능"
    )

    render_html(
        f"""
        <div class="status-panel">
            <div class="status-title">
                현재 Stack 상태
            </div>

            <div class="status-item">
                <span class="status-label">저장된 데이터 수</span>
                <span class="status-value">{current_size}개</span>
            </div>

            <div class="status-item">
                <span class="status-label">최대 저장 가능 수</span>
                <span class="status-value">{max_size}개</span>
            </div>

            <div class="status-item">
                <span class="status-label">남은 공간</span>
                <span class="status-value">{remaining_space}개</span>
            </div>

            <div class="status-item">
                <span class="status-label">현재 TOP</span>
                <span class="status-value">{top_value}</span>
            </div>

            <div class="status-item">
                <span class="status-label">다음 Pop 값</span>
                <span class="status-value">{top_value}</span>
            </div>

            <div class="status-item">
                <span class="status-label">Stack 상태</span>
                <span class="status-value">{stack_status}</span>
            </div>
        </div>
        """
    )


# ============================================================
# 5. 최근 연산 메시지
# ============================================================

def render_operation_message(
    operation_result: dict | None
) -> None:
    """
    최근 실행한 Stack 연산 결과를 표시합니다.
    """

    if not operation_result:
        render_html(
            """
            <div class="info-box">
                아직 실행한 연산이 없습니다.<br>
                값을 입력하고 Push 버튼을 눌러 보세요.
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
            <strong>{message}</strong><br>
            {concept}
        </div>
        """
    )


# ============================================================
# 6. 간단한 코드 표시
# ============================================================

def render_stack_code(
    active_operation: str | None = None
) -> None:
    """
    Stack의 핵심 Python 코드를 표시합니다.
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

    code_text = (
        f"# 현재 실행한 연산: {active_name}\n\n"
        "def push(value):\n"
        "    stack.append(value)\n\n"
        "def pop():\n"
        "    return stack.pop()\n\n"
        "def peek():\n"
        "    return stack[-1]"
    )

    render_html(
        f"""
        <div class="data-code">
            <pre style="
                margin: 0;
                white-space: pre-wrap;
                font-family: Consolas, 'Courier New', monospace;
            ">{escape(code_text)}</pre>
        </div>
        """
    )


# ============================================================
# 7. 연산 기록
# ============================================================

def render_operation_history(
    history: list[dict]
) -> None:
    """
    최근 Stack 연산 기록을 표시합니다.
    """

    if not history:
        st.info(
            "아직 저장된 연산 기록이 없습니다."
        )
        return

    recent_history = history[-10:]

    history_blocks = []

    for number, item in enumerate(
        reversed(recent_history),
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

    history_html = "\n".join(history_blocks)

    render_html(
        f"""
        <div class="step-panel">
            <div class="step-title">
                최근 연산 기록
            </div>

            {history_html}
        </div>
        """
    )