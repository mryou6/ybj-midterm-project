"""
자료구조 종합 형성평가의 핵심 로직을 담당하는 모듈입니다.

주요 기능
1. JSON 문항 데이터 불러오기
2. 문항 데이터 검증
3. 영역별 문항 무작위 추출
4. 난이도를 고려한 문항 추출
5. 선택지 순서 무작위 배열
6. 답안 채점
7. 영역별 점수 계산
8. 오답 개념 분석
9. 성취 수준 판정
10. 오답 재도전 문항 생성
11. CSV 평가 결과 저장
12. 학생별 응시 횟수 계산
"""

from __future__ import annotations

import csv
import json
import random
from collections import Counter
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any


# ============================================================
# 1. 기본 경로와 상수
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

DEFAULT_QUESTION_PATH = (
    PROJECT_ROOT
    / "data"
    / "formative_questions.json"
)

DEFAULT_RESULT_PATH = (
    PROJECT_ROOT
    / "results"
    / "formative_results.csv"
)


SUPPORTED_DOMAINS = [
    "stack",
    "queue",
    "tree",
    "graph",
]

DOMAIN_LABELS = {
    "stack": "Stack",
    "queue": "Queue",
    "tree": "Tree",
    "graph": "Graph",
}

SUPPORTED_DIFFICULTIES = [
    "basic",
    "intermediate",
    "advanced",
]

ACHIEVEMENT_DESCRIPTIONS = {
    "A": "개념 이해 우수",
    "B": "개념 이해 양호",
    "C": "기본 개념 이해",
    "D": "일부 개념 보완 필요",
    "E": "기초 개념 재학습 필요",
}


RESULT_CSV_HEADERS = [
    "submitted_at",
    "student_grade",
    "student_class",
    "student_number",
    "student_name",
    "attempt",
    "total_score",
    "total_questions",
    "percentage",
    "achievement_level",
    "stack_score",
    "stack_total",
    "queue_score",
    "queue_total",
    "tree_score",
    "tree_total",
    "graph_score",
    "graph_total",
    "incorrect_concepts",
    "question_ids",
    "student_answers",
    "correct_answers",
    "incorrect_question_ids",
]


# ============================================================
# 2. 공통 보조 함수
# ============================================================

def normalize_text(
    value: Any,
) -> str:
    """
    비교 및 저장에 사용할 문자열을 정리합니다.
    """

    if value is None:
        return ""

    return str(value).strip()


def safe_integer(
    value: Any,
    default: int = 0,
) -> int:
    """
    값을 안전하게 정수로 변환합니다.
    """

    try:
        return int(value)

    except (TypeError, ValueError):
        return default


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    값을 안전하게 실수로 변환합니다.
    """

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def join_csv_values(
    values: list[Any],
    separator: str = "|",
) -> str:
    """
    리스트를 CSV 한 칸에 저장하기 위한 문자열로 변환합니다.
    """

    return separator.join(
        normalize_text(value)
        for value in values
    )


def get_domain_label(
    domain: str,
) -> str:
    """
    내부 영역 이름을 화면 표시용 이름으로 변환합니다.
    """

    return DOMAIN_LABELS.get(
        str(domain).lower(),
        str(domain),
    )


# ============================================================
# 3. 문항 데이터 불러오기
# ============================================================

def load_question_bank(
    file_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    JSON 파일에서 형성평가 문항을 불러옵니다.

    Args:
        file_path:
            문항 JSON 파일 경로.
            생략하면 data/formative_questions.json을 사용합니다.

    Returns:
        JSON 전체 데이터

    Raises:
        FileNotFoundError:
            문항 파일이 없는 경우

        ValueError:
            JSON 형식이나 문항 구조가 올바르지 않은 경우
    """

    question_path = Path(
        file_path
        if file_path is not None
        else DEFAULT_QUESTION_PATH
    )

    if not question_path.exists():
        raise FileNotFoundError(
            f"형성평가 문항 파일을 찾을 수 없습니다: "
            f"{question_path}"
        )

    if not question_path.is_file():
        raise ValueError(
            f"문항 경로가 파일이 아닙니다: "
            f"{question_path}"
        )

    try:
        with question_path.open(
            "r",
            encoding="utf-8",
        ) as question_file:
            question_bank = json.load(
                question_file
            )

    except json.JSONDecodeError as error:
        raise ValueError(
            "formative_questions.json의 JSON 형식이 "
            f"올바르지 않습니다: {error}"
        ) from error

    if not isinstance(
        question_bank,
        dict,
    ):
        raise ValueError(
            "문항 JSON의 최상위 데이터는 객체 형식이어야 합니다."
        )

    validation_result = validate_question_bank(
        question_bank
    )

    if not validation_result["success"]:
        error_text = "\n".join(
            validation_result["errors"]
        )

        raise ValueError(
            "형성평가 문항 데이터에 오류가 있습니다.\n"
            f"{error_text}"
        )

    return question_bank


