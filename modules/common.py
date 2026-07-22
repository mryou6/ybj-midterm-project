"""
Data Structure Playground에서 공통으로 사용하는 기능을 제공합니다.

주요 기능
- 프로젝트 경로 관리
- 공통 CSS 적용
- Noto Sans KR 폰트 적용
- HTML 출력
- 세션 상태 초기화
- 공통 화면 요소 출력
"""

import base64
import textwrap
from html import escape
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# 1. 프로젝트 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
STYLES_DIR = ASSETS_DIR / "styles"
IMAGES_DIR = ASSETS_DIR / "images"

FONTS_DIR = BASE_DIR / "fonts"
DATA_DIR = BASE_DIR / "data"
COMPONENTS_DIR = BASE_DIR / "components"


# ============================================================
# 2. HTML 출력
# ============================================================

def render_html(html_text: str) -> None:
    """
    입력한 문자열을 Markdown이 아닌 순수 HTML로 출력합니다.

    st.markdown()을 사용하면 중첩된 div, p, span 태그가
    Markdown 코드 블록으로 해석될 수 있으므로 st.html()을 사용합니다.
    """

    cleaned_html = textwrap.dedent(html_text).strip()

    if not cleaned_html:
        return

    st.html(cleaned_html)


# ============================================================
# 3. 파일 Base64 변환
# ============================================================

def file_to_base64(file_path: Path) -> str:
    """
    파일을 Base64 문자열로 변환합니다.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"파일을 찾을 수 없습니다: {file_path}"
        )

    return base64.b64encode(
        file_path.read_bytes()
    ).decode("utf-8")


# ============================================================
# 4. 폰트 적용
# ============================================================

def load_fonts() -> None:
    """
    프로젝트의 Noto Sans KR 폰트를 웹앱에 적용합니다.

    용량과 실행 속도를 고려하여 자주 사용하는
    Regular, SemiBold, Bold, ExtraBold만 등록합니다.
    """

    font_settings = [
        ("NotoSansKR-Regular.ttf", 400),
        ("NotoSansKR-SemiBold.ttf", 600),
        ("NotoSansKR-Bold.ttf", 700),
        ("NotoSansKR-ExtraBold.ttf", 800),
    ]

    font_rules = []

    for file_name, font_weight in font_settings:
        font_path = FONTS_DIR / file_name

        if not font_path.exists():
            continue

        try:
            encoded_font = file_to_base64(font_path)

            font_rules.append(
                f"""
                @font-face {{
                    font-family: "Noto Sans KR";
                    src: url("data:font/ttf;base64,{encoded_font}")
                        format("truetype");
                    font-style: normal;
                    font-weight: {font_weight};
                    font-display: swap;
                }}
                """
            )

        except (OSError, ValueError):
            continue

    if not font_rules:
        return

    font_css = "\n".join(font_rules)

    render_html(
        f"""
        <style>
        {font_css}

        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"],
        button,
        input,
        textarea,
        select {{
            font-family:
                "Noto Sans KR",
                "Malgun Gothic",
                sans-serif !important;
        }}
        </style>
        """
    )


# ============================================================
# 5. CSS 적용
# ============================================================

def load_css() -> None:
    """
    assets/styles/style.css를 적용합니다.
    """

    css_path = STYLES_DIR / "style.css"

    if not css_path.exists():
        st.warning(
            f"공통 스타일 파일을 찾지 못했습니다: {css_path}"
        )
        return

    try:
        # st.html은 CSS 파일 경로를 전달하면
        # 자동으로 style 태그를 적용합니다.
        st.html(css_path)

    except OSError as error:
        st.error(
            f"스타일 파일을 불러오는 중 오류가 발생했습니다: {error}"
        )


def apply_common_style() -> None:
    """
    공통 폰트와 CSS를 적용합니다.
    """

    load_fonts()
    load_css()


# ============================================================
# 6. Session State 초기화
# ============================================================

def initialize_session_state(
    key: str,
    default_value: Any
) -> None:
    """
    Session State에 키가 없으면 기본값을 저장합니다.
    """

    if key not in st.session_state:
        st.session_state[key] = default_value


def initialize_common_states() -> None:
    """
    앱 전체의 공통 상태를 초기화합니다.
    """

    initialize_session_state(
        "current_structure",
        None
    )

    initialize_session_state(
        "activity_count",
        0
    )


# ============================================================
# 7. 페이지 제목
# ============================================================

def render_page_header(
    title: str,
    description: str,
    icon: str = "🧩"
) -> None:
    """
    페이지의 상단 제목 영역을 출력합니다.
    """

    safe_title = escape(str(title))
    safe_description = escape(str(description))
    safe_icon = escape(str(icon))

    render_html(
        f"""
        <section class="main-hero">
            <h1 class="main-hero-title">
                {safe_icon} {safe_title}
            </h1>

            <div class="main-hero-subtitle">
                {safe_description}
            </div>
        </section>
        """
    )


# ============================================================
# 8. 섹션 제목
# ============================================================

def render_section_title(title: str) -> None:
    """
    공통 섹션 제목을 출력합니다.
    """

    render_html(
        f"""
        <h2 class="section-title">
            {escape(str(title))}
        </h2>
        """
    )


# ============================================================
# 9. 개념 설명 상자
# ============================================================

def render_concept_box(
    title: str,
    text: str
) -> None:
    """
    자료구조 개념 설명 상자를 출력합니다.
    """

    safe_title = escape(str(title))
    safe_text = escape(str(text))

    render_html(
        f"""
        <section class="concept-box">
            <div class="concept-title">
                {safe_title}
            </div>

            <div class="concept-text">
                {safe_text}
            </div>
        </section>
        """
    )


# ============================================================
# 10. 안내 메시지
# ============================================================

def render_message(
    message: str,
    message_type: str = "info",
    allow_html: bool = False
) -> None:
    """
    공통 메시지 상자를 출력합니다.

    message_type:
    - info
    - success
    - warning
    - error
    """

    allowed_types = {
        "info",
        "success",
        "warning",
        "error",
    }

    if message_type not in allowed_types:
        message_type = "info"

    displayed_message = (
        message
        if allow_html
        else escape(str(message))
    )

    render_html(
        f"""
        <div class="{message_type}-box">
            {displayed_message}
        </div>
        """
    )


# ============================================================
# 11. 하단 문구
# ============================================================

def render_footer() -> None:
    """
    페이지 하단 공통 안내 문구를 출력합니다.
    """

    render_html(
        """
        <footer class="footer-note">
            Data Structure Playground<br>
            직접 조작하고 관찰하며 자료구조의 원리를 알아보세요.
        </footer>
        """
    )