"""
Queue 자료구조의 핵심 로직을 구현하는 모듈입니다.

주요 기능
- Enqueue
- Dequeue
- Front 확인
- Rear 확인
- 빈 Queue 확인
- 가득 찬 Queue 확인
- Queue 초기화
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
            max_size: Queue에 저장할 수 있는 최대 데이터 개수
        """

        if max_size <= 0:
            raise ValueError(
                "Queue의 최대 크기는 1 이상이어야 합니다."
            )

        self.max_size = max_size
        self.items: list[Any] = []

    def enqueue(self, value: Any) -> dict:
        """
        Queue의 REAR 위치에 새로운 값을 추가합니다.

        Args:
            value: Queue에 추가할 값

        Returns:
            연산 결과와 설명을 담은 딕셔너리
        """

        if self.is_full():
            return {
                "success": False,
                "action": "enqueue",
                "value": value,
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
            "message": (
                f"{value}이(가) Queue의 뒤쪽인 "
                "REAR에 추가되었습니다."
            ),
            "concept": (
                "Queue에 새로 들어온 데이터는 "
                "대기열의 가장 뒤쪽에 놓입니다."
            ),
        }

    def dequeue(self) -> dict:
        """
        Queue의 FRONT 값을 제거하고 반환합니다.

        Returns:
            제거된 값과 연산 결과를 담은 딕셔너리
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "dequeue",
                "value": None,
                "message": (
                    "Queue가 비어 있어 꺼낼 데이터가 없습니다."
                ),
                "concept": (
                    "비어 있는 Queue에서 데이터를 꺼내려고 하는 "
                    "상태를 Queue Underflow라고 합니다."
                ),
            }

        removed_value = self.items.pop(0)

        return {
            "success": True,
            "action": "dequeue",
            "value": removed_value,
            "message": (
                f"가장 먼저 들어왔던 {removed_value}이(가) "
                "Queue에서 제거되었습니다."
            ),
            "concept": (
                "Queue는 먼저 들어온 데이터가 먼저 나오는 "
                "FIFO 구조입니다."
            ),
        }

    def front(self) -> dict:
        """
        Queue의 FRONT 값을 제거하지 않고 확인합니다.
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "front",
                "value": None,
                "message": (
                    "Queue가 비어 있어 FRONT 값을 "
                    "확인할 수 없습니다."
                ),
                "concept": (
                    "FRONT는 Queue에서 다음에 제거될 "
                    "데이터의 위치입니다."
                ),
            }

        front_value = self.items[0]

        return {
            "success": True,
            "action": "front",
            "value": front_value,
            "message": (
                f"현재 Queue의 FRONT 값은 "
                f"{front_value}입니다."
            ),
            "concept": (
                "FRONT 확인은 데이터를 제거하지 않고 "
                "다음에 나올 값만 확인합니다."
            ),
        }

    def rear(self) -> dict:
        """
        Queue의 REAR 값을 제거하지 않고 확인합니다.
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "rear",
                "value": None,
                "message": (
                    "Queue가 비어 있어 REAR 값을 "
                    "확인할 수 없습니다."
                ),
                "concept": (
                    "REAR는 Queue에서 가장 최근에 추가된 "
                    "데이터의 위치입니다."
                ),
            }

        rear_value = self.items[-1]

        return {
            "success": True,
            "action": "rear",
            "value": rear_value,
            "message": (
                f"현재 Queue의 REAR 값은 "
                f"{rear_value}입니다."
            ),
            "concept": (
                "REAR 확인은 Queue의 가장 뒤쪽 값을 "
                "제거하지 않고 확인합니다."
            ),
        }

    def clear(self) -> dict:
        """
        Queue의 모든 데이터를 제거합니다.
        """

        removed_count = len(self.items)

        self.items.clear()

        return {
            "success": True,
            "action": "clear",
            "value": None,
            "message": (
                f"Queue를 초기화했습니다. "
                f"{removed_count}개의 데이터가 제거되었습니다."
            ),
            "concept": (
                "초기화하면 Queue는 아무 데이터도 없는 "
                "빈 상태가 됩니다."
            ),
        }

    def is_empty(self) -> bool:
        """
        Queue가 비어 있는지 확인합니다.
        """

        return len(self.items) == 0

    def is_full(self) -> bool:
        """
        Queue가 최대 크기에 도달했는지 확인합니다.
        """

        return len(self.items) >= self.max_size

    def size(self) -> int:
        """
        현재 Queue에 저장된 데이터 수를 반환합니다.
        """

        return len(self.items)

    def front_value(self) -> Any | None:
        """
        현재 FRONT 값을 반환합니다.
        """

        if self.is_empty():
            return None

        return self.items[0]

    def rear_value(self) -> Any | None:
        """
        현재 REAR 값을 반환합니다.
        """

        if self.is_empty():
            return None

        return self.items[-1]

    def remaining_space(self) -> int:
        """
        Queue에 데이터를 더 저장할 수 있는 공간을 반환합니다.
        """

        return self.max_size - len(self.items)

    def to_list(self) -> list[Any]:
        """
        Queue 데이터를 리스트 복사본으로 반환합니다.
        """

        return self.items.copy()

    def load_items(self, values: list[Any]) -> None:
        """
        외부 데이터로 Queue 상태를 복원합니다.

        Streamlit Session State와 연결할 때 사용합니다.
        """

        if len(values) > self.max_size:
            raise ValueError(
                "복원할 데이터의 개수가 Queue 최대 크기보다 많습니다."
            )

        self.items = values.copy()