# ============================================================
# 4. 문항 데이터 검증
# ============================================================

def validate_question(
    question: dict[str, Any],
    expected_domain: str | None = None,
) -> list[str]:
    """
    개별 문항의 필수 항목과 데이터 구조를 확인합니다.

    Returns:
        오류 메시지 목록
    """

    errors: list[str] = []

    required_fields = [
        "id",
        "domain",
        "type",
        "difficulty",
        "concept",
        "question",
        "options",
        "answer",
        "explanation",
    ]

    for field_name in required_fields:
        if field_name not in question:
            errors.append(
                f"필수 항목 '{field_name}'이(가) 없습니다."
            )

    if errors:
        return errors

    question_id = normalize_text(
        question.get("id")
    )

    domain = normalize_text(
        question.get("domain")
    ).lower()

    question_type = normalize_text(
        question.get("type")
    )

    difficulty = normalize_text(
        question.get("difficulty")
    ).lower()

    question_text = normalize_text(
        question.get("question")
    )

    concept = normalize_text(
        question.get("concept")
    )

    answer = normalize_text(
        question.get("answer")
    )

    explanation = normalize_text(
        question.get("explanation")
    )

    options = question.get(
        "options"
    )

    if not question_id:
        errors.append(
            "문항 ID가 비어 있습니다."
        )

    if domain not in SUPPORTED_DOMAINS:
        errors.append(
            f"지원하지 않는 영역입니다: {domain}"
        )

    if (
        expected_domain is not None
        and domain != expected_domain
    ):
        errors.append(
            f"문항 영역 '{domain}'이(가) "
            f"배치된 영역 '{expected_domain}'과 다릅니다."
        )

    if question_type != "multiple_choice":
        errors.append(
            f"현재 지원하지 않는 문항 유형입니다: "
            f"{question_type}"
        )

    if difficulty not in SUPPORTED_DIFFICULTIES:
        errors.append(
            f"지원하지 않는 난이도입니다: {difficulty}"
        )

    if not question_text:
        errors.append(
            "문항 내용이 비어 있습니다."
        )

    if not concept:
        errors.append(
            "평가 개념이 비어 있습니다."
        )

    if not explanation:
        errors.append(
            "문항 해설이 비어 있습니다."
        )

    if not isinstance(
        options,
        list,
    ):
        errors.append(
            "선택지는 리스트 형식이어야 합니다."
        )

    else:
        cleaned_options = [
            normalize_text(option)
            for option in options
        ]

        if len(cleaned_options) < 2:
            errors.append(
                "객관식 문항은 선택지가 2개 이상이어야 합니다."
            )

        if any(
            not option
            for option in cleaned_options
        ):
            errors.append(
                "비어 있는 선택지가 포함되어 있습니다."
            )

        if len(
            set(cleaned_options)
        ) != len(cleaned_options):
            errors.append(
                "중복된 선택지가 포함되어 있습니다."
            )

        if answer not in cleaned_options:
            errors.append(
                f"정답 '{answer}'이(가) 선택지에 없습니다."
            )

    return errors


def validate_question_bank(
    question_bank: dict[str, Any],
) -> dict[str, Any]:
    """
    전체 문항 데이터의 구조와 문항 ID 중복을 확인합니다.

    Returns:
        {
            "success": bool,
            "errors": list[str],
            "question_count": int,
            "domain_counts": dict
        }
    """

    errors: list[str] = []
    question_ids: list[str] = []
    domain_counts: dict[str, int] = {}
    total_count = 0

    for domain in SUPPORTED_DOMAINS:
        domain_questions = question_bank.get(
            domain
        )

        if domain_questions is None:
            errors.append(
                f"'{domain}' 영역이 없습니다."
            )
            continue

        if not isinstance(
            domain_questions,
            list,
        ):
            errors.append(
                f"'{domain}' 영역의 문항은 리스트 형식이어야 합니다."
            )
            continue

        domain_counts[domain] = len(
            domain_questions
        )

        total_count += len(
            domain_questions
        )

        for index, question in enumerate(
            domain_questions,
            start=1,
        ):
            if not isinstance(
                question,
                dict,
            ):
                errors.append(
                    f"{domain} 영역 {index}번째 문항이 "
                    "객체 형식이 아닙니다."
                )
                continue

            question_errors = validate_question(
                question,
                expected_domain=domain,
            )

            question_id = normalize_text(
                question.get(
                    "id",
                    f"{domain}_{index}",
                )
            )

            question_ids.append(
                question_id
            )

            for error in question_errors:
                errors.append(
                    f"[{question_id}] {error}"
                )

    duplicated_ids = sorted(
        question_id
        for question_id, count
        in Counter(question_ids).items()
        if count > 1
    )

    if duplicated_ids:
        errors.append(
            "중복된 문항 ID가 있습니다: "
            + ", ".join(
                duplicated_ids
            )
        )

    metadata = question_bank.get(
        "metadata",
        {},
    )

    if isinstance(
        metadata,
        dict,
    ):
        metadata_total = metadata.get(
            "total_questions"
        )

        if metadata_total is not None:
            if safe_integer(
                metadata_total,
                -1,
            ) != total_count:
                errors.append(
                    "metadata의 total_questions와 "
                    f"실제 문항 수가 다릅니다. "
                    f"metadata={metadata_total}, 실제={total_count}"
                )

    return {
        "success": not errors,
        "errors": errors,
        "question_count": total_count,
        "domain_counts": domain_counts,
    }


