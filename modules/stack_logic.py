"""
Stack 자료구조의 핵심 로직을 구현하는 모듈입니다.

주요 기능
- Push
- Pop
- Peek
- 빈 Stack 확인
- 가득 찬 Stack 확인
- Stack 초기화
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
            max_size: Stack에 저장할 수 있는 최대 데이터 개수
        """

        if max_size <= 0:
            raise ValueError(
                "Stack의 최대 크기는 1 이상이어야 합니다."
            )

        self.max_size = max_size
        self.items: list[Any] = []

    def push(self, value: Any) -> dict:
        """
        Stack의 가장 위에 새로운 값을 추가합니다.

        Args:
            value: Stack에 추가할 값

        Returns:
            연산 성공 여부와 설명을 담은 딕셔너리
        """

        if self.is_full():
            return {
                "success": False,
                "action": "push",
                "value": value,
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
            "message": (
                f"{value}이(가) Stack의 가장 위에 추가되었습니다."
            ),
            "concept": (
                "Stack에서는 새로 들어온 데이터가 "
                "항상 가장 위에 놓입니다."
            ),
        }

    def pop(self) -> dict:
        """
        Stack의 가장 위에 있는 값을 제거하고 반환합니다.

        Returns:
            제거된 값과 연산 결과를 담은 딕셔너리
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "pop",
                "value": None,
                "message": (
                    "Stack이 비어 있어 꺼낼 데이터가 없습니다."
                ),
                "concept": (
                    "비어 있는 Stack에서 데이터를 꺼내려고 하는 "
                    "상태를 Stack Underflow라고 합니다."
                ),
            }

        removed_value = self.items.pop()

        return {
            "success": True,
            "action": "pop",
            "value": removed_value,
            "message": (
                f"가장 위에 있던 {removed_value}이(가) "
                "Stack에서 제거되었습니다."
            ),
            "concept": (
                "Stack은 마지막에 들어온 데이터가 "
                "가장 먼저 나오는 LIFO 구조입니다."
            ),
        }

    def peek(self) -> dict:
        """
        Stack의 가장 위에 있는 값을 제거하지 않고 확인합니다.

        Returns:
            TOP 값과 연산 결과를 담은 딕셔너리
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "peek",
                "value": None,
                "message": (
                    "Stack이 비어 있어 확인할 데이터가 없습니다."
                ),
                "concept": (
                    "Peek 연산은 데이터를 제거하지 않고 "
                    "가장 위의 값만 확인합니다."
                ),
            }

        top_value = self.items[-1]

        return {
            "success": True,
            "action": "peek",
            "value": top_value,
            "message": (
                f"현재 Stack의 가장 위에 있는 값은 "
                f"{top_value}입니다."
            ),
            "concept": (
                "Peek 연산은 Stack의 상태를 바꾸지 않습니다."
            ),
        }

    def clear(self) -> dict:
        """
        Stack의 모든 데이터를 제거합니다.

        Returns:
            초기화 결과를 담은 딕셔너리
        """

        removed_count = len(self.items)

        self.items.clear()

        return {
            "success": True,
            "action": "clear",
            "value": None,
            "message": (
                f"Stack을 초기화했습니다. "
                f"{removed_count}개의 데이터가 제거되었습니다."
            ),
            "concept": (
                "초기화하면 Stack은 아무 데이터도 없는 "
                "빈 상태가 됩니다."
            ),
        }

    def is_empty(self) -> bool:
        """
        Stack이 비어 있는지 확인합니다.
        """

        return len(self.items) == 0

    def is_full(self) -> bool:
        """
        Stack이 최대 크기에 도달했는지 확인합니다.
        """

        return len(self.items) >= self.max_size

    def size(self) -> int:
        """
        현재 Stack에 저장된 데이터 수를 반환합니다.
        """

        return len(self.items)

    def top(self) -> Any | None:
        """
        현재 TOP 값을 반환합니다.

        Stack이 비어 있으면 None을 반환합니다.
        """

        if self.is_empty():
            return None

        return self.items[-1]

    def remaining_space(self) -> int:
        """
        Stack에 데이터를 더 저장할 수 있는 공간을 반환합니다.
        """

        return self.max_size - len(self.items)

    def to_list(self) -> list[Any]:
        """
        Stack 데이터를 리스트 형태로 반환합니다.

        원본 리스트가 직접 수정되지 않도록 복사본을 반환합니다.
        """

        return self.items.copy()

    def load_items(self, values: list[Any]) -> None:
        """
        외부에서 전달된 값으로 Stack 상태를 복원합니다.

        Streamlit Session State와 연결할 때 사용합니다.

        Args:
            values: 복원할 데이터 목록
        """

        if len(values) > self.max_size:
            raise ValueError(
                "복원할 데이터의 개수가 Stack 최대 크기보다 많습니다."
            )

        self.items = values.copy()