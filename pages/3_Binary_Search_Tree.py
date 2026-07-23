"""
Tree 자료구조 체험 페이지입니다.

지원하는 학습 모드
1. 일반 이진 트리
   - 부모, 왼쪽 자식, 오른쪽 자식 관계 직접 입력
   - 전위, 중위, 후위 순회
   - 노드 수, 단말 노드 수, 높이 확인

2. 이진 탐색 트리
   - 숫자 크기에 따라 자동 삽입
   - 여러 숫자 일괄 삽입
   - 값 탐색
   - 전위, 중위, 후위 순회
"""

from html import escape

import streamlit as st

from components.bst_visualizer import (
    render_bst,
    render_bst_code,
    render_bst_status,
    render_operation_history,
    render_operation_message,
    render_traversal_result,
)
from modules.binary_tree_logic import BinaryTree
from modules.bst_logic import BinarySearchTree
from modules.common import (
    apply_common_style,
    initialize_session_state,
    render_concept_box,
    render_footer,
    render_html,
    render_message,
    render_page_header,
    render_section_title,
)


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="Tree 체험",
    page_icon="🌳",
    layout="wide",
)

apply_common_style()


# ============================================================
# 2. Session State 초기화
# ============================================================

# ------------------------------------------------------------
# 공통 설정
# ------------------------------------------------------------

initialize_session_state(
    "tree_learning_mode",
    "일반 이진 트리",
)


# ------------------------------------------------------------
# 일반 이진 트리 상태
# ------------------------------------------------------------

initialize_session_state(
    "binary_tree_rules",
    [],
)

initialize_session_state(
    "binary_tree_last_result",
    None,
)

initialize_session_state(
    "binary_tree_history",
    [],
)

initialize_session_state(
    "binary_tree_traversal_name",
    None,
)

initialize_session_state(
    "binary_tree_traversal_values",
    [],
)

initialize_session_state(
    "binary_tree_quiz_score",
    0,
)

initialize_session_state(
    "binary_tree_quiz_submitted",
    False,
)


# ------------------------------------------------------------
# 이진 탐색 트리 상태
# ------------------------------------------------------------

initialize_session_state(
    "bst_values",
    [],
)

initialize_session_state(
    "bst_last_result",
    None,
)

initialize_session_state(
    "bst_history",
    [],
)

initialize_session_state(
    "bst_highlighted_path",
    [],
)

initialize_session_state(
    "bst_found_value",
    None,
)

initialize_session_state(
    "bst_target_value",
    None,
)

initialize_session_state(
    "bst_traversal_name",
    None,
)

initialize_session_state(
    "bst_traversal_values",
    [],
)

initialize_session_state(
    "bst_quiz_score",
    0,
)

initialize_session_state(
    "bst_quiz_submitted",
    False,
)

initialize_session_state(
    "bst_prediction_submitted",
    False,
)

initialize_session_state(
    "bst_prediction_answer",
    None,
)


# ============================================================
# 3. 트리 객체 생성 및 상태 복원
# ============================================================

binary_tree = BinaryTree()

if st.session_state.binary_tree_rules:
    binary_tree.load_rules(
        st.session_state.binary_tree_rules
    )


bst = BinarySearchTree()

if st.session_state.bst_values:
    bst.load_values(
        st.session_state.bst_values
    )


# ============================================================
# 4. 일반 이진 트리 공통 함수
# ============================================================

def save_binary_tree_state() -> None:
    """
    일반 이진 트리의 부모·자식 관계를 Session State에 저장합니다.
    """

    st.session_state.binary_tree_rules = (
        binary_tree.to_rules()
    )


def record_binary_tree_operation(
    result: dict,
    changes_tree: bool = False,
) -> None:
    """
    일반 이진 트리의 연산 결과를 기록합니다.
    """

    st.session_state.binary_tree_last_result = result
    st.session_state.binary_tree_history.append(result)

    if changes_tree:
        save_binary_tree_state()

        st.session_state.binary_tree_traversal_name = None
        st.session_state.binary_tree_traversal_values = []


