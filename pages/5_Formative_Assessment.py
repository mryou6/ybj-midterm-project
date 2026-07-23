"""
자료구조 종합 형성평가 페이지입니다.

지원 기능
1. 학생 정보 입력
2. 영역별 무작위 문항 출제
3. 선택지 순서 무작위 배열
4. 응답 진행률 확인
5. 미응답 문항 검사
6. 평가 채점
7. CSV 결과 저장
8. 총점 및 영역별 결과 확인
9. 문항별 정답과 해설 확인
10. 오답 문항 다시 풀기
11. 새로운 종합평가 시작
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from components.formative_assessment_visualizer import (
    render_all_question_results,
    render_answer_summary,
    render_assessment_guidelines,
    render_assessment_intro,
    render_assessment_progress,
    render_assessment_result_summary,
    render_domain_result_table,
    render_multiple_choice_question,
    render_retry_guide,
    render_save_result_message,
    render_student_information,
    render_unanswered_warning,
)
from modules.common import (
    apply_common_style,
    initialize_session_state,
    render_concept_box,
    render_footer,
    render_message,
    render_page_header,
    render_section_title,
)
from modules.formative_assessment_logic import (
    create_assessment_questions,
    create_retry_questions,
    get_answered_count,
    get_next_attempt_number,
    get_student_attempt_count,
    get_unanswered_numbers,
    grade_assessment,
    load_question_bank,
    save_assessment_result,
    validate_student_info,
)


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="자료구조 종합 형성평가",
    page_icon="📝",
    layout="wide",
)

apply_common_style()


# ============================================================
# 2. 평가 기본 설정
# ============================================================

QUESTION_DISTRIBUTION = {
    "stack": 3,
    "queue": 3,
    "tree": 3,
    "graph": 3,
}

DIFFICULTY_DISTRIBUTION = {
    "basic": 1,
    "intermediate": 1,
    "advanced": 1,
}

TOTAL_QUESTIONS = sum(
    QUESTION_DISTRIBUTION.values()
)


# ============================================================
# 3. Session State 초기화
# ============================================================

initialize_session_state(
    "formative_stage",
    "setup",
)

initialize_session_state(
    "formative_student_info",
    {},
)

initialize_session_state(
    "formative_questions",
    [],
)

initialize_session_state(
    "formative_answers",
    {},
)

initialize_session_state(
    "formative_result",
    None,
)

initialize_session_state(
    "formative_save_result",
    None,
)

initialize_session_state(
    "formative_attempt",
    None,
)

initialize_session_state(
    "formative_show_answer_summary",
    False,
)

initialize_session_state(
    "formative_show_incorrect_only",
    False,
)

initialize_session_state(
    "formative_question_bank_error",
    None,
)


# ------------------------------------------------------------
# 오답 재도전 상태
# ------------------------------------------------------------

initialize_session_state(
    "formative_retry_questions",
    [],
)

initialize_session_state(
    "formative_retry_answers",
    {},
)

initialize_session_state(
    "formative_retry_result",
    None,
)

initialize_session_state(
    "formative_retry_active",
    False,
)

initialize_session_state(
    "formative_retry_show_incorrect_only",
    False,
)


# ============================================================
# 4. 문항 데이터 불러오기
# ============================================================

try:
    question_bank = load_question_bank()
    st.session_state.formative_question_bank_error = None

except (FileNotFoundError, ValueError, OSError) as error:
    question_bank = None
    st.session_state.formative_question_bank_error = str(
        error
    )


# ============================================================
# 5. 공통 보조 함수
# ============================================================

def clear_widget_keys(
    prefixes: list[str],
) -> None:
    """
    지정한 접두어로 시작하는 Streamlit 위젯 상태를 삭제합니다.
    """

    keys_to_delete = [
        key
        for key in st.session_state.keys()
        if any(
            str(key).startswith(prefix)
            for prefix in prefixes
        )
    ]

    for key in keys_to_delete:
        del st.session_state[key]


def reset_formative_assessment(
    keep_student_info: bool = False,
) -> None:
    """
    종합 형성평가 상태를 초기화합니다.

    Args:
        keep_student_info:
            True이면 기존 학생 정보를 유지합니다.
    """

    saved_student_info = (
        dict(
            st.session_state.formative_student_info
        )
        if keep_student_info
        else {}
    )

    st.session_state.formative_stage = "setup"

    st.session_state.formative_student_info = (
        saved_student_info
    )

    st.session_state.formative_questions = []
    st.session_state.formative_answers = {}
    st.session_state.formative_result = None
    st.session_state.formative_save_result = None
    st.session_state.formative_attempt = None

    st.session_state.formative_show_answer_summary = False
    st.session_state.formative_show_incorrect_only = False

    st.session_state.formative_retry_questions = []
    st.session_state.formative_retry_answers = {}
    st.session_state.formative_retry_result = None
    st.session_state.formative_retry_active = False
    st.session_state.formative_retry_show_incorrect_only = False

    clear_widget_keys(
        [
            "formative_question_",
            "formative_retry_question_",
            "formative_setup_",
        ]
    )


def sync_answers_from_widgets(
    questions: list[dict[str, Any]],
    answer_state_key: str,
    widget_prefix: str,
) -> None:
    """
    Streamlit radio 위젯의 현재 선택값을 답안 딕셔너리에 반영합니다.
    """

    answers = dict(
        st.session_state.get(
            answer_state_key,
            {},
        )
    )

    for question in questions:
        question_id = str(
            question.get(
                "id",
                "",
            )
        )

        widget_key = (
            f"{widget_prefix}_{question_id}"
        )

        if widget_key in st.session_state:
            selected_answer = st.session_state[
                widget_key
            ]

            if (
                selected_answer is not None
                and str(selected_answer).strip()
            ):
                answers[question_id] = (
                    selected_answer
                )

    st.session_state[
        answer_state_key
    ] = answers


def start_new_assessment(
    student_info: dict[str, Any],
) -> None:
    """
    학생 정보를 저장하고 새로운 종합평가 문항을 생성합니다.
    """

    if question_bank is None:
        return

    clear_widget_keys(
        [
            "formative_question_",
            "formative_retry_question_",
        ]
    )

    questions = create_assessment_questions(
        question_bank=question_bank,
        distribution=QUESTION_DISTRIBUTION,
        difficulty_distribution=(
            DIFFICULTY_DISTRIBUTION
        ),
        shuffle_options=True,
        shuffle_question_order=True,
    )

    attempt = get_next_attempt_number(
        student_info
    )

    st.session_state.formative_student_info = dict(
        student_info
    )

    st.session_state.formative_questions = (
        questions
    )

    st.session_state.formative_answers = {}
    st.session_state.formative_result = None
    st.session_state.formative_save_result = None
    st.session_state.formative_attempt = attempt

    st.session_state.formative_show_answer_summary = False
    st.session_state.formative_show_incorrect_only = False

    st.session_state.formative_retry_questions = []
    st.session_state.formative_retry_answers = {}
    st.session_state.formative_retry_result = None
    st.session_state.formative_retry_active = False

    st.session_state.formative_stage = "assessment"


def submit_main_assessment() -> None:
    """
    종합 형성평가를 채점하고 CSV에 결과를 저장합니다.
    """

    questions = (
        st.session_state.formative_questions
    )

    sync_answers_from_widgets(
        questions=questions,
        answer_state_key="formative_answers",
        widget_prefix="formative_question",
    )

    answers = (
        st.session_state.formative_answers
    )

    result = grade_assessment(
        questions=questions,
        answers=answers,
        require_all_answers=True,
    )

    if not result.get(
        "success",
        False,
    ):
        st.session_state.formative_result = (
            result
        )

        return

    save_result = save_assessment_result(
        student_info=(
            st.session_state.formative_student_info
        ),
        assessment_result=result,
        attempt=(
            st.session_state.formative_attempt
        ),
    )

    st.session_state.formative_result = result
    st.session_state.formative_save_result = (
        save_result
    )

    st.session_state.formative_stage = "result"


def start_retry_assessment() -> None:
    """
    최초 평가에서 틀린 문항만 이용해 재도전을 시작합니다.
    """

    original_questions = (
        st.session_state.formative_questions
    )

    original_result = (
        st.session_state.formative_result
    )

    if not original_result:
        return

    retry_questions = create_retry_questions(
        original_questions=original_questions,
        assessment_result=original_result,
        shuffle_options=True,
        shuffle_question_order=False,
    )

    clear_widget_keys(
        [
            "formative_retry_question_",
        ]
    )

    st.session_state.formative_retry_questions = (
        retry_questions
    )

    st.session_state.formative_retry_answers = {}
    st.session_state.formative_retry_result = None
    st.session_state.formative_retry_active = True
    st.session_state.formative_retry_show_incorrect_only = False

    st.session_state.formative_stage = "retry"


def submit_retry_assessment() -> None:
    """
    오답 재도전을 채점합니다.

    재도전 결과는 학습 피드백용으로만 사용하며,
    전체 종합평가 CSV에는 추가 저장하지 않습니다.
    """

    retry_questions = (
        st.session_state.formative_retry_questions
    )

    sync_answers_from_widgets(
        questions=retry_questions,
        answer_state_key="formative_retry_answers",
        widget_prefix="formative_retry_question",
    )

    retry_result = grade_assessment(
        questions=retry_questions,
        answers=(
            st.session_state.formative_retry_answers
        ),
        require_all_answers=True,
    )

    st.session_state.formative_retry_result = (
        retry_result
    )

    if retry_result.get(
        "success",
        False,
    ):
        st.session_state.formative_stage = (
            "retry_result"
        )


def get_answer_for_question(
    question_id: str,
    answer_state_key: str,
) -> Any:
    """
    답안 딕셔너리에서 특정 문항의 답을 반환합니다.
    """

    answers = st.session_state.get(
        answer_state_key,
        {},
    )

    return answers.get(
        question_id
    )


# ============================================================
# 6. 페이지 상단
# ============================================================

render_page_header(
    title="자료구조 종합 형성평가",
    description=(
        "Stack, Queue, Tree, Graph의 핵심 개념을 "
        "확인하고 영역별 학습 상태를 점검해 보세요."
    ),
    icon="📝",
)


# ============================================================
# 7. 문항 파일 오류 처리
# ============================================================

if st.session_state.formative_question_bank_error:

    render_section_title(
        "문항 파일 확인"
    )

    render_message(
        (
            "형성평가 문항 데이터를 불러오지 못했습니다."
        ),
        message_type="warning",
    )

    st.code(
        st.session_state.formative_question_bank_error,
        language="text",
    )

    st.info(
        "data/formative_questions.json 파일의 위치와 "
        "JSON 형식을 확인해 주세요."
    )

    render_footer()

    st.stop()


# ============================================================
# 8. 평가 준비 화면
# ============================================================

if st.session_state.formative_stage == "setup":

    render_section_title(
        "1. 형성평가 안내"
    )

    render_assessment_intro(
        total_questions=TOTAL_QUESTIONS,
        distribution=QUESTION_DISTRIBUTION,
    )

    render_assessment_guidelines()

    render_concept_box(
        title="평가 결과는 학습 점검을 위해 사용됩니다.",
        text=(
            "제출한 결과는 results/formative_results.csv에 "
            "저장됩니다. 오답 재도전 결과는 학습 피드백용으로만 "
            "사용되며 종합평가 결과 파일에는 추가 저장되지 않습니다."
        ),
    )

    render_section_title(
        "2. 학생 정보 입력"
    )

    previous_info = (
        st.session_state.formative_student_info
    )

    with st.form(
        "formative_student_form"
    ):
        info_col1, info_col2, info_col3 = st.columns(
            3
        )

        with info_col1:
            student_grade = st.selectbox(
                "학년",
                options=[
                    1,
                    2,
                    3,
                ],
                index=max(
                    0,
                    min(
                        int(
                            previous_info.get(
                                "grade",
                                1,
                            )
                        )
                        - 1,
                        2,
                    ),
                ),
                key="formative_setup_grade",
            )

        with info_col2:
            previous_class = int(
                previous_info.get(
                    "class",
                    1,
                )
            )

            student_class = st.number_input(
                "반",
                min_value=1,
                max_value=20,
                value=max(
                    1,
                    previous_class,
                ),
                step=1,
                key="formative_setup_class",
            )

        with info_col3:
            previous_number = int(
                previous_info.get(
                    "number",
                    1,
                )
            )

            student_number = st.number_input(
                "번호",
                min_value=1,
                max_value=100,
                value=max(
                    1,
                    previous_number,
                ),
                step=1,
                key="formative_setup_number",
            )

        student_name = st.text_input(
            "이름 또는 별칭",
            value=str(
                previous_info.get(
                    "name",
                    "",
                )
            ),
            placeholder="예: 김학생",
            max_chars=30,
            key="formative_setup_name",
        )

        start_clicked = st.form_submit_button(
            "📝 형성평가 시작",
            use_container_width=True,
        )

    if start_clicked:
        entered_student_info = {
            "grade": int(
                student_grade
            ),
            "class": int(
                student_class
            ),
            "number": int(
                student_number
            ),
            "name": student_name.strip(),
        }

        validation = validate_student_info(
            entered_student_info
        )

        if not validation.get(
            "success",
            False,
        ):
            render_message(
                validation.get(
                    "message",
                    "학생 정보를 확인해 주세요.",
                ),
                message_type="warning",
            )

        else:
            start_new_assessment(
                validation["student_info"]
            )

            st.rerun()

    st.markdown("")

    render_section_title(
        "3. 평가 구성"
    )

    structure_col1, structure_col2 = st.columns(
        2
    )

    with structure_col1:
        st.markdown(
            """
