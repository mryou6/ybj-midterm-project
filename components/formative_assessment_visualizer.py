"""
자료구조 종합 형성평가의 화면 요소를 담당하는 컴포넌트입니다.

주요 기능
1. 학생 정보 표시
2. 평가 안내 및 문항 구성 표시
3. 평가 진행률 표시
4. 객관식 문항 출력
5. 미응답 문항 안내
6. 총점과 성취 수준 표시
7. 영역별 평가 결과 표시
8. 문항별 정답·오답 및 해설 표시
9. 오답 개념 분석
10. 재도전 안내

이 파일은 평가 문항과 채점 로직을 직접 처리하지 않습니다.
평가 로직에서 생성된 문항 및 결과 데이터를 화면에 표시합니다.
"""

from __future__ import annotations

from html import escape
from typing import Any, Callable

import pandas as pd
import streamlit as st

from modules.common import render_html


# ============================================================
# 1. 공통 상수
# ============================================================

DOMAIN_LABELS = {
    "stack": "Stack",
    "queue": "Queue",
    "tree": "Tree",
    "graph": "Graph",
}

DOMAIN_ICONS = {
    "stack": "📚",
    "queue": "🚶",
    "tree": "🌳",
    "graph": "🕸️",
}

DIFFICULTY_LABELS = {
    "basic": "기초",
    "intermediate": "중간",
    "advanced": "심화",
}

ACHIEVEMENT_DESCRIPTIONS = {
    "A": "개념 이해 우수",
    "B": "개념 이해 양호",
    "C": "기본 개념 이해",
    "D": "일부 개념 보완 필요",
    "E": "기초 개념 재학습 필요",
}


# ============================================================
# 2. 공통 보조 함수
# ============================================================

def get_domain_label(
    domain: str,
) -> str:
    """
    영역의 내부 이름을 화면 표시용 이름으로 변환합니다.
    """

    return DOMAIN_LABELS.get(
        str(domain).lower(),
        str(domain),
    )


def get_domain_icon(
    domain: str,
) -> str:
    """
    영역에 맞는 아이콘을 반환합니다.
    """

    return DOMAIN_ICONS.get(
        str(domain).lower(),
        "📘",
    )


def get_difficulty_label(
    difficulty: str,
) -> str:
    """
    난이도의 내부 이름을 한글로 변환합니다.
    """

    return DIFFICULTY_LABELS.get(
        str(difficulty).lower(),
        str(difficulty),
    )


def format_percentage(
    value: Any,
) -> str:
    """
    백분율 값을 화면 표시용 문자열로 변환합니다.
    """

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return "0%"

    if numeric_value.is_integer():
        return f"{int(numeric_value)}%"

    return f"{numeric_value:.1f}%"


def normalize_answer_text(
    answer: Any,
) -> str:
    """
    답안 값을 화면에 표시할 문자열로 변환합니다.
    """

    if answer is None:
        return "미응답"

    answer_text = str(answer).strip()

    if not answer_text:
        return "미응답"

    return answer_text


# ============================================================
# 3. 평가 안내 카드
# ============================================================