# ============================================================
# 5. 문항 목록 정리
# ============================================================

def get_all_questions(
    question_bank: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    모든 영역의 문항을 하나의 목록으로 반환합니다.
    """

    questions: list[dict[str, Any]] = []

    for domain in SUPPORTED_DOMAINS:
        domain_questions = question_bank.get(
            domain,
            [],
        )

        for question in domain_questions:
            questions.append(
                deepcopy(question)
            )

    return questions


def get_questions_by_domain(
    question_bank: dict[str, Any],
    domain: str,
) -> list[dict[str, Any]]:
    """
    특정 영역의 문항 목록을 반환합니다.
    """

    normalized_domain = str(
        domain
    ).lower()

    if normalized_domain not in SUPPORTED_DOMAINS:
        raise ValueError(
            f"지원하지 않는 영역입니다: {domain}"
        )

    return deepcopy(
        question_bank.get(
            normalized_domain,
            [],
        )
    )


def get_question_by_id(
    question_bank: dict[str, Any],
    question_id: str,
) -> dict[str, Any] | None:
    """
    문항 ID로 특정 문항을 찾습니다.
    """

    normalized_id = normalize_text(
        question_id
    )

    for question in get_all_questions(
        question_bank
    ):
        if normalize_text(
            question.get("id")
        ) == normalized_id:
            return question

    return None


# ============================================================
# 6. 선택지 순서 무작위 배열
# ============================================================

def shuffle_question_options(
    question: dict[str, Any],
    random_generator: random.Random | None = None,
) -> dict[str, Any]:
    """
    문항의 선택지 순서를 무작위로 섞습니다.

    정답은 선택지 문자열 자체로 저장되어 있으므로
    선택지 순서가 바뀌어도 정답 판정에는 문제가 없습니다.
    """

    generator = (
        random_generator
        if random_generator is not None
        else random.Random()
    )

    shuffled_question = deepcopy(
        question
    )

    options = list(
        shuffled_question.get(
            "options",
            [],
        )
    )

    generator.shuffle(
        options
    )

    shuffled_question["options"] = options

    return shuffled_question


# ============================================================
# 7. 난이도별 문항 추출
# ============================================================

def select_questions_by_difficulty(
    questions: list[dict[str, Any]],
    count: int,
    difficulty_distribution: dict[str, int] | None = None,
    random_generator: random.Random | None = None,
) -> list[dict[str, Any]]:
    """
    특정 영역의 문항에서 난이도를 고려해 문항을 추출합니다.

    difficulty_distribution 예:
        {
            "basic": 1,
            "intermediate": 1,
            "advanced": 1,
        }

    특정 난이도의 문항이 부족하면 남은 문항 중에서 채웁니다.
    """

    generator = (
        random_generator
        if random_generator is not None
        else random.Random()
    )

    safe_count = max(
        0,
        int(count),
    )

    if safe_count == 0:
        return []

    if safe_count > len(questions):
        raise ValueError(
            f"요청한 문항 수 {safe_count}개가 "
            f"사용 가능한 문항 수 {len(questions)}개보다 많습니다."
        )

    available_questions = deepcopy(
        questions
    )

    selected_questions: list[
        dict[str, Any]
    ] = []

    selected_ids: set[str] = set()

    # 난이도 지정이 없으면 전체에서 무작위 추출
    if not difficulty_distribution:
        selected_questions = generator.sample(
            available_questions,
            safe_count,
        )

        return selected_questions

    requested_total = sum(
        max(
            0,
            safe_integer(
                difficulty_count
            ),
        )
        for difficulty_count
        in difficulty_distribution.values()
    )

    if requested_total > safe_count:
        raise ValueError(
            "난이도별 문항 수 합계가 "
            "전체 추출 문항 수보다 많습니다."
        )

    # 난이도별 우선 추출
    for difficulty in SUPPORTED_DIFFICULTIES:
        requested_count = max(
            0,
            safe_integer(
                difficulty_distribution.get(
                    difficulty,
                    0,
                )
            ),
        )

        if requested_count == 0:
            continue

        difficulty_questions = [
            question
            for question in available_questions
            if normalize_text(
                question.get("difficulty")
            ).lower() == difficulty
        ]

        selected_count = min(
            requested_count,
            len(difficulty_questions),
        )

        if selected_count > 0:
            difficulty_selected = generator.sample(
                difficulty_questions,
                selected_count,
            )

            for question in difficulty_selected:
                question_id = normalize_text(
                    question.get("id")
                )

                if question_id not in selected_ids:
                    selected_questions.append(
                        question
                    )
                    selected_ids.add(
                        question_id
                    )

    # 부족한 문항은 남은 전체 문항에서 보충
    remaining_count = (
        safe_count
        - len(selected_questions)
    )

    if remaining_count > 0:
        remaining_questions = [
            question
            for question in available_questions
            if normalize_text(
                question.get("id")
            ) not in selected_ids
        ]

        if remaining_count > len(
            remaining_questions
        ):
            raise ValueError(
                "문항 추출 과정에서 사용할 수 있는 문항이 부족합니다."
            )

        additional_questions = generator.sample(
            remaining_questions,
            remaining_count,
        )

        selected_questions.extend(
            additional_questions
        )

    return selected_questions


# ============================================================
# 8. 종합평가 문항 생성
# ============================================================

def create_assessment_questions(
    question_bank: dict[str, Any],
    distribution: dict[str, int],
    difficulty_distribution: (
        dict[str, dict[str, int]]
        | dict[str, int]
        | None
    ) = None,
    shuffle_options: bool = True,
    shuffle_question_order: bool = True,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """
    영역별 문항 수에 맞춰 종합 형성평가 문항을 생성합니다.

    Args:
        question_bank:
            load_question_bank()로 불러온 데이터

        distribution:
            영역별 추출 문항 수

            예:
                {
                    "stack": 3,
                    "queue": 3,
                    "tree": 3,
                    "graph": 3,
                }

        difficulty_distribution:
            모든 영역에 동일하게 적용할 경우:

                {
                    "basic": 1,
                    "intermediate": 1,
                    "advanced": 1,
                }

            영역별로 다르게 적용할 경우:

                {
                    "stack": {
                        "basic": 1,
                        "intermediate": 1,
                        "advanced": 1,
                    },
                    ...
                }

        shuffle_options:
            선택지 순서를 섞을지 여부

        shuffle_question_order:
            영역을 섞어 문항 순서를 무작위로 할지 여부

        seed:
            같은 문항 구성을 재현할 때 사용할 시드

    Returns:
        평가에 사용할 문항 목록
    """

    generator = random.Random(
        seed
    )

    selected_questions: list[
        dict[str, Any]
    ] = []

    for domain in SUPPORTED_DOMAINS:
        requested_count = max(
            0,
            safe_integer(
                distribution.get(
                    domain,
                    0,
                )
            ),
        )

        if requested_count == 0:
            continue

        domain_questions = get_questions_by_domain(
            question_bank,
            domain,
        )

        domain_difficulty_distribution = None

        if difficulty_distribution:
            # 영역별 난이도 딕셔너리인지 확인
            if (
                domain in difficulty_distribution
                and isinstance(
                    difficulty_distribution.get(
                        domain
                    ),
                    dict,
                )
            ):
                domain_difficulty_distribution = (
                    difficulty_distribution.get(
                        domain
                    )
                )

            # 전체 공통 난이도 딕셔너리
            elif any(
                difficulty in difficulty_distribution
                for difficulty in SUPPORTED_DIFFICULTIES
            ):
                domain_difficulty_distribution = (
                    difficulty_distribution
                )

        domain_selected = (
            select_questions_by_difficulty(
                questions=domain_questions,
                count=requested_count,
                difficulty_distribution=(
                    domain_difficulty_distribution
                ),
                random_generator=generator,
            )
        )

        selected_questions.extend(
            domain_selected
        )

    if shuffle_options:
        selected_questions = [
            shuffle_question_options(
                question,
                random_generator=generator,
            )
            for question in selected_questions
        ]

    if shuffle_question_order:
        generator.shuffle(
            selected_questions
        )

    # 화면에서 원래 문항 번호를 추적하기 위한 번호 저장
    for question_number, question in enumerate(
        selected_questions,
        start=1,
    ):
        question["question_number"] = (
            question_number
        )

    return selected_questions


# ============================================================
# 9. 응답 상태 확인
# ============================================================

def get_answered_count(
    questions: list[dict[str, Any]],
    answers: dict[str, Any],
) -> int:
    """
    현재 응답한 문항 수를 반환합니다.
    """

    answered_count = 0

    for question in questions:
        question_id = normalize_text(
            question.get("id")
        )

        answer = normalize_text(
            answers.get(
                question_id
            )
        )

        if answer:
            answered_count += 1

    return answered_count


def get_unanswered_questions(
    questions: list[dict[str, Any]],
    answers: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    아직 응답하지 않은 문항 목록을 반환합니다.
    """

    unanswered_questions: list[
        dict[str, Any]
    ] = []

    for question in questions:
        question_id = normalize_text(
            question.get("id")
        )

        answer = normalize_text(
            answers.get(
                question_id
            )
        )

        if not answer:
            unanswered_questions.append(
                question
            )

    return unanswered_questions


def get_unanswered_numbers(
    questions: list[dict[str, Any]],
    answers: dict[str, Any],
) -> list[int]:
    """
    아직 응답하지 않은 문항 번호를 반환합니다.
    """

    unanswered_numbers: list[int] = []

    for index, question in enumerate(
        questions,
        start=1,
    ):
        question_id = normalize_text(
            question.get("id")
        )

        answer = normalize_text(
            answers.get(
                question_id
            )
        )

        if not answer:
            unanswered_numbers.append(
                safe_integer(
                    question.get(
                        "question_number",
                        index,
                    ),
                    index,
                )
            )

    return unanswered_numbers


def is_assessment_complete(
    questions: list[dict[str, Any]],
    answers: dict[str, Any],
) -> bool:
    """
    모든 문항에 답했는지 확인합니다.
    """

    if not questions:
        return False

    return not get_unanswered_questions(
        questions,
        answers,
    )


# ============================================================
# 10. 성취 수준 판정
# ============================================================

def determine_achievement_level(
    percentage: float,
) -> dict[str, str]:
    """
    백분율 점수에 따라 성취 수준을 판정합니다.

    기준:
        90 이상: A
        80 이상: B
        70 이상: C
        60 이상: D
        60 미만: E
    """

    score = max(
        0.0,
        min(
            safe_float(
                percentage
            ),
            100.0,
        ),
    )

    if score >= 90:
        level = "A"

    elif score >= 80:
        level = "B"

    elif score >= 70:
        level = "C"

    elif score >= 60:
        level = "D"

    else:
        level = "E"

    return {
        "level": level,
        "description": (
            ACHIEVEMENT_DESCRIPTIONS[
                level
            ]
        ),
    }


# ============================================================
# 11. 답안 채점
# ============================================================

def grade_assessment(
    questions: list[dict[str, Any]],
    answers: dict[str, Any],
    require_all_answers: bool = True,
) -> dict[str, Any]:
    """
    학생 답안을 채점하고 종합 결과를 생성합니다.

    Args:
        questions:
            출제된 문항 목록

        answers:
            {
                "stack_001": "LIFO",
                "queue_001": "FIFO",
                ...
            }

        require_all_answers:
            True이면 미응답 문항이 있을 때 채점을 중단합니다.

    Returns:
        formative_assessment_visualizer.py와 호환되는 결과
    """

    if not questions:
        return {
            "success": False,
            "message": (
                "채점할 문항이 없습니다."
            ),
            "unanswered_numbers": [],
        }

    unanswered_numbers = get_unanswered_numbers(
        questions,
        answers,
    )

    if (
        require_all_answers
        and unanswered_numbers
    ):
        return {
            "success": False,
            "message": (
                "아직 응답하지 않은 문항이 있습니다."
            ),
            "unanswered_numbers": (
                unanswered_numbers
            ),
        }

    question_results: list[
        dict[str, Any]
    ] = []

    domain_results: dict[
        str,
        dict[str, Any]
    ] = {
        domain: {
            "score": 0,
            "total": 0,
            "percentage": 0.0,
        }
        for domain in SUPPORTED_DOMAINS
    }

    incorrect_concepts: list[str] = []
    incorrect_question_ids: list[str] = []

    total_score = 0

    for index, question in enumerate(
        questions,
        start=1,
    ):
        question_id = normalize_text(
            question.get("id")
        )

        domain = normalize_text(
            question.get("domain")
        ).lower()

        student_answer = normalize_text(
            answers.get(
                question_id
            )
        )

        correct_answer = normalize_text(
            question.get("answer")
        )

        is_correct = (
            bool(student_answer)
            and student_answer
            == correct_answer
        )

        if is_correct:
            total_score += 1

        if domain not in domain_results:
            domain_results[domain] = {
                "score": 0,
                "total": 0,
                "percentage": 0.0,
            }

        domain_results[domain]["total"] += 1

        if is_correct:
            domain_results[domain]["score"] += 1

        else:
            concept = normalize_text(
                question.get("concept")
            )

            if concept:
                incorrect_concepts.append(
                    concept
                )

            incorrect_question_ids.append(
                question_id
            )

        question_number = safe_integer(
            question.get(
                "question_number",
                index,
            ),
            index,
        )

        question_results.append(
            {
                "question_number": question_number,
                "question_id": question_id,
                "domain": domain,
                "difficulty": normalize_text(
                    question.get(
                        "difficulty"
                    )
                ),
                "concept": normalize_text(
                    question.get(
                        "concept"
                    )
                ),
                "question": normalize_text(
                    question.get(
                        "question"
                    )
                ),
                "student_answer": (
                    student_answer
                    if student_answer
                    else None
                ),
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": normalize_text(
                    question.get(
                        "explanation"
                    )
                ),
            }
        )

    total_questions = len(
        questions
    )

    percentage = round(
        (
            total_score
            / total_questions
            * 100
        )
        if total_questions > 0
        else 0.0,
        1,
    )

    for domain, domain_result in domain_results.items():
        domain_total = safe_integer(
            domain_result.get(
                "total"
            )
        )

        domain_score = safe_integer(
            domain_result.get(
                "score"
            )
        )

        domain_percentage = round(
            (
                domain_score
                / domain_total
                * 100
            )
            if domain_total > 0
            else 0.0,
            1,
        )

        domain_result["percentage"] = (
            domain_percentage
        )

    achievement = determine_achievement_level(
        percentage
    )

    unique_incorrect_concepts = list(
        dict.fromkeys(
            incorrect_concepts
        )
    )

    return {
        "success": True,
        "message": (
            "형성평가 채점이 완료되었습니다."
        ),
        "total_score": total_score,
        "total_questions": total_questions,
        "percentage": percentage,
        "achievement_level": (
            achievement["level"]
        ),
        "achievement_description": (
            achievement["description"]
        ),
        "domain_results": domain_results,
        "incorrect_concepts": (
            unique_incorrect_concepts
        ),
        "incorrect_question_ids": (
            incorrect_question_ids
        ),
        "incorrect_count": len(
            incorrect_question_ids
        ),
        "question_results": (
            question_results
        ),
        "unanswered_numbers": (
            unanswered_numbers
        ),
    }


