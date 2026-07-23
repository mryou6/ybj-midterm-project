"""
Stack 활용 기능의 시각화 컴포넌트입니다.

지원 기능
1. 괄호 검사 결과 시각화
2. 후위 표기법 계산 결과 시각화
3. 단계별 Stack 상태 표시
4. 이전 단계·다음 단계 이동
5. 전체 처리 과정 표시
6. 활용 사례 Python 코드 표시

이 파일은 modules/stack_application_logic.py에서 반환한
결과 딕셔너리를 화면에 표시합니다.
"""

from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from modules.common import render_html


# ============================================================
# 1. 공통 보조 함수
# ============================================================

def format_display_value(
    value: Any,
) -> str:
    """
    화면에 표시하기 적절한 문자열로 값을 변환합니다.
    """

    if value is None:
        return ""

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))

        return (
            f"{value:.10f}"
            .rstrip("0")
            .rstrip(".")
        )

    return str(value)


def format_stack_text(
    stack_values: list[Any] | None,
) -> str:
    """
    Stack 값을 BOTTOM부터 TOP 방향의 문자열로 변환합니다.
    """

    if not stack_values:
        return "비어 있음"

    return " → ".join(
        format_display_value(value)
        for value in stack_values
    )


def get_operation_label(
    operation: str | None,
) -> str:
    """
    내부 연산 이름을 사용자용 한글 표현으로 변환합니다.
    """

    operation_labels = {
        "push": "Push",
        "pop": "Pop",
        "calculate": "계산 후 Push",
        "complete": "검사 완료",
        "error": "오류 발견",
    }

    return operation_labels.get(
        operation,
        operation or "확인",
    )


def get_operation_icon(
    operation: str | None,
) -> str:
    """
    연산 유형에 알맞은 아이콘을 반환합니다.
    """

    operation_icons = {
        "push": "📥",
        "pop": "📤",
        "calculate": "🧮",
        "complete": "✅",
        "error": "⚠️",
    }

    return operation_icons.get(
        operation,
        "🔍",
    )


def get_result_type(
    result: dict | None,
) -> str:
    """
    실행 결과의 기능 유형을 판별합니다.
    """

    if not result:
        return "unknown"

    action = result.get(
        "action"
    )

    if action == "bracket_check":
        return "bracket"

    if action == "postfix_calculate":
        return "postfix"

    return "unknown"


# ============================================================
# 2. 최종 실행 결과 표시
# ============================================================

def render_application_result(
    result: dict | None,
) -> None:
    """
    Stack 활용 기능의 최종 결과를 표시합니다.

    괄호 검사:
        올바른 괄호식인지 표시

    후위 표기법:
        최종 계산값 표시
    """

    if not result:
        return

    success = bool(
        result.get("success")
    )

    message = escape(
        str(
            result.get(
                "message",
                "",
            )
        )
    )

    concept = escape(
        str(
            result.get(
                "concept",
                "",
            )
        )
    )

    result_type = get_result_type(
        result
    )

    if success:
        box_class = "quiz-result-correct"
        result_icon = "✅"
        result_title = "실행 결과"

    else:
        box_class = "quiz-result-wrong"
        result_icon = "⚠️"
        result_title = "확인 결과"

    additional_html = ""

    if (
        result_type == "postfix"
        and success
    ):
        final_result = escape(
            format_display_value(
                result.get("result")
            )
        )

        additional_html = f"""
        <div class="application-final-value">
            최종 계산 결과
            <strong>{final_result}</strong>
        </div>
        """

    elif (
        result_type == "bracket"
        and success
    ):
        additional_html = """
        <div class="application-final-value">
            최종 Stack
            <strong>비어 있음</strong>
        </div>
        """

    elif not success:
        error_index = result.get(
            "error_index"
        )

        error_token = result.get(
            "error_token"
        )

        error_details: list[str] = []

        if error_index is not None:
            error_details.append(
                f"오류 위치: {escape(str(error_index))}"
            )

        if error_token is not None:
            error_details.append(
                f"오류 문자·토큰: "
                f"{escape(str(error_token))}"
            )

        if error_details:
            additional_html = f"""
            <div class="application-error-details">
                {' · '.join(error_details)}
            </div>
            """

    render_html(
        f"""
        <style>
            .application-final-value {{
                margin-top: 14px;
                padding: 12px 16px;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.72);
                font-size: 15px;
            }}

            .application-final-value strong {{
                margin-left: 8px;
                font-size: 20px;
            }}

            .application-error-details {{
                margin-top: 13px;
                font-size: 14px;
                font-weight: 600;
            }}
        </style>

        <section class="{box_class}">
            <div style="
                margin-bottom: 8px;
                font-size: 18px;
                font-weight: 800;
            ">
                {result_icon} {result_title}
            </div>

            <div>
                {message}
            </div>

            {additional_html}

            {
                f'''
                <div style="
                    margin-top: 14px;
                    line-height: 1.7;
                    font-size: 14px;
                ">
                    {concept}
                </div>
                '''
                if concept
                else ""
            }
        </section>
        """
    )