def render_binary_tree_status(
    tree: BinaryTree,
) -> None:
    """
    일반 이진 트리의 현재 상태를 표시합니다.
    """

    if tree.is_empty():
        render_html(
            """
            <section class="status-panel">
                <div class="status-title">
                    일반 이진 트리 현재 상태
                </div>

                <div class="status-item">
                    <span class="status-label">
                        상태
                    </span>

                    <span class="status-value">
                        비어 있음
                    </span>
                </div>
            </section>
            """
        )
        return

    root_value = escape(
        str(tree.root.value)
    )

    preorder_text = " → ".join(
        escape(str(value))
        for value in tree.preorder()
    )

    render_html(
        f"""
        <section class="status-panel">
            <div class="status-title">
                일반 이진 트리 현재 상태
            </div>

            <div class="status-item">
                <span class="status-label">
                    ROOT
                </span>

                <span class="status-value">
                    {root_value}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    전체 노드
                </span>

                <span class="status-value">
                    {tree.size()}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    단말 노드
                </span>

                <span class="status-value">
                    {tree.leaf_count()}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    비단말 노드
                </span>

                <span class="status-value">
                    {tree.non_leaf_count()}개
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    높이
                </span>

                <span class="status-value">
                    {tree.height()}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    트리의 차수
                </span>

                <span class="status-value">
                    {tree.maximum_degree()}
                </span>
            </div>

            <div class="status-item">
                <span class="status-label">
                    전위 순회
                </span>

                <span class="status-value">
                    {preorder_text}
                </span>
            </div>
        </section>
        """
    )


def render_binary_tree_code(
    active_operation: str | None = None,
) -> None:
    """
    일반 이진 트리의 핵심 Python 코드를 표시합니다.
    """

    build_code = """
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


nodes["A"].left = nodes["B"]
nodes["A"].right = nodes["C"]
"""

    preorder_code = """
def preorder(node):
    if node is None:
        return

    print(node.value)
    preorder(node.left)
    preorder(node.right)
"""

    inorder_code = """
def inorder(node):
    if node is None:
        return

    inorder(node.left)
    print(node.value)
    inorder(node.right)
"""

    postorder_code = """
def postorder(node):
    if node is None:
        return

    postorder(node.left)
    postorder(node.right)
    print(node.value)
"""

    st.markdown(
        "#### 일반 이진 트리 Python 코드"
    )

    code_tabs = st.tabs(
        [
            "트리 구성",
            "전위 순회",
            "중위 순회",
            "후위 순회",
        ]
    )

    with code_tabs[0]:
        st.code(
            build_code.strip(),
            language="python",
        )

        if active_operation == "build":
            st.caption(
                "현재 실행한 기능: 부모·자식 관계로 트리 구성"
            )

    with code_tabs[1]:
        st.code(
            preorder_code.strip(),
            language="python",
        )

    with code_tabs[2]:
        st.code(
            inorder_code.strip(),
            language="python",
        )

    with code_tabs[3]:
        st.code(
            postorder_code.strip(),
            language="python",
        )


# ============================================================
# 5. BST 공통 함수
# ============================================================

def parse_bst_values(
    input_text: str,
) -> tuple[list[int], list[str]]:
    """
    쉼표로 구분된 문자열을 정수 목록으로 변환합니다.

    Returns:
        정상 숫자 목록, 잘못 입력된 값 목록
    """

    parsed_values: list[int] = []
    invalid_values: list[str] = []

    for raw_value in input_text.split(","):
        cleaned_value = raw_value.strip()

        if not cleaned_value:
            continue

        try:
            integer_value = int(cleaned_value)

            if integer_value not in parsed_values:
                parsed_values.append(integer_value)

        except ValueError:
            invalid_values.append(
                cleaned_value
            )

    return parsed_values, invalid_values


def save_bst_state() -> None:
    """
    현재 BST 구조를 복원할 수 있도록 전위 순회 값을 저장합니다.
    """

    st.session_state.bst_values = bst.to_list()


def reset_bst_visual_feedback() -> None:
    """
    BST 탐색 경로와 순회 표시를 초기화합니다.
    """

    st.session_state.bst_highlighted_path = []
    st.session_state.bst_found_value = None
    st.session_state.bst_target_value = None
    st.session_state.bst_traversal_name = None
    st.session_state.bst_traversal_values = []


def reset_bst_prediction() -> None:
    """
    BST 상태가 변경되면 이전 예측 결과를 초기화합니다.
    """

    st.session_state.bst_prediction_submitted = False
    st.session_state.bst_prediction_answer = None

    if "bst_prediction_radio" in st.session_state:
        del st.session_state["bst_prediction_radio"]