# ============================================================
# 12. 오답 문항 재도전
# ============================================================

def create_retry_questions(
    original_questions: list[dict[str, Any]],
    assessment_result: dict[str, Any],
    shuffle_options: bool = True,
    shuffle_question_order: bool = False,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """
    오답 문항만 다시 풀기 위한 문항 목록을 생성합니다.
    """

    incorrect_question_ids = set(
        assessment_result.get(
            "incorrect_question_ids",
            [],
        )
    )

    retry_questions = [
        deepcopy(question)
        for question in original_questions
        if normalize_text(
            question.get("id")
        ) in incorrect_question_ids
    ]

    generator = random.Random(
        seed
    )

    if shuffle_options:
        retry_questions = [
            shuffle_question_options(
                question,
                random_generator=generator,
            )
            for question in retry_questions
        ]

    if shuffle_question_order:
        generator.shuffle(
            retry_questions
        )

    for question_number, question in enumerate(
        retry_questions,
        start=1,
    ):
        question["question_number"] = (
            question_number
        )

    return retry_questions


# ============================================================
# 13. CSV 파일 준비
# ============================================================

def ensure_result_csv(
    file_path: str | Path | None = None,
) -> Path:
    """
    평가 결과 CSV가 없거나 비어 있으면 헤더를 생성합니다.

    Returns:
        준비된 CSV 파일 경로
    """

    result_path = Path(
        file_path
        if file_path is not None
        else DEFAULT_RESULT_PATH
    )

    result_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    should_write_header = (
        not result_path.exists()
        or result_path.stat().st_size == 0
    )

    if should_write_header:
        with result_path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as result_file:
            writer = csv.DictWriter(
                result_file,
                fieldnames=RESULT_CSV_HEADERS,
            )

            writer.writeheader()

    return result_path


# ============================================================
# 14. 기존 결과 읽기
# ============================================================

def read_result_rows(
    file_path: str | Path | None = None,
) -> list[dict[str, str]]:
    """
    저장된 평가 결과 CSV의 모든 행을 읽습니다.
    """

    result_path = ensure_result_csv(
        file_path
    )

    try:
        with result_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as result_file:
            reader = csv.DictReader(
                result_file
            )

            return [
                dict(row)
                for row in reader
            ]

    except csv.Error as error:
        raise ValueError(
            "형성평가 결과 CSV를 읽는 중 "
            f"오류가 발생했습니다: {error}"
        ) from error


# ============================================================
# 15. 학생 식별 및 응시 횟수
# ============================================================

def normalize_student_info(
    student_info: dict[str, Any],
) -> dict[str, str]:
    """
    학생 정보를 CSV 저장용 문자열로 정리합니다.
    """

    return {
        "grade": normalize_text(
            student_info.get(
                "grade"
            )
        ),
        "class": normalize_text(
            student_info.get(
                "class"
            )
        ),
        "number": normalize_text(
            student_info.get(
                "number"
            )
        ),
        "name": normalize_text(
            student_info.get(
                "name"
            )
        ),
    }


def validate_student_info(
    student_info: dict[str, Any],
) -> dict[str, Any]:
    """
    학생 정보의 필수 입력 여부를 확인합니다.
    """

    normalized_info = normalize_student_info(
        student_info
    )

    missing_fields: list[str] = []

    field_labels = {
        "grade": "학년",
        "class": "반",
        "number": "번호",
        "name": "이름 또는 별칭",
    }

    for field_name, field_label in field_labels.items():
        if not normalized_info[field_name]:
            missing_fields.append(
                field_label
            )

    return {
        "success": not missing_fields,
        "missing_fields": missing_fields,
        "student_info": normalized_info,
        "message": (
            ""
            if not missing_fields
            else (
                "다음 학생 정보를 입력해 주세요: "
                + ", ".join(
                    missing_fields
                )
            )
        ),
    }


def is_same_student(
    result_row: dict[str, Any],
    student_info: dict[str, Any],
) -> bool:
    """
    CSV 행과 입력된 학생 정보가 같은 학생인지 확인합니다.
    """

    normalized_info = normalize_student_info(
        student_info
    )

    return (
        normalize_text(
            result_row.get(
                "student_grade"
            )
        )
        == normalized_info["grade"]
        and normalize_text(
            result_row.get(
                "student_class"
            )
        )
        == normalized_info["class"]
        and normalize_text(
            result_row.get(
                "student_number"
            )
        )
        == normalized_info["number"]
        and normalize_text(
            result_row.get(
                "student_name"
            )
        )
        == normalized_info["name"]
    )


def get_student_attempt_count(
    student_info: dict[str, Any],
    file_path: str | Path | None = None,
) -> int:
    """
    해당 학생이 기존에 제출한 평가 횟수를 반환합니다.
    """

    rows = read_result_rows(
        file_path
    )

    return sum(
        1
        for row in rows
        if is_same_student(
            row,
            student_info,
        )
    )


def get_next_attempt_number(
    student_info: dict[str, Any],
    file_path: str | Path | None = None,
) -> int:
    """
    다음 제출에 사용할 응시 차수를 반환합니다.
    """

    rows = read_result_rows(
        file_path
    )

    attempts: list[int] = []

    for row in rows:
        if is_same_student(
            row,
            student_info,
        ):
            attempts.append(
                safe_integer(
                    row.get(
                        "attempt"
                    ),
                    0,
                )
            )

    if not attempts:
        return 1

    return max(
        attempts
    ) + 1


# ============================================================
# 16. CSV 저장 행 생성
# ============================================================

def create_result_row(
    student_info: dict[str, Any],
    assessment_result: dict[str, Any],
    attempt: int,
    submitted_at: str | None = None,
) -> dict[str, Any]:
    """
    채점 결과를 CSV 한 행 구조로 변환합니다.
    """

    normalized_info = normalize_student_info(
        student_info
    )

    domain_results = assessment_result.get(
        "domain_results",
        {},
    )

    question_results = assessment_result.get(
        "question_results",
        [],
    )

    question_ids = [
        result.get(
            "question_id",
            "",
        )
        for result in question_results
    ]

    student_answers = [
        (
            result.get(
                "student_answer"
            )
            if result.get(
                "student_answer"
            ) is not None
            else ""
        )
        for result in question_results
    ]

    correct_answers = [
        result.get(
            "correct_answer",
            "",
        )
        for result in question_results
    ]

    incorrect_question_ids = (
        assessment_result.get(
            "incorrect_question_ids",
            [],
        )
    )

    incorrect_concepts = (
        assessment_result.get(
            "incorrect_concepts",
            [],
        )
    )

    def domain_value(
        domain: str,
        key: str,
    ) -> int:
        return safe_integer(
            domain_results
            .get(
                domain,
                {},
            )
            .get(
                key,
                0,
            )
        )

    return {
        "submitted_at": (
            submitted_at
            or datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ),
        "student_grade": normalized_info[
            "grade"
        ],
        "student_class": normalized_info[
            "class"
        ],
        "student_number": normalized_info[
            "number"
        ],
        "student_name": normalized_info[
            "name"
        ],
        "attempt": int(
            attempt
        ),
        "total_score": safe_integer(
            assessment_result.get(
                "total_score"
            )
        ),
        "total_questions": safe_integer(
            assessment_result.get(
                "total_questions"
            )
        ),
        "percentage": safe_float(
            assessment_result.get(
                "percentage"
            )
        ),
        "achievement_level": normalize_text(
            assessment_result.get(
                "achievement_level"
            )
        ),
        "stack_score": domain_value(
            "stack",
            "score",
        ),
        "stack_total": domain_value(
            "stack",
            "total",
        ),
        "queue_score": domain_value(
            "queue",
            "score",
        ),
        "queue_total": domain_value(
            "queue",
            "total",
        ),
        "tree_score": domain_value(
            "tree",
            "score",
        ),
        "tree_total": domain_value(
            "tree",
            "total",
        ),
        "graph_score": domain_value(
            "graph",
            "score",
        ),
        "graph_total": domain_value(
            "graph",
            "total",
        ),
        "incorrect_concepts": join_csv_values(
            incorrect_concepts
        ),
        "question_ids": join_csv_values(
            question_ids
        ),
        "student_answers": join_csv_values(
            student_answers
        ),
        "correct_answers": join_csv_values(
            correct_answers
        ),
        "incorrect_question_ids": join_csv_values(
            incorrect_question_ids
        ),
    }


# ============================================================
# 17. 평가 결과 CSV 저장
# ============================================================

def save_assessment_result(
    student_info: dict[str, Any],
    assessment_result: dict[str, Any],
    file_path: str | Path | None = None,
    attempt: int | None = None,
) -> dict[str, Any]:
    """
    평가 결과를 CSV에 한 행 추가합니다.

    Returns:
        {
            "success": bool,
            "message": str,
            "attempt": int,
            "file_path": str,
            "row": dict | None
        }
    """

    student_validation = validate_student_info(
        student_info
    )

    if not student_validation["success"]:
        return {
            "success": False,
            "message": student_validation[
                "message"
            ],
            "attempt": None,
            "file_path": None,
            "row": None,
        }

    if not assessment_result.get(
        "success",
        False,
    ):
        return {
            "success": False,
            "message": (
                "채점이 완료되지 않은 결과는 저장할 수 없습니다."
            ),
            "attempt": None,
            "file_path": None,
            "row": None,
        }

    result_path = ensure_result_csv(
        file_path
    )

    resolved_attempt = (
        int(attempt)
        if attempt is not None
        else get_next_attempt_number(
            student_info,
            result_path,
        )
    )

    result_row = create_result_row(
        student_info=student_info,
        assessment_result=assessment_result,
        attempt=resolved_attempt,
    )

    try:
        with result_path.open(
            "a",
            encoding="utf-8-sig",
            newline="",
        ) as result_file:
            writer = csv.DictWriter(
                result_file,
                fieldnames=RESULT_CSV_HEADERS,
                extrasaction="ignore",
            )

            writer.writerow(
                result_row
            )

    except OSError as error:
        return {
            "success": False,
            "message": (
                "평가 결과 파일에 저장하지 못했습니다: "
                f"{error}"
            ),
            "attempt": resolved_attempt,
            "file_path": str(
                result_path
            ),
            "row": None,
        }

    return {
        "success": True,
        "message": (
            f"{normalized_student_name(student_info)} 학생의 "
            f"{resolved_attempt}차 평가 결과가 저장되었습니다."
        ),
        "attempt": resolved_attempt,
        "file_path": str(
            result_path
        ),
        "row": result_row,
    }


def normalized_student_name(
    student_info: dict[str, Any],
) -> str:
    """
    저장 메시지에 사용할 학생 이름을 반환합니다.
    """

    student_name = normalize_text(
        student_info.get(
            "name"
        )
    )

    return (
        student_name
        if student_name
        else "응시자"
    )


# ============================================================
# 18. 학생별 최근 결과 조회
# ============================================================

def get_student_results(
    student_info: dict[str, Any],
    file_path: str | Path | None = None,
) -> list[dict[str, str]]:
    """
    특정 학생의 모든 평가 결과를 반환합니다.
    """

    rows = read_result_rows(
        file_path
    )

    student_rows = [
        row
        for row in rows
        if is_same_student(
            row,
            student_info,
        )
    ]

    student_rows.sort(
        key=lambda row: (
            safe_integer(
                row.get(
                    "attempt"
                )
            ),
            normalize_text(
                row.get(
                    "submitted_at"
                )
            ),
        )
    )

    return student_rows


def get_latest_student_result(
    student_info: dict[str, Any],
    file_path: str | Path | None = None,
) -> dict[str, str] | None:
    """
    특정 학생의 가장 최근 평가 결과를 반환합니다.
    """

    student_results = get_student_results(
        student_info,
        file_path,
    )

    if not student_results:
        return None

    return student_results[-1]


# ============================================================
# 19. 결과 통계
# ============================================================

def calculate_result_statistics(
    file_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    저장된 전체 평가 결과의 간단한 통계를 계산합니다.
    """

    rows = read_result_rows(
        file_path
    )

    if not rows:
        return {
            "submission_count": 0,
            "student_count": 0,
            "average_percentage": 0.0,
            "achievement_counts": {
                level: 0
                for level in [
                    "A",
                    "B",
                    "C",
                    "D",
                    "E",
                ]
            },
        }

    student_keys = {
        (
            normalize_text(
                row.get(
                    "student_grade"
                )
            ),
            normalize_text(
                row.get(
                    "student_class"
                )
            ),
            normalize_text(
                row.get(
                    "student_number"
                )
            ),
            normalize_text(
                row.get(
                    "student_name"
                )
            ),
        )
        for row in rows
    }

    percentages = [
        safe_float(
            row.get(
                "percentage"
            )
        )
        for row in rows
    ]

    achievement_counts = {
        level: 0
        for level in [
            "A",
            "B",
            "C",
            "D",
            "E",
        ]
    }

    for row in rows:
        level = normalize_text(
            row.get(
                "achievement_level"
            )
        )

        if level in achievement_counts:
            achievement_counts[level] += 1

    return {
        "submission_count": len(
            rows
        ),
        "student_count": len(
            student_keys
        ),
        "average_percentage": round(
            sum(percentages)
            / len(percentages),
            1,
        ),
        "achievement_counts": (
            achievement_counts
        ),
    }