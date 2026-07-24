"""
자료구조 종합 형성평가 결과를 분석하는 교사용 대시보드입니다.

주요 기능
- CSV 평가 결과 불러오기
- 학년·반·응시 차수 필터링
- 전체 응시 현황 요약
- 영역별 평균 정답률 시각화
- 학생별 총점 비교
- 성취 수준 분포
- 오답 개념 빈도 분석
- 학생 개인별 상세 결과 확인
- 전체 기록과 최신 응시 기록 전환
- 필터링된 결과 CSV 다운로드
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from modules.common import (
    apply_common_style,
    render_concept_box,
    render_footer,
    render_html,
    render_page_header,
    render_section_title,
)


# ============================================================
# 1. 페이지 설정
# ============================================================

st.set_page_config(
    page_title="형성평가 결과 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_common_style()


# ============================================================
# 2. 기본 경로 및 상수
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

RESULT_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "formative_results.csv"
)

STUDENT_KEY_COLUMNS = [
    "student_grade",
    "student_class",
    "student_number",
    "student_name",
]

DOMAIN_CONFIG = {
    "Stack": {
        "score": "stack_score",
        "total": "stack_total",
    },
    "Queue": {
        "score": "queue_score",
        "total": "queue_total",
    },
    "Tree": {
        "score": "tree_score",
        "total": "tree_total",
    },
    "Graph": {
        "score": "graph_score",
        "total": "graph_total",
    },
}

REQUIRED_COLUMNS = [
    "submitted_at",
    "student_grade",
    "student_class",
    "student_number",
    "student_name",
    "attempt",
    "total_score",
    "total_questions",
    "percentage",
    "achievement_level",
    "stack_score",
    "stack_total",
    "queue_score",
    "queue_total",
    "tree_score",
    "tree_total",
    "graph_score",
    "graph_total",
    "incorrect_concepts",
    "question_ids",
    "student_answers",
    "correct_answers",
    "incorrect_question_ids",
]

NUMERIC_COLUMNS = [
    "student_grade",
    "student_class",
    "student_number",
    "attempt",
    "total_score",
    "total_questions",
    "percentage",
    "stack_score",
    "stack_total",
    "queue_score",
    "queue_total",
    "tree_score",
    "tree_total",
    "graph_score",
    "graph_total",
]

ACHIEVEMENT_ORDER = [
    "A",
    "B",
    "C",
    "D",
    "E",
]

ACHIEVEMENT_LABELS = {
    "A": "A · 개념 이해 우수",
    "B": "B · 개념 이해 양호",
    "C": "C · 기본 개념 이해",
    "D": "D · 일부 개념 보완 필요",
    "E": "E · 기초 개념 재학습 필요",
}

CONCEPT_KOREAN_LABELS = {
    "LIFO": "LIFO",
    "Push": "Push 연산",
    "Pop": "Pop 연산",
    "TOP": "Stack의 TOP",
    "Stack operation": "Stack 연산",
    "Stack trace": "Stack 실행 추적",
    "Bracket checking": "괄호 검사",
    "Postfix notation": "후위 표기법",
    "Postfix operand order": "후위 표기법 피연산자 순서",
    "FIFO": "FIFO",
    "Enqueue": "Enqueue 연산",
    "Dequeue": "Dequeue 연산",
    "Queue operation": "Queue 연산",
    "FRONT and REAR": "Queue의 FRONT와 REAR",
    "Linear queue limitation": "선형 Queue의 한계",
    "Circular queue empty condition": "원형 Queue의 공백 조건",
    "Circular queue full condition": "원형 Queue의 포화 조건",
    "Circular movement": "원형 Queue의 인덱스 이동",
    "Circular queue capacity": "원형 Queue의 실제 용량",
    "Root node": "루트 노드",
    "Leaf node": "단말 노드",
    "Binary tree": "이진 트리",
    "Preorder traversal": "전위 순회",
    "Inorder traversal": "중위 순회",
    "Postorder traversal": "후위 순회",
    "BST insertion": "이진 탐색 트리 삽입",
    "BST inorder": "이진 탐색 트리 중위 순회",
    "BST trace": "이진 탐색 트리 실행 추적",
    "Vertex": "정점",
    "Edge": "간선",
    "Undirected graph": "무방향 Graph",
    "Adjacency matrix": "인접 행렬",
    "Adjacency matrix symmetry": "인접 행렬의 대칭성",
    "Adjacency list": "인접 리스트",
    "DFS": "깊이 우선 탐색",
    "BFS": "너비 우선 탐색",
    "DFS data structure": "DFS에서 사용하는 자료구조",
    "BFS data structure": "BFS에서 사용하는 자료구조",
}


# ============================================================
# 3. 데이터 불러오기 및 전처리
# ============================================================

@st.cache_data(
    show_spinner=False,
)
def load_result_data(
    file_path: str,
    modified_time: float,
) -> tuple[pd.DataFrame, str | None]:
    """
    평가 결과 CSV를 불러오고 기본 형식을 정리합니다.

    modified_time은 CSV 파일이 변경될 때 캐시를 갱신하기 위해
    함수 매개변수로 전달합니다.
    """

    del modified_time

    path = Path(
        file_path
    )

    if not path.exists():
        return (
            pd.DataFrame(),
            "평가 결과 CSV 파일이 없습니다.",
        )

    if path.stat().st_size == 0:
        return (
            pd.DataFrame(),
            None,
        )

    try:
        dataframe = pd.read_csv(
            path,
            encoding="utf-8-sig",
        )

    except pd.errors.EmptyDataError:
        return (
            pd.DataFrame(),
            None,
        )

    except UnicodeDecodeError:
        try:
            dataframe = pd.read_csv(
                path,
                encoding="utf-8",
            )

        except Exception as error:
            return (
                pd.DataFrame(),
                f"CSV 인코딩을 확인하지 못했습니다: {error}",
            )

    except Exception as error:
        return (
            pd.DataFrame(),
            f"평가 결과 CSV를 읽는 중 오류가 발생했습니다: {error}",
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        return (
            pd.DataFrame(),
            (
                "CSV에 필요한 열이 없습니다: "
                + ", ".join(
                    missing_columns
                )
            ),
        )

    dataframe = dataframe.copy()

    for column in NUMERIC_COLUMNS:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    integer_columns = [
        column
        for column in NUMERIC_COLUMNS
        if column != "percentage"
    ]

    for column in integer_columns:
        dataframe[column] = (
            dataframe[column]
            .fillna(0)
            .astype(int)
        )

    dataframe["percentage"] = (
        dataframe["percentage"]
        .fillna(0.0)
        .astype(float)
        .clip(
            lower=0,
            upper=100,
        )
    )

    dataframe["submitted_at"] = pd.to_datetime(
        dataframe["submitted_at"],
        errors="coerce",
    )

    text_columns = [
        "student_name",
        "achievement_level",
        "incorrect_concepts",
        "question_ids",
        "student_answers",
        "correct_answers",
        "incorrect_question_ids",
    ]

    for column in text_columns:
        dataframe[column] = (
            dataframe[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    dataframe["student_name"] = (
        dataframe["student_name"]
        .replace(
            "",
            "이름 없음",
        )
    )

    dataframe["student_key"] = (
        dataframe["student_grade"].astype(str)
        + "-"
        + dataframe["student_class"].astype(str)
        + "-"
        + dataframe["student_number"].astype(str)
        + "-"
        + dataframe["student_name"]
    )

    dataframe["student_label"] = (
        dataframe["student_grade"].astype(str)
        + "학년 "
        + dataframe["student_class"].astype(str)
        + "반 "
        + dataframe["student_number"].astype(str)
        + "번 "
        + dataframe["student_name"]
    )

    dataframe["submitted_at_text"] = (
        dataframe["submitted_at"]
        .dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        .fillna("-")
    )

    return (
        dataframe,
        None,
    )


def get_latest_attempts(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    학생별 가장 최근 응시 결과만 반환합니다.

    응시 차수가 높은 기록을 우선하며, 차수가 같으면
    제출 시각이 늦은 기록을 사용합니다.
    """

    if dataframe.empty:
        return dataframe.copy()

    sorted_dataframe = dataframe.sort_values(
        by=[
            "student_key",
            "attempt",
            "submitted_at",
        ],
        ascending=[
            True,
            True,
            True,
        ],
        na_position="first",
    )

    latest_dataframe = (
        sorted_dataframe
        .drop_duplicates(
            subset=[
                "student_key",
            ],
            keep="last",
        )
        .reset_index(
            drop=True
        )
    )

    return latest_dataframe