# ============================================================
# 3. 단계별 Stack 시각화
# ============================================================

def render_application_stack(
    stack_values: list[Any] | None,
    title: str = "현재 Stack",
    highlighted_value: Any | None = None,
) -> None:
    """
    Stack 상태를 세로 방향으로 표시합니다.

    리스트의 마지막 값이 TOP에 위치합니다.

    Args:
        stack_values:
            BOTTOM부터 TOP 순서로 저장된 Stack 값

        title:
            시각화 제목

        highlighted_value:
            강조해서 표시할 값
    """

    values = list(
        stack_values or []
    )

    if not values:
        render_html(
            f"""
            <section class="application-stack-panel">
                <div class="application-stack-title">
                    {escape(title)}
                </div>

                <div class="application-empty-stack">
                    Stack이 비어 있습니다.
                </div>

                <div class="application-stack-bottom">
                    BOTTOM
                </div>
            </section>

            <style>
                .application-stack-panel {{
                    padding: 22px;
                    border: 1px solid #d6e1eb;
                    border-radius: 16px;
                    background: #f8fbfe;
                    min-height: 280px;
                }}

                .application-stack-title {{
                    margin-bottom: 18px;
                    color: #173d65;
                    font-size: 18px;
                    font-weight: 800;
                    text-align: center;
                }}

                .application-empty-stack {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 150px;
                    border: 2px dashed #b8c9d8;
                    border-radius: 14px;
                    background: #ffffff;
                    color: #8595a5;
                    font-size: 15px;
                }}

                .application-stack-bottom {{
                    margin-top: 12px;
                    color: #718398;
                    font-size: 12px;
                    font-weight: 700;
                    text-align: center;
                }}
            </style>
            """
        )
        return

    stack_blocks: list[str] = []

    reversed_values = list(
        reversed(values)
    )

    for visual_index, value in enumerate(
        reversed_values
    ):
        is_top = visual_index == 0

        value_text = escape(
            format_display_value(value)
        )

        is_highlighted = (
            highlighted_value is not None
            and value == highlighted_value
        )

        slot_classes = [
            "application-stack-slot",
        ]

        if is_top:
            slot_classes.append(
                "top-slot"
            )

        if is_highlighted:
            slot_classes.append(
                "highlighted-slot"
            )

        labels: list[str] = []

        if is_top:
            labels.append(
                """
                <span class="application-stack-label top-label">
                    TOP
                </span>
                """
            )

        if is_highlighted:
            labels.append(
                """
                <span class="
                    application-stack-label highlighted-label
                ">
                    현재 값
                </span>
                """
            )

        stack_blocks.append(
            f"""
            <div class="application-stack-row">
                <div class="{' '.join(slot_classes)}">
                    {value_text}
                </div>

                <div class="application-stack-label-area">
                    {''.join(labels)}
                </div>
            </div>
            """
        )

    render_html(
        f"""
        <style>
            .application-stack-panel {{
                padding: 22px;
                border: 1px solid #d6e1eb;
                border-radius: 16px;
                background: #f8fbfe;
                min-height: 280px;
            }}

            .application-stack-title {{
                margin-bottom: 18px;
                color: #173d65;
                font-size: 18px;
                font-weight: 800;
                text-align: center;
            }}

            .application-stack-list {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
            }}

            .application-stack-row {{
                display: grid;
                grid-template-columns: minmax(140px, 220px) 85px;
                align-items: center;
                gap: 10px;
                width: 100%;
                justify-content: center;
            }}

            .application-stack-slot {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 55px;
                padding: 8px 14px;
                border: 2px solid #9ebbd5;
                border-radius: 10px;
                background: #ffffff;
                color: #173d65;
                font-size: 19px;
                font-weight: 800;
                box-sizing: border-box;
            }}

            .application-stack-slot.top-slot {{
                border-color: #3478b8;
                background: #eaf4ff;
            }}

            .application-stack-slot.highlighted-slot {{
                box-shadow: 0 0 0 3px rgba(52, 120, 184, 0.18);
                transform: scale(1.02);
            }}

            .application-stack-label-area {{
                min-height: 40px;
            }}

            .application-stack-label {{
                display: block;
                width: fit-content;
                margin: 2px 0;
                padding: 3px 9px;
                border-radius: 999px;
                font-size: 11px;
                font-weight: 800;
            }}

            .top-label {{
                background: #dceeff;
                color: #1c5f99;
            }}

            .highlighted-label {{
                background: #fff2d9;
                color: #8a5d00;
            }}

            .application-stack-bottom {{
                margin-top: 14px;
                color: #718398;
                font-size: 12px;
                font-weight: 700;
                text-align: center;
            }}
        </style>

        <section class="application-stack-panel">
            <div class="application-stack-title">
                {escape(title)}
            </div>

            <div class="application-stack-list">
                {''.join(stack_blocks)}
            </div>

            <div class="application-stack-bottom">
                BOTTOM
            </div>
        </section>
        """
    )


