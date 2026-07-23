"""
Queue 자료구조의 핵심 로직을 구현하는 모듈입니다.

주요 기능
- Enqueue
- 여러 값 일괄 Enqueue
- Dequeue
- FRONT 확인
- REAR 확인
- Queue 초기화
- Queue 상태 확인
"""

from typing import Any


class Queue:
    """
    리스트를 이용해 구현한 Queue 클래스입니다.

    Queue는 먼저 삽입한 데이터가 가장 먼저 제거되는
    FIFO(First In, First Out) 구조입니다.
    """

    def __init__(self, max_size: int = 5):
        """
        Queue 객체를 생성합니다.

        Args:
            max_size: Queue의 최대 저장 크기
        """

        if max_size < 1:
            raise ValueError(
                "Queue의 최대 크기는 1 이상이어야 합니다."
            )

        self.max_size = max_size
        self.items: list[Any] = []

    # ========================================================
    # Enqueue
    # ========================================================

    def enqueue(self, value: Any) -> dict:
        """
        Queue의 REAR에 값 하나를 추가합니다.
        """

        if self.is_full():
            return {
                "success": False,
                "action": "enqueue",
                "value": value,
                "values": [value],
                "message": (
                    f"Queue가 가득 차서 {value}을(를) "
                    "추가할 수 없습니다."
                ),
                "concept": (
                    "더 이상 데이터를 넣을 공간이 없는 상태를 "
                    "Queue Overflow라고 합니다."
                ),
            }

        self.items.append(value)

        return {
            "success": True,
            "action": "enqueue",
            "value": value,
            "values": [value],
            "message": (
                f"{value}이(가) Queue의 REAR에 추가되었습니다."
            ),
            "concept": (
                "새로 들어온 데이터는 Queue의 가장 뒤쪽에 놓입니다."
            ),
        }

    def enqueue_many(
        self,
        values: list[Any],
    ) -> dict:
        """
        여러 값을 입력된 순서대로 Queue에 추가합니다.

        예:
            A, B, C를 입력하면
            A → B → C 순서로 Enqueue됩니다.

            FRONT는 A,
            REAR는 C가 됩니다.
        """

        cleaned_values = [
            str(value).strip()
            for value in values
            if str(value).strip()
        ]

        if not cleaned_values:
            return {
                "success": False,
                "action": "enqueue_many",
                "value": None,
                "values": [],
                "message": (
                    "Queue에 넣을 값을 입력해 주세요."
                ),
                "concept": (
                    "여러 값은 쉼표로 구분하여 입력할 수 있습니다."
                ),
            }

        required_space = len(cleaned_values)
        available_space = self.remaining_space()

        if required_space > available_space:
            return {
                "success": False,
                "action": "enqueue_many",
                "value": None,
                "values": cleaned_values,
                "message": (
                    f"{required_space}개의 값을 추가하려고 했지만 "
                    f"현재 남은 공간은 {available_space}칸입니다."
                ),
                "concept": (
                    "일부 값만 추가하지 않고 전체 Enqueue를 "
                    "취소했습니다. Queue 크기를 늘리거나 "
                    "입력값을 줄여 주세요."
                ),
            }

        self.items.extend(cleaned_values)

        values_text = ", ".join(cleaned_values)
        rear_value = cleaned_values[-1]

        return {
            "success": True,
            "action": "enqueue_many",
            "value": rear_value,
            "values": cleaned_values,
            "message": (
                f"{values_text}을(를) 순서대로 Queue에 추가했습니다."
            ),
            "concept": (
                f"마지막에 추가된 {rear_value}이(가) 현재 REAR입니다."
            ),
        }

    # ========================================================
    # Dequeue
    # ========================================================

    def dequeue(self) -> dict:
        """
        Queue의 FRONT 값을 제거합니다.
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "dequeue",
                "value": None,
                "values": [],
                "message": (
                    "Queue가 비어 있어 꺼낼 데이터가 없습니다."
                ),
                "concept": (
                    "빈 Queue에서 데이터를 꺼내려는 상태를 "
                    "Queue Underflow라고 합니다."
                ),
            }

        removed_value = self.items.pop(0)

        return {
            "success": True,
            "action": "dequeue",
            "value": removed_value,
            "values": [removed_value],
            "message": (
                f"FRONT에 있던 {removed_value}이(가) 제거되었습니다."
            ),
            "concept": (
                "Queue는 먼저 들어온 데이터가 가장 먼저 나오는 "
                "FIFO 구조입니다."
            ),
        }

    # ========================================================
    # FRONT 확인
    # ========================================================

    def front(self) -> dict:
        """
        FRONT 값을 제거하지 않고 확인합니다.
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "front",
                "value": None,
                "values": [],
                "message": (
                    "Queue가 비어 있어 FRONT 값을 확인할 수 없습니다."
                ),
                "concept": (
                    "FRONT는 다음 Dequeue에서 제거될 데이터입니다."
                ),
            }

        front_value = self.items[0]

        return {
            "success": True,
            "action": "front",
            "value": front_value,
            "values": [front_value],
            "message": (
                f"현재 Queue의 FRONT는 {front_value}입니다."
            ),
            "concept": (
                "FRONT 확인은 데이터를 제거하지 않고 "
                "다음에 나올 값만 확인합니다."
            ),
        }

    # ========================================================
    # REAR 확인
    # ========================================================

    def rear(self) -> dict:
        """
        REAR 값을 제거하지 않고 확인합니다.
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "rear",
                "value": None,
                "values": [],
                "message": (
                    "Queue가 비어 있어 REAR 값을 확인할 수 없습니다."
                ),
                "concept": (
                    "REAR는 가장 최근에 추가된 데이터입니다."
                ),
            }

        rear_value = self.items[-1]

        return {
            "success": True,
            "action": "rear",
            "value": rear_value,
            "values": [rear_value],
            "message": (
                f"현재 Queue의 REAR는 {rear_value}입니다."
            ),
            "concept": (
                "REAR 확인은 데이터를 제거하지 않고 "
                "가장 뒤쪽 값만 확인합니다."
            ),
        }

    # ========================================================
    # 초기화
    # ========================================================

    def clear(self) -> dict:
        """
        Queue의 모든 값을 제거합니다.
        """

        removed_count = len(self.items)
        self.items.clear()

        return {
            "success": True,
            "action": "clear",
            "value": None,
            "values": [],
            "message": (
                f"Queue를 초기화했습니다. "
                f"{removed_count}개의 데이터가 제거되었습니다."
            ),
            "concept": (
                "초기화하면 Queue는 빈 상태가 됩니다."
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

    def front_value(self) -> Any | None:
        if self.is_empty():
            return None

        return self.items[0]

    def rear_value(self) -> Any | None:
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
        Session State의 값으로 Queue 상태를 복원합니다.
        """

        if len(values) > self.max_size:
            raise ValueError(
                "복원할 데이터 수가 Queue 최대 크기보다 많습니다."
            )

        self.items = values.copy()