def safe_percentage(
    score: Any,
    total: Any,
) -> float:
    """
    정답 수와 문항 수로 정답률을 계산합니다.
    """

    try:
        score_value = float(
            score
        )
        total_value = float(
            total
        )

    except (TypeError, ValueError):
        return 0.0

    if total_value <= 0:
        return 0.0

    return round(
        score_value
        / total_value
        * 100,
        1,
    )


def translate_concept(
    concept: str,
) -> str:
    """
    JSON에 저장된 영어 개념명을 한글 표시명으로 변환합니다.
    """

    cleaned_concept = str(
        concept
    ).strip()

    if not cleaned_concept:
        return ""

    return CONCEPT_KOREAN_LABELS.get(
        cleaned_concept,
        cleaned_concept,
    )


def explode_incorrect_concepts(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    incorrect_concepts 열의 | 구분 데이터를 행 단위로 분리합니다.
    """

    if (
        dataframe.empty
        or "incorrect_concepts"
        not in dataframe.columns
    ):
        return pd.DataFrame(
            columns=[
                "concept",
                "concept_label",
                "student_key",
                "student_label",
            ]
        )

    rows: list[
        dict[str, Any]
    ] = []

    for _, row in dataframe.iterrows():
        raw_concepts = str(
            row.get(
                "incorrect_concepts",
                "",
            )
        ).strip()

        if not raw_concepts:
            continue

        concepts = [
            concept.strip()
            for concept in raw_concepts.split(
                "|"
            )
            if concept.strip()
        ]

        for concept in concepts:
            rows.append(
                {
                    "concept": concept,
                    "concept_label": translate_concept(
                        concept
                    ),
                    "student_key": row.get(
                        "student_key",
                        "",
                    ),
                    "student_label": row.get(
                        "student_label",
                        "",
                    ),
                }
            )

    return pd.DataFrame(
        rows
    )


def calculate_domain_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    영역별 총 정답 수와 총 문항 수를 이용해 평균 정답률을 계산합니다.

    학생별 백분율의 단순 평균이 아니라 전체 정답 수를
    전체 출제 문항 수로 나누어 계산합니다.
    """

    rows: list[
        dict[str, Any]
    ] = []

    for domain, columns in DOMAIN_CONFIG.items():
        score_sum = dataframe[
            columns["score"]
        ].sum()

        total_sum = dataframe[
            columns["total"]
        ].sum()

        percentage = safe_percentage(
            score_sum,
            total_sum,
        )

        rows.append(
            {
                "영역": domain,
                "정답 수": int(
                    score_sum
                ),
                "문항 수": int(
                    total_sum
                ),
                "평균 정답률": percentage,
            }
        )

    return pd.DataFrame(
        rows
    )


def calculate_student_domain_profile(
    student_row: pd.Series,
) -> pd.DataFrame:
    """
    학생 한 명의 영역별 정답률을 계산합니다.
    """

    rows: list[
        dict[str, Any]
    ] = []

    for domain, columns in DOMAIN_CONFIG.items():
        score = int(
            student_row.get(
                columns["score"],
                0,
            )
        )

        total = int(
            student_row.get(
                columns["total"],
                0,
            )
        )

        rows.append(
            {
                "영역": domain,
                "정답 수": score,
                "문항 수": total,
                "정답률": safe_percentage(
                    score,
                    total,
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


def build_student_result_table(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    교사용 학생별 결과 표를 생성합니다.
    """

    result_table = pd.DataFrame(
        {
            "학년": dataframe[
                "student_grade"
            ],
            "반": dataframe[
                "student_class"
            ],
            "번호": dataframe[
                "student_number"
            ],
            "이름": dataframe[
                "student_name"
            ],
            "응시 차수": dataframe[
                "attempt"
            ],
            "총점": dataframe[
                "total_score"
            ],
            "전체 문항": dataframe[
                "total_questions"
            ],
            "정답률": dataframe[
                "percentage"
            ],
            "성취 수준": dataframe[
                "achievement_level"
            ],
            "Stack": (
                dataframe["stack_score"].astype(str)
                + "/"
                + dataframe["stack_total"].astype(str)
            ),
            "Queue": (
                dataframe["queue_score"].astype(str)
                + "/"
                + dataframe["queue_total"].astype(str)
            ),
            "Tree": (
                dataframe["tree_score"].astype(str)
                + "/"
                + dataframe["tree_total"].astype(str)
            ),
            "Graph": (
                dataframe["graph_score"].astype(str)
                + "/"
                + dataframe["graph_total"].astype(str)
            ),
            "제출 일시": dataframe[
                "submitted_at_text"
            ],
        }
    )

    return (
        result_table
        .sort_values(
            by=[
                "학년",
                "반",
                "번호",
                "응시 차수",
            ]
        )
        .reset_index(
            drop=True
        )
    )


def dataframe_to_csv_bytes(
    dataframe: pd.DataFrame,
) -> bytes:
    """
    DataFrame을 Excel에서 열기 좋은 UTF-8 BOM CSV로 변환합니다.
    """

    csv_text = dataframe.to_csv(
        index=False,
        encoding="utf-8-sig",
    )

    return (
        "\ufeff"
        + csv_text
    ).encode(
        "utf-8"
    )


# ============================================================
# 4. 시각화 함수
# ============================================================

def render_metric_summary(
    dataframe: pd.DataFrame,
) -> None:
    """
    전체 평가 핵심 지표를 표시합니다.
    """

    unique_student_count = dataframe[
        "student_key"
    ].nunique()

    submission_count = len(
        dataframe
    )

    average_percentage = (
        dataframe["percentage"].mean()
        if not dataframe.empty
        else 0.0
    )

    relearning_count = dataframe.loc[
        dataframe["percentage"] < 60,
        "student_key",
    ].nunique()

    metric_col1, metric_col2, metric_col3, metric_col4 = (
        st.columns(
            4
        )
    )

    with metric_col1:
        st.metric(
            "응시 학생 수",
            f"{unique_student_count}명",
        )

    with metric_col2:
        st.metric(
            "분석 기록 수",
            f"{submission_count}건",
        )

    with metric_col3:
        st.metric(
            "평균 정답률",
            f"{average_percentage:.1f}%",
        )

    with metric_col4:
        st.metric(
            "기초 재학습 필요",
            f"{relearning_count}명",
            help="정답률 60% 미만인 학생 수입니다.",
        )


def render_domain_chart(
    domain_summary: pd.DataFrame,
) -> None:
    """
    영역별 평균 정답률 막대그래프를 표시합니다.
    """

    if domain_summary.empty:
        st.info(
            "영역별 분석 데이터가 없습니다."
        )
        return

    chart_data = (
        domain_summary[
            [
                "영역",
                "평균 정답률",
            ]
        ]
        .set_index(
            "영역"
        )
    )

    st.bar_chart(
        chart_data,
        y="평균 정답률",
        horizontal=True,
        height=320,
        use_container_width=True,
    )

    display_table = domain_summary.copy()

    st.dataframe(
        display_table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "영역": st.column_config.TextColumn(
                "영역",
                width="medium",
            ),
            "정답 수": st.column_config.NumberColumn(
                "전체 정답 수",
                format="%d",
            ),
            "문항 수": st.column_config.NumberColumn(
                "전체 출제 문항",
                format="%d",
            ),
            "평균 정답률": st.column_config.ProgressColumn(
                "평균 정답률",
                min_value=0,
                max_value=100,
                format="%.1f%%",
            ),
        },
    )


def render_student_score_chart(
    dataframe: pd.DataFrame,
) -> None:
    """
    학생별 정답률 비교 막대그래프를 표시합니다.
    """

    if dataframe.empty:
        st.info(
            "학생별 분석 데이터가 없습니다."
        )
        return

    student_scores = (
        dataframe[
            [
                "student_label",
                "percentage",
            ]
        ]
        .sort_values(
            by="percentage",
            ascending=True,
        )
        .set_index(
            "student_label"
        )
    )

    chart_height = max(
        320,
        min(
            900,
            len(
                student_scores
            )
            * 38,
        ),
    )

    st.bar_chart(
        student_scores,
        y="percentage",
        horizontal=True,
        height=chart_height,
        use_container_width=True,
    )


def render_achievement_chart(
    dataframe: pd.DataFrame,
) -> None:
    """
    성취 수준별 학생 수를 막대그래프로 표시합니다.
    """

    achievement_counts = (
        dataframe[
            "achievement_level"
        ]
        .value_counts()
        .reindex(
            ACHIEVEMENT_ORDER,
            fill_value=0,
        )
        .rename_axis(
            "성취 수준"
        )
        .reset_index(
            name="학생 수"
        )
    )

    achievement_counts[
        "성취 수준"
    ] = achievement_counts[
        "성취 수준"
    ].map(
        lambda level: ACHIEVEMENT_LABELS.get(
            level,
            level,
        )
    )

    chart_data = achievement_counts.set_index(
        "성취 수준"
    )

    st.bar_chart(
        chart_data,
        y="학생 수",
        horizontal=True,
        height=320,
        use_container_width=True,
    )


def render_incorrect_concept_chart(
    dataframe: pd.DataFrame,
    top_n: int,
) -> None:
    """
    오답 개념 빈도를 가로 막대그래프로 표시합니다.
    """

    concept_dataframe = explode_incorrect_concepts(
        dataframe
    )

    if concept_dataframe.empty:
        st.success(
            "선택된 결과에는 오답 개념이 없습니다."
        )
        return

    concept_counts = (
        concept_dataframe[
            "concept_label"
        ]
        .value_counts()
        .rename_axis(
            "오답 개념"
        )
        .reset_index(
            name="오답 횟수",
        )
    )

    concept_student_counts = (
        concept_dataframe
        .groupby(
            "concept_label"
        )[
            "student_key"
        ]
        .nunique()
        .rename(
            "오답 학생 수"
        )
        .reset_index()
        .rename(
            columns={
                "concept_label": "오답 개념",
            }
        )
    )

    concept_summary = concept_counts.merge(
        concept_student_counts,
        on="오답 개념",
        how="left",
    )

    concept_summary = (
        concept_summary
        .head(
            top_n
        )
        .sort_values(
            by="오답 횟수",
            ascending=True,
        )
    )

    chart_data = (
        concept_summary[
            [
                "오답 개념",
                "오답 횟수",
            ]
        ]
        .set_index(
            "오답 개념"
        )
    )

    chart_height = max(
        320,
        len(
            concept_summary
        )
        * 45,
    )

    st.bar_chart(
        chart_data,
        y="오답 횟수",
        horizontal=True,
        height=chart_height,
        use_container_width=True,
    )

    concept_summary = concept_summary.sort_values(
        by=[
            "오답 횟수",
            "오답 학생 수",
        ],
        ascending=[
            False,
            False,
        ],
    )

    st.dataframe(
        concept_summary,
        hide_index=True,
        use_container_width=True,
        column_config={
            "오답 개념": st.column_config.TextColumn(
                "오답 개념",
                width="large",
            ),
            "오답 횟수": st.column_config.NumberColumn(
                "오답 횟수",
                format="%d회",
            ),
            "오답 학생 수": st.column_config.NumberColumn(
                "오답 학생 수",
                format="%d명",
            ),
        },
    )


def render_student_detail(
    dataframe: pd.DataFrame,
) -> None:
    """
    선택한 학생의 개별 평가 결과를 표시합니다.
    """

    if dataframe.empty:
        st.info(
            "표시할 학생 데이터가 없습니다."
        )
        return

    student_options = (
        dataframe[
            [
                "student_key",
                "student_label",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            by="student_label"
        )
    )

    student_label_map = dict(
        zip(
            student_options[
                "student_key"
            ],
            student_options[
                "student_label"
            ],
        )
    )

    selected_student_key = st.selectbox(
        "학생 선택",
        options=list(
            student_label_map.keys()
        ),
        format_func=lambda key: student_label_map[
            key
        ],
        key="dashboard_selected_student",
    )

    student_records = (
        dataframe.loc[
            dataframe[
                "student_key"
            ]
            == selected_student_key
        ]
        .sort_values(
            by=[
                "attempt",
                "submitted_at",
            ],
            ascending=[
                False,
                False,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    if student_records.empty:
        st.warning(
            "선택한 학생의 평가 기록을 찾을 수 없습니다."
        )
        return

    attempt_options = list(
        student_records.index
    )

    selected_record_index = st.selectbox(
        "응시 기록 선택",
        options=attempt_options,
        format_func=lambda index: (
            f"{int(student_records.loc[index, 'attempt'])}차 평가"
            f" · {student_records.loc[index, 'submitted_at_text']}"
            f" · {student_records.loc[index, 'percentage']:.1f}%"
        ),
        key="dashboard_selected_attempt",
    )

    selected_record = student_records.loc[
        selected_record_index
    ]

    student_name = selected_record[
        "student_name"
    ]

    st.markdown(
        f"#### {student_name} 학생의 평가 결과"
    )

    detail_col1, detail_col2, detail_col3, detail_col4 = (
        st.columns(
            4
        )
    )

    with detail_col1:
        st.metric(
            "총점",
            (
                f"{int(selected_record['total_score'])}"
                f" / {int(selected_record['total_questions'])}"
            ),
        )

    with detail_col2:
        st.metric(
            "정답률",
            f"{selected_record['percentage']:.1f}%",
        )

    with detail_col3:
        st.metric(
            "성취 수준",
            selected_record[
                "achievement_level"
            ],
        )

    with detail_col4:
        st.metric(
            "응시 차수",
            f"{int(selected_record['attempt'])}차",
        )

    profile_dataframe = calculate_student_domain_profile(
        selected_record
    )

    profile_col1, profile_col2 = st.columns(
        [
            1.3,
            1,
        ]
    )

    with profile_col1:
        st.markdown(
            "##### 영역별 정답률"
        )

        profile_chart_data = (
            profile_dataframe[
                [
                    "영역",
                    "정답률",
                ]
            ]
            .set_index(
                "영역"
            )
        )

        st.bar_chart(
            profile_chart_data,
            y="정답률",
            horizontal=True,
            height=300,
            use_container_width=True,
        )

    with profile_col2:
        st.markdown(
            "##### 영역별 상세 점수"
        )

        st.dataframe(
            profile_dataframe,
            hide_index=True,
            use_container_width=True,
            column_config={
                "영역": st.column_config.TextColumn(
                    "영역",
                ),
                "정답 수": st.column_config.NumberColumn(
                    "정답 수",
                    format="%d",
                ),
                "문항 수": st.column_config.NumberColumn(
                    "문항 수",
                    format="%d",
                ),
                "정답률": st.column_config.ProgressColumn(
                    "정답률",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%",
                ),
            },
        )

    raw_incorrect_concepts = str(
        selected_record[
            "incorrect_concepts"
        ]
    ).strip()

    if raw_incorrect_concepts:
        concepts = [
            translate_concept(
                concept
            )
            for concept in raw_incorrect_concepts.split(
                "|"
            )
            if concept.strip()
        ]

        concept_badges = "".join(
            f"""
            <span class="dashboard-concept-badge">
                {concept}
            </span>
            """
            for concept in concepts
        )

        render_html(
            f"""
            <style>
                .dashboard-concept-panel {{
                    padding: 18px;
                    margin-top: 10px;
                    border: 1px solid #ead9c5;
                    border-radius: 14px;
                    background: #fff9ef;
                }}

                .dashboard-concept-title {{
                    margin-bottom: 12px;
                    color: #76501a;
                    font-weight: 800;
                }}

                .dashboard-concept-list {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                }}

                .dashboard-concept-badge {{
                    display: inline-block;
                    padding: 6px 11px;
                    border: 1px solid #eadbc8;
                    border-radius: 999px;
                    background: #ffffff;
                    color: #72501f;
                    font-size: 13px;
                    font-weight: 700;
                }}
            </style>

            <section class="dashboard-concept-panel">
                <div class="dashboard-concept-title">
                    📌 보완이 필요한 개념
                </div>

                <div class="dashboard-concept-list">
                    {concept_badges}
                </div>
            </section>
            """
        )

    else:
        st.success(
            "이 평가 기록에서는 보완이 필요한 오답 개념이 없습니다."
        )

    if len(
        student_records
    ) >= 2:
        st.markdown(
            "##### 응시 차수별 정답률 변화"
        )

        progress_dataframe = (
            student_records[
                [
                    "attempt",
                    "percentage",
                ]
            ]
            .sort_values(
                by="attempt"
            )
            .rename(
                columns={
                    "attempt": "응시 차수",
                    "percentage": "정답률",
                }
            )
        )

        progress_dataframe[
            "응시 차수"
        ] = (
            progress_dataframe[
                "응시 차수"
            ]
            .astype(str)
            + "차"
        )

        progress_chart_data = (
            progress_dataframe
            .set_index(
                "응시 차수"
            )
        )

        st.line_chart(
            progress_chart_data,
            y="정답률",
            height=300,
            use_container_width=True,
        )


# ============================================================
# 5. 페이지 상단
# ============================================================

render_page_header(
    title="형성평가 결과 대시보드",
    description=(
        "학생들의 자료구조 형성평가 결과를 학급 전체와 "
        "개인 측면에서 분석합니다."
    ),
    icon="📊",
)

render_concept_box(
    title="CSV는 저장소, 대시보드는 분석 화면입니다.",
    text=(
        "학생이 제출한 평가 결과는 CSV에 누적하고, 이 페이지에서는 "
        "CSV를 자동으로 읽어 전체 성취도, 영역별 정답률, 오답 개념, "
        "학생별 학습 상태를 표와 그래프로 보여줍니다."
    ),
)


# ============================================================
# 6. CSV 불러오기
# ============================================================

file_modified_time = (
    RESULT_CSV_PATH.stat().st_mtime
    if RESULT_CSV_PATH.exists()
    else 0.0
)

result_dataframe, load_error = load_result_data(
    str(
        RESULT_CSV_PATH
    ),
    file_modified_time,
)


# ============================================================
# 7. 불러오기 오류 및 빈 데이터 처리
# ============================================================

if load_error:
    render_section_title(
        "평가 결과 파일 확인"
    )

    st.error(
        load_error
    )

    st.code(
        str(
            RESULT_CSV_PATH
        ),
        language="text",
    )

    st.info(
        "results/formative_results.csv 파일과 "
        "RESULT_CSV_HEADERS 구조를 확인해 주세요."
    )

    if st.button(
        "🔄 다시 불러오기",
        key="reload_dashboard_error",
    ):
        st.cache_data.clear()
        st.rerun()

    render_footer()
    st.stop()


if result_dataframe.empty:
    render_section_title(
        "아직 저장된 평가 결과가 없습니다"
    )

    st.info(
        "학생이 종합 형성평가를 제출하면 이 페이지에 "
        "학급 현황과 시각화 결과가 표시됩니다."
    )

    st.code(
        str(
            RESULT_CSV_PATH
        ),
        language="text",
    )

    st.markdown(
        """
평가 결과가 저장되면 다음 분석이 제공됩니다.

- 응시 학생 수와 평균 정답률
- Stack, Queue, Tree, Graph 영역별 평균
- 학생별 정답률 비교
- 성취 수준 분포
- 오답 개념 빈도
- 학생 개인별 상세 결과
        """
    )

    if st.button(
        "🔄 평가 결과 다시 확인",
        key="reload_empty_dashboard",
    ):
        st.cache_data.clear()
        st.rerun()

    render_footer()
    st.stop()


# ============================================================
# 8. 사이드바 필터
# ============================================================

with st.sidebar:
    st.markdown(
        "## 📊 결과 분석 설정"
    )

    if st.button(
        "🔄 CSV 새로고침",
        use_container_width=True,
        key="refresh_dashboard_csv",
    ):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    record_mode = st.radio(
        "분석할 평가 기록",
        options=[
            "학생별 최신 결과",
            "모든 응시 기록",
        ],
        index=0,
        help=(
            "최신 결과는 학생마다 가장 최근에 제출한 "
            "평가 1건만 분석합니다."
        ),
    )

    available_grades = sorted(
        result_dataframe[
            "student_grade"
        ].unique()
    )

    selected_grades = st.multiselect(
        "학년",
        options=available_grades,
        default=available_grades,
        format_func=lambda value: f"{int(value)}학년",
    )

    grade_filtered_for_class = result_dataframe[
        result_dataframe[
            "student_grade"
        ].isin(
            selected_grades
        )
    ]

    available_classes = sorted(
        grade_filtered_for_class[
            "student_class"
        ].unique()
    )

    selected_classes = st.multiselect(
        "반",
        options=available_classes,
        default=available_classes,
        format_func=lambda value: f"{int(value)}반",
    )

    achievement_options = [
        level
        for level in ACHIEVEMENT_ORDER
        if level
        in result_dataframe[
            "achievement_level"
        ].unique()
    ]

    selected_achievement_levels = st.multiselect(
        "성취 수준",
        options=achievement_options,
        default=achievement_options,
        format_func=lambda value: ACHIEVEMENT_LABELS.get(
            value,
            value,
        ),
    )

    student_search_text = st.text_input(
        "학생 이름 검색",
        placeholder="이름 일부 입력",
    ).strip()

    st.divider()

    top_n_concepts = st.slider(
        "표시할 주요 오답 개념 수",
        min_value=3,
        max_value=15,
        value=10,
        step=1,
    )


# ============================================================
# 9. 필터 적용
# ============================================================

filtered_dataframe = result_dataframe.copy()

filtered_dataframe = filtered_dataframe[
    filtered_dataframe[
        "student_grade"
    ].isin(
        selected_grades
    )
]

filtered_dataframe = filtered_dataframe[
    filtered_dataframe[
        "student_class"
    ].isin(
        selected_classes
    )
]

filtered_dataframe = filtered_dataframe[
    filtered_dataframe[
        "achievement_level"
    ].isin(
        selected_achievement_levels
    )
]

if student_search_text:
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe[
            "student_name"
        ].str.contains(
            student_search_text,
            case=False,
            na=False,
        )
    ]

if record_mode == "학생별 최신 결과":
    analysis_dataframe = get_latest_attempts(
        filtered_dataframe
    )

else:
    analysis_dataframe = (
        filtered_dataframe
        .sort_values(
            by=[
                "student_grade",
                "student_class",
                "student_number",
                "attempt",
            ]
        )
        .reset_index(
            drop=True
        )
    )


# ============================================================
# 10. 필터 결과 없음
# ============================================================

if analysis_dataframe.empty:
    render_section_title(
        "필터 결과"
    )

    st.warning(
        "현재 필터 조건에 해당하는 평가 결과가 없습니다."
    )

    st.info(
        "사이드바에서 학년, 반, 성취 수준 또는 학생 이름 "
        "검색 조건을 변경해 주세요."
    )

    render_footer()
    st.stop()


# ============================================================
# 11. 전체 현황
# ============================================================

render_section_title(
    "1. 전체 평가 현황"
)

mode_text = (
    "학생별 최신 평가 결과를 기준으로 분석하고 있습니다."
    if record_mode == "학생별 최신 결과"
    else "선택된 모든 응시 기록을 기준으로 분석하고 있습니다."
)

st.caption(
    mode_text
)

render_metric_summary(
    analysis_dataframe
)

latest_submission_time = (
    analysis_dataframe[
        "submitted_at"
    ].max()
)

if pd.notna(
    latest_submission_time
):
    st.caption(
        "선택된 데이터의 최근 제출 시각: "
        + latest_submission_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


# ============================================================
# 12. 영역별 분석
# ============================================================

render_section_title(
    "2. 영역별 평균 정답률"
)

domain_summary = calculate_domain_summary(
    analysis_dataframe
)

weakest_domain_row = domain_summary.sort_values(
    by="평균 정답률"
).iloc[0]

strongest_domain_row = domain_summary.sort_values(
    by="평균 정답률",
    ascending=False,
).iloc[0]

summary_col1, summary_col2 = st.columns(
    2
)

with summary_col1:
    render_concept_box(
        title="가장 높은 영역",
        text=(
            f"{strongest_domain_row['영역']} 영역의 평균 정답률은 "
            f"{strongest_domain_row['평균 정답률']:.1f}%입니다."
        ),
    )

with summary_col2:
    render_concept_box(
        title="우선 보완할 영역",
        text=(
            f"{weakest_domain_row['영역']} 영역의 평균 정답률은 "
            f"{weakest_domain_row['평균 정답률']:.1f}%입니다."
        ),
    )

render_domain_chart(
    domain_summary
)


# ============================================================
# 13. 학생별 성취도와 성취 수준
# ============================================================

render_section_title(
    "3. 학생별 성취도"
)

score_col, achievement_col = st.columns(
    [
        1.45,
        1,
    ]
)

with score_col:
    st.markdown(
        "#### 학생별 정답률 비교"
    )

    render_student_score_chart(
        analysis_dataframe
    )

with achievement_col:
    st.markdown(
        "#### 성취 수준 분포"
    )

    render_achievement_chart(
        analysis_dataframe
    )


# ============================================================
# 14. 오답 개념 분석
# ============================================================

render_section_title(
    "4. 주요 오답 개념"
)

render_incorrect_concept_chart(
    analysis_dataframe,
    top_n=top_n_concepts,
)


# ============================================================
# 15. 학생 개인별 상세 분석
# ============================================================

render_section_title(
    "5. 학생 개인별 상세 분석"
)

# 개인 기록에서는 최신 결과 모드와 관계없이
# 현재 학년·반·성취 수준·이름 필터에 맞는 전체 응시 기록을 사용합니다.
render_student_detail(
    filtered_dataframe
)


# ============================================================
# 16. 학생별 결과표
# ============================================================

render_section_title(
    "6. 학생별 결과표"
)

student_result_table = build_student_result_table(
    analysis_dataframe
)

st.dataframe(
    student_result_table,
    hide_index=True,
    use_container_width=True,
    column_config={
        "학년": st.column_config.NumberColumn(
            "학년",
            format="%d",
            width="small",
        ),
        "반": st.column_config.NumberColumn(
            "반",
            format="%d",
            width="small",
        ),
        "번호": st.column_config.NumberColumn(
            "번호",
            format="%d",
            width="small",
        ),
        "이름": st.column_config.TextColumn(
            "이름",
            width="medium",
        ),
        "응시 차수": st.column_config.NumberColumn(
            "응시 차수",
            format="%d차",
            width="small",
        ),
        "총점": st.column_config.NumberColumn(
            "총점",
            format="%d",
            width="small",
        ),
        "전체 문항": st.column_config.NumberColumn(
            "전체 문항",
            format="%d",
            width="small",
        ),
        "정답률": st.column_config.ProgressColumn(
            "정답률",
            min_value=0,
            max_value=100,
            format="%.1f%%",
            width="medium",
        ),
        "성취 수준": st.column_config.TextColumn(
            "성취 수준",
            width="small",
        ),
        "제출 일시": st.column_config.TextColumn(
            "제출 일시",
            width="medium",
        ),
    },
)


# ============================================================
# 17. 데이터 다운로드
# ============================================================

render_section_title(
    "7. 결과 파일 내려받기"
)

download_col1, download_col2 = st.columns(
    2
)

with download_col1:
    st.download_button(
        label="📥 현재 분석 결과 내려받기",
        data=dataframe_to_csv_bytes(
            analysis_dataframe.drop(
                columns=[
                    "student_key",
                    "student_label",
                    "submitted_at_text",
                ],
                errors="ignore",
            )
        ),
        file_name=(
            "formative_results_filtered.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )

with download_col2:
    st.download_button(
        label="📥 교사용 요약표 내려받기",
        data=dataframe_to_csv_bytes(
            student_result_table
        ),
        file_name=(
            "formative_results_teacher_summary.csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )

st.caption(
    "다운로드 파일은 UTF-8 BOM 형식으로 생성되어 "
    "Excel에서 한글이 깨질 가능성을 줄였습니다."
)


# ============================================================
# 18. 페이지 하단
# ============================================================

render_footer()