def render_assessment_intro(
    total_questions: int,
    distribution: dict[str, int],
) -> None:
    """
    형성평가의 목적과 문항 구성을 표시합니다.

    Args:
        total_questions:
            전체 문항 수

        distribution:
            영역별 문항 수

            예:
                {
                    "stack": 3,
                    "queue": 3,
                    "tree": 3,
                    "graph": 3,
                }
    """

    render_html(
        f"""
        <section class="concept-box">
            <div class="concept-title">
                자료구조 종합 형성평가
            </div>

            <div class="concept-text">
                Stack, Queue, Tree, Graph의 핵심 개념을
                객관식 문항으로 확인합니다. 평가 제출 후에는
                총점뿐만 아니라 영역별 성취도와 보완이 필요한
                개념을 확인할 수 있습니다.
            </div>
        </section>
        """
    )

    domain_cards: list[str] = []

    for domain in [
        "stack",
        "queue",
        "tree",
        "graph",
    ]:
        question_count = int(
            distribution.get(
                domain,
                0,
            )
        )

        domain_cards.append(
            f"""
            <article class="assessment-domain-card">
                <div class="assessment-domain-icon">
                    {get_domain_icon(domain)}
                </div>

                <div class="assessment-domain-name">
                    {escape(get_domain_label(domain))}
                </div>

                <div class="assessment-domain-count">
                    {question_count}문항
                </div>
            </article>
            """
        )

    render_html(
        f"""
        <style>
            .assessment-summary-panel {{
                padding: 20px;
                margin: 14px 0 20px 0;
                border: 1px solid #d7e2ec;
                border-radius: 16px;
                background: #f8fbfe;
            }}

            .assessment-total-count {{
                margin-bottom: 18px;
                color: #173d65;
                font-size: 17px;
                font-weight: 800;
                text-align: center;
            }}

            .assessment-domain-grid {{
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 12px;
            }}

            .assessment-domain-card {{
                padding: 17px 12px;
                border: 1px solid #dbe5ee;
                border-radius: 13px;
                background: #ffffff;
                text-align: center;
            }}

            .assessment-domain-icon {{
                margin-bottom: 7px;
                font-size: 25px;
            }}

            .assessment-domain-name {{
                color: #173d65;
                font-size: 15px;
                font-weight: 800;
            }}

            .assessment-domain-count {{
                margin-top: 5px;
                color: #718295;
                font-size: 13px;
                font-weight: 600;
            }}

            @media (max-width: 800px) {{
                .assessment-domain-grid {{
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }}
            }}
        </style>

        <section class="assessment-summary-panel">
            <div class="assessment-total-count">
                전체 {int(total_questions)}문항
            </div>

            <div class="assessment-domain-grid">
                {''.join(domain_cards)}
            </div>
        </section>
        """
    )


# ============================================================
# 4. 학생 정보 표시
# ============================================================

def render_student_information(
    student_info: dict[str, Any],
) -> None:
    """
    입력된 학생 정보를 카드 형태로 표시합니다.

    예상 데이터:
        {
            "grade": 2,
            "class": 3,
            "number": 7,
            "name": "김학생",
        }
    """

    grade = escape(
        str(
            student_info.get(
                "grade",
                "-",
            )
        )
    )

    class_number = escape(
        str(
            student_info.get(
                "class",
                "-",
            )
        )
    )

    student_number = escape(
        str(
            student_info.get(
                "number",
                "-",
            )
        )
    )

    student_name = escape(
        str(
            student_info.get(
                "name",
                "-",
            )
        )
    )

    render_html(
        f"""
        <section class="status-panel">
            <div class="status-title">
                응시자 정보
            </div>

            <div class="status-item">
                <span class="status-label">
                    학년
                </span>

                <span class="status-value">
                    {grade}학년
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    반
                </span>

                <span class="status-value">
                    {class_number}반
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    번호
                </span>

                <span class="status-value">
                    {student_number}번
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    이름·별칭
                </span>

                <span class="status-value">
                    {student_name}
                </span>
            </div>
        </section>
        """
    )


# ============================================================
# 5. 평가 주의사항
# ============================================================

def render_assessment_guidelines() -> None:
    """
    평가 전 학생에게 보여줄 안내 사항을 표시합니다.
    """

    render_html(
        """
        <div class="info-box">
            <strong>평가 안내</strong><br><br>

            ① 모든 문항에 답한 뒤 평가를 제출하세요.<br>
            ② 제출 전에는 선택한 답을 자유롭게 변경할 수 있습니다.<br>
            ③ 제출 후에는 정답, 해설, 영역별 결과를 확인할 수 있습니다.<br>
            ④ 결과는 학습 상태를 점검하기 위한 형성평가 자료로 활용됩니다.
        </div>
        """
    )


# ============================================================
# 6. 평가 진행률
# ============================================================

