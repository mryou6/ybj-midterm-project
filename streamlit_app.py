import streamlit as st

from modules.common import (
    apply_common_style,
    render_concept_box,
    render_footer,
    render_message,
    render_page_header,
)


st.set_page_config(
    page_title="Data Structure Playground",
    page_icon="🧩",
    layout="wide"
)

apply_common_style()

render_page_header(
    title="자료구조 놀이터",
    description=(
        "코드를 몰라도 괜찮습니다. "
        "직접 조작하며 자료구조의 원리를 체험해 보세요."
    ),
    icon="🎡"
)

render_concept_box(
    title="자료구조란 무엇인가요?",
    text=(
        "자료구조는 컴퓨터가 데이터를 효율적으로 "
        "저장하고 처리하기 위해 사용하는 정리 방법입니다."
    )
)

render_message(
    "공통 CSS와 Noto Sans KR 폰트가 정상적으로 적용되었습니다.",
    "success"
)

render_footer()