"""
Stack 자료구조 시각화 모듈입니다.

주요 기능
- Stack 블록 시각화
- 전체 저장 공간 표시
- TOP 표시
- 현재 상태 표시
- 최근 연산 메시지
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

def render_stack(
    items: list[Any],
    max_size: int
) -> None:
    """
    Stack 데이터를 위에서 아래로 표시합니다.

    화면 맨 위:
        가장 최근에 삽입한 TOP

    화면 맨 아래:
        가장 먼저 삽입한 데이터
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
                    값을 입력하고 Push를 눌러 보세요.
                </div>
            </div>
            """
        )
        return

    blocks = []

    # 마지막 데이터가 TOP이므로 역순으로 표시
    for display_index, value in enumerate(reversed(items)):
        is_top = display_index == 0

        classes = ["stack-item"]

        if is_top:
            classes.append("stack-item-top")

        class_name = " ".join(classes)

        top_text = (
            '<div class="stack-label">'
            'TOP · 가장 먼저 나올 데이터'
            '</div>'
            if is_top
            else ""
        )

        blocks.append(
            f"""
            <div class="{class_name}">
                {top_text}
                <div>{format_value(value)}</div>
            </div>
            """
        )

    render_html(
        f"""
        <div class="stack-wrapper"
             style="flex-direction: column;">
            {''.join(blocks)}
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
    데이터와 빈 저장 공간을 함께 표시합니다.
    """

    if max_size <= 0:
        st.error(
            "Stack의 최대 크기는 1 이상이어야 합니다."
        )
        return

    blocks = []

    used_count = len(items)
    empty_count = max_size - used_count

    # 빈 공간은 위쪽, 사용 데이터는 아래쪽에 배치하되
    # 사용 데이터 중 TOP은 가장 위에 표시
    for stack_index in range(max_size - 1, -1, -1):

        if stack_index >= used_count:
            blocks.append(
                """
                <div class="stack-item"
                     style="
                         border-style: dashed;
                         background-color: transparent;
                         color: #8a99a8;
                     ">
                    빈 공간
                </div>
                """
            )

        else:
            value = items[stack_index]
            is_top = stack_index == used_count - 1

            class_name = (
                "stack-item stack-item-top"
                if is_top
                else "stack-item"
            )

            top_text = (
                '<div class="stack-label">TOP</div>'
                if is_top
                else ""
            )

            blocks.append(
                f"""
                <div class="{class_name}">
                    {top_text}
                    <div>{format_value(value)}</div>
                </div>
                """
            )

    render_html(
        f"""
        <div class="stack-wrapper"
             style="flex-direction: column;">
            {''.join(blocks)}
        </div>
        """
    )

    st.caption(
        f"사용 중인 공간: {used_count}칸 · "
        f"남은 공간: {empty_count}칸"
    )


# ============================================================
# 4. 현재 상태 패널
# ============================================================

def render_stack_status(
    items: list[Any],
    max_size: int
) -> None:
    """
    Stack의 현재 상태를 표 형태로 표시합니다.
    """

    current_size = len(items)
    remaining_space = max_size - current_size

    top_value = (
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
                    {top_value}
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
# 5. 연산 메시지
# ============================================================

def render_operation_message(
    operation_result: dict | None
) -> None:
    """
    가장 최근에 실행한 연산 결과를 표시합니다.
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
            <strong>{message}</strong>
            <br>
            {concept}
        </div>
        """
    )


# ============================================================
# 6. Python 코드
# ============================================================

def render_stack_code(
    active_operation: str | None = None
) -> None:
    """
    Stack 핵심 코드를 실제 코드 블록으로 출력합니다.
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
        f"**현재 실행한 연산: `{active_name}`**"
    )

    code_text = """def push(value):
    stack.append(value)

def pop():
    return stack.pop()

def peek():
    return stack[-1]
"""

    st.code(
        code_text,
        language="python",
        line_numbers=True
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