# ============================================================
# 4. 현재 단계 정보 표시
# ============================================================

def render_current_step_information(
    step: dict,
    current_index: int,
    total_steps: int,
    result_type: str,
) -> None:
    """
    현재 단계의 토큰, 연산, 설명 및 계산식을 표시합니다.
    """

    operation = step.get(
        "operation"
    )

    operation_label = get_operation_label(
        operation
    )

    operation_icon = get_operation_icon(
        operation
    )

    token = step.get(
        "token"
    )

    token_text = (
        escape(str(token))
        if token is not None
        else "최종 확인"
    )

    description = escape(
        str(
            step.get(
                "description",
                "",
            )
        )
    )

    calculation = step.get(
        "calculation"
    )

    calculation_html = ""

    if calculation:
        calculation_html = f"""
        <div class="application-calculation">
            <span>계산식</span>
            <strong>
                {escape(str(calculation))}
            </strong>
        </div>
        """

    operand_html = ""

    if (
        result_type == "postfix"
        and step.get("left_operand") is not None
        and step.get("right_operand") is not None
    ):
        left_operand = escape(
            format_display_value(
                step.get("left_operand")
            )
        )

        right_operand = escape(
            format_display_value(
                step.get("right_operand")
            )
        )

        operand_html = f"""
        <div class="application-operands">
            <div>
                <span>왼쪽 피연산자</span>
                <strong>{left_operand}</strong>
            </div>

            <div>
                <span>오른쪽 피연산자</span>
                <strong>{right_operand}</strong>
            </div>
        </div>
        """

    render_html(
        f"""
        <style>
            .application-step-card {{
                padding: 20px;
                border: 1px solid #d8e2eb;
                border-radius: 15px;
                background: #ffffff;
            }}

            .application-step-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 12px;
                margin-bottom: 14px;
            }}

            .application-step-number {{
                color: #667b90;
                font-size: 13px;
                font-weight: 700;
            }}

            .application-operation-badge {{
                padding: 5px 11px;
                border-radius: 999px;
                background: #e9f3fc;
                color: #245d8d;
                font-size: 13px;
                font-weight: 800;
            }}

            .application-token {{
                margin-bottom: 12px;
                color: #173d65;
                font-size: 24px;
                font-weight: 900;
            }}

            .application-step-description {{
                line-height: 1.75;
                color: #40566c;
                font-size: 15px;
            }}

            .application-calculation {{
                margin-top: 15px;
                padding: 12px 14px;
                border-radius: 10px;
                background: #f3f8fc;
            }}

            .application-calculation span {{
                display: block;
                margin-bottom: 5px;
                color: #6d7d8c;
                font-size: 12px;
                font-weight: 700;
            }}

            .application-calculation strong {{
                color: #173d65;
                font-size: 18px;
            }}

            .application-operands {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-top: 14px;
            }}

            .application-operands > div {{
                padding: 11px;
                border-radius: 10px;
                background: #fafbfd;
            }}

            .application-operands span {{
                display: block;
                margin-bottom: 5px;
                color: #748597;
                font-size: 12px;
            }}

            .application-operands strong {{
                color: #173d65;
                font-size: 18px;
            }}
        </style>

        <section class="application-step-card">
            <div class="application-step-header">
                <div class="application-step-number">
                    단계 {current_index + 1} / {total_steps}
                </div>

                <div class="application-operation-badge">
                    {operation_icon} {escape(operation_label)}
                </div>
            </div>

            <div class="application-token">
                {token_text}
            </div>

            <div class="application-step-description">
                {description}
            </div>

            {operand_html}
            {calculation_html}
        </section>
        """
    )


