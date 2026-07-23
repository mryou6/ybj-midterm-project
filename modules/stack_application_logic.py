"""
Stack의 활용 사례에 필요한 핵심 로직을 구현하는 모듈입니다.

지원 기능
1. 괄호 검사
   - 소괄호 ()
   - 중괄호 {}
   - 대괄호 []
   - 단계별 Stack 상태 기록

2. 후위 표기법 계산
   - 덧셈 +
   - 뺄셈 -
   - 곱셈 *
   - 나눗셈 /
   - 나머지 %
   - 거듭제곱 ^
   - 음수와 실수 지원
   - 단계별 Stack 상태 기록
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Any


# ============================================================
# 1. 공통 결과 자료형
# ============================================================

@dataclass
class StackApplicationResult:
    """
    Stack 활용 기능의 실행 결과를 저장합니다.

    Attributes:
        success:
            입력 분석과 실행이 정상적으로 끝났는지 여부

        action:
            실행한 기능 이름

        message:
            사용자에게 보여줄 결과 메시지

        concept:
            학습 개념 설명

        steps:
            단계별 Stack 변화 기록

        final_stack:
            실행이 끝난 후 Stack 상태

        result:
            괄호 검사의 참·거짓 또는 후위 표기법 계산 결과

        error_index:
            괄호 검사에서 오류가 발생한 문자 위치

        error_token:
            오류가 발생한 문자 또는 토큰
    """

    success: bool
    action: str
    message: str
    concept: str
    steps: list[dict[str, Any]]
    final_stack: list[Any]
    result: Any = None
    error_index: int | None = None
    error_token: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Streamlit Session State와 시각화 함수에서 사용하기 쉽도록
        결과를 딕셔너리로 변환합니다.
        """

        return {
            "success": self.success,
            "action": self.action,
            "message": self.message,
            "concept": self.concept,
            "steps": self.steps,
            "final_stack": self.final_stack,
            "result": self.result,
            "error_index": self.error_index,
            "error_token": self.error_token,
        }


# ============================================================
# 2. 괄호 검사
# ============================================================

