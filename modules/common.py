"""
Data Structure Playground에서 공통으로 사용하는 기능을 제공합니다.

주요 기능
- 프로젝트 경로 관리
- 공통 CSS 적용
- Noto Sans KR 폰트 적용
- 공통 페이지 설정
- 세션 상태 초기화
"""

import base64
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# 1. 프로젝트 경로 설정
# ============================================================

# common.py는 modules 폴더 안에 있으므로
# parent.parent를 사용하면 프로젝트의 최상위 폴더가 됩니다.
BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
STYLES_DIR = ASSETS_DIR / "styles"
IMAGES_DIR = ASSETS_DIR / "images"

FONTS_DIR = BASE_DIR / "fonts"
DATA_DIR = BASE_DIR / "data"
COMPONENTS_DIR = BASE_DIR / "components"


# ============================================================
# 2. 파일을 Base64 문자열로 변환
# ============================================================

def file_to_base64(file_path: Path) -> str:
    """
    폰트나 이미지 파일을 Base64 문자열로 변환합니다.

    Args:
        file_path: 변환할 파일 경로

    Returns:
        Base64로 인코딩된 문자열

    Raises:
        FileNotFoundError: 파일이 존재하지 않을 때
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"파일을 찾을 수 없습니다: {file_path}"
        )

    encoded_data = base64.b64encode(
        file_path.read_bytes()
    ).decode("utf-8")

    return encoded_data


# ============================================================
# 3. Noto Sans KR 폰트 적용
# ============================================================

def load_fonts() -> None:
    """
    fonts 폴더의 Noto Sans KR 폰트를 Streamlit에 적용합니다.

    폰트 파일을 Base64로 변환하므로 로컬 환경뿐만 아니라
    Streamlit Cloud에서도 동일하게 적용할 수 있습니다.
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
            )

        except (OSError, ValueError):
            continue

    if not font_face_rules:
        return

    font_css = "\n".join(font_face_rules)

    st.markdown(
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
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 4. 공통 CSS 적용
# ============================================================

def load_css() -> None:
    """
    assets/styles/style.css 파일을 읽어 Streamlit에 적용합니다.
    """

    css_path = STYLES_DIR / "style.css"

    if not css_path.exists():
        st.warning(
            "공통 스타일 파일을 찾지 못했습니다: "
            f"{css_path}"
        )
        return

    try:
        css_text = css_path.read_text(
            encoding="utf-8"
        )

        st.markdown(
            f"<style>{css_text}</style>",
            unsafe_allow_html=True
        )

    except UnicodeDecodeError:
        st.error(
            "style.css 파일을 UTF-8 형식으로 읽을 수 없습니다."
        )

    except OSError as error:
        st.error(
            f"스타일 파일을 불러오는 중 오류가 발생했습니다: {error}"
        )


# ============================================================
# 5. 공통 디자인 적용
# ============================================================

def apply_common_style() -> None:
    """
    모든 Streamlit 페이지에 폰트와 CSS를 적용합니다.

    각 페이지에서 다음과 같이 호출합니다.

    apply_common_style()
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
    지정한 키가 세션 상태에 없으면 기본값을 저장합니다.

    Args:
        key: 세션 상태 키
        default_value: 처음 사용할 기본값
    """

    if key not in st.session_state:
        st.session_state[key] = default_value


def initialize_common_states() -> None:
    """
    앱 전체에서 공통으로 사용할 세션 상태를 초기화합니다.
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
    각 자료구조 페이지의 공통 제목 영역을 출력합니다.

    Args:
        title: 페이지 제목
        description: 페이지 설명
        icon: 제목 앞에 표시할 이모지
    """

    st.markdown(
        f"""
        <div class="main-hero">
            <h1 class="main-hero-title">
                {icon} {title}
            </h1>

            <p class="main-hero-subtitle">
                {description}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 8. 공통 개념 설명 상자
# ============================================================

def render_concept_box(
    title: str,
    text: str
) -> None:
    """
    자료구조의 핵심 개념을 설명하는 상자를 출력합니다.
    """

    st.markdown(
        f"""
        <div class="concept-box">
            <div class="concept-title">
                {title}
            </div>

            <p class="concept-text">
                {text}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 9. 공통 안내 메시지
# ============================================================

def render_message(
    message: str,
    message_type: str = "info"
) -> None:
    """
    CSS가 적용된 공통 메시지 상자를 출력합니다.

    message_type
    - info
    - success
    - warning
    - error
    """

    allowed_types = {
        "info",
        "success",
        "warning",
        "error"
    }

    if message_type not in allowed_types:
        message_type = "info"

    st.markdown(
        f"""
        <div class="{message_type}-box">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 10. 공통 하단 문구
# ============================================================

def render_footer() -> None:
    """
    각 페이지 아래에 공통 안내 문구를 출력합니다.
    """

    st.markdown(
        """
        <div class="footer-note">
            Data Structure Playground<br>
            직접 조작하고 관찰하며 자료구조의 원리를 알아보세요.
        </div>
        """,
        unsafe_allow_html=True
    )