def render_assessment_progress(
    answered_count: int,
    total_questions: int,
) -> None:
    """
    현재까지 답한 문항 수와 진행률을 표시합니다.
    """

    safe_total = max(
        int(total_questions),
        1,
    )

    safe_answered = max(
        0,
        min(
            int(answered_count),
            safe_total,
        ),
    )

    percentage = (
        safe_answered
        / safe_total
        * 100
    )

    st.progress(
        safe_answered / safe_total,
    )

    render_html(
        f"""
        <div style="
            margin-top: 7px;
            margin-bottom: 18px;
            color: #5f7285;
            font-size: 14px;
            font-weight: 700;
            text-align: right;
        ">
            응답 {safe_answered} / {safe_total}문항
            · {percentage:.0f}% 완료
        </div>
        """
    )


# ============================================================
# 7. 문항 카드
# ============================================================

def render_question_header(
    question_number: int,
    question: dict[str, Any],
) -> None:
    """
    문항 번호, 영역, 난이도, 개념을 표시합니다.
    """

    domain = str(
        question.get(
            "domain",
            "",
        )
    )

    difficulty = str(
        question.get(
            "difficulty",
            "",
        )
    )

    concept = escape(
        str(
            question.get(
                "concept",
                "",
            )
        )
    )

    question_text = escape(
        str(
            question.get(
                "question",
                "",
            )
        )
    )

    render_html(
        f"""
        <style>
            .formative-question-card {{
                padding: 20px 22px;
                margin-top: 14px;
                margin-bottom: 10px;
                border: 1px solid #d7e2ec;
                border-radius: 16px;
                background: #ffffff;
            }}

            .formative-question-meta {{
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 7px;
                margin-bottom: 14px;
            }}

            .formative-question-number {{
                margin-right: 4px;
                color: #173d65;
                font-size: 14px;
                font-weight: 900;
            }}

            .formative-meta-badge {{
                padding: 4px 9px;
                border-radius: 999px;
                background: #edf5fb;
                color: #37658d;
                font-size: 11px;
                font-weight: 800;
            }}

            .formative-question-text {{
                line-height: 1.7;
                color: #1d3b56;
                font-size: 17px;
                font-weight: 800;
            }}
        </style>

        <section class="formative-question-card">
            <div class="formative-question-meta">
                <span class="formative-question-number">
                    문제 {int(question_number)}
                </span>

                <span class="formative-meta-badge">
                    {get_domain_icon(domain)}
                    {escape(get_domain_label(domain))}
                </span>

                <span class="formative-meta-badge">
                    난이도:
                    {escape(get_difficulty_label(difficulty))}
                </span>

                <span class="formative-meta-badge">
                    {concept}
                </span>
            </div>

            <div class="formative-question-text">
                {question_text}
            </div>
        </section>
        """
    )


def render_multiple_choice_question(
    question_number: int,
    question: dict[str, Any],
    selected_answer: str | None = None,
    key_prefix: str = "formative",
    disabled: bool = False,
    on_change: Callable[[], None] | None = None,
) -> str | None:
    """
    객관식 문항 하나를 출력하고 선택한 답을 반환합니다.

    Args:
        question_number:
            화면에 표시할 문항 번호

        question:
            JSON에서 불러온 문항 딕셔너리

        selected_answer:
            기존 선택 답안

        key_prefix:
            위젯 키 충돌 방지용 접두어

        disabled:
            평가 제출 후 선택을 비활성화할지 여부

        on_change:
            답안 변경 시 실행할 콜백

    Returns:
        선택한 답안 문자열 또는 None
    """

    render_question_header(
        question_number=question_number,
        question=question,
    )

    question_id = str(
        question.get(
            "id",
            f"question_{question_number}",
        )
    )

    options = list(
        question.get(
            "options",
            [],
        )
    )

    selected_index = None

    if selected_answer in options:
        selected_index = options.index(
            selected_answer
        )

    answer = st.radio(
        label=f"{question_number}번 답 선택",
        options=options,
        index=selected_index,
        key=f"{key_prefix}_{question_id}",
        label_visibility="collapsed",
        disabled=disabled,
        on_change=on_change,
    )

    return answer