# ============================================================
# 5. 단계별 탐색 기능
# ============================================================

def render_step_navigator(
    result: dict | None,
    key_prefix: str,
) -> None:
    """
    실행 과정을 이전·다음 버튼으로 탐색합니다.

    Args:
        result:
            괄호 검사 또는 후위 표기법 실행 결과

        key_prefix:
            Streamlit 위젯 키 충돌을 막기 위한 접두어

            예:
                "bracket"
                "postfix"
    """

    if not result:
        st.info(
            "기능을 실행하면 단계별 Stack 변화가 표시됩니다."
        )
        return

    steps = result.get(
        "steps",
        [],
    )

    if not steps:
        st.info(
            "표시할 실행 단계가 없습니다."
        )
        return

    index_key = (
        f"{key_prefix}_application_step_index"
    )

    result_signature_key = (
        f"{key_prefix}_application_result_signature"
    )

    result_signature = str(
        [
            (
                step.get("token"),
                step.get("operation"),
                step.get("description"),
            )
            for step in steps
        ]
    )

    # 새로운 실행 결과가 들어오면 첫 단계로 초기화합니다.
    if (
        result_signature_key not in st.session_state
        or st.session_state[result_signature_key]
        != result_signature
    ):
        st.session_state[
            result_signature_key
        ] = result_signature

        st.session_state[
            index_key
        ] = 0

    if index_key not in st.session_state:
        st.session_state[
            index_key
        ] = 0

    current_index = st.session_state[
        index_key
    ]

    current_index = max(
        0,
        min(
            current_index,
            len(steps) - 1,
        ),
    )

    st.session_state[
        index_key
    ] = current_index

    current_step = steps[
        current_index
    ]

    result_type = get_result_type(
        result
    )

    # --------------------------------------------------------
    # 단계 이동 버튼
    # --------------------------------------------------------

    first_col, previous_col, count_col, next_col, last_col = (
        st.columns(
            [1, 1, 1.2, 1, 1]
        )
    )

    with first_col:
        first_clicked = st.button(
            "⏮ 처음",
            key=f"{key_prefix}_step_first",
            use_container_width=True,
            disabled=current_index == 0,
        )

    with previous_col:
        previous_clicked = st.button(
            "◀ 이전",
            key=f"{key_prefix}_step_previous",
            use_container_width=True,
            disabled=current_index == 0,
        )

    with count_col:
        st.markdown(
            (
                "<div style='"
                "padding-top: 10px;"
                "text-align: center;"
                "font-weight: 800;"
                "color: #173d65;"
                "'>"
                f"{current_index + 1} / {len(steps)}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    with next_col:
        next_clicked = st.button(
            "다음 ▶",
            key=f"{key_prefix}_step_next",
            use_container_width=True,
            disabled=current_index >= len(steps) - 1,
        )

    with last_col:
        last_clicked = st.button(
            "마지막 ⏭",
            key=f"{key_prefix}_step_last",
            use_container_width=True,
            disabled=current_index >= len(steps) - 1,
        )

    if first_clicked:
        st.session_state[
            index_key
        ] = 0
        st.rerun()

    if previous_clicked:
        st.session_state[
            index_key
        ] = max(
            0,
            current_index - 1,
        )
        st.rerun()

    if next_clicked:
        st.session_state[
            index_key
        ] = min(
            len(steps) - 1,
            current_index + 1,
        )
        st.rerun()

    if last_clicked:
        st.session_state[
            index_key
        ] = len(steps) - 1
        st.rerun()

    # --------------------------------------------------------
    # 현재 단계 표시
    # --------------------------------------------------------

    st.markdown("")

    information_col, stack_col = st.columns(
        [1.15, 1],
    )

    with information_col:
        render_current_step_information(
            step=current_step,
            current_index=current_index,
            total_steps=len(steps),
            result_type=result_type,
        )

        before_stack = current_step.get(
            "stack_before",
            [],
        )

        after_stack = current_step.get(
            "stack_after",
            [],
        )

        before_text = escape(
            format_stack_text(
                before_stack
            )
        )

        after_text = escape(
            format_stack_text(
                after_stack
            )
        )

        render_html(
            f"""
            <section class="status-panel">
                <div class="status-title">
                    Stack 변화
                </div>

                <div class="status-item">
                    <span class="status-label">
                        연산 전
                    </span>

                    <span class="status-value">
                        {before_text}
                    </span>
                </div>

                <div class="status-item">
                    <span class="status-label">
                        연산 후
                    </span>

                    <span class="status-value">
                        {after_text}
                    </span>
                </div>
            </section>
            """
        )

    with stack_col:
        highlighted_value = None

        if current_step.get(
            "operation"
        ) in {
            "push",
            "calculate",
        }:
            highlighted_value = current_step.get(
                "result"
            )

            if (
                result_type == "bracket"
                and current_step.get("token")
            ):
                highlighted_value = current_step.get(
                    "token"
                )

        render_application_stack(
            stack_values=current_step.get(
                "stack_after",
                [],
            ),
            title="연산 후 Stack",
            highlighted_value=highlighted_value,
        )


# ============================================================
# 6. 전체 단계 표
# ============================================================

def render_steps_table(
    result: dict | None,
) -> None:
    """
    전체 실행 단계를 표로 표시합니다.
    """

    if not result:
        return

    steps = result.get(
        "steps",
        [],
    )

    if not steps:
        return

    result_type = get_result_type(
        result
    )

    rows: list[dict[str, Any]] = []

    for index, step in enumerate(
        steps,
        start=1,
    ):
        token = step.get(
            "token"
        )

        token_text = (
            str(token)
            if token is not None
            else "최종 확인"
        )

        row = {
            "단계": index,
            "문자·토큰": token_text,
            "연산": get_operation_label(
                step.get("operation")
            ),
            "연산 전 Stack": format_stack_text(
                step.get(
                    "stack_before",
                    [],
                )
            ),
            "연산 후 Stack": format_stack_text(
                step.get(
                    "stack_after",
                    [],
                )
            ),
            "설명": step.get(
                "description",
                "",
            ),
        }

        if result_type == "postfix":
            row["계산식"] = (
                step.get("calculation")
                or ""
            )

        rows.append(
            row
        )

    steps_df = pd.DataFrame(
        rows
    )

    st.dataframe(
        steps_df,
        width="stretch",
        hide_index=True,
        column_config={
            "단계": st.column_config.NumberColumn(
                "단계",
                width="small",
                format="%d",
            ),
            "문자·토큰": st.column_config.TextColumn(
                "문자·토큰",
                width="small",
            ),
            "연산": st.column_config.TextColumn(
                "연산",
                width="small",
            ),
            "연산 전 Stack": st.column_config.TextColumn(
                "연산 전 Stack",
                width="medium",
            ),
            "연산 후 Stack": st.column_config.TextColumn(
                "연산 후 Stack",
                width="medium",
            ),
            "설명": st.column_config.TextColumn(
                "설명",
                width="large",
            ),
        },
    )


# ============================================================
# 7. 괄호 검사 전용 설명
# ============================================================

def render_bracket_guide() -> None:
    """
    괄호 검사의 Stack 활용 원리를 표시합니다.
    """

    render_html(
        """
        <section class="concept-box">
            <div class="concept-title">
                괄호 검사 방법
            </div>

            <div class="concept-text">
                여는 괄호를 만나면 Stack에 Push합니다.
                닫는 괄호를 만나면 Stack의 TOP과 짝이 맞는지
                확인한 후 Pop합니다. 모든 문자를 확인한 뒤
                Stack이 비어 있으면 올바른 괄호식입니다.
            </div>
        </section>
        """
    )

    guide_col1, guide_col2, guide_col3 = st.columns(
        3
    )

    with guide_col1:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">
                    📥
                </div>

                <div class="structure-card-title">
                    여는 괄호
                </div>

                <div class="structure-card-description">
                    (, {, [ 기호를 만나면 Stack에 Push합니다.
                </div>

                <span class="structure-card-keyword">
                    Push
                </span>
            </article>
            """
        )

    with guide_col2:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">
                    🔍
                </div>

                <div class="structure-card-title">
                    짝 확인
                </div>

                <div class="structure-card-description">
                    닫는 괄호와 Stack TOP의 종류를 비교합니다.
                </div>

                <span class="structure-card-keyword">
                    Match
                </span>
            </article>
            """
        )

    with guide_col3:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">
                    📤
                </div>

                <div class="structure-card-title">
                    닫는 괄호
                </div>

                <div class="structure-card-description">
                    짝이 맞으면 여는 괄호를 Stack에서 Pop합니다.
                </div>

                <span class="structure-card-keyword">
                    Pop
                </span>
            </article>
            """
        )


# ============================================================
# 8. 후위 표기법 전용 설명
# ============================================================

def render_postfix_guide() -> None:
    """
    후위 표기법 계산의 Stack 활용 원리를 표시합니다.
    """

    render_html(
        """
        <section class="concept-box">
            <div class="concept-title">
                후위 표기법 계산 방법
            </div>

            <div class="concept-text">
                숫자를 만나면 Stack에 Push합니다. 연산자를 만나면
                Stack에서 숫자 두 개를 Pop하여 계산하고,
                계산 결과를 다시 Stack에 Push합니다.
            </div>
        </section>
        """
    )

    render_html(
        """
        <div class="warning-box">
            <strong>피연산자의 순서에 주의하세요.</strong><br>
            먼저 Pop한 값은 오른쪽 피연산자이고,
            두 번째로 Pop한 값은 왼쪽 피연산자입니다.<br><br>

            예: <strong>8 2 -</strong>는
            <strong>8 - 2</strong>로 계산합니다.
        </div>
        """
    )


# ============================================================
# 9. 활용 사례 Python 코드
# ============================================================

def render_stack_application_code(
    application_type: str,
) -> None:
    """
    괄호 검사 또는 후위 표기법의 핵심 Python 코드를 표시합니다.

    Args:
        application_type:
            "bracket" 또는 "postfix"
    """

    bracket_code = """
def check_brackets(expression):
    stack = []
    pairs = {
        ")": "(",
        "}": "{",
        "]": "["
    }

    for char in expression:
        if char in "({[":
            stack.append(char)

        elif char in ")}]":
            if not stack:
                return False

            opening = stack.pop()

            if opening != pairs[char]:
                return False

    return len(stack) == 0
"""

    postfix_code = """
def calculate_postfix(tokens):
    stack = []

    for token in tokens:
        if token.lstrip("-").replace(".", "", 1).isdigit():
            stack.append(float(token))

        else:
            right = stack.pop()
            left = stack.pop()

            if token == "+":
                result = left + right
            elif token == "-":
                result = left - right
            elif token == "*":
                result = left * right
            elif token == "/":
                result = left / right

            stack.append(result)

    return stack.pop()
"""

    if application_type == "bracket":
        st.markdown(
            "#### 괄호 검사 Python 코드"
        )

        st.code(
            bracket_code.strip(),
            language="python",
        )

    elif application_type == "postfix":
        st.markdown(
            "#### 후위 표기법 계산 Python 코드"
        )

        st.code(
            postfix_code.strip(),
            language="python",
        )


# ============================================================
# 10. 괄호 검사 전체 시각화
# ============================================================

def render_bracket_check_visualization(
    result: dict | None,
    key_prefix: str = "bracket",
) -> None:
    """
    괄호 검사 결과와 단계별 과정을 한 번에 표시합니다.
    """

    render_application_result(
        result
    )

    st.markdown(
        "#### 단계별 괄호 검사 과정"
    )

    render_step_navigator(
        result=result,
        key_prefix=key_prefix,
    )

    if result and result.get("steps"):
        with st.expander(
            "전체 괄호 검사 과정 보기",
            expanded=False,
        ):
            render_steps_table(
                result
            )


# ============================================================
# 11. 후위 표기법 전체 시각화
# ============================================================

def render_postfix_visualization(
    result: dict | None,
    key_prefix: str = "postfix",
) -> None:
    """
    후위 표기법 계산 결과와 단계별 과정을 한 번에 표시합니다.
    """

    render_application_result(
        result
    )

    st.markdown(
        "#### 단계별 계산 과정"
    )

    render_step_navigator(
        result=result,
        key_prefix=key_prefix,
    )

    if result and result.get("steps"):
        with st.expander(
            "전체 후위 표기법 계산 과정 보기",
            expanded=False,
        ):
            render_steps_table(
                result
            )