class BracketChecker:
    """
    Stack을 이용해 괄호의 짝과 순서를 검사합니다.

    지원하는 괄호:
    - ()
    - {}
    - []
    """

    OPENING_BRACKETS = {
        "(",
        "{",
        "[",
    }

    CLOSING_TO_OPENING = {
        ")": "(",
        "}": "{",
        "]": "[",
    }

    BRACKET_NAMES = {
        "(": "소괄호",
        ")": "소괄호",
        "{": "중괄호",
        "}": "중괄호",
        "[": "대괄호",
        "]": "대괄호",
    }

    @classmethod
    def check(
        cls,
        expression: str,
        ignore_non_brackets: bool = True,
    ) -> dict[str, Any]:
        """
        입력 문자열의 괄호가 올바르게 구성되었는지 검사합니다.

        Args:
            expression:
                검사할 문자열

            ignore_non_brackets:
                True이면 괄호가 아닌 문자는 검사에서 제외합니다.
                False이면 괄호가 아닌 문자를 오류로 처리합니다.

        Returns:
            검사 결과 딕셔너리

        예:
            ({[]})  -> 올바른 괄호식
            ([)]    -> 잘못된 괄호식
            (()     -> 닫히지 않은 괄호 존재
        """

        expression = str(expression)

        if not expression.strip():
            return StackApplicationResult(
                success=False,
                action="bracket_check",
                message="검사할 괄호식을 입력해 주세요.",
                concept=(
                    "여는 괄호는 Stack에 Push하고, "
                    "닫는 괄호가 나오면 가장 위의 괄호와 짝을 확인합니다."
                ),
                steps=[],
                final_stack=[],
                result=False,
            ).to_dict()

        stack: list[dict[str, Any]] = []
        steps: list[dict[str, Any]] = []
        bracket_count = 0

        for index, character in enumerate(
            expression,
            start=1,
        ):
            stack_before = cls._stack_characters(
                stack
            )

            # ------------------------------------------------
            # 여는 괄호
            # ------------------------------------------------

            if character in cls.OPENING_BRACKETS:
                bracket_count += 1

                stack.append(
                    {
                        "character": character,
                        "index": index,
                    }
                )

                steps.append(
                    {
                        "step": len(steps) + 1,
                        "character_index": index,
                        "token": character,
                        "token_type": "opening_bracket",
                        "operation": "push",
                        "description": (
                            f"{character}은(는) 여는 "
                            f"{cls.BRACKET_NAMES[character]}이므로 "
                            "Stack에 Push합니다."
                        ),
                        "stack_before": stack_before,
                        "stack_after": cls._stack_characters(
                            stack
                        ),
                        "matched_token": None,
                        "is_error": False,
                    }
                )

                continue

            # ------------------------------------------------
            # 닫는 괄호
            # ------------------------------------------------

            if character in cls.CLOSING_TO_OPENING:
                bracket_count += 1
                expected_opening = (
                    cls.CLOSING_TO_OPENING[character]
                )

                # Stack이 비어 있는데 닫는 괄호가 나온 경우
                if not stack:
                    steps.append(
                        {
                            "step": len(steps) + 1,
                            "character_index": index,
                            "token": character,
                            "token_type": "closing_bracket",
                            "operation": "error",
                            "description": (
                                f"{character}에 대응하는 여는 괄호가 "
                                "Stack에 없습니다."
                            ),
                            "stack_before": stack_before,
                            "stack_after": stack_before,
                            "matched_token": None,
                            "expected_token": expected_opening,
                            "is_error": True,
                        }
                    )

                    return StackApplicationResult(
                        success=False,
                        action="bracket_check",
                        message=(
                            f"{index}번째 문자 {character} 앞에 "
                            "대응하는 여는 괄호가 없습니다."
                        ),
                        concept=(
                            "닫는 괄호를 만났을 때 Stack이 비어 있으면 "
                            "짝이 맞지 않는 괄호식입니다."
                        ),
                        steps=steps,
                        final_stack=[],
                        result=False,
                        error_index=index,
                        error_token=character,
                    ).to_dict()

                top_item = stack[-1]
                top_character = top_item["character"]

                # Stack TOP과 닫는 괄호의 종류가 다른 경우
                if top_character != expected_opening:
                    steps.append(
                        {
                            "step": len(steps) + 1,
                            "character_index": index,
                            "token": character,
                            "token_type": "closing_bracket",
                            "operation": "error",
                            "description": (
                                f"현재 TOP은 {top_character}이지만 "
                                f"{character}과(와) 짝이 맞지 않습니다."
                            ),
                            "stack_before": stack_before,
                            "stack_after": stack_before,
                            "matched_token": top_character,
                            "expected_token": expected_opening,
                            "is_error": True,
                        }
                    )

                    return StackApplicationResult(
                        success=False,
                        action="bracket_check",
                        message=(
                            f"{index}번째 문자 {character}과(와) "
                            f"Stack TOP의 {top_character}이(가) "
                            "서로 짝이 맞지 않습니다."
                        ),
                        concept=(
                            "닫는 괄호는 가장 최근에 Push된 "
                            "같은 종류의 여는 괄호와 짝을 이루어야 합니다."
                        ),
                        steps=steps,
                        final_stack=stack_before,
                        result=False,
                        error_index=index,
                        error_token=character,
                    ).to_dict()

                # 올바른 짝이면 Pop
                popped_item = stack.pop()

                steps.append(
                    {
                        "step": len(steps) + 1,
                        "character_index": index,
                        "token": character,
                        "token_type": "closing_bracket",
                        "operation": "pop",
                        "description": (
                            f"{character}과(와) TOP의 "
                            f"{popped_item['character']}이(가) "
                            "짝이 맞으므로 Pop합니다."
                        ),
                        "stack_before": stack_before,
                        "stack_after": cls._stack_characters(
                            stack
                        ),
                        "matched_token": (
                            popped_item["character"]
                        ),
                        "matched_index": (
                            popped_item["index"]
                        ),
                        "is_error": False,
                    }
                )

                continue

            # ------------------------------------------------
            # 괄호가 아닌 문자
            # ------------------------------------------------

            if not ignore_non_brackets:
                steps.append(
                    {
                        "step": len(steps) + 1,
                        "character_index": index,
                        "token": character,
                        "token_type": "invalid_character",
                        "operation": "error",
                        "description": (
                            f"{character}은(는) 지원하지 않는 문자입니다."
                        ),
                        "stack_before": stack_before,
                        "stack_after": stack_before,
                        "matched_token": None,
                        "is_error": True,
                    }
                )

                return StackApplicationResult(
                    success=False,
                    action="bracket_check",
                    message=(
                        f"{index}번째 문자 {character}은(는) "
                        "괄호가 아닙니다."
                    ),
                    concept=(
                        "이 검사에서는 소괄호, 중괄호, 대괄호만 "
                        "사용할 수 있습니다."
                    ),
                    steps=steps,
                    final_stack=stack_before,
                    result=False,
                    error_index=index,
                    error_token=character,
                ).to_dict()

        # ----------------------------------------------------
        # 괄호가 하나도 없는 경우
        # ----------------------------------------------------

        if bracket_count == 0:
            return StackApplicationResult(
                success=False,
                action="bracket_check",
                message="입력한 문자열에 검사할 괄호가 없습니다.",
                concept=(
                    "(), {}, [] 중 하나 이상의 괄호를 입력해 주세요."
                ),
                steps=steps,
                final_stack=[],
                result=False,
            ).to_dict()

        # ----------------------------------------------------
        # 모든 문자를 확인한 뒤 Stack에 괄호가 남은 경우
        # ----------------------------------------------------

        if stack:
            remaining_characters = cls._stack_characters(
                stack
            )

            remaining_text = ", ".join(
                remaining_characters
            )

            first_unclosed = stack[-1]

            steps.append(
                {
                    "step": len(steps) + 1,
                    "character_index": None,
                    "token": None,
                    "token_type": "final_check",
                    "operation": "error",
                    "description": (
                        "문자열 확인이 끝났지만 Stack에 "
                        f"{remaining_text}이(가) 남아 있습니다."
                    ),
                    "stack_before": remaining_characters,
                    "stack_after": remaining_characters,
                    "matched_token": None,
                    "is_error": True,
                }
            )

            return StackApplicationResult(
                success=False,
                action="bracket_check",
                message=(
                    "닫히지 않은 여는 괄호가 남아 있습니다: "
                    f"{remaining_text}"
                ),
                concept=(
                    "모든 닫는 괄호를 처리한 후 Stack이 비어 있어야 "
                    "올바른 괄호식입니다."
                ),
                steps=steps,
                final_stack=remaining_characters,
                result=False,
                error_index=first_unclosed["index"],
                error_token=first_unclosed["character"],
            ).to_dict()

        # ----------------------------------------------------
        # 정상 완료
        # ----------------------------------------------------

        steps.append(
            {
                "step": len(steps) + 1,
                "character_index": None,
                "token": None,
                "token_type": "final_check",
                "operation": "complete",
                "description": (
                    "모든 괄호를 확인했고 Stack이 비어 있습니다."
                ),
                "stack_before": [],
                "stack_after": [],
                "matched_token": None,
                "is_error": False,
            }
        )

        return StackApplicationResult(
            success=True,
            action="bracket_check",
            message="모든 괄호의 짝과 순서가 올바릅니다.",
            concept=(
                "여는 괄호는 Push하고, 닫는 괄호는 대응하는 "
                "여는 괄호를 Pop합니다. 마지막에 Stack이 비어 있으면 "
                "올바른 괄호식입니다."
            ),
            steps=steps,
            final_stack=[],
            result=True,
        ).to_dict()

    @staticmethod
    def _stack_characters(
        stack: list[dict[str, Any]],
    ) -> list[str]:
        """
        내부 Stack 정보에서 괄호 문자만 추출합니다.
        """

        return [
            str(item["character"])
            for item in stack
        ]


