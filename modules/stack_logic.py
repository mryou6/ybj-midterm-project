"""
Stack 자료구조의 핵심 로직을 구현하는 모듈입니다.

주요 기능
- Push
- 여러 값 일괄 Push
- Pop
- Peek
- Stack 초기화
- Stack 상태 확인
"""

from typing import Any


class Stack:
    """
    리스트를 이용해 구현한 Stack 클래스입니다.

    Stack은 마지막에 삽입한 데이터가 가장 먼저 제거되는
    LIFO(Last In, First Out) 구조입니다.
    """

    def __init__(self, max_size: int = 5):
        """
        Stack 객체를 생성합니다.

        Args:
            max_size: Stack의 최대 저장 크기
        """

        if max_size < 1:
            raise ValueError(
                "Stack의 최대 크기는 1 이상이어야 합니다."
            )

        self.max_size = max_size
        self.items: list[Any] = []

    # ========================================================
    # Push
    # ========================================================

    def push(self, value: Any) -> dict:
        """
        Stack의 TOP에 값 하나를 추가합니다.
        """

        if self.is_full():
            return {
                "success": False,
                "action": "push",
                "value": value,
                "values": [value],
                "message": (
                    f"Stack이 가득 차서 {value}을(를) "
                    "추가할 수 없습니다."
                ),
                "concept": (
                    "더 이상 데이터를 넣을 공간이 없는 상태를 "
                    "Stack Overflow라고 합니다."
                ),
            }

        self.items.append(value)

        return {
            "success": True,
            "action": "push",
            "value": value,
            "values": [value],
            "message": (
                f"{value}이(가) Stack의 가장 위에 추가되었습니다."
            ),
            "concept": (
                "새로 들어온 데이터는 항상 Stack의 TOP에 놓입니다."
            ),
        }

    def push_many(
        self,
        values: list[Any],
    ) -> dict:
        """
        여러 값을 입력된 순서대로 Stack에 추가합니다.

        예:
            A, B, C를 입력하면
            A → B → C 순서로 Push되고 C가 TOP이 됩니다.
        """

        cleaned_values = [
            str(value).strip()
            for value in values
            if str(value).strip()
        ]

        if not cleaned_values:
            return {
                "success": False,
                "action": "push_many",
                "value": None,
                "values": [],
                "message": "Stack에 넣을 값을 입력해 주세요.",
                "concept": (
                    "여러 값은 쉼표로 구분하여 입력할 수 있습니다."
                ),
            }

        required_space = len(cleaned_values)
        available_space = self.remaining_space()

        if required_space > available_space:
            return {
                "success": False,
                "action": "push_many",
                "value": None,
                "values": cleaned_values,
                "message": (
                    f"{required_space}개의 값을 추가하려고 했지만 "
                    f"현재 남은 공간은 {available_space}칸입니다."
                ),
                "concept": (
                    "일부 값만 추가하지 않고 전체 Push를 취소했습니다. "
                    "Stack 크기를 늘리거나 입력값을 줄여 주세요."
                ),
            }

        self.items.extend(cleaned_values)

        values_text = ", ".join(cleaned_values)
        top_value = cleaned_values[-1]

        return {
            "success": True,
            "action": "push_many",
            "value": top_value,
            "values": cleaned_values,
            "message": (
                f"{values_text}을(를) 순서대로 Stack에 추가했습니다."
            ),
            "concept": (
                f"마지막에 추가된 {top_value}이(가) 현재 TOP입니다."
            ),
        }

    # ========================================================
    # Pop
    # ========================================================

    def pop(self) -> dict:
        """
        Stack의 TOP 값을 제거합니다.
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "pop",
                "value": None,
                "values": [],
                "message": (
                    "Stack이 비어 있어 꺼낼 데이터가 없습니다."
                ),
                "concept": (
                    "빈 Stack에서 데이터를 꺼내려는 상태를 "
                    "Stack Underflow라고 합니다."
                ),
            }

        removed_value = self.items.pop()

        return {
            "success": True,
            "action": "pop",
            "value": removed_value,
            "values": [removed_value],
            "message": (
                f"TOP에 있던 {removed_value}이(가) 제거되었습니다."
            ),
            "concept": (
                "Stack은 마지막에 들어온 데이터가 가장 먼저 나오는 "
                "LIFO 구조입니다."
            ),
        }

    # ========================================================
    # Peek
    # ========================================================

    def peek(self) -> dict:
        """
        TOP 값을 제거하지 않고 확인합니다.
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "peek",
                "value": None,
                "values": [],
                "message": (
                    "Stack이 비어 있어 확인할 값이 없습니다."
                ),
                "concept": (
                    "Peek는 데이터를 제거하지 않고 TOP만 확인합니다."
                ),
            }

        top_value = self.items[-1]

        return {
            "success": True,
            "action": "peek",
            "value": top_value,
            "values": [top_value],
            "message": (
                f"현재 Stack의 TOP은 {top_value}입니다."
            ),
            "concept": (
                "Peek 연산은 Stack의 현재 상태를 바꾸지 않습니다."
            ),
        }

    # ========================================================
    # 초기화
    # ========================================================

    def clear(self) -> dict:
        """
        Stack의 모든 값을 제거합니다.
        """

        removed_count = len(self.items)
        self.items.clear()

        return {
            "success": True,
            "action": "clear",
            "value": None,
            "values": [],
            "message": (
                f"Stack을 초기화했습니다. "
                f"{removed_count}개의 데이터가 제거되었습니다."
            ),
            "concept": (
                "초기화하면 Stack은 빈 상태가 됩니다."
            ),
        }

    # ========================================================
    # 상태 확인
    # ========================================================

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def is_full(self) -> bool:
        return len(self.items) >= self.max_size

    def size(self) -> int:
        return len(self.items)

    def top(self) -> Any | None:
        if self.is_empty():
            return None

        return self.items[-1]

    def remaining_space(self) -> int:
        return self.max_size - len(self.items)

    def to_list(self) -> list[Any]:
        return self.items.copy()

    def load_items(
        self,
        values: list[Any],
    ) -> None:
        """
        Session State의 값으로 Stack 상태를 복원합니다.
        """

        if len(values) > self.max_size:
            raise ValueError(
                "복원할 데이터 수가 Stack 최대 크기보다 많습니다."
            )

        self.items = values.copy()