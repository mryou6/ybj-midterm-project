"""
Binary Search Tree의 핵심 로직을 구현하는 모듈입니다.

주요 기능
- 노드 한 개 삽입
- 여러 노드 일괄 삽입
- 값 탐색
- 전위·중위·후위 순회
- 최소값·최대값 확인
- 트리 높이와 노드 수 계산
- 트리 초기화
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Node:
    """
    이진 탐색 트리의 노드를 표현합니다.
    """

    value: int
    left: Node | None = None
    right: Node | None = None


class BinarySearchTree:
    """
    이진 탐색 트리 클래스입니다.

    저장 규칙
    - 현재 노드보다 작은 값은 왼쪽
    - 현재 노드보다 큰 값은 오른쪽
    - 중복 값은 저장하지 않음
    """

    def __init__(self):
        """
        빈 이진 탐색 트리를 생성합니다.
        """

        self.root: Node | None = None

    # ========================================================
    # 노드 한 개 삽입
    # ========================================================

    def insert(self, value: int) -> dict[str, Any]:
        """
        이진 탐색 트리에 정수 하나를 삽입합니다.

        Args:
            value: 삽입할 정수

        Returns:
            삽입 성공 여부와 비교·이동 경로
        """

        value = int(value)

        if self.root is None:
            self.root = Node(value)

            return {
                "success": True,
                "action": "insert",
                "value": value,
                "values": [value],
                "path": [value],
                "message": (
                    f"{value}이(가) 트리의 ROOT로 삽입되었습니다."
                ),
                "concept": (
                    "빈 트리에 처음 삽입한 값은 ROOT가 됩니다."
                ),
            }

        current = self.root
        path: list[int] = []

        while current is not None:
            path.append(current.value)

            if value == current.value:
                return {
                    "success": False,
                    "action": "insert",
                    "value": value,
                    "values": [value],
                    "path": path,
                    "message": (
                        f"{value}은(는) 이미 트리에 존재합니다."
                    ),
                    "concept": (
                        "이번 학습용 이진 탐색 트리에서는 "
                        "중복 값을 저장하지 않습니다."
                    ),
                }

            if value < current.value:
                if current.left is None:
                    current.left = Node(value)
                    path.append(value)

                    return {
                        "success": True,
                        "action": "insert",
                        "value": value,
                        "values": [value],
                        "path": path,
                        "message": (
                            f"{value}이(가) {current.value}의 "
                            "왼쪽 자식으로 삽입되었습니다."
                        ),
                        "concept": (
                            "현재 노드보다 작은 값은 왼쪽으로 이동합니다."
                        ),
                    }

                current = current.left

            else:
                if current.right is None:
                    current.right = Node(value)
                    path.append(value)

                    return {
                        "success": True,
                        "action": "insert",
                        "value": value,
                        "values": [value],
                        "path": path,
                        "message": (
                            f"{value}이(가) {current.value}의 "
                            "오른쪽 자식으로 삽입되었습니다."
                        ),
                        "concept": (
                            "현재 노드보다 큰 값은 오른쪽으로 이동합니다."
                        ),
                    }

                current = current.right

        return {
            "success": False,
            "action": "insert",
            "value": value,
            "values": [value],
            "path": path,
            "message": "값을 삽입할 수 없습니다.",
            "concept": "현재 트리 상태를 다시 확인해 주세요.",
        }

    # ========================================================
    # 여러 노드 일괄 삽입
    # ========================================================

    def insert_many(
        self,
        values: list[int],
    ) -> dict[str, Any]:
        """
        여러 정수를 입력 순서대로 이진 탐색 트리에 삽입합니다.

        예:
            [50, 30, 70]을 입력하면
            50 → 30 → 70 순서로 삽입됩니다.

        중복 값은 건너뛰고, 나머지 값은 정상적으로 삽입합니다.
        """

        cleaned_values: list[int] = []

        for value in values:
            integer_value = int(value)

            if integer_value not in cleaned_values:
                cleaned_values.append(integer_value)

        if not cleaned_values:
            return {
                "success": False,
                "action": "insert_many",
                "value": None,
                "values": [],
                "path": [],
                "added": [],
                "duplicates": [],
                "message": "삽입할 숫자를 입력해 주세요.",
                "concept": (
                    "여러 숫자는 쉼표로 구분하여 입력할 수 있습니다."
                ),
            }

        added_values: list[int] = []
        duplicate_values: list[int] = []
        insertion_paths: dict[int, list[int]] = {}

        for value in cleaned_values:
            result = self.insert(value)

            insertion_paths[value] = result.get(
                "path",
                [],
            )

            if result["success"]:
                added_values.append(value)
            else:
                duplicate_values.append(value)

        if added_values:
            added_text = ", ".join(
                str(value)
                for value in added_values
            )

            if duplicate_values:
                duplicate_text = ", ".join(
                    str(value)
                    for value in duplicate_values
                )

                message = (
                    f"{added_text}을(를) 입력 순서대로 삽입했습니다. "
                    f"이미 존재하는 {duplicate_text}은(는) "
                    "추가하지 않았습니다."
                )

            else:
                message = (
                    f"{added_text}을(를) 입력 순서대로 "
                    "트리에 삽입했습니다."
                )

            return {
                "success": True,
                "action": "insert_many",
                "value": added_values[-1],
                "values": cleaned_values,
                "path": insertion_paths.get(
                    added_values[-1],
                    [],
                ),
                "added": added_values,
                "duplicates": duplicate_values,
                "paths": insertion_paths,
                "message": message,
                "concept": (
                    "숫자를 정렬한 것이 아니라 입력된 순서대로 "
                    "하나씩 크기를 비교하여 배치했습니다."
                ),
            }

        duplicate_text = ", ".join(
            str(value)
            for value in duplicate_values
        )

        return {
            "success": False,
            "action": "insert_many",
            "value": None,
            "values": cleaned_values,
            "path": [],
            "added": [],
            "duplicates": duplicate_values,
            "paths": insertion_paths,
            "message": (
                f"입력한 숫자 {duplicate_text}은(는) "
                "모두 이미 트리에 존재합니다."
            ),
            "concept": (
                "이번 이진 탐색 트리에서는 중복 값을 저장하지 않습니다."
            ),
        }

    # ========================================================
    # 탐색
    # ========================================================

    def search(self, value: int) -> dict[str, Any]:
        """
        이진 탐색 트리에서 값을 탐색합니다.
        """

        value = int(value)
        current = self.root
        path: list[int] = []

        while current is not None:
            path.append(current.value)

            if value == current.value:
                return {
                    "success": True,
                    "action": "search",
                    "value": value,
                    "values": [value],
                    "path": path,
                    "message": (
                        f"{value}을(를) 트리에서 찾았습니다."
                    ),
                    "concept": (
                        "현재 값과의 크기를 비교하여 "
                        "필요한 방향만 탐색했습니다."
                    ),
                }

            if value < current.value:
                current = current.left
            else:
                current = current.right

        return {
            "success": False,
            "action": "search",
            "value": value,
            "values": [value],
            "path": path,
            "message": (
                f"{value}은(는) 트리에 존재하지 않습니다."
            ),
            "concept": (
                "이동할 자식 노드가 더 이상 없으면 "
                "해당 값이 없다고 판단합니다."
            ),
        }

    # ========================================================
    # 순회
    # ========================================================

    def preorder(self) -> list[int]:
        """
        전위 순회: ROOT → LEFT → RIGHT
        """

        result: list[int] = []

        def traverse(node: Node | None) -> None:
            if node is None:
                return

            result.append(node.value)
            traverse(node.left)
            traverse(node.right)

        traverse(self.root)

        return result

    def inorder(self) -> list[int]:
        """
        중위 순회: LEFT → ROOT → RIGHT
        """

        result: list[int] = []

        def traverse(node: Node | None) -> None:
            if node is None:
                return

            traverse(node.left)
            result.append(node.value)
            traverse(node.right)

        traverse(self.root)

        return result

    def postorder(self) -> list[int]:
        """
        후위 순회: LEFT → RIGHT → ROOT
        """

        result: list[int] = []

        def traverse(node: Node | None) -> None:
            if node is None:
                return

            traverse(node.left)
            traverse(node.right)
            result.append(node.value)

        traverse(self.root)

        return result

    # ========================================================
    # 트리 상태
    # ========================================================

    def is_empty(self) -> bool:
        return self.root is None

    def size(self) -> int:
        """
        전체 노드 수를 반환합니다.
        """

        def count_nodes(node: Node | None) -> int:
            if node is None:
                return 0

            return (
                1
                + count_nodes(node.left)
                + count_nodes(node.right)
            )

        return count_nodes(self.root)

    def height(self) -> int:
        """
        빈 트리는 0, ROOT만 있으면 높이는 1입니다.
        """

        def calculate_height(node: Node | None) -> int:
            if node is None:
                return 0

            return 1 + max(
                calculate_height(node.left),
                calculate_height(node.right),
            )

        return calculate_height(self.root)

    def minimum(self) -> int | None:
        if self.root is None:
            return None

        current = self.root

        while current.left is not None:
            current = current.left

        return current.value

    def maximum(self) -> int | None:
        if self.root is None:
            return None

        current = self.root

        while current.right is not None:
            current = current.right

        return current.value

    # ========================================================
    # 초기화 및 복원
    # ========================================================

    def clear(self) -> dict[str, Any]:
        """
        트리의 모든 노드를 제거합니다.
        """

        removed_count = self.size()
        self.root = None

        return {
            "success": True,
            "action": "clear",
            "value": None,
            "values": [],
            "path": [],
            "message": (
                f"트리를 초기화했습니다. "
                f"{removed_count}개의 노드가 제거되었습니다."
            ),
            "concept": (
                "초기화하면 ROOT를 포함한 모든 노드가 제거됩니다."
            ),
        }

    def to_list(self) -> list[int]:
        """
        트리를 다시 같은 모양으로 복원할 수 있도록
        전위 순회 순서로 값을 반환합니다.
        """

        return self.preorder()

    def load_values(
        self,
        values: list[int],
    ) -> None:
        """
        저장된 삽입 순서로 트리를 복원합니다.
        """

        self.root = None

        for value in values:
            self.insert(int(value))