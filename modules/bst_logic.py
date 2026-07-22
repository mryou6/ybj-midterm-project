"""
Binary Search Tree의 핵심 로직을 구현하는 모듈입니다.

주요 기능
- Node 클래스
- 노드 삽입
- 값 탐색
- 전위 순회
- 중위 순회
- 후위 순회
- 트리 높이 계산
- 노드 수 계산
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

    규칙
    - 현재 노드보다 작은 값은 왼쪽에 저장합니다.
    - 현재 노드보다 큰 값은 오른쪽에 저장합니다.
    - 중복 값은 저장하지 않습니다.
    """

    def __init__(self):
        """
        빈 이진 탐색 트리를 생성합니다.
        """

        self.root: Node | None = None

    # ========================================================
    # 삽입
    # ========================================================

    def insert(self, value: int) -> dict[str, Any]:
        """
        이진 탐색 트리에 값을 삽입합니다.

        Args:
            value: 삽입할 정수

        Returns:
            삽입 결과와 비교 경로를 담은 딕셔너리
        """

        if self.root is None:
            self.root = Node(value)

            return {
                "success": True,
                "action": "insert",
                "value": value,
                "path": [value],
                "message": (
                    f"{value}이(가) 트리의 첫 번째 노드인 "
                    "ROOT에 삽입되었습니다."
                ),
                "concept": (
                    "트리가 비어 있을 때 처음 삽입한 값은 "
                    "ROOT 노드가 됩니다."
                ),
            }

        current = self.root
        path = []

        while current is not None:
            path.append(current.value)

            if value == current.value:
                return {
                    "success": False,
                    "action": "insert",
                    "value": value,
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
                        "path": path,
                        "message": (
                            f"{value}이(가) {current.value}의 "
                            "왼쪽 자식 노드로 삽입되었습니다."
                        ),
                        "concept": (
                            "현재 노드보다 작은 값은 "
                            "왼쪽 방향으로 이동합니다."
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
                        "path": path,
                        "message": (
                            f"{value}이(가) {current.value}의 "
                            "오른쪽 자식 노드로 삽입되었습니다."
                        ),
                        "concept": (
                            "현재 노드보다 큰 값은 "
                            "오른쪽 방향으로 이동합니다."
                        ),
                    }

                current = current.right

        return {
            "success": False,
            "action": "insert",
            "value": value,
            "path": path,
            "message": "값을 삽입할 수 없습니다.",
            "concept": "트리 상태를 다시 확인해 주세요.",
        }

    # ========================================================
    # 탐색
    # ========================================================

    def search(self, value: int) -> dict[str, Any]:
        """
        이진 탐색 트리에서 값을 탐색합니다.

        Args:
            value: 찾을 정수

        Returns:
            탐색 성공 여부와 방문 경로
        """

        current = self.root
        path = []

        while current is not None:
            path.append(current.value)

            if value == current.value:
                return {
                    "success": True,
                    "action": "search",
                    "value": value,
                    "path": path,
                    "message": (
                        f"{value}을(를) 트리에서 찾았습니다."
                    ),
                    "concept": (
                        "값의 크기를 비교하며 필요한 방향만 "
                        "탐색했기 때문에 모든 노드를 확인할 필요가 없습니다."
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
            "path": path,
            "message": (
                f"{value}은(는) 트리에 존재하지 않습니다."
            ),
            "concept": (
                "탐색 중 더 이동할 노드가 없으면 "
                "해당 값이 트리에 없다고 판단합니다."
            ),
        }

    # ========================================================
    # 순회
    # ========================================================

    def preorder(self) -> list[int]:
        """
        전위 순회 결과를 반환합니다.

        방문 순서:
        ROOT → LEFT → RIGHT
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
        중위 순회 결과를 반환합니다.

        방문 순서:
        LEFT → ROOT → RIGHT
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
        후위 순회 결과를 반환합니다.

        방문 순서:
        LEFT → RIGHT → ROOT
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
    # 상태 확인
    # ========================================================

    def is_empty(self) -> bool:
        """
        트리가 비어 있는지 확인합니다.
        """

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
        트리의 높이를 반환합니다.

        빈 트리의 높이는 0,
        ROOT만 있는 트리의 높이는 1로 계산합니다.
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
        """
        트리에서 가장 작은 값을 반환합니다.
        """

        if self.root is None:
            return None

        current = self.root

        while current.left is not None:
            current = current.left

        return current.value

    def maximum(self) -> int | None:
        """
        트리에서 가장 큰 값을 반환합니다.
        """

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
        트리 값을 전위 순회 순서의 리스트로 반환합니다.

        Session State에 저장할 때 사용합니다.
        """

        return self.preorder()

    def load_values(self, values: list[int]) -> None:
        """
        값 목록을 순서대로 삽입하여 트리를 복원합니다.

        Args:
            values: 삽입 순서가 유지된 값 목록
        """

        self.root = None

        for value in values:
            self.insert(int(value))