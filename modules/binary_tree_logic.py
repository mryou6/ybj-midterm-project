"""
일반 이진 트리의 핵심 로직을 구현하는 모듈입니다.

주요 기능
- 부모·왼쪽 자식·오른쪽 자식 관계 입력
- 일반 이진 트리 생성
- 전위·중위·후위 순회
- 노드 수, 단말 노드 수, 높이 계산
- 입력 오류 검사
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BinaryTreeNode:
    """
    일반 이진 트리의 노드입니다.
    """

    value: str
    left: BinaryTreeNode | None = None
    right: BinaryTreeNode | None = None


class BinaryTree:
    """
    사용자가 부모·왼쪽 자식·오른쪽 자식을 직접 지정하는
    일반 이진 트리입니다.

    이진 탐색 트리와 달리 값의 크기를 비교하지 않습니다.
    """

    def __init__(self):
        self.root: BinaryTreeNode | None = None
        self.nodes: dict[str, BinaryTreeNode] = {}
        self.rules: list[tuple[str, str | None, str | None]] = []

    # ========================================================
    # 입력값 정리
    # ========================================================

    @staticmethod
    def normalize_value(value: str) -> str | None:
        """
        노드 이름을 정리합니다.

        '.', 'none', 'null', 빈 문자열은
        자식 노드가 없는 것으로 처리합니다.
        """

        cleaned_value = str(value).strip().upper()

        if cleaned_value in {
            "",
            ".",
            "NONE",
            "NULL",
        }:
            return None

        return cleaned_value

    @classmethod
    def parse_rules(
        cls,
        input_text: str,
    ) -> dict[str, Any]:
        """
        여러 줄의 트리 입력을 관계 목록으로 변환합니다.

        입력 예:
            A, B, C
            B, D, E
            C, ., F

        공백 구분 입력도 허용합니다.

        입력 예:
            A B C
            B D E
            C . F
        """

        parsed_rules: list[
            tuple[str, str | None, str | None]
        ] = []

        errors: list[str] = []

        lines = [
            line.strip()
            for line in str(input_text).splitlines()
            if line.strip()
        ]

        if not lines:
            return {
                "success": False,
                "rules": [],
                "errors": [
                    "트리를 구성할 노드 관계를 입력해 주세요."
                ],
            }

        for line_number, line in enumerate(
            lines,
            start=1,
        ):
            if "," in line:
                parts = [
                    part.strip()
                    for part in line.split(",")
                ]
            else:
                parts = line.split()

            if len(parts) != 3:
                errors.append(
                    f"{line_number}번째 줄은 "
                    "'부모, 왼쪽 자식, 오른쪽 자식' "
                    "형식으로 입력해야 합니다."
                )
                continue

            parent = cls.normalize_value(parts[0])
            left = cls.normalize_value(parts[1])
            right = cls.normalize_value(parts[2])

            if parent is None:
                errors.append(
                    f"{line_number}번째 줄의 부모 노드가 비어 있습니다."
                )
                continue

            if left == parent or right == parent:
                errors.append(
                    f"{line_number}번째 줄에서 노드 {parent}이(가) "
                    "자기 자신을 자식으로 가질 수 없습니다."
                )
                continue

            if (
                left is not None
                and right is not None
                and left == right
            ):
                errors.append(
                    f"{line_number}번째 줄에서 왼쪽과 오른쪽 자식이 "
                    f"모두 {left}입니다."
                )
                continue

            parsed_rules.append(
                (
                    parent,
                    left,
                    right,
                )
            )

        return {
            "success": not errors,
            "rules": parsed_rules,
            "errors": errors,
        }

    # ========================================================
    # 트리 생성
    # ========================================================

    def build_from_rules(
        self,
        rules: list[
            tuple[str, str | None, str | None]
        ],
    ) -> dict[str, Any]:
        """
        부모·왼쪽 자식·오른쪽 자식 관계로 트리를 생성합니다.
        """

        if not rules:
            return {
                "success": False,
                "action": "build",
                "value": None,
                "message": (
                    "트리를 구성할 관계가 없습니다."
                ),
                "concept": (
                    "부모, 왼쪽 자식, 오른쪽 자식 관계를 "
                    "한 줄씩 입력해 주세요."
                ),
            }

        parent_names = [
            parent
            for parent, _, _ in rules
        ]

        duplicated_parents = sorted(
            {
                parent
                for parent in parent_names
                if parent_names.count(parent) > 1
            }
        )

        if duplicated_parents:
            duplicate_text = ", ".join(
                duplicated_parents
            )

            return {
                "success": False,
                "action": "build",
                "value": None,
                "message": (
                    f"부모 노드 {duplicate_text}의 관계가 "
                    "두 번 이상 정의되었습니다."
                ),
                "concept": (
                    "각 부모 노드의 왼쪽·오른쪽 자식 관계는 "
                    "한 번만 입력해야 합니다."
                ),
            }

        all_node_names: set[str] = set()
        child_names: list[str] = []

        for parent, left, right in rules:
            all_node_names.add(parent)

            if left is not None:
                all_node_names.add(left)
                child_names.append(left)

            if right is not None:
                all_node_names.add(right)
                child_names.append(right)

        duplicated_children = sorted(
            {
                child
                for child in child_names
                if child_names.count(child) > 1
            }
        )

        if duplicated_children:
            duplicate_text = ", ".join(
                duplicated_children
            )

            return {
                "success": False,
                "action": "build",
                "value": None,
                "message": (
                    f"노드 {duplicate_text}이(가) "
                    "둘 이상의 부모를 가지고 있습니다."
                ),
                "concept": (
                    "트리에서 ROOT를 제외한 모든 노드는 "
                    "하나의 부모만 가져야 합니다."
                ),
            }

        root_candidates = [
            node_name
            for node_name in all_node_names
            if node_name not in child_names
        ]

        if len(root_candidates) == 0:
            return {
                "success": False,
                "action": "build",
                "value": None,
                "message": (
                    "ROOT 노드를 찾을 수 없습니다."
                ),
                "concept": (
                    "모든 노드가 다른 노드의 자식이면 "
                    "사이클이 존재할 가능성이 있습니다."
                ),
            }

        if len(root_candidates) > 1:
            candidate_text = ", ".join(
                sorted(root_candidates)
            )

            return {
                "success": False,
                "action": "build",
                "value": None,
                "message": (
                    f"ROOT 후보가 여러 개입니다: {candidate_text}"
                ),
                "concept": (
                    "하나의 트리에는 ROOT가 하나만 존재해야 합니다. "
                    "서로 연결되지 않은 노드가 있는지 확인해 주세요."
                ),
            }

        nodes = {
            node_name: BinaryTreeNode(
                value=node_name
            )
            for node_name in all_node_names
        }

        for parent, left, right in rules:
            parent_node = nodes[parent]

            parent_node.left = (
                nodes[left]
                if left is not None
                else None
            )

            parent_node.right = (
                nodes[right]
                if right is not None
                else None
            )

        root_name = root_candidates[0]
        root_node = nodes[root_name]

        visited: set[str] = set()
        visiting: set[str] = set()

        def detect_cycle(
            node: BinaryTreeNode | None,
        ) -> bool:
            if node is None:
                return False

            if node.value in visiting:
                return True

            if node.value in visited:
                return False

            visiting.add(node.value)

            if detect_cycle(node.left):
                return True

            if detect_cycle(node.right):
                return True

            visiting.remove(node.value)
            visited.add(node.value)

            return False

        if detect_cycle(root_node):
            return {
                "success": False,
                "action": "build",
                "value": None,
                "message": (
                    "노드 관계에 사이클이 존재합니다."
                ),
                "concept": (
                    "트리는 출발 노드로 다시 돌아오는 "
                    "사이클을 가질 수 없습니다."
                ),
            }

        if len(visited) != len(nodes):
            disconnected_nodes = sorted(
                set(nodes.keys()) - visited
            )

            disconnected_text = ", ".join(
                disconnected_nodes
            )

            return {
                "success": False,
                "action": "build",
                "value": None,
                "message": (
                    f"ROOT와 연결되지 않은 노드가 있습니다: "
                    f"{disconnected_text}"
                ),
                "concept": (
                    "하나의 트리에 포함된 모든 노드는 "
                    "ROOT에서 연결되어야 합니다."
                ),
            }

        self.root = root_node
        self.nodes = nodes
        self.rules = rules.copy()

        return {
            "success": True,
            "action": "build",
            "value": root_name,
            "message": (
                f"ROOT가 {root_name}인 일반 이진 트리를 "
                "생성했습니다."
            ),
            "concept": (
                "노드 값의 크기가 아니라 입력한 "
                "왼쪽·오른쪽 자식 관계에 따라 트리를 구성했습니다."
            ),
        }

    def build_from_text(
        self,
        input_text: str,
    ) -> dict[str, Any]:
        """
        입력 문자열을 분석하고 트리를 생성합니다.
        """

        parse_result = self.parse_rules(
            input_text
        )

        if not parse_result["success"]:
            return {
                "success": False,
                "action": "build",
                "value": None,
                "message": (
                    "입력 형식을 확인해 주세요."
                ),
                "concept": " / ".join(
                    parse_result["errors"]
                ),
            }

        return self.build_from_rules(
            parse_result["rules"]
        )

    # ========================================================
    # 순회
    # ========================================================

    def preorder(self) -> list[str]:
        """
        전위 순회: ROOT → LEFT → RIGHT
        """

        result: list[str] = []

        def traverse(
            node: BinaryTreeNode | None,
        ) -> None:
            if node is None:
                return

            result.append(node.value)
            traverse(node.left)
            traverse(node.right)

        traverse(self.root)

        return result

    def inorder(self) -> list[str]:
        """
        중위 순회: LEFT → ROOT → RIGHT
        """

        result: list[str] = []

        def traverse(
            node: BinaryTreeNode | None,
        ) -> None:
            if node is None:
                return

            traverse(node.left)
            result.append(node.value)
            traverse(node.right)

        traverse(self.root)

        return result

    def postorder(self) -> list[str]:
        """
        후위 순회: LEFT → RIGHT → ROOT
        """

        result: list[str] = []

        def traverse(
            node: BinaryTreeNode | None,
        ) -> None:
            if node is None:
                return

            traverse(node.left)
            traverse(node.right)
            result.append(node.value)

        traverse(self.root)

        return result

    # ========================================================
    # 트리 정보
    # ========================================================

    def is_empty(self) -> bool:
        return self.root is None

    def size(self) -> int:
        return len(self.nodes)

    def leaf_count(self) -> int:
        """
        자식이 없는 단말 노드 수를 반환합니다.
        """

        def count_leaf(
            node: BinaryTreeNode | None,
        ) -> int:
            if node is None:
                return 0

            if (
                node.left is None
                and node.right is None
            ):
                return 1

            return (
                count_leaf(node.left)
                + count_leaf(node.right)
            )

        return count_leaf(self.root)

    def non_leaf_count(self) -> int:
        """
        비단말 노드 수를 반환합니다.
        """

        return self.size() - self.leaf_count()

    def height(self) -> int:
        """
        ROOT만 있는 트리의 높이를 1로 계산합니다.
        """

        def calculate_height(
            node: BinaryTreeNode | None,
        ) -> int:
            if node is None:
                return 0

            return 1 + max(
                calculate_height(node.left),
                calculate_height(node.right),
            )

        return calculate_height(self.root)

    def maximum_degree(self) -> int:
        """
        트리 내 노드의 최대 차수를 반환합니다.
        """

        maximum = 0

        def inspect(
            node: BinaryTreeNode | None,
        ) -> None:
            nonlocal maximum

            if node is None:
                return

            degree = int(
                node.left is not None
            ) + int(
                node.right is not None
            )

            maximum = max(
                maximum,
                degree,
            )

            inspect(node.left)
            inspect(node.right)

        inspect(self.root)

        return maximum

    # ========================================================
    # 저장 및 초기화
    # ========================================================

    def to_rules(
        self,
    ) -> list[
        tuple[str, str | None, str | None]
    ]:
        return self.rules.copy()

    def load_rules(
        self,
        rules: list[
            tuple[str, str | None, str | None]
        ],
    ) -> None:
        if not rules:
            self.clear()
            return

        self.build_from_rules(
            rules
        )

    def clear(self) -> dict[str, Any]:
        removed_count = self.size()

        self.root = None
        self.nodes = {}
        self.rules = []

        return {
            "success": True,
            "action": "clear",
            "value": None,
            "message": (
                f"일반 이진 트리를 초기화했습니다. "
                f"{removed_count}개의 노드가 제거되었습니다."
            ),
            "concept": (
                "초기화하면 모든 부모·자식 관계가 제거됩니다."
            ),
        }