# ============================================================
# 8. 미응답 문항 안내
# ============================================================

def render_unanswered_warning(
    unanswered_numbers: list[int],
) -> None:
    """
    응답하지 않은 문항 번호를 안내합니다.
    """

    if not unanswered_numbers:
        return

    number_text = ", ".join(
        str(number)
        for number in unanswered_numbers
    )

    render_html(
        f"""
        <div class="warning-box">
            <strong>아직 답하지 않은 문항이 있습니다.</strong><br><br>
            미응답 문항: {escape(number_text)}번<br>
            모든 문항에 답한 뒤 평가를 제출해 주세요.
        </div>
        """
    )


# ============================================================
# 9. 최종 점수 카드
# ============================================================

def render_total_score(
    result: dict[str, Any],
) -> None:
    """
    총점, 백분율, 성취 수준을 표시합니다.

    예상 데이터:
        {
            "total_score": 9,
            "total_questions": 12,
            "percentage": 75.0,
            "achievement_level": "C",
            "achievement_description": "기본 개념 이해"
        }
    """

    total_score = int(
        result.get(
            "total_score",
            0,
        )
    )

    total_questions = int(
        result.get(
            "total_questions",
            0,
        )
    )

    percentage = result.get(
        "percentage",
        0,
    )

    achievement_level = str(
        result.get(
            "achievement_level",
            "E",
        )
    )

    achievement_description = str(
        result.get(
            "achievement_description",
            ACHIEVEMENT_DESCRIPTIONS.get(
                achievement_level,
                "",
            ),
        )
    )

    percentage_text = format_percentage(
        percentage
    )

    if achievement_level == "A":
        result_class = "achievement-a"
        result_icon = "🏆"
    elif achievement_level == "B":
        result_class = "achievement-b"
        result_icon = "🌟"
    elif achievement_level == "C":
        result_class = "achievement-c"
        result_icon = "👍"
    elif achievement_level == "D":
        result_class = "achievement-d"
        result_icon = "📘"
    else:
        result_class = "achievement-e"
        result_icon = "🌱"

    render_html(
        f"""
        <style>
            .assessment-result-card {{
                padding: 28px;
                border-radius: 18px;
                text-align: center;
                border: 1px solid #d7e2ec;
            }}

            .achievement-a {{
                background: #eef9f1;
            }}

            .achievement-b {{
                background: #f0f7ff;
            }}

            .achievement-c {{
                background: #fff9eb;
            }}

            .achievement-d {{
                background: #fff4e9;
            }}

            .achievement-e {{
                background: #fff0f0;
            }}

            .assessment-result-icon {{
                margin-bottom: 7px;
                font-size: 36px;
            }}

            .assessment-result-score {{
                color: #173d65;
                font-size: 34px;
                font-weight: 900;
            }}

            .assessment-result-percentage {{
                margin-top: 4px;
                color: #48637c;
                font-size: 20px;
                font-weight: 800;
            }}

            .assessment-result-level {{
                display: inline-block;
                margin-top: 14px;
                padding: 7px 15px;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.78);
                color: #173d65;
                font-size: 15px;
                font-weight: 900;
            }}

            .assessment-result-description {{
                margin-top: 12px;
                color: #516779;
                font-size: 15px;
                font-weight: 600;
            }}
        </style>

        <section class="assessment-result-card {result_class}">
            <div class="assessment-result-icon">
                {result_icon}
            </div>

            <div class="assessment-result-score">
                {total_score} / {total_questions}
            </div>

            <div class="assessment-result-percentage">
                {escape(percentage_text)}
            </div>

            <div class="assessment-result-level">
                성취 수준 {escape(achievement_level)}
            </div>

            <div class="assessment-result-description">
                {escape(achievement_description)}
            </div>
        </section>
        """
    )