def record_bst_operation(
    result: dict,
    changes_tree: bool = False,
) -> None:
    """
    BST 연산 결과를 저장합니다.
    """

    st.session_state.bst_last_result = result
    st.session_state.bst_history.append(result)

    st.session_state.bst_highlighted_path = result.get(
        "path",
        [],
    )

    st.session_state.bst_target_value = result.get(
        "value"
    )

    if (
        result.get("action") == "search"
        and result.get("success")
    ):
        st.session_state.bst_found_value = result.get(
            "value"
        )
    else:
        st.session_state.bst_found_value = None

    save_bst_state()

    if changes_tree:
        reset_bst_prediction()


# ============================================================
# 6. 페이지 상단
# ============================================================

render_page_header(
    title="Tree 체험하기",
    description=(
        "일반 이진 트리와 이진 탐색 트리의 차이를 살펴보고, "
        "노드의 관계와 순회 과정을 직접 확인해 보세요."
    ),
    icon="🌳",
)


# ============================================================
# 7. 트리 유형 선택
# ============================================================

render_section_title(
    "학습할 트리 유형 선택"
)

tree_mode = st.radio(
    "트리 유형",
    [
        "일반 이진 트리",
        "이진 탐색 트리",
    ],
    horizontal=True,
    key="tree_learning_mode",
)

if tree_mode == "일반 이진 트리":
    render_message(
        (
            "일반 이진 트리는 값의 크기를 비교하지 않고, "
            "사용자가 부모와 왼쪽·오른쪽 자식의 관계를 "
            "직접 지정합니다."
        ),
        message_type="info",
    )

else:
    render_message(
        (
            "이진 탐색 트리는 현재 노드보다 작은 값을 왼쪽에, "
            "큰 값을 오른쪽에 자동으로 배치합니다."
        ),
        message_type="info",
    )


# ============================================================
# 8. 일반 이진 트리 모드
# ============================================================

if tree_mode == "일반 이진 트리":

    # --------------------------------------------------------
    # 8-1. 개념 설명
    # --------------------------------------------------------

    render_section_title(
        "1. 일반 이진 트리는 무엇인가요?"
    )

    render_concept_box(
        title="부모와 자식의 위치를 직접 정하는 트리입니다.",
        text=(
            "일반 이진 트리는 값의 크기와 관계없이 각 노드의 "
            "왼쪽 자식과 오른쪽 자식을 직접 지정합니다. "
            "각 노드는 최대 두 개의 자식을 가질 수 있습니다."
        ),
    )

    concept_col1, concept_col2, concept_col3 = st.columns(3)

    with concept_col1:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">
                    🌱
                </div>

                <div class="structure-card-title">
                    ROOT
                </div>

                <div class="structure-card-description">
                    트리의 가장 위에 위치하며 부모가 없는 노드입니다.
                </div>

                <span class="structure-card-keyword">
                    최상위 노드
                </span>
            </article>
            """
        )

    with concept_col2:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">
                    ↙️
                </div>

                <div class="structure-card-title">
                    왼쪽 자식
                </div>

                <div class="structure-card-description">
                    부모 노드의 왼쪽 아래에 연결되는 자식 노드입니다.
                </div>

                <span class="structure-card-keyword">
                    LEFT
                </span>
            </article>
            """
        )

    with concept_col3:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">
                    ↘️
                </div>

                <div class="structure-card-title">
                    오른쪽 자식
                </div>

                <div class="structure-card-description">
                    부모 노드의 오른쪽 아래에 연결되는 자식 노드입니다.
                </div>

                <span class="structure-card-keyword">
                    RIGHT
                </span>
            </article>
            """
        )

    render_message(
        (
            "자식 노드가 없는 경우에는 "
            "<strong>.</strong>으로 입력합니다."
        ),
        message_type="info",
        allow_html=True,
    )


    # --------------------------------------------------------
    # 8-2. 트리 직접 구성
    # --------------------------------------------------------

    render_section_title(
        "2. 일반 이진 트리 직접 구성하기"
    )

    control_col, visual_col = st.columns(
        [1, 1.8]
    )

    with control_col:
        st.subheader(
            "노드 관계 입력"
        )

        default_example = """A, B, C
