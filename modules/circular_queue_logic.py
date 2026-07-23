"""
원형 큐(Circular Queue)의 핵심 로직을 구현하는 모듈입니다.

구현 규칙
- 배열 크기는 기본 5
- front와 rear의 초기값은 0
- 한 칸을 항상 비워 둠
- 실제 저장 가능 데이터 수는 SIZE - 1
- 배열의 마지막 다음 위치는 다시 0번 인덱스로 이동
"""

from typing import Any


class CircularQueue:
    """
    고정 크기 배열을 이용한 원형 큐입니다.

    이 구현에서:
    - front는 첫 데이터 바로 앞의 빈 칸을 가리킵니다.
    - rear는 마지막으로 삽입된 데이터 위치를 가리킵니다.
    """

    def __init__(self, max_size: int = 5):
        if max_size < 3:
            raise ValueError(
                "원형 큐의 크기는 3 이상이어야 합니다."
            )

        self.max_size = max_size
        self.items: list[Any | None] = [
            None
            for _ in range(max_size)
        ]

        self.front = 0
        self.rear = 0

    # ========================================================
    # 상태 확인
    # ========================================================

    def is_empty(self) -> bool:
        """
        front와 rear가 같으면 공백 상태입니다.
        """

        return self.front == self.rear

    def is_full(self) -> bool:
        """
        rear의 다음 위치가 front이면 포화 상태입니다.
        """

        next_rear = (
            self.rear + 1
        ) % self.max_size

        return next_rear == self.front

    def size(self) -> int:
        """
        현재 저장된 데이터 수를 계산합니다.
        """

        return (
            self.rear
            - self.front
            + self.max_size
        ) % self.max_size

    def capacity(self) -> int:
        """
        실제 데이터 저장 가능 개수입니다.

        한 칸을 비워 두므로 SIZE - 1입니다.
        """

        return self.max_size - 1

    def remaining_space(self) -> int:
        """
        앞으로 저장할 수 있는 데이터 개수입니다.
        """

        return self.capacity() - self.size()

    def next_front_index(self) -> int | None:
        """
        다음 Dequeue에서 제거할 데이터의 인덱스입니다.
        """

        if self.is_empty():
            return None

        return (
            self.front + 1
        ) % self.max_size

    def next_rear_index(self) -> int:
        """
        다음 Enqueue에서 사용할 인덱스입니다.
        """

        return (
            self.rear + 1
        ) % self.max_size

    # ========================================================
    # Enqueue
    # ========================================================

    def enqueue(
        self,
        value: Any,
    ) -> dict:
        """
        원형 큐의 REAR 다음 위치에 값을 삽입합니다.
        """

        if self.is_full():
            return {
                "success": False,
                "action": "enqueue",
                "value": value,
                "values": [value],
                "message": (
                    f"원형 큐가 가득 차서 "
                    f"{value}을(를) 삽입할 수 없습니다."
                ),
                "concept": (
                    "원형 큐는 공백과 포화 상태를 구분하기 위해 "
                    "한 칸을 항상 비워 둡니다."
                ),
                "front": self.front,
                "rear": self.rear,
            }

        self.rear = self.next_rear_index()
        self.items[self.rear] = value

        return {
            "success": True,
            "action": "enqueue",
            "value": value,
            "values": [value],
            "message": (
                f"{value}이(가) 인덱스 "
                f"{self.rear}에 삽입되었습니다."
            ),
            "concept": (
                "rear는 (rear + 1) % SIZE를 이용해 "
                "다음 위치로 이동합니다."
            ),
            "front": self.front,
            "rear": self.rear,
        }

    def enqueue_many(
        self,
        values: list[Any],
    ) -> dict:
        """
        여러 값을 입력 순서대로 원형 큐에 삽입합니다.

        남은 공간보다 입력값이 많으면
        일부만 삽입하지 않고 전체 연산을 취소합니다.
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
                    "원형 큐에 삽입할 값을 입력해 주세요."
                ),
                "concept": (
                    "여러 값은 쉼표로 구분할 수 있습니다."
                ),
                "front": self.front,
                "rear": self.rear,
            }

        if len(cleaned_values) > self.remaining_space():
            return {
                "success": False,
                "action": "enqueue_many",
                "value": None,
                "values": cleaned_values,
                "message": (
                    f"{len(cleaned_values)}개의 값을 "
                    f"삽입하려고 했지만 현재 남은 공간은 "
                    f"{self.remaining_space()}칸입니다."
                ),
                "concept": (
                    "일부 값만 삽입하지 않고 "
                    "전체 Enqueue를 취소했습니다."
                ),
                "front": self.front,
                "rear": self.rear,
            }

        inserted_indexes: list[int] = []

        for value in cleaned_values:
            self.rear = self.next_rear_index()
            self.items[self.rear] = value
            inserted_indexes.append(self.rear)

        values_text = ", ".join(cleaned_values)

        return {
            "success": True,
            "action": "enqueue_many",
            "value": cleaned_values[-1],
            "values": cleaned_values,
            "indexes": inserted_indexes,
            "message": (
                f"{values_text}을(를) 순서대로 "
                "원형 큐에 삽입했습니다."
            ),
            "concept": (
                "배열의 마지막 위치를 지나면 "
                "다시 0번 인덱스로 이동합니다."
            ),
            "front": self.front,
            "rear": self.rear,
        }

    # ========================================================
    # Dequeue
    # ========================================================

    def dequeue(self) -> dict:
        """
        FRONT 다음 위치의 데이터를 제거합니다.
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "dequeue",
                "value": None,
                "values": [],
                "message": (
                    "원형 큐가 비어 있어 "
                    "꺼낼 데이터가 없습니다."
                ),
                "concept": (
                    "front와 rear가 같으면 공백 상태입니다."
                ),
                "front": self.front,
                "rear": self.rear,
            }

        self.front = (
            self.front + 1
        ) % self.max_size

        removed_value = self.items[self.front]
        removed_index = self.front

        self.items[self.front] = None

        return {
            "success": True,
            "action": "dequeue",
            "value": removed_value,
            "values": [removed_value],
            "index": removed_index,
            "message": (
                f"인덱스 {removed_index}에 있던 "
                f"{removed_value}이(가) 제거되었습니다."
            ),
            "concept": (
                "front는 (front + 1) % SIZE를 이용해 "
                "다음 위치로 이동합니다."
            ),
            "front": self.front,
            "rear": self.rear,
        }

    # ========================================================
    # FRONT와 REAR 확인
    # ========================================================

    def peek_front(self) -> dict:
        """
        다음에 제거될 값을 확인합니다.
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "front",
                "value": None,
                "values": [],
                "message": (
                    "원형 큐가 비어 있어 "
                    "FRONT 데이터를 확인할 수 없습니다."
                ),
                "concept": (
                    "실제 첫 데이터는 front의 다음 위치에 있습니다."
                ),
                "front": self.front,
                "rear": self.rear,
            }

        data_index = self.next_front_index()
        front_value = self.items[data_index]

        return {
            "success": True,
            "action": "front",
            "value": front_value,
            "values": [front_value],
            "message": (
                f"다음에 제거될 값은 "
                f"{front_value}입니다."
            ),
            "concept": (
                f"front는 {self.front}이고, 실제 첫 데이터는 "
                f"인덱스 {data_index}에 있습니다."
            ),
            "front": self.front,
            "rear": self.rear,
        }

    def peek_rear(self) -> dict:
        """
        가장 최근에 삽입된 값을 확인합니다.
        """

        if self.is_empty():
            return {
                "success": False,
                "action": "rear",
                "value": None,
                "values": [],
                "message": (
                    "원형 큐가 비어 있어 "
                    "REAR 데이터를 확인할 수 없습니다."
                ),
                "concept": (
                    "공백 상태에서는 front와 rear가 같습니다."
                ),
                "front": self.front,
                "rear": self.rear,
            }

        rear_value = self.items[self.rear]

        return {
            "success": True,
            "action": "rear",
            "value": rear_value,
            "values": [rear_value],
            "message": (
                f"현재 REAR 데이터는 "
                f"{rear_value}입니다."
            ),
            "concept": (
                f"rear는 마지막 데이터가 저장된 "
                f"인덱스 {self.rear}을 가리킵니다."
            ),
            "front": self.front,
            "rear": self.rear,
        }

    # ========================================================
    # 초기화 및 상태 저장
    # ========================================================

    def clear(self) -> dict:
        """
        원형 큐를 초기 상태로 되돌립니다.
        """

        removed_count = self.size()

        self.items = [
            None
            for _ in range(self.max_size)
        ]

        self.front = 0
        self.rear = 0

        return {
            "success": True,
            "action": "clear",
            "value": None,
            "values": [],
            "message": (
                f"원형 큐를 초기화했습니다. "
                f"{removed_count}개의 데이터가 제거되었습니다."
            ),
            "concept": (
                "초기화 후에는 front와 rear가 모두 0입니다."
            ),
            "front": self.front,
            "rear": self.rear,
        }

    def to_state(self) -> dict:
        """
        Session State에 저장할 상태를 반환합니다.
        """

        return {
            "items": self.items.copy(),
            "front": self.front,
            "rear": self.rear,
            "max_size": self.max_size,
        }

    def load_state(
        self,
        items: list[Any | None],
        front: int,
        rear: int,
    ) -> None:
        """
        Session State에서 원형 큐 상태를 복원합니다.
        """

        if len(items) != self.max_size:
            raise ValueError(
                "저장된 배열 크기가 현재 원형 큐 크기와 다릅니다."
            )

        if not (
            0 <= front < self.max_size
            and 0 <= rear < self.max_size
        ):
            raise ValueError(
                "front 또는 rear의 인덱스가 올바르지 않습니다."
            )

        self.items = items.copy()
        self.front = front
        self.rear = rear

    def data_values(self) -> list[Any]:
        """
        FRONT부터 REAR까지 실제 데이터만 순서대로 반환합니다.
        """

        values: list[Any] = []

        current = self.front

        while current != self.rear:
            current = (
                current + 1
            ) % self.max_size

            values.append(
                self.items[current]
            )

        return values