# ============================================================
# 10. 영역별 결과
# ============================================================

def render_domain_results(
    domain_results: dict[str, dict[str, Any]],
) -> None:
    """
    Stack, Queue, Tree, Graph 영역별 결과를 표시합니다.

    예상 데이터:
        {
            "stack": {
                "score": 2,
                "total": 3,
                "percentage": 66.7,
            },
            ...
        }
    """

    domain_cards: list[str] = []

    for domain in [
        "stack",
        "queue",
        "tree",
        "graph",
    ]:
        domain_result = domain_results.get(
            domain,
            {},
        )

        score = int(
            domain_result.get(
                "score",
                0,
            )
        )

        total = int(
            domain_result.get(
                "total",
                0,
            )
        )

        percentage = float(
            domain_result.get(
                "percentage",
                0,
            )
        )

        if total == 0:
            feedback = "평가 문항 없음"
        elif percentage >= 80:
            feedback = "개념 이해 우수"
        elif percentage >= 60:
            feedback = "일부 개념 복습 권장"
        else:
            feedback = "핵심 개념 재학습 필요"

        domain_cards.append(
            f"""
            <article class="domain-result-card">
                <div class="domain-result-icon">
                    {get_domain_icon(domain)}
                </div>

                <div class="domain-result-title">
                    {escape(get_domain_label(domain))}
                </div>

                <div class="domain-result-score">
                    {score} / {total}
                </div>

                <div class="domain-result-percentage">
                    {percentage:.0f}%
                </div>

                <div class="domain-progress-track">
                    <div
                        class="domain-progress-value"
                        style="width: {max(0, min(percentage, 100))}%;">
                    </div>
                </div>

                <div class="domain-result-feedback">
                    {escape(feedback)}
                </div>
            </article>
            """
        )

    render_html(
        f"""
        <style>
            .domain-result-grid {{
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 13px;
                margin-top: 14px;
                margin-bottom: 20px;
            }}

            .domain-result-card {{
                padding: 19px 14px;
                border: 1px solid #d9e4ed;
                border-radius: 15px;
                background: #ffffff;
                text-align: center;
            }}

            .domain-result-icon {{
                font-size: 27px;
            }}

            .domain-result-title {{
                margin-top: 6px;
                color: #173d65;
                font-size: 16px;
                font-weight: 900;
            }}

            .domain-result-score {{
                margin-top: 12px;
                color: #234d72;
                font-size: 22px;
                font-weight: 900;
            }}

            .domain-result-percentage {{
                margin-top: 3px;
                color: #6a7f91;
                font-size: 13px;
                font-weight: 700;
            }}

            .domain-progress-track {{
                width: 100%;
                height: 8px;
                margin-top: 11px;
                overflow: hidden;
                border-radius: 999px;
                background: #e9eff4;
            }}

            .domain-progress-value {{
                height: 100%;
                border-radius: 999px;
                background: #4b87ba;
            }}

            .domain-result-feedback {{
                margin-top: 10px;
                min-height: 38px;
                color: #617587;
                font-size: 12px;
                font-weight: 600;
            }}

            @media (max-width: 800px) {{
                .domain-result-grid {{
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }}
            }}
        </style>

        <div class="domain-result-grid">
            {''.join(domain_cards)}
        </div>
        """
    )


# ============================================================
# 11. 문항별 채점 결과
# ============================================================