#### 문항 구성

- Stack 3문항
- Queue 3문항
- Tree 3문항
- Graph 3문항
- 총 12문항
            """
        )

    with structure_col2:
        st.markdown(
            """
#### 난이도 구성

각 영역에서 다음과 같이 출제됩니다.

- 기초 1문항
- 중간 1문항
- 심화 1문항
            """
        )


# ============================================================
# 9. 종합평가 응시 화면
# ============================================================

elif st.session_state.formative_stage == "assessment":

    questions = (
        st.session_state.formative_questions
    )

    student_info = (
        st.session_state.formative_student_info
    )

    sync_answers_from_widgets(
        questions=questions,
        answer_state_key="formative_answers",
        widget_prefix="formative_question",
    )

    answers = (
        st.session_state.formative_answers
    )

    answered_count = get_answered_count(
        questions=questions,
        answers=answers,
    )

    render_section_title(
        "1. 응시자 정보"
    )

    student_col, attempt_col = st.columns(
        [1.5, 1]
    )

    with student_col:
        render_student_information(
            student_info
        )

    with attempt_col:
        previous_attempt_count = max(
            0,
            int(
                st.session_state.formative_attempt
                or 1
            )
            - 1,
        )

        render_concept_box(
            title=(
                f"{st.session_state.formative_attempt}차 평가"
            ),
            text=(
                f"이전 제출 횟수는 "
                f"{previous_attempt_count}회입니다. "
                "현재 평가를 제출하면 새로운 결과가 저장됩니다."
            ),
        )

    render_section_title(
        "2. 문제 풀기"
    )

    render_assessment_progress(
        answered_count=answered_count,
        total_questions=len(
            questions
        ),
    )

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

        selected_answer = (
            render_multiple_choice_question(
                question_number=index,
                question=question,
                selected_answer=(
                    get_answer_for_question(
                        question_id,
                        "formative_answers",
                    )
                ),
                key_prefix="formative_question",
                disabled=False,
            )
        )

        if (
            selected_answer is not None
            and str(selected_answer).strip()
        ):
            st.session_state.formative_answers[
                question_id
            ] = selected_answer

        st.markdown("")

    sync_answers_from_widgets(
        questions=questions,
        answer_state_key="formative_answers",
        widget_prefix="formative_question",
    )

    answers = (
        st.session_state.formative_answers
    )

    unanswered_numbers = get_unanswered_numbers(
        questions=questions,
        answers=answers,
    )

    render_section_title(
        "3. 답안 제출"
    )

    button_col1, button_col2, button_col3 = st.columns(
        [1, 1, 1]
    )

    with button_col1:
        if st.button(
            "📋 응답 현황 보기",
            use_container_width=True,
            key="show_answer_summary_button",
        ):
            st.session_state.formative_show_answer_summary = (
                not st.session_state.formative_show_answer_summary
            )

            st.rerun()

    with button_col2:
        submit_clicked = st.button(
            "✅ 형성평가 제출",
            use_container_width=True,
            key="submit_formative_assessment",
            type="primary",
        )

    with button_col3:
        cancel_clicked = st.button(
            "🔄 평가 취소",
            use_container_width=True,
            key="cancel_formative_assessment",
        )

    if st.session_state.formative_show_answer_summary:
        st.markdown(
            "#### 문항별 응답 현황"
        )

        render_answer_summary(
            questions=questions,
            answers=answers,
        )

    if submit_clicked:
        if unanswered_numbers:
            render_unanswered_warning(
                unanswered_numbers
            )

        else:
            submit_main_assessment()

            if (
                st.session_state.formative_result
                and st.session_state
                .formative_result
                .get(
                    "success",
                    False,
                )
            ):
                st.rerun()

    elif unanswered_numbers:
        st.caption(
            f"현재 미응답 문항: "
            f"{len(unanswered_numbers)}개"
        )

    if cancel_clicked:
        reset_formative_assessment(
            keep_student_info=True
        )

        st.rerun()


# ============================================================
# 10. 최초 평가 결과 화면
# ============================================================

elif st.session_state.formative_stage == "result":

    result = (
        st.session_state.formative_result
    )

    save_result = (
        st.session_state.formative_save_result
    )

    student_info = (
        st.session_state.formative_student_info
    )

    if not result:
        st.warning(
            "표시할 평가 결과가 없습니다."
        )

    else:
        render_section_title(
            "1. 평가 결과"
        )

        result_student_col, result_attempt_col = (
            st.columns(
                [1.5, 1]
            )
        )

        with result_student_col:
            render_student_information(
                student_info
            )

        with result_attempt_col:
            render_concept_box(
                title=(
                    f"{st.session_state.formative_attempt}차 "
                    "종합 형성평가"
                ),
                text=(
                    "최초 종합평가 결과입니다. "
                    "오답 다시 풀기는 별도의 학습 활동으로 "
                    "진행됩니다."
                ),
            )

        render_assessment_result_summary(
            result
        )

        if save_result:
            render_save_result_message(
                success=bool(
                    save_result.get(
                        "success",
                        False,
                    )
                ),
                message=save_result.get(
                    "message"
                ),
            )

        render_section_title(
            "2. 영역별 상세 결과"
        )

        render_domain_result_table(
            result.get(
                "domain_results",
                {},
            )
        )

        render_section_title(
            "3. 문항별 결과 및 해설"
        )

        result_filter = st.radio(
            "표시할 문항",
            [
                "전체 문항",
                "오답 문항만",
            ],
            horizontal=True,
            key="formative_result_filter",
        )

        render_all_question_results(
            question_results=result.get(
                "question_results",
                [],
            ),
            incorrect_only=(
                result_filter
                == "오답 문항만"
            ),
        )

        render_section_title(
            "4. 다음 학습"
        )

        incorrect_count = int(
            result.get(
                "incorrect_count",
                0,
            )
        )

        render_retry_guide(
            incorrect_count=incorrect_count
        )

        action_col1, action_col2, action_col3 = (
            st.columns(
                [1, 1, 1]
            )
        )

        with action_col1:
            retry_clicked = st.button(
                "🔁 오답 다시 풀기",
                use_container_width=True,
                key="start_formative_retry",
                disabled=incorrect_count == 0,
            )

        with action_col2:
            new_assessment_clicked = st.button(
                "📝 새 종합평가",
                use_container_width=True,
                key="start_new_formative_assessment",
            )

        with action_col3:
            change_student_clicked = st.button(
                "👤 다른 학생으로 응시",
                use_container_width=True,
                key="change_formative_student",
            )

        if retry_clicked:
            start_retry_assessment()
            st.rerun()

        if new_assessment_clicked:
            current_student_info = dict(
                st.session_state.formative_student_info
            )

            reset_formative_assessment(
                keep_student_info=True
            )

            start_new_assessment(
                current_student_info
            )

            st.rerun()

        if change_student_clicked:
            reset_formative_assessment(
                keep_student_info=False
            )

            st.rerun()


# ============================================================
# 11. 오답 재도전 응시 화면
# ============================================================

elif st.session_state.formative_stage == "retry":

    retry_questions = (
        st.session_state.formative_retry_questions
    )

    sync_answers_from_widgets(
        questions=retry_questions,
        answer_state_key="formative_retry_answers",
        widget_prefix="formative_retry_question",
    )

    retry_answers = (
        st.session_state.formative_retry_answers
    )

    retry_answered_count = get_answered_count(
        questions=retry_questions,
        answers=retry_answers,
    )

    render_section_title(
        "1. 오답 다시 풀기"
    )

    render_concept_box(
        title=(
            f"오답 {len(retry_questions)}문항에 다시 도전합니다."
        ),
        text=(
            "선택지의 순서는 이전 평가와 달라질 수 있습니다. "
            "정답을 외우기보다 관련 개념과 자료구조의 동작 원리를 "
            "생각하며 문제를 풀어 보세요."
        ),
    )

    render_assessment_progress(
        answered_count=retry_answered_count,
        total_questions=len(
            retry_questions
        ),
    )

    for index, question in enumerate(
        retry_questions,
        start=1,
    ):
        question_id = str(
            question.get(
                "id",
                f"retry_question_{index}",
            )
        )

        selected_answer = (
            render_multiple_choice_question(
                question_number=index,
                question=question,
                selected_answer=(
                    get_answer_for_question(
                        question_id,
                        "formative_retry_answers",
                    )
                ),
                key_prefix=(
                    "formative_retry_question"
                ),
                disabled=False,
            )
        )

        if (
            selected_answer is not None
            and str(selected_answer).strip()
        ):
            st.session_state.formative_retry_answers[
                question_id
            ] = selected_answer

        st.markdown("")

    sync_answers_from_widgets(
        questions=retry_questions,
        answer_state_key="formative_retry_answers",
        widget_prefix="formative_retry_question",
    )

    retry_answers = (
        st.session_state.formative_retry_answers
    )

    retry_unanswered_numbers = (
        get_unanswered_numbers(
            questions=retry_questions,
            answers=retry_answers,
        )
    )

    render_section_title(
        "2. 재도전 제출"
    )

    retry_button_col1, retry_button_col2 = st.columns(
        2
    )

    with retry_button_col1:
        retry_submit_clicked = st.button(
            "✅ 재도전 결과 확인",
            use_container_width=True,
            key="submit_formative_retry",
            type="primary",
        )

    with retry_button_col2:
        retry_cancel_clicked = st.button(
            "↩ 최초 평가 결과로 돌아가기",
            use_container_width=True,
            key="cancel_formative_retry",
        )

    if retry_submit_clicked:
        if retry_unanswered_numbers:
            render_unanswered_warning(
                retry_unanswered_numbers
            )

        else:
            submit_retry_assessment()

            if (
                st.session_state.formative_retry_result
                and st.session_state
                .formative_retry_result
                .get(
                    "success",
                    False,
                )
            ):
                st.rerun()

    if retry_cancel_clicked:
        st.session_state.formative_stage = "result"
        st.session_state.formative_retry_active = False

        clear_widget_keys(
            [
                "formative_retry_question_",
            ]
        )

        st.rerun()


# ============================================================
# 12. 오답 재도전 결과 화면
# ============================================================

elif st.session_state.formative_stage == "retry_result":

    retry_result = (
        st.session_state.formative_retry_result
    )

    original_result = (
        st.session_state.formative_result
    )

    render_section_title(
        "1. 오답 재도전 결과"
    )

    if not retry_result:
        st.warning(
            "표시할 재도전 결과가 없습니다."
        )

    else:
        render_assessment_result_summary(
            retry_result
        )

        render_message(
            (
                "오답 재도전 결과는 학습 피드백용이며, "
                "results/formative_results.csv에는 별도로 "
                "저장하지 않습니다."
            ),
            message_type="info",
        )

        original_incorrect_count = int(
            original_result.get(
                "incorrect_count",
                0,
            )
            if original_result
            else 0
        )

        retry_incorrect_count = int(
            retry_result.get(
                "incorrect_count",
                0,
            )
        )

        improved_count = max(
            0,
            original_incorrect_count
            - retry_incorrect_count,
        )

        comparison_col1, comparison_col2, comparison_col3 = (
            st.columns(
                3
            )
        )

        with comparison_col1:
            st.metric(
                "처음 틀린 문항",
                f"{original_incorrect_count}개",
            )

        with comparison_col2:
            st.metric(
                "재도전 오답",
                f"{retry_incorrect_count}개",
            )

        with comparison_col3:
            st.metric(
                "새롭게 맞힌 문항",
                f"{improved_count}개",
            )

        render_section_title(
            "2. 재도전 문항 해설"
        )

        retry_result_filter = st.radio(
            "표시할 재도전 문항",
            [
                "전체 문항",
                "아직 틀린 문항만",
            ],
            horizontal=True,
            key="formative_retry_result_filter",
        )

        render_all_question_results(
            question_results=retry_result.get(
                "question_results",
                [],
            ),
            incorrect_only=(
                retry_result_filter
                == "아직 틀린 문항만"
            ),
        )

        render_section_title(
            "3. 다음 활동"
        )

        retry_action_col1, retry_action_col2, retry_action_col3 = (
            st.columns(
                3
            )
        )

        with retry_action_col1:
            retry_again_clicked = st.button(
                "🔁 남은 오답 다시 풀기",
                use_container_width=True,
                key="retry_incorrect_again",
                disabled=retry_incorrect_count == 0,
            )

        with retry_action_col2:
            original_result_clicked = st.button(
                "📊 최초 결과 보기",
                use_container_width=True,
                key="show_original_result",
            )

        with retry_action_col3:
            new_full_assessment_clicked = st.button(
                "📝 새 종합평가",
                use_container_width=True,
                key="new_full_assessment_after_retry",
            )

        if retry_again_clicked:
            current_retry_questions = (
                st.session_state.formative_retry_questions
            )

            next_retry_questions = create_retry_questions(
                original_questions=current_retry_questions,
                assessment_result=retry_result,
                shuffle_options=True,
                shuffle_question_order=False,
            )

            clear_widget_keys(
                [
                    "formative_retry_question_",
                ]
            )

            st.session_state.formative_retry_questions = (
                next_retry_questions
            )

            st.session_state.formative_retry_answers = {}
            st.session_state.formative_retry_result = None
            st.session_state.formative_stage = "retry"

            st.rerun()

        if original_result_clicked:
            st.session_state.formative_stage = "result"
            st.rerun()

        if new_full_assessment_clicked:
            current_student_info = dict(
                st.session_state.formative_student_info
            )

            reset_formative_assessment(
                keep_student_info=True
            )

            start_new_assessment(
                current_student_info
            )

            st.rerun()


# ============================================================
# 13. 알 수 없는 상태 복구
# ============================================================

else:

    st.warning(
        "평가 진행 상태를 확인할 수 없어 초기 화면으로 돌아갑니다."
    )

    reset_formative_assessment(
        keep_student_info=False
    )

    st.rerun()


# ============================================================
# 14. 페이지 하단
# ============================================================

render_footer()