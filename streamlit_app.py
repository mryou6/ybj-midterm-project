import streamlit as st

# 반드시 다른 Streamlit 명령보다 먼저 실행
st.set_page_config(
    page_title="자료구조 놀이터",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.common import (
    apply_common_style,
    render_footer,
    render_html,
    render_page_header,
    render_section_title,
)

apply_common_style()

render_page_header(
    title="자료구조 놀이터",
    description=(
        "Stack, Queue, Binary Search Tree, Graph를 "
        "직접 조작하고 시각적으로 체험하는 자료구조 학습 웹앱입니다."
    ),
    icon="🧩",
)

render_section_title(
    "누구나 쉽게 체험하는 자료구조"
)

render_html(
    """
    <div class="concept-box">
        <div class="concept-title">
            코드를 몰라도 괜찮습니다!
        </div>

        <div class="concept-text">
            값을 직접 넣고 꺼내거나 탐색하면서
            자료구조가 작동하는 과정을 시각적으로 확인해 보세요.
        </div>
    </div>
    """
)

render_footer()