def render_question_result(
    question_number: int,
    question_result: dict[str, Any],
) -> None:
    """
    한 문항의 채점 결과와 해설을 표시합니다.

    예상 데이터:
        {
            "question_id": "stack_001",
            "domain": "stack",
            "difficulty": "basic",
            "concept": "LIFO",
            "question": "...",
            "student_answer": "...",
            "correct_answer": "...",
            "is_correct": True,
            "explanation": "..."
        }
    """

    is_correct = bool(
        question_result.get(
            "is_correct",
            False,
        )
    )

    domain = str(
        question_result.get(
            "domain",
            "",
        )
    )

    concept = escape(
        str(
            question_result.get(
                "concept",
                "",
            )
        )
    )

    question_text = escape(
        str(
            question_result.get(
                "question",
                "",
            )
        )
    )

    student_answer = escape(
        normalize_answer_text(
            question_result.get(
                "student_answer"
            )
        )
    )

    correct_answer = escape(
        normalize_answer_text(
            question_result.get(
                "correct_answer"
            )
        )
    )

    explanation = escape(
        str(
            question_result.get(
                "explanation",
                "",
            )
        )
    )

    if is_correct:
        result_class = "question-result-correct"
        result_icon = "✅"
        result_label = "정답"
    else:
        result_class = "question-result-incorrect"
        result_icon = "❌"
        result_label = "오답"

    render_html(
        f"""
        <style>
            .question-result-card {{
                padding: 20px;
                margin: 12px 0;
                border-radius: 15px;
                border: 1px solid #d8e3ec;
            }}

            .question-result-correct {{
                background: #f1faf4;
            }}

            .question-result-incorrect {{
                background: #fff3f3;
            }}

            .question-result-header {{
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                align-items: center;
                gap: 8px;
                margin-bottom: 12px;
            }}

            .question-result-number {{
                color: #173d65;
                font-size: 15px;
                font-weight: 900;
            }}

            .question-result-badge {{
                padding: 4px 10px;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.8);
                color: #315875;
                font-size: 12px;
                font-weight: 800;
            }}

            .question-result-text {{
                margin-bottom: 15px;
                line-height: 1.7;
                color: #24435d;
                font-size: 15px;
                font-weight: 700;
            }}

            .question-answer-row {{
                display: grid;
                grid-template-columns: 120px 1fr;
                gap: 8px;
                padding: 7px 0;
                border-bottom: 1px solid rgba(130, 150, 170, 0.18);
            }}

            .question-answer-label {{
                color: #697d8f;
                font-size: 13px;
                font-weight: 800;
            }}

            .question-answer-value {{
                color: #173d65;
                font-size: 14px;
                font-weight: 700;
            }}

            .question-explanation {{
                margin-top: 14px;
                padding: 13px 15px;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.72);
                line-height: 1.7;
                color: #4c6275;
                font-size: 14px;
            }}
        </style>

        <section class="question-result-card {result_class}">
            <div class="question-result-header">
                <div class="question-result-number">
                    {result_icon} 문제 {int(question_number)}
                    · {escape(result_label)}
                </div>

                <div>
                    <span class="question-result-badge">
                        {get_domain_icon(domain)}
                        {escape(get_domain_label(domain))}
                    </span>

                    <span class="question-result-badge">
                        {concept}
                    </span>
                </div>
            </div>

            <div class="question-result-text">
                {question_text}
            </div>

            <div class="question-answer-row">
                <div class="question-answer-label">
                    나의 답
                </div>

                <div class="question-answer-value">
                    {student_answer}
                </div>
            </div>

            <div class="question-answer-row">
                <div class="question-answer-label">
                    정답
                </div>

                <div class="question-answer-value">
                    {correct_answer}
                </div>
            </div>

            <div class="question-explanation">
                <strong>해설</strong><br>
                {explanation}
            </div>
        </section>
        """
    )


def render_all_question_results(
    question_results: list[dict[str, Any]],
    incorrect_only: bool = False,
) -> None:
    """
    모든 문항의 채점 결과를 표시합니다.

    Args:
        question_results:
            문항별 채점 결과 목록

        incorrect_only:
            True이면 오답 문항만 표시
    """

    filtered_results = question_results

    if incorrect_only:
        filtered_results = [
            result
            for result in question_results
            if not result.get(
                "is_correct",
                False,
            )
        ]

    if not filtered_results:
        if incorrect_only:
            st.success(
                "오답 문항이 없습니다. 모든 문항을 맞혔습니다!"
            )
        else:
            st.info(
                "표시할 문항 결과가 없습니다."
            )

        return

    for question_number, result in enumerate(
        filtered_results,
        start=1,
    ):
        original_number = result.get(
            "question_number",
            question_number,
        )

        render_question_result(
            question_number=int(original_number),
            question_result=result,
        )