# ============================================================
# 3. 후위 표기법 계산
# ============================================================

class PostfixCalculator:
    """
    Stack을 이용해 후위 표기법을 계산합니다.

    지원 연산자:
    - +
    - -
    - *
    - /
    - %
    - ^

    입력 권장 형식:
        3 5 + 2 *

    한 자리 숫자만 사용한 경우에는 공백 없이 입력할 수도 있습니다.
        35+2*
    """

    OPERATORS = {
        "+",
        "-",
        "*",
        "/",
        "%",
        "^",
    }

    OPERATOR_NAMES = {
        "+": "덧셈",
        "-": "뺄셈",
        "*": "곱셈",
        "/": "나눗셈",
        "%": "나머지",
        "^": "거듭제곱",
    }

    @classmethod
    def calculate(
        cls,
        expression: str,
    ) -> dict[str, Any]:
        """
        후위 표기법을 계산합니다.

        Args:
            expression:
                계산할 후위 표기법 문자열

        Returns:
            계산 결과와 단계별 Stack 변화

        주의:
            연산자에서 먼저 Pop되는 값은 오른쪽 피연산자,
            두 번째로 Pop되는 값은 왼쪽 피연산자입니다.

            예:
                8 2 -
                왼쪽 피연산자 8, 오른쪽 피연산자 2
                결과는 8 - 2 = 6
        """

        expression = str(expression).strip()

        if not expression:
            return StackApplicationResult(
                success=False,
                action="postfix_calculate",
                message="계산할 후위 표기법을 입력해 주세요.",
                concept=(
                    "예: 3 5 + 2 * 처럼 숫자와 연산자를 "
                    "공백으로 구분해 입력할 수 있습니다."
                ),
                steps=[],
                final_stack=[],
                result=None,
            ).to_dict()

        token_result = cls.tokenize(
            expression
        )

        if not token_result["success"]:
            return StackApplicationResult(
                success=False,
                action="postfix_calculate",
                message=token_result["message"],
                concept=token_result["concept"],
                steps=[],
                final_stack=[],
                result=None,
                error_index=token_result.get(
                    "error_index"
                ),
                error_token=token_result.get(
                    "error_token"
                ),
            ).to_dict()

        tokens: list[str] = token_result["tokens"]

        if not tokens:
            return StackApplicationResult(
                success=False,
                action="postfix_calculate",
                message="계산할 토큰이 없습니다.",
                concept=(
                    "숫자와 연산자를 입력해 주세요."
                ),
                steps=[],
                final_stack=[],
                result=None,
            ).to_dict()

        stack: list[float | int] = []
        steps: list[dict[str, Any]] = []

        for token_index, token in enumerate(
            tokens,
            start=1,
        ):
            stack_before = stack.copy()

            # ------------------------------------------------
            # 숫자 토큰
            # ------------------------------------------------

            if cls.is_number(token):
                number = cls.parse_number(
                    token
                )

                stack.append(
                    number
                )

                steps.append(
                    {
                        "step": len(steps) + 1,
                        "token_index": token_index,
                        "token": token,
                        "token_type": "number",
                        "operation": "push",
                        "description": (
                            f"{cls.format_number(number)}은(는) "
                            "피연산자이므로 Stack에 Push합니다."
                        ),
                        "stack_before": stack_before,
                        "stack_after": stack.copy(),
                        "left_operand": None,
                        "right_operand": None,
                        "calculation": None,
                        "result": number,
                        "is_error": False,
                    }
                )

                continue

            # ------------------------------------------------
            # 연산자 토큰
            # ------------------------------------------------

            if token in cls.OPERATORS:
                if len(stack) < 2:
                    steps.append(
                        {
                            "step": len(steps) + 1,
                            "token_index": token_index,
                            "token": token,
                            "token_type": "operator",
                            "operation": "error",
                            "description": (
                                f"연산자 {token}을(를) 계산하려면 "
                                "Stack에 피연산자가 2개 필요합니다."
                            ),
                            "stack_before": stack_before,
                            "stack_after": stack_before,
                            "left_operand": None,
                            "right_operand": None,
                            "calculation": None,
                            "result": None,
                            "is_error": True,
                        }
                    )

                    return StackApplicationResult(
                        success=False,
                        action="postfix_calculate",
                        message=(
                            f"{token_index}번째 토큰 {token} 앞에 "
                            "피연산자가 부족합니다."
                        ),
                        concept=(
                            "이항 연산자를 만나면 Stack에서 "
                            "피연산자 두 개를 Pop해야 합니다."
                        ),
                        steps=steps,
                        final_stack=stack.copy(),
                        result=None,
                        error_index=token_index,
                        error_token=token,
                    ).to_dict()

                # 먼저 꺼낸 값은 오른쪽 피연산자
                right_operand = stack.pop()

                # 두 번째로 꺼낸 값은 왼쪽 피연산자
                left_operand = stack.pop()

                operation_result = cls.apply_operator(
                    operator=token,
                    left_operand=left_operand,
                    right_operand=right_operand,
                )

                if not operation_result["success"]:
                    steps.append(
                        {
                            "step": len(steps) + 1,
                            "token_index": token_index,
                            "token": token,
                            "token_type": "operator",
                            "operation": "error",
                            "description": (
                                operation_result["message"]
                            ),
                            "stack_before": stack_before,
                            "stack_after": stack.copy(),
                            "left_operand": left_operand,
                            "right_operand": right_operand,
                            "calculation": (
                                f"{cls.format_number(left_operand)} "
                                f"{token} "
                                f"{cls.format_number(right_operand)}"
                            ),
                            "result": None,
                            "is_error": True,
                        }
                    )

                    return StackApplicationResult(
                        success=False,
                        action="postfix_calculate",
                        message=operation_result["message"],
                        concept=operation_result["concept"],
                        steps=steps,
                        final_stack=stack.copy(),
                        result=None,
                        error_index=token_index,
                        error_token=token,
                    ).to_dict()

                calculated_value = (
                    operation_result["result"]
                )

                stack.append(
                    calculated_value
                )

                calculation_text = (
                    f"{cls.format_number(left_operand)} "
                    f"{token} "
                    f"{cls.format_number(right_operand)} "
                    f"= {cls.format_number(calculated_value)}"
                )

                steps.append(
                    {
                        "step": len(steps) + 1,
                        "token_index": token_index,
                        "token": token,
                        "token_type": "operator",
                        "operation": "calculate",
                        "description": (
                            f"{cls.format_number(right_operand)}과(와) "
                            f"{cls.format_number(left_operand)}을(를) "
                            "Pop하여 계산한 뒤 결과 "
                            f"{cls.format_number(calculated_value)}을(를) "
                            "다시 Push합니다."
                        ),
                        "stack_before": stack_before,
                        "stack_after": stack.copy(),
                        "left_operand": left_operand,
                        "right_operand": right_operand,
                        "calculation": calculation_text,
                        "result": calculated_value,
                        "is_error": False,
                    }
                )

                continue

            # ------------------------------------------------
            # 지원하지 않는 토큰
            # ------------------------------------------------

            steps.append(
                {
                    "step": len(steps) + 1,
                    "token_index": token_index,
                    "token": token,
                    "token_type": "invalid",
                    "operation": "error",
                    "description": (
                        f"{token}은(는) 숫자 또는 지원 연산자가 아닙니다."
                    ),
                    "stack_before": stack_before,
                    "stack_after": stack_before,
                    "left_operand": None,
                    "right_operand": None,
                    "calculation": None,
                    "result": None,
                    "is_error": True,
                }
            )

            return StackApplicationResult(
                success=False,
                action="postfix_calculate",
                message=(
                    f"{token_index}번째 토큰 {token}을(를) "
                    "해석할 수 없습니다."
                ),
                concept=(
                    "숫자와 +, -, *, /, %, ^ 연산자만 "
                    "사용할 수 있습니다."
                ),
                steps=steps,
                final_stack=stack.copy(),
                result=None,
                error_index=token_index,
                error_token=token,
            ).to_dict()

        # ----------------------------------------------------
        # 모든 토큰을 처리한 후 Stack 검사
        # ----------------------------------------------------

        if len(stack) != 1:
            remaining_text = ", ".join(
                cls.format_number(value)
                for value in stack
            )

            steps.append(
                {
                    "step": len(steps) + 1,
                    "token_index": None,
                    "token": None,
                    "token_type": "final_check",
                    "operation": "error",
                    "description": (
                        "모든 토큰을 처리했지만 Stack에 "
                        f"{len(stack)}개의 값이 남아 있습니다."
                    ),
                    "stack_before": stack.copy(),
                    "stack_after": stack.copy(),
                    "left_operand": None,
                    "right_operand": None,
                    "calculation": None,
                    "result": None,
                    "is_error": True,
                }
            )

            return StackApplicationResult(
                success=False,
                action="postfix_calculate",
                message=(
                    "후위 표기법이 완성되지 않았습니다. "
                    f"Stack에 남은 값: {remaining_text}"
                ),
                concept=(
                    "모든 연산이 끝난 후 Stack에는 "
                    "최종 계산 결과 하나만 남아야 합니다."
                ),
                steps=steps,
                final_stack=stack.copy(),
                result=None,
            ).to_dict()

        final_result = cls.normalize_result(
            stack[0]
        )

        steps.append(
            {
                "step": len(steps) + 1,
                "token_index": None,
                "token": None,
                "token_type": "final_check",
                "operation": "complete",
                "description": (
                    "모든 토큰을 처리했고 Stack에 "
                    "최종 결과 하나만 남았습니다."
                ),
                "stack_before": stack.copy(),
                "stack_after": stack.copy(),
                "left_operand": None,
                "right_operand": None,
                "calculation": None,
                "result": final_result,
                "is_error": False,
            }
        )

        return StackApplicationResult(
            success=True,
            action="postfix_calculate",
            message=(
                "후위 표기법 계산 결과는 "
                f"{cls.format_number(final_result)}입니다."
            ),
            concept=(
                "숫자는 Push하고, 연산자를 만나면 피연산자 두 개를 "
                "Pop하여 계산한 뒤 결과를 다시 Push합니다."
            ),
            steps=steps,
            final_stack=[
                final_result
            ],
            result=final_result,
        ).to_dict()

    # ========================================================
    # 토큰 분석
    # ========================================================

    @classmethod
    def tokenize(
        cls,
        expression: str,
    ) -> dict[str, Any]:
        """
        후위 표기법 문자열을 토큰 목록으로 변환합니다.

        지원 형식:
        1. 공백 구분
           "12 3 +"

        2. 한 자리 숫자 형태
           "35+2*"

        공백 없는 입력에 여러 자리 숫자가 포함되면
        숫자 경계를 알 수 없으므로 공백 입력을 안내합니다.
        """

        cleaned_expression = expression.strip()

        if not cleaned_expression:
            return {
                "success": False,
                "tokens": [],
                "message": (
                    "계산할 후위 표기법을 입력해 주세요."
                ),
                "concept": (
                    "예: 3 5 + 2 *"
                ),
            }

        # 공백이 포함된 경우
        if any(
            character.isspace()
            for character in cleaned_expression
        ):
            tokens = cleaned_expression.split()

            invalid_tokens = [
                token
                for token in tokens
                if (
                    not cls.is_number(token)
                    and token not in cls.OPERATORS
                )
            ]

            if invalid_tokens:
                invalid_text = ", ".join(
                    invalid_tokens
                )

                return {
                    "success": False,
                    "tokens": [],
                    "message": (
                        "해석할 수 없는 토큰이 포함되어 있습니다: "
                        f"{invalid_text}"
                    ),
                    "concept": (
                        "숫자와 +, -, *, /, %, ^ 연산자만 "
                        "입력해 주세요."
                    ),
                    "error_token": invalid_tokens[0],
                }

            return {
                "success": True,
                "tokens": tokens,
                "message": "",
                "concept": "",
            }

        # 공백이 없는 경우에는 한 자리 숫자와 연산자만 허용
        tokens: list[str] = []

        for index, character in enumerate(
            cleaned_expression,
            start=1,
        ):
            if character.isdigit():
                tokens.append(
                    character
                )

            elif character in cls.OPERATORS:
                tokens.append(
                    character
                )

            else:
                return {
                    "success": False,
                    "tokens": [],
                    "message": (
                        f"{index}번째 문자 {character}을(를) "
                        "해석할 수 없습니다."
                    ),
                    "concept": (
                        "여러 자리 숫자, 음수, 실수는 "
                        "공백으로 구분해 입력해 주세요. "
                        "예: 12 -3.5 +"
                    ),
                    "error_index": index,
                    "error_token": character,
                }

        return {
            "success": True,
            "tokens": tokens,
            "message": "",
            "concept": "",
        }

    # ========================================================
    # 계산 관련 보조 함수
    # ========================================================

    @staticmethod
    def is_number(
        token: str,
    ) -> bool:
        """
        문자열이 정수 또는 실수인지 확인합니다.
        """

        try:
            float(token)
            return True

        except (TypeError, ValueError):
            return False

    @staticmethod
    def parse_number(
        token: str,
    ) -> int | float:
        """
        숫자 문자열을 int 또는 float로 변환합니다.
        """

        number = float(token)

        if number.is_integer():
            return int(number)

        return number

    @classmethod
    def apply_operator(
        cls,
        operator: str,
        left_operand: Real,
        right_operand: Real,
    ) -> dict[str, Any]:
        """
        피연산자 두 개에 연산자를 적용합니다.
        """

        try:
            if operator == "+":
                result = (
                    left_operand
                    + right_operand
                )

            elif operator == "-":
                result = (
                    left_operand
                    - right_operand
                )

            elif operator == "*":
                result = (
                    left_operand
                    * right_operand
                )

            elif operator == "/":
                if right_operand == 0:
                    return {
                        "success": False,
                        "result": None,
                        "message": (
                            "0으로 나눌 수 없습니다."
                        ),
                        "concept": (
                            "나눗셈에서 오른쪽 피연산자는 "
                            "0이 될 수 없습니다."
                        ),
                    }

                result = (
                    left_operand
                    / right_operand
                )

            elif operator == "%":
                if right_operand == 0:
                    return {
                        "success": False,
                        "result": None,
                        "message": (
                            "0으로 나머지 연산을 할 수 없습니다."
                        ),
                        "concept": (
                            "나머지 연산의 오른쪽 피연산자는 "
                            "0이 될 수 없습니다."
                        ),
                    }

                result = (
                    left_operand
                    % right_operand
                )

            elif operator == "^":
                result = (
                    left_operand
                    ** right_operand
                )

            else:
                return {
                    "success": False,
                    "result": None,
                    "message": (
                        f"지원하지 않는 연산자입니다: {operator}"
                    ),
                    "concept": (
                        "지원 연산자는 +, -, *, /, %, ^입니다."
                    ),
                }

        except OverflowError:
            return {
                "success": False,
                "result": None,
                "message": (
                    "계산 결과가 너무 커서 처리할 수 없습니다."
                ),
                "concept": (
                    "입력한 숫자나 거듭제곱 값을 줄여 주세요."
                ),
            }

        except (ArithmeticError, ValueError) as error:
            return {
                "success": False,
                "result": None,
                "message": (
                    f"계산 중 오류가 발생했습니다: {error}"
                ),
                "concept": (
                    "피연산자와 연산자의 순서를 확인해 주세요."
                ),
            }

        # 복소수 결과는 이번 학습용 계산기에서 제외
        if isinstance(
            result,
            complex,
        ):
            return {
                "success": False,
                "result": None,
                "message": (
                    "복소수 결과는 지원하지 않습니다."
                ),
                "concept": (
                    "실수 범위에서 계산할 수 있는 식을 입력해 주세요."
                ),
            }

        return {
            "success": True,
            "result": cls.normalize_result(
                result
            ),
            "message": "",
            "concept": "",
        }

    @staticmethod
    def normalize_result(
        value: Real,
    ) -> int | float:
        """
        계산 결과가 정수 형태이면 int로 변환하고,
        실수이면 부동소수점 오차를 줄여 반환합니다.
        """

        numeric_value = float(value)

        if numeric_value.is_integer():
            return int(
                numeric_value
            )

        return round(
            numeric_value,
            10,
        )

    @staticmethod
    def format_number(
        value: Any,
    ) -> str:
        """
        화면에 표시하기 좋은 숫자 문자열로 변환합니다.
        """

        if isinstance(
            value,
            bool,
        ):
            return str(value)

        if isinstance(
            value,
            int,
        ):
            return str(value)

        if isinstance(
            value,
            float,
        ):
            if value.is_integer():
                return str(
                    int(value)
                )

            return (
                f"{value:.10f}"
                .rstrip("0")
                .rstrip(".")
            )

        return str(value)


# ============================================================
# 4. 외부 호출용 함수
# ============================================================

def check_brackets(
    expression: str,
    ignore_non_brackets: bool = True,
) -> dict[str, Any]:
    """
    괄호 검사 기능을 간단하게 호출하기 위한 함수입니다.
    """

    return BracketChecker.check(
        expression=expression,
        ignore_non_brackets=ignore_non_brackets,
    )


def calculate_postfix(
    expression: str,
) -> dict[str, Any]:
    """
    후위 표기법 계산 기능을 간단하게 호출하기 위한 함수입니다.
    """

    return PostfixCalculator.calculate(
        expression=expression
    )