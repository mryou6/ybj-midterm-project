"""
Data Structure Playground에서 공통으로 사용하는 기능을 제공합니다.

주요 기능
- 프로젝트 경로 관리
- 공통 CSS 적용
- Noto Sans KR 폰트 적용
- HTML 안전 출력
- 세션 상태 초기화
- 공통 페이지 요소 출력
"""

import base64
import textwrap
from html import escape
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# 1. 프로젝트 경로 설정
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
STYLES_DIR = ASSETS_DIR / "styles"
IMAGES_DIR = ASSETS_DIR / "images"

FONTS_DIR = BASE_DIR / "fonts"
DATA_DIR = BASE_DIR / "data"
COMPONENTS_DIR = BASE_DIR / "components"


# ============================================================
# 2. 공통 HTML 출력
# ============================================================

def render_html(html_text: str) -> None:
    """
    들여쓰기를 제거한 HTML을 Streamlit 화면에 출력합니다.

    여러 줄 문자열 앞에 공백이 있으면 Streamlit이 HTML을
    코드 블록으로 해석할 수 있으므로 textwrap.dedent()를 사용합니다.
    """

    cleaned_html = textwrap.dedent(html_text).strip()

    st.markdown(
        cleaned_html,
        unsafe_allow_html=True
    )


# ============================================================
# 3. 파일 Base64 변환
# ============================================================

def file_to_base64(file_path: Path) -> str:
    """
    폰트나 이미지 파일을 Base64 문자열로 변환합니다.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"파일을 찾을 수 없습니다: {file_path}"
        )

    return base64.b64encode(
        file_path.read_bytes()
    ).decode("utf-8")


# ============================================================
# 4. Noto Sans KR 폰트 적용
# ============================================================

def load_fonts() -> None:
    """
    fonts 폴더에 있는 Noto Sans KR 폰트를 등록합니다.
    """

    font_settings = [
        ("NotoSansKR-Thin.ttf", 100),
        ("NotoSansKR-ExtraLight.ttf", 200),
        ("NotoSansKR-Light.ttf", 300),
        ("NotoSansKR-Regular.ttf", 400),
        ("NotoSansKR-Medium.ttf", 500),
        ("NotoSansKR-SemiBold.ttf", 600),
        ("NotoSansKR-Bold.ttf", 700),
        ("NotoSansKR-ExtraBold.ttf", 800),
        ("NotoSansKR-Black.ttf", 900),
    ]

    font_face_rules = []

    for file_name, font_weight in font_settings:
        font_path = FONTS_DIR / file_name

        if not font_path.exists():
            continue

        try:
            encoded_font = file_to_base64(font_path)

            font_face_rules.append(
                textwrap.dedent(
                    f"""
                    @font-face {{
                        font-family: "Noto Sans KR";
                        src: url(
                            data:font/ttf;base64,{encoded_font}
                        ) format("truetype");
                        font-weight: {font_weight};
                        font-style: normal;
                        font-display: swap;
                    }}
                    """
                ).strip()
            )

        except (OSError, ValueError):
            continue

    if not font_face_rules:
        return

    font_css = "\n".join(font_face_rules)

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
                sans-serif;
        }}
        </style>
        """
    )


# ============================================================
# 5. 공통 CSS 적용
# ============================================================

def load_css() -> None:
    """
    assets/styles/style.css를 읽어 적용합니다.
    """

    css_path = STYLES_DIR / "style.css"

    if not css_path.exists():
        st.warning(
            f"공통 스타일 파일을 찾지 못했습니다: {css_path}"
        )
        return

    try:
        css_text = css_path.read_text(
            encoding="utf-8"
        )

        render_html(
            f"""
            <style>
            {css_text}
            </style>
            """
        )

    except UnicodeDecodeError:
        st.error(
            "style.css 파일을 UTF-8 형식으로 읽을 수 없습니다."
        )

    except OSError as error:
        st.error(
            f"스타일 파일을 불러오는 중 오류가 발생했습니다: {error}"
        )


def apply_common_style() -> None:
    """
    폰트와 공통 CSS를 모두 적용합니다.
    """

    load_fonts()
    load_css()


# ============================================================
# 6. 세션 상태 초기화
# ============================================================

def initialize_session_state(
    key: str,
    default_value: Any
) -> None:
    """
    지정한 키가 Session State에 없으면 기본값을 저장합니다.
    """

    if key not in st.session_state:
        st.session_state[key] = default_value


def initialize_common_states() -> None:
    """
    앱 전체에서 공통으로 사용할 상태를 초기화합니다.
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
# 7. 공통 페이지 제목
# ============================================================

def render_page_header(
    title: str,
    description: str,
    icon: str = "🧩"
) -> None:
    """
    각 페이지의 제목 영역을 출력합니다.
    """

    safe_title = escape(title)
    safe_description = escape(description)
    safe_icon = escape(icon)

    render_html(
        f"""
        <div class="main-hero">
            <h1 class="main-hero-title">
                {safe_icon} {safe_title}
            </h1>

            <p class="main-hero-subtitle">
                {safe_description}
            </p>
        </div>
        """
    )


# ============================================================
# 8. 개념 설명 상자
# ============================================================

def render_concept_box(
    title: str,
    text: str
) -> None:
    """
    자료구조의 핵심 개념 설명 상자를 출력합니다.
    """

    safe_title = escape(title)
    safe_text = escape(text)

    render_html(
        f"""
        <div class="concept-box">
            <div class="concept-title">
                {safe_title}
            </div>

            <div class="concept-text">
                {safe_text}
            </div>
        </div>
        """
    )


# ============================================================
# 9. 공통 안내 메시지
# ============================================================

def render_message(
    message: str,
    message_type: str = "info",
    allow_html: bool = False
) -> None:
    """
    CSS가 적용된 공통 메시지 상자를 출력합니다.

    Args:
        message: 출력할 메시지
        message_type: info, success, warning, error
        allow_html: 메시지 내부 HTML 허용 여부
    """

    allowed_types = {
        "info",
        "success",
        "warning",
        "error"
    }

    if message_type not in allowed_types:
        message_type = "info"

    displayed_message = (
        message
        if allow_html
        else escape(message)
    )

    render_html(
        f"""
        <div class="{message_type}-box">
            {displayed_message}
        </div>
        """
    )


# ============================================================
# 10. 섹션 제목
# ============================================================

def render_section_title(title: str) -> None:
    """
    공통 섹션 제목을 출력합니다.
    """

    render_html(
        f"""
        <div class="section-title">
            {escape(title)}
        </div>
        """
    )


# ============================================================
# 11. 하단 문구
# ============================================================

def render_footer() -> None:
    """
    공통 하단 문구를 출력합니다.
    """

    render_html(
        """
        <div class="footer-note">
            Data Structure Playground<br>
            직접 조작하고 관찰하며 자료구조의 원리를 알아보세요.
        </div>
        """
    )