B, D, E
C, ., F
D, G, H
E, ., .
F, ., .
G, ., .
H, ., ."""

        tree_input_text = st.text_area(
            "부모, 왼쪽 자식, 오른쪽 자식",
            placeholder=default_example,
            height=260,
            help=(
                "한 줄에 부모, 왼쪽 자식, 오른쪽 자식을 입력하세요. "
                "쉼표 또는 공백으로 구분할 수 있고, "
                "자식이 없는 경우에는 .을 입력합니다."
            ),
            key="binary_tree_input_text",
        )

        render_html(
            """
            <div class="info-box">
                <strong>입력 방법</strong><br>
                A, B, C<br>
                B, D, E<br>
                C, ., F<br><br>

                위 입력은 A의 왼쪽 자식이 B,
                오른쪽 자식이 C라는 뜻입니다.
            </div>
            """
        )

        build_col1, build_col2 = st.columns(2)

        with build_col1:
            build_clicked = st.button(
                "🌳 트리 생성",
                use_container_width=True,
                key="build_binary_tree",
            )

        with build_col2:
            sample_clicked = st.button(
                "📘 예제 불러오기",
                use_container_width=True,
                key="load_binary_tree_sample",
            )

        clear_clicked = st.button(
            "🔄 일반 이진 트리 초기화",
            use_container_width=True,
            key="clear_binary_tree",
        )

        if build_clicked:
            result = binary_tree.build_from_text(
                tree_input_text
            )

            record_binary_tree_operation(
                result,
                changes_tree=result["success"],
            )

            st.rerun()

        if sample_clicked:
            result = binary_tree.build_from_text(
                default_example
            )

            result["message"] = (
                "A부터 H까지의 노드로 예제 이진 트리를 "
                "생성했습니다."
            )

            record_binary_tree_operation(
                result,
                changes_tree=result["success"],
            )

            st.session_state.binary_tree_input_text = (
                default_example
            )

            st.rerun()

        if clear_clicked:
            result = binary_tree.clear()

            record_binary_tree_operation(
                result,
                changes_tree=True,
            )

            st.session_state.binary_tree_rules = []
            st.session_state.binary_tree_quiz_submitted = False

            if "binary_tree_input_text" in st.session_state:
                st.session_state.binary_tree_input_text = ""

            st.rerun()

        render_operation_message(
            st.session_state.binary_tree_last_result
        )

    with visual_col:
        st.subheader(
            "일반 이진 트리 시각화"
        )

        render_bst(
            binary_tree,
            highlighted_path=[],
            found_value=None,
            target_value=None,
        )


    # --------------------------------------------------------
    # 8-3. 현재 상태와 코드
    # --------------------------------------------------------

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        render_binary_tree_status(
            binary_tree
        )

    with status_col2:
        active_operation = None

        if st.session_state.binary_tree_last_result:
            active_operation = (
                st.session_state
                .binary_tree_last_result
                .get("action")
            )

        render_binary_tree_code(
            active_operation
        )


    # --------------------------------------------------------
    # 8-4. 순회 체험
    # --------------------------------------------------------

    render_section_title(
        "3. 일반 이진 트리 순회하기"
    )

    render_concept_box(
        title="ROOT를 방문하는 순서에 따라 결과가 달라집니다.",
        text=(
            "전위 순회는 ROOT를 먼저 방문하고, "
            "중위 순회는 왼쪽 서브트리 다음에 ROOT를 방문하며, "
            "후위 순회는 ROOT를 마지막에 방문합니다."
        ),
    )

    traversal_col1, traversal_col2, traversal_col3 = st.columns(3)

    with traversal_col1:
        binary_preorder_clicked = st.button(
            "전위 순회",
            use_container_width=True,
            key="binary_tree_preorder",
            disabled=binary_tree.is_empty(),
        )

    with traversal_col2:
        binary_inorder_clicked = st.button(
            "중위 순회",
            use_container_width=True,
            key="binary_tree_inorder",
            disabled=binary_tree.is_empty(),
        )

    with traversal_col3:
        binary_postorder_clicked = st.button(
            "후위 순회",
            use_container_width=True,
            key="binary_tree_postorder",
            disabled=binary_tree.is_empty(),
        )

    if binary_preorder_clicked:
        st.session_state.binary_tree_traversal_name = (
            "전위 순회"
        )

        st.session_state.binary_tree_traversal_values = (
            binary_tree.preorder()
        )

    if binary_inorder_clicked:
        st.session_state.binary_tree_traversal_name = (
            "중위 순회"
        )

        st.session_state.binary_tree_traversal_values = (
            binary_tree.inorder()
        )

    if binary_postorder_clicked:
        st.session_state.binary_tree_traversal_name = (
            "후위 순회"
        )

        st.session_state.binary_tree_traversal_values = (
            binary_tree.postorder()
        )

    if st.session_state.binary_tree_traversal_name:
        render_traversal_result(
            st.session_state.binary_tree_traversal_name,
            st.session_state.binary_tree_traversal_values,
        )

    if binary_tree.is_empty():
        st.info(
            "순회 활동을 하려면 먼저 일반 이진 트리를 생성해 주세요."
        )


    # --------------------------------------------------------
    # 8-5. 일반 이진 트리 학습 확인
    # --------------------------------------------------------

    render_section_title(
        "4. 학습 확인하기"
    )

    with st.form(
        "binary_tree_quiz_form"
    ):
        binary_question1 = st.radio(
            "1. 일반 이진 트리에서 각 노드가 가질 수 있는 "
            "최대 자식 노드 수는?",
            [
                "1개",
                "2개",
                "제한 없음",
            ],
            index=None,
        )

        binary_question2 = st.radio(
            "2. 부모 노드가 없는 최상위 노드는?",
            [
                "단말 노드",
                "형제 노드",
                "루트 노드",
            ],
            index=None,
        )

        binary_question3 = st.radio(
            "3. 전위 순회의 방문 순서는?",
            [
                "ROOT → LEFT → RIGHT",
                "LEFT → ROOT → RIGHT",
                "LEFT → RIGHT → ROOT",
            ],
            index=None,
        )

        binary_question4 = st.radio(
            "4. 자식 노드가 없는 노드는?",
            [
                "단말 노드",
                "부모 노드",
                "루트 노드",
            ],
            index=None,
        )

        binary_quiz_submitted = st.form_submit_button(
            "학습 결과 확인"
        )

    if binary_quiz_submitted:
        score = 0

        if binary_question1 == "2개":
            score += 1

        if binary_question2 == "루트 노드":
            score += 1

        if binary_question3 == "ROOT → LEFT → RIGHT":
            score += 1

        if binary_question4 == "단말 노드":
            score += 1

        st.session_state.binary_tree_quiz_score = score
        st.session_state.binary_tree_quiz_submitted = True

    if st.session_state.binary_tree_quiz_submitted:
        score = st.session_state.binary_tree_quiz_score

        if score == 4:
            render_message(
                "4문제를 모두 맞혔습니다! 일반 이진 트리의 "
                "기본 원리를 잘 이해했습니다.",
                message_type="success",
            )

        else:
            render_message(
                f"4문제 중 {score}문제를 맞혔습니다. "
                "노드 관계와 순회 방법을 다시 확인해 보세요.",
                message_type="warning",
            )


    # --------------------------------------------------------
    # 8-6. 일반 이진 트리 연산 기록
    # --------------------------------------------------------

    with st.expander(
        "일반 이진 트리 연산 기록 보기",
        expanded=False,
    ):
        render_operation_history(
            st.session_state.binary_tree_history
        )

        if st.session_state.binary_tree_history:
            if st.button(
                "연산 기록 삭제",
                key="clear_binary_tree_history",
            ):
                st.session_state.binary_tree_history = []
                st.rerun()


# ============================================================
# 9. 이진 탐색 트리 모드
# ============================================================

else:

    # --------------------------------------------------------
    # 9-1. 개념 설명
    # --------------------------------------------------------

    render_section_title(
        "1. Binary Search Tree는 무엇인가요?"
    )

    render_concept_box(
        title="숫자에 따라 갈림길을 선택하는 트리입니다.",
        text=(
            "현재 노드보다 작은 값은 왼쪽에, 큰 값은 오른쪽에 "
            "저장합니다. 값을 정렬한 후 배치하는 것이 아니라 "
            "입력한 순서대로 하나씩 비교하여 위치를 결정합니다."
        ),
    )

    concept_col1, concept_col2, concept_col3 = st.columns(3)

    with concept_col1:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">
                    ⬅️
                </div>

                <div class="structure-card-title">
                    작은 값
                </div>

                <div class="structure-card-description">
                    현재 노드보다 작은 값은 왼쪽 방향으로 이동합니다.
                </div>

                <span class="structure-card-keyword">
                    LEFT
                </span>
            </article>
            """
        )

    with concept_col2:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">
                    🌱
                </div>

                <div class="structure-card-title">
                    ROOT
                </div>

                <div class="structure-card-description">
                    가장 처음 삽입한 값이 트리의 ROOT가 됩니다.
                </div>

                <span class="structure-card-keyword">
                    시작 노드
                </span>
            </article>
            """
        )

    with concept_col3:
        render_html(
            """
            <article class="structure-card">
                <div class="structure-card-icon">
                    ➡️
                </div>

                <div class="structure-card-title">
                    큰 값
                </div>

                <div class="structure-card-description">
                    현재 노드보다 큰 값은 오른쪽 방향으로 이동합니다.
                </div>

                <span class="structure-card-keyword">
                    RIGHT
                </span>
            </article>
            """
        )

    render_message(
        (
            "예: <strong>50, 30, 70</strong>을 입력하면 "
            "50이 ROOT, 30은 왼쪽, 70은 오른쪽에 배치됩니다."
        ),
        message_type="info",
        allow_html=True,
    )


    # --------------------------------------------------------
    # 9-2. BST 직접 체험
    # --------------------------------------------------------

    render_section_title(
        "2. 이진 탐색 트리 직접 체험하기"
    )

    control_col, visual_col = st.columns(
        [1, 1.9]
    )

    with control_col:
        st.subheader(
            "트리 조작"
        )

        insert_text = st.text_input(
            "삽입할 정수",
            placeholder="예: 50 또는 50, 30, 70, 20",
            help=(
                "여러 숫자는 쉼표로 구분하세요. "
                "숫자는 입력한 순서대로 삽입됩니다."
            ),
            max_chars=200,
            key="bst_insert_text",
        )

        parsed_values, invalid_values = parse_bst_values(
            insert_text
        )

        if parsed_values:
            preview_text = " → ".join(
                str(value)
                for value in parsed_values
            )

            root_preview = (
                bst.root.value
                if bst.root is not None
                else parsed_values[0]
            )

            render_html(
                f"""
                <div class="info-box">
                    <strong>삽입 순서</strong><br>
                    {escape(preview_text)}<br><br>

                    현재 트리가 비어 있다면
                    <strong>{root_preview}</strong>이(가)
                    ROOT가 됩니다.
                </div>
                """
            )

        if invalid_values:
            invalid_text = ", ".join(
                escape(value)
                for value in invalid_values
            )

            render_message(
                (
                    "정수가 아닌 입력이 포함되어 있습니다: "
                    f"{invalid_text}"
                ),
                message_type="warning",
            )

        insert_clicked = st.button(
            "🌱 숫자 삽입",
            use_container_width=True,
            key="bst_insert_button",
        )

        st.markdown(
            "#### 숫자 탐색"
        )

        search_value = st.number_input(
            "탐색할 정수",
            min_value=-9999,
            max_value=9999,
            value=50,
            step=1,
            key="bst_search_value",
        )

        search_clicked = st.button(
            "🔍 숫자 탐색",
            use_container_width=True,
            key="bst_search_button",
        )

        sample_clicked = st.button(
            "🌳 예제 트리 만들기",
            use_container_width=True,
            key="bst_sample_button",
        )

        clear_clicked = st.button(
            "🔄 이진 탐색 트리 초기화",
            use_container_width=True,
            key="bst_clear_button",
        )

        if insert_clicked:
            values, invalid = parse_bst_values(
                insert_text
            )

            if invalid:
                result = {
                    "success": False,
                    "action": "insert_many",
                    "value": None,
                    "values": [],
                    "path": [],
                    "message": (
                        "정수가 아닌 값이 포함되어 "
                        "삽입을 취소했습니다."
                    ),
                    "concept": (
                        "쉼표 사이에는 정수만 입력해 주세요."
                    ),
                }

            elif not values:
                result = {
                    "success": False,
                    "action": "insert",
                    "value": None,
                    "values": [],
                    "path": [],
                    "message": (
                        "삽입할 정수를 입력해 주세요."
                    ),
                    "concept": (
                        "여러 숫자는 쉼표로 구분하여 "
                        "입력할 수 있습니다."
                    ),
                }

            elif len(values) == 1:
                result = bst.insert(
                    values[0]
                )

            else:
                result = bst.insert_many(
                    values
                )

            record_bst_operation(
                result,
                changes_tree=result["success"],
            )

            st.rerun()

        if search_clicked:
            reset_bst_visual_feedback()

            result = bst.search(
                int(search_value)
            )

            record_bst_operation(
                result,
                changes_tree=False,
            )

            st.rerun()

        if sample_clicked:
            bst.clear()

            example_values = [
                50,
                30,
                70,
                20,
                40,
                60,
                80,
            ]

            result = bst.insert_many(
                example_values
            )

            result["message"] = (
                "50, 30, 70, 20, 40, 60, 80으로 "
                "예제 이진 탐색 트리를 만들었습니다."
            )

            record_bst_operation(
                result,
                changes_tree=True,
            )

            reset_bst_visual_feedback()

            st.rerun()

        if clear_clicked:
            result = bst.clear()

            record_bst_operation(
                result,
                changes_tree=True,
            )

            reset_bst_visual_feedback()

            st.session_state.bst_values = []
            st.session_state.bst_quiz_submitted = False

            st.rerun()

        render_operation_message(
            st.session_state.bst_last_result
        )

    with visual_col:
        st.subheader(
            "Binary Search Tree 시각화"
        )

        render_bst(
            bst,
            highlighted_path=(
                st.session_state.bst_highlighted_path
            ),
            found_value=(
                st.session_state.bst_found_value
            ),
            target_value=(
                st.session_state.bst_target_value
            ),
        )


    # --------------------------------------------------------
    # 9-3. BST 상태와 코드
    # --------------------------------------------------------

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        render_bst_status(
            bst
        )

    with status_col2:
        active_operation = None

        if st.session_state.bst_last_result:
            active_operation = (
                st.session_state
                .bst_last_result
                .get("action")
            )

        render_bst_code(
            active_operation
        )


    # --------------------------------------------------------
    # 9-4. BST 순회
    # --------------------------------------------------------

    render_section_title(
        "3. 이진 탐색 트리 순회하기"
    )

    render_concept_box(
        title="ROOT를 언제 방문하느냐에 따라 순회가 달라집니다.",
        text=(
            "전위 순회는 ROOT를 먼저, 중위 순회는 ROOT를 가운데, "
            "후위 순회는 ROOT를 마지막에 방문합니다. "
            "BST를 중위 순회하면 값이 오름차순으로 출력됩니다."
        ),
    )

    traversal_col1, traversal_col2, traversal_col3 = st.columns(3)

    with traversal_col1:
        bst_preorder_clicked = st.button(
            "전위 순회",
            use_container_width=True,
            key="bst_preorder_button",
            disabled=bst.is_empty(),
        )

    with traversal_col2:
        bst_inorder_clicked = st.button(
            "중위 순회",
            use_container_width=True,
            key="bst_inorder_button",
            disabled=bst.is_empty(),
        )

    with traversal_col3:
        bst_postorder_clicked = st.button(
            "후위 순회",
            use_container_width=True,
            key="bst_postorder_button",
            disabled=bst.is_empty(),
        )

    if bst_preorder_clicked:
        st.session_state.bst_traversal_name = (
            "전위 순회"
        )

        st.session_state.bst_traversal_values = (
            bst.preorder()
        )

    if bst_inorder_clicked:
        st.session_state.bst_traversal_name = (
            "중위 순회"
        )

        st.session_state.bst_traversal_values = (
            bst.inorder()
        )

    if bst_postorder_clicked:
        st.session_state.bst_traversal_name = (
            "후위 순회"
        )

        st.session_state.bst_traversal_values = (
            bst.postorder()
        )

    if st.session_state.bst_traversal_name:
        render_traversal_result(
            st.session_state.bst_traversal_name,
            st.session_state.bst_traversal_values,
        )

    if bst.is_empty():
        st.info(
            "순회 활동을 하려면 먼저 숫자를 삽입해 주세요."
        )


    # --------------------------------------------------------
    # 9-5. BST 삽입 방향 예측
    # --------------------------------------------------------

    render_section_title(
        "4. 삽입 방향 예측하기"
    )

    if bst.root is None:
        st.info(
            "예측 활동을 하려면 먼저 숫자를 삽입해 주세요."
        )

    else:
        prediction_value = st.number_input(
            "예측할 새로운 정수",
            min_value=-9999,
            max_value=9999,
            value=25,
            step=1,
            key="bst_prediction_value",
        )

        prediction = st.radio(
            "ROOT에서의 첫 이동 방향",
            [
                "왼쪽",
                "오른쪽",
                "이동하지 않음",
            ],
            index=None,
            key="bst_prediction_radio",
        )

        if st.button(
            "예측 결과 확인",
            key="check_bst_prediction",
        ):
            st.session_state.bst_prediction_submitted = True
            st.session_state.bst_prediction_answer = prediction

        if st.session_state.bst_prediction_submitted:
            root_value = bst.root.value

            if prediction_value < root_value:
                correct_answer = "왼쪽"

            elif prediction_value > root_value:
                correct_answer = "오른쪽"

            else:
                correct_answer = "이동하지 않음"

            selected_answer = (
                st.session_state.bst_prediction_answer
            )

            if selected_answer is None:
                render_message(
                    "답을 선택한 뒤 결과를 확인해 주세요.",
                    message_type="warning",
                )

            elif selected_answer == correct_answer:
                render_message(
                    (
                        "정답입니다! ROOT에서의 첫 이동 방향은 "
                        f"{correct_answer}입니다."
                    ),
                    message_type="success",
                )

            else:
                render_message(
                    (
                        f"정답은 {correct_answer}입니다. "
                        "ROOT와 입력값의 크기를 비교해 보세요."
                    ),
                    message_type="warning",
                )


    # --------------------------------------------------------
    # 9-6. BST 학습 확인
    # --------------------------------------------------------

    render_section_title(
        "5. 학습 확인하기"
    )

    with st.form(
        "bst_quiz_form"
    ):
        bst_question1 = st.radio(
            "1. 현재 노드보다 작은 값은 어느 방향에 저장되나요?",
            [
                "왼쪽",
                "오른쪽",
                "아무 위치",
            ],
            index=None,
        )

        bst_question2 = st.radio(
            "2. 현재 노드보다 큰 값은 어느 방향에 저장되나요?",
            [
                "왼쪽",
                "오른쪽",
                "ROOT 위쪽",
            ],
            index=None,
        )

        bst_question3 = st.radio(
            "3. 중위 순회의 방문 순서는?",
            [
                "ROOT → LEFT → RIGHT",
                "LEFT → ROOT → RIGHT",
                "LEFT → RIGHT → ROOT",
            ],
            index=None,
        )

        bst_question4 = st.radio(
            "4. BST의 중위 순회 결과는?",
            [
                "오름차순",
                "ROOT만 출력",
                "무작위 순서",
            ],
            index=None,
        )

        bst_quiz_submitted = st.form_submit_button(
            "학습 결과 확인"
        )

    if bst_quiz_submitted:
        score = 0

        if bst_question1 == "왼쪽":
            score += 1

        if bst_question2 == "오른쪽":
            score += 1

        if bst_question3 == "LEFT → ROOT → RIGHT":
            score += 1

        if bst_question4 == "오름차순":
            score += 1

        st.session_state.bst_quiz_score = score
        st.session_state.bst_quiz_submitted = True

    if st.session_state.bst_quiz_submitted:
        score = st.session_state.bst_quiz_score

        if score == 4:
            render_message(
                "4문제를 모두 맞혔습니다! 이진 탐색 트리의 "
                "기본 원리를 잘 이해했습니다.",
                message_type="success",
            )

        else:
            render_message(
                f"4문제 중 {score}문제를 맞혔습니다. "
                "삽입 규칙과 순회 방법을 다시 확인해 보세요.",
                message_type="warning",
            )


    # --------------------------------------------------------
    # 9-7. BST 연산 기록
    # --------------------------------------------------------

    with st.expander(
        "이진 탐색 트리 연산 기록 보기",
        expanded=False,
    ):
        render_operation_history(
            st.session_state.bst_history
        )

        if st.session_state.bst_history:
            if st.button(
                "연산 기록 삭제",
                key="clear_bst_history",
            ):
                st.session_state.bst_history = []
                st.rerun()


# ============================================================
# 10. 페이지 하단
# ============================================================

render_footer()