# ============================================================
# 12. 오답 개념 분석
# ============================================================

def render_incorrect_concepts(
    incorrect_concepts: list[str],
) -> None:
    """
    오답과 관련된 개념 목록을 표시합니다.
    """

    cleaned_concepts = []

    for concept in incorrect_concepts:
        concept_text = str(concept).strip()

        if (
            concept_text
            and concept_text not in cleaned_concepts
        ):
            cleaned_concepts.append(
                concept_text
            )

    if not cleaned_concepts:
        render_html(
            """
            <div class="success-box">
                <strong>보완이 필요한 개념이 없습니다.</strong><br>
                이번 평가에서 모든 핵심 개념을 정확하게 이해했습니다.
            </div>
            """
        )
        return

    concept_badges = "".join(
        f"""
        <span class="incorrect-concept-badge">
            {escape(concept)}
        </span>
        """
        for concept in cleaned_concepts
    )

    render_html(
        f"""
        <style>
            .incorrect-concept-panel {{
                padding: 20px;
                border: 1px solid #ead9c5;
                border-radius: 15px;
                background: #fff9ef;
            }}

            .incorrect-concept-title {{
                margin-bottom: 10px;
                color: #76501a;
                font-size: 17px;
                font-weight: 900;
            }}

            .incorrect-concept-description {{
                margin-bottom: 14px;
                line-height: 1.7;
                color: #756348;
                font-size: 14px;
            }}

            .incorrect-concept-badges {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }}

            .incorrect-concept-badge {{
                padding: 6px 11px;
                border-radius: 999px;
                background: #ffffff;
                border: 1px solid #eadbc8;
                color: #72501f;
                font-size: 13px;
                font-weight: 800;
            }}
        </style>

        <section class="incorrect-concept-panel">
            <div class="incorrect-concept-title">
                📌 다시 확인할 개념
            </div>

            <div class="incorrect-concept-description">
                아래 개념과 관련된 문항에서 오답이 발생했습니다.
                해당 자료구조 페이지의 체험 활동과 개념 설명을
                다시 확인해 보세요.
            </div>

            <div class="incorrect-concept-badges">
                {concept_badges}
            </div>
        </section>
        """
    )


# ============================================================
# 13. 영역별 결과 표
# ============================================================

def render_domain_result_table(
    domain_results: dict[str, dict[str, Any]],
) -> None:
    """
    영역별 결과를 DataFrame 표로 표시합니다.
    """

    rows: list[dict[str, Any]] = []

    for domain in [
        "stack",
        "queue",
        "tree",
        "graph",
    ]:
        result = domain_results.get(
            domain,
            {},
        )

        score = int(
            result.get(
                "score",
                0,
            )
        )

        total = int(
            result.get(
                "total",
                0,
            )
        )

        percentage = float(
            result.get(
                "percentage",
                0,
            )
        )

        rows.append(
            {
                "영역": (
                    f"{get_domain_icon(domain)} "
                    f"{get_domain_label(domain)}"
                ),
                "정답 수": score,
                "문항 수": total,
                "정답률": percentage,
            }
        )

    domain_df = pd.DataFrame(
        rows
    )

    st.dataframe(
        domain_df,
        width="stretch",
        hide_index=True,
        column_config={
            "영역": st.column_config.TextColumn(
                "영역",
                width="medium",
            ),
            "정답 수": st.column_config.NumberColumn(
                "정답 수",
                width="small",
                format="%d",
            ),
            "문항 수": st.column_config.NumberColumn(
                "문항 수",
                width="small",
                format="%d",
            ),
            "정답률": st.column_config.ProgressColumn(
                "정답률",
                min_value=0,
                max_value=100,
                format="%.0f%%",
            ),
        },
    )


# ============================================================
# 14. 재도전 안내
# ============================================================

def render_retry_guide(
    incorrect_count: int,
) -> None:
    """
    오답 문항 재도전에 관한 안내를 표시합니다.
    """

    if incorrect_count <= 0:
        render_html(
            """
            <div class="success-box">
                <strong>재도전이 필요하지 않습니다.</strong><br>
                모든 문항을 맞혔습니다. 다른 자료구조 체험 활동으로
                학습 내용을 확장해 보세요.
            </div>
            """
        )
        return

    render_html(
        f"""
        <div class="info-box">
            <strong>오답 다시 풀기</strong><br><br>

            현재 오답 문항은 <strong>{int(incorrect_count)}개</strong>입니다.
            오답 다시 풀기를 시작하면 틀린 문항만 모아서
            다시 도전할 수 있습니다.
        </div>
        """
    )


# ============================================================
# 15. 저장 결과 안내
# ============================================================

def render_save_result_message(
    success: bool,
    message: str | None = None,
) -> None:
    """
    CSV 평가 결과 저장 성공 또는 실패 메시지를 표시합니다.
    """

    if success:
        display_message = (
            message
            or "평가 결과가 정상적으로 저장되었습니다."
        )

        render_html(
            f"""
            <div class="success-box">
                <strong>저장 완료</strong><br>
                {escape(display_message)}
            </div>
            """
        )

    else:
        display_message = (
            message
            or "평가 결과를 저장하지 못했습니다."
        )

        render_html(
            f"""
            <div class="warning-box">
                <strong>저장 실패</strong><br>
                {escape(display_message)}
            </div>
            """
        )


# ============================================================
# 16. 평가 완료 전체 화면
# ============================================================

def render_assessment_result_summary(
    result: dict[str, Any],
) -> None:
    """
    평가 완료 후 핵심 결과를 한 번에 표시합니다.

    예상 result 구조:
        {
            "total_score": 9,
            "total_questions": 12,
            "percentage": 75.0,
            "achievement_level": "C",
            "achievement_description": "기본 개념 이해",
            "domain_results": {...},
            "incorrect_concepts": [...],
            "question_results": [...]
        }
    """

    render_total_score(
        result
    )

    st.markdown(
        "#### 영역별 결과"
    )

    render_domain_results(
        result.get(
            "domain_results",
            {},
        )
    )

    st.markdown(
        "#### 오답 개념 분석"
    )

    render_incorrect_concepts(
        result.get(
            "incorrect_concepts",
            [],
        )
    )


# ============================================================
# 17. 문항 응답 요약
# ============================================================

def render_answer_summary(
    questions: list[dict[str, Any]],
    answers: dict[str, Any],
) -> None:
    """
    제출 전 문항별 응답 여부를 표로 보여줍니다.
    """

    rows: list[dict[str, Any]] = []

    for index, question in enumerate(
        questions,
        start=1,
    ):
        question_id = str(
            question.get(
                "id",
                f"question_{index}",
            )
        )

        answer = answers.get(
            question_id
        )

        rows.append(
            {
                "문항": index,
                "영역": get_domain_label(
                    str(
                        question.get(
                            "domain",
                            "",
                        )
                    )
                ),
                "개념": str(
                    question.get(
                        "concept",
                        "",
                    )
                ),
                "응답 상태": (
                    "응답 완료"
                    if answer is not None
                    and str(answer).strip()
                    else "미응답"
                ),
            }
        )

    summary_df = pd.DataFrame(
        rows
    )

    st.dataframe(
        summary_df,
        width="stretch",
        hide_index=True,
        column_config={
            "문항": st.column_config.NumberColumn(
                "문항",
                width="small",
                format="%d",
            ),
            "영역": st.column_config.TextColumn(
                "영역",
                width="small",
            ),
            "개념": st.column_config.TextColumn(
                "개념",
                width="medium",
            ),
            "응답 상태": st.column_config.TextColumn(
                "응답 상태",
                width="small",
            ),
        },
    )