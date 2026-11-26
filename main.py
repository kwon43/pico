
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

# ======================================
# 1. 웹페이지 기본 설정
# ======================================
st.set_page_config(
    page_title="스마트 가방 준비물 검사기",
    page_icon="🎒",
    layout="wide"
)

# ======================================
# 2. 프로젝트 정보
# ======================================
ITEMS = {
    1: "PHONE",
    2: "NOTEBOOK",
    3: "PENCILCASE"
}

KOREAN_NAMES = {
    1: "휴대폰",
    2: "공책",
    3: "필통"
}

# ======================================
# 3. 웹페이지 디자인
# ======================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg, #0b1220, #15263f
    );
    color: white;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #ffffff !important;
}

[data-testid="stMetric"] {
    background-color: #1b3049;
    border-radius: 15px;
    padding: 20px;
    border: 1px solid #344e68;
}

[data-testid="stMetricLabel"] {
    color: #c4d5e5;
}

[data-testid="stMetricValue"] {
    color: #ffffff;
}

.stButton > button {
    border-radius: 12px;
    font-weight: bold;
}

.hero {
    background: linear-gradient(
        120deg, #173b55, #126a72
    );
    padding: 36px;
    border-radius: 20px;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 38px;
    margin-bottom: 12px;
}

.hero p {
    color: #e1f2f5;
    font-size: 17px;
    line-height: 1.8;
}

.oled {
    background-color: #06141c;
    border: 8px solid #344d65;
    border-radius: 18px;
    padding: 22px;
    min-height: 210px;
    color: #a5ffcb;
    font-family: monospace;
    font-size: 19px;
    line-height: 2;
    white-space: pre-wrap;
}

.feature {
    background: #192f48;
    border: 1px solid #36516a;
    border-radius: 15px;
    padding: 20px;
    min-height: 135px;
    margin-bottom: 12px;
}

.feature h3 {
    font-size: 18px;
}

.feature p {
    color: #c9d8e5;
    font-size: 14px;
    line-height: 1.7;
}

.notice {
    background: #16334a;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #31566d;
}
</style>
""", unsafe_allow_html=True)

# ======================================
# 4. 시뮬레이터 상태 저장
# ======================================
if "found" not in st.session_state:
    st.session_state.found = set()

if "scanning" not in st.session_state:
    st.session_state.scanning = False

if "started" not in st.session_state:
    st.session_state.started = False

if "armed" not in st.session_state:
    st.session_state.armed = {
        item_id: True for item_id in ITEMS
    }

if "logs" not in st.session_state:
    st.session_state.logs = []


def add_log(message):
    now = datetime.now().strftime("%H:%M:%S")

    st.session_state.logs.insert(
        0,
        {
            "시간": now,
            "작동 기록": message
        }
    )

    st.session_state.logs = (
        st.session_state.logs[:30]
    )


# ======================================
# 5. 검사 시작
# ======================================
def start_scan():
    st.session_state.scanning = True
    st.session_state.started = True

    add_log("초록 버튼 - 검사 시작 / 이어서 검사")


# ======================================
# 6. 새 검사
# ======================================
def reset_scan():
    st.session_state.found = set()

    st.session_state.armed = {
        item_id: True for item_id in ITEMS
    }

    st.session_state.scanning = True
    st.session_state.started = True

    add_log("초록 버튼 길게 - 새 검사")


# ======================================
# 7. 검사 종료
# ======================================
def stop_scan():
    st.session_state.scanning = False

    add_log("빨간 버튼 - 검사 종료")


# ======================================
# 8. 물건 인식
# ======================================
def recognize(item_id):

    if not st.session_state.scanning:
        return

    if not st.session_state.armed[item_id]:
        return

    name = KOREAN_NAMES[item_id]

    # 첫 번째 인식
    if item_id not in st.session_state.found:

        st.session_state.found.add(item_id)

        add_log(
            name + " 첫 번째 인식 - 확인 완료"
        )

    # 두 번째 인식
    else:

        st.session_state.found.remove(item_id)

        add_log(
            name + " 두 번째 인식 - 확인 취소"
        )

    # 같은 물건을 계속 보고 있을 때
    # 중복 인식하지 않도록 잠금
    st.session_state.armed[item_id] = False


# ======================================
# 9. 카메라 시야에서 물건 제거
# ======================================
def remove_from_camera(item_id):

    if st.session_state.scanning:

        st.session_state.armed[item_id] = True

        add_log(
            KOREAN_NAMES[item_id]
            + " - 카메라 시야에서 제거"
        )


# ======================================
# 10. OLED 화면 시뮬레이션
# ======================================
def get_oled_text():

    if not st.session_state.started:
        return "ON"

    # 검사 중
    if st.session_state.scanning:

        lines = [
            "SCANNING {}/{}".format(
                len(st.session_state.found),
                len(ITEMS)
            )
        ]

        for item_id, name in ITEMS.items():

            if item_id in st.session_state.found:
                mark = "✓"
            else:
                mark = "□"

            lines.append(
                "{} {}".format(mark, name)
            )

        return "\n".join(lines)

    # 검사 종료
    missing = [
        name
        for item_id, name in ITEMS.items()
        if item_id not in st.session_state.found
    ]

    if not missing:
        return "ALL READY!"

    return "MISSING:\n" + "\n".join(missing)


# ======================================
# 11. 준비물 현황 그래프
# ======================================
def make_chart():

    checked = len(st.session_state.found)
    missing = len(ITEMS) - checked

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["확인 완료", "미확인"],
                values=[checked, missing],
                hole=0.7,
                marker=dict(
                    colors=["#23c9ac", "#38516b"]
                ),
                textinfo="none"
            )
        ]
    )

    fig.update_layout(
        height=280,
        margin=dict(
            t=20,
            b=20,
            l=20,
            r=20
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        annotations=[
            dict(
                text="{}/{}".format(
                    checked, len(ITEMS)
                ),
                x=0.5,
                y=0.5,
                font_size=28,
                showarrow=False,
                font_color="white"
            )
        ]
    )

    return fig


# ======================================
# 12. 사이드바
# ======================================
with st.sidebar:

    st.title("🎒 SMART BAG")

    st.caption(
        "AI 기반 스마트 준비물 검사기"
    )

    st.divider()

    st.subheader("프로젝트 기술")

    st.write("🐍 MicroPython")
    st.write("🖥️ Raspberry Pi Pico")
    st.write("📷 HUSKYLENS")
    st.write("📟 OLED SSD1315")
    st.write("💡 WS2813 LED")
    st.write("🌐 Streamlit")

    st.divider()

    st.subheader("현재 시뮬레이터 상태")

    if st.session_state.scanning:
        st.success("검사 진행 중")
    else:
        st.info("검사 대기 / 종료")

    st.write(
        "확인된 준비물: {} / {}".format(
            len(st.session_state.found),
            len(ITEMS)
        )
    )


# ======================================
# 13. 메인 제목
# ======================================
st.markdown("""
<div class="hero">
    <h1>🎒 스마트 가방 준비물 검사기</h1>
    <p>
        인공지능 카메라를 활용하여
        학교 준비물을 확인하고,
        빠진 물건을 알려주는
        피지컬 컴퓨팅 프로젝트입니다.
    </p>
    <p>
        Raspberry Pi Pico와 HUSKYLENS,
        OLED, LED, 버튼을 이용해
        제작하였습니다.
    </p>
</div>
""", unsafe_allow_html=True)


# ======================================
# 14. 프로젝트 요약 지표
# ======================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("준비물 종류", "3종")

with col2:
    st.metric("AI 센서", "HUSKYLENS")

with col3:
    st.metric("LED 개수", "10개")

with col4:
    st.metric("입력 버튼", "2개")


# ======================================
# 15. 메뉴
# ======================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 프로젝트 소개",
    "🎮 작동 체험",
    "🔌 하드웨어 구성",
    "🛠️ 제작 과정"
])


# ======================================
# 16. 프로젝트 소개
# ======================================
with tab1:

    st.header("프로젝트 소개")

    st.subheader("💡 제작 동기")

    st.write("""
    학생들은 학교에 갈 때
    공책이나 필통 같은 준비물을
    빠뜨리는 경우가 있습니다.

    이를 해결하기 위해
    인공지능 카메라가 준비물을 인식하고
    OLED에 확인 결과를 표시하는
    스마트 가방을 제작하였습니다.
    """)

    st.subheader("📸 실제 작품 사진")

    photo = Path("assets/smartbag.jpg")

    if photo.exists():
        st.image(
            str(photo),
            caption="스마트 가방 검사기",
            use_container_width=True
        )
    else:
        st.info(
            "GitHub에 assets/smartbag.jpg 사진을 "
            "올리면 이곳에 작품 사진이 표시됩니다."
        )

    st.subheader("✨ 주요 기능")

    features = [
        (
            "🧠 AI 물체 인식",
            "HUSKYLENS Object Classification으로 "
            "휴대폰, 공책, 필통을 구분합니다."
        ),
        (
            "✅ 실시간 체크리스트",
            "확인된 준비물은 OLED에 "
            "체크 표시로 나타납니다."
        ),
        (
            "🔁 중복 인식 취소",
            "같은 물건을 카메라에서 뺐다가 "
            "다시 보여주면 확인이 취소됩니다."
        ),
        (
            "💡 자동 LED 조명",
            "검사를 시작하면 LED가 켜지고 "
            "종료하면 꺼집니다."
        )
    ]

    left, right = st.columns(2)

    for i, (title, description) in enumerate(features):

        with (left if i % 2 == 0 else right):

            st.markdown(
                f"""
                <div class="feature">
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.subheader("⚙️ 작동 순서")

    st.markdown("""
    1. 보조배터리로 Pico에 전원을 공급합니다.
    2. OLED에 `ON`이 표시됩니다.
    3. 초록 버튼을 눌러 검사를 시작합니다.
    4. HUSKYLENS가 준비물을 인식합니다.
    5. 인식된 준비물에 체크 표시가 나타납니다.
    6. 빨간 버튼을 누르면 검사가 종료됩니다.
    7. 빠진 물건은 `MISSING:`으로 표시됩니다.
    """)

    st.info(
        "이 프로젝트는 카메라에 물건을 보여주어 "
        "준비 여부를 확인하는 방식입니다."
    )


# ======================================
# 17. 작동 체험
# ======================================
with tab2:

    st.header("🎮 스마트 가방 작동 체험")

    st.write(
        "실제 센서가 없어도 "
        "웹에서 검사 과정을 체험할 수 있습니다."
    )

    st.caption(
        "이 화면은 실제 HUSKYLENS와 연결된 "
        "데이터가 아닌 시뮬레이션입니다."
    )

    # 버튼
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button(
            "🟢 검사 시작 / 이어서",
            use_container_width=True,
            type="primary",
            disabled=st.session_state.scanning
        ):
            start_scan()
            st.rerun()

    with c2:
        if st.button(
            "🔴 검사 종료",
            use_container_width=True,
            disabled=not st.session_state.scanning
        ):
            stop_scan()
            st.rerun()

    with c3:
        if st.button(
            "🔄 처음부터 새 검사",
            use_container_width=True
        ):
            reset_scan()
            st.rerun()

    st.divider()

    # OLED와 그래프
    left, right = st.columns(2)

    with left:

        st.subheader("📟 OLED 화면")

        oled_text = get_oled_text()

        st.markdown(
            '<div class="oled">{}</div>'.format(
                oled_text
            ),
            unsafe_allow_html=True
        )

        st.caption(
            "웹에서 재현한 OLED 화면입니다."
        )

    with right:

        st.subheader("📊 준비물 확인 현황")

        st.plotly_chart(
            make_chart(),
            use_container_width=True,
            config={"displayModeBar": False}
        )

        progress = (
            len(st.session_state.found)
            / len(ITEMS)
        )

        st.progress(progress)

    st.divider()

    st.subheader("📷 HUSKYLENS 인식 체험")

    st.write("""
    **사용 방법**

    1. 초록 버튼으로 검사를 시작합니다.
    2. 물건 인식 버튼을 누릅니다.
    3. 확인 체크가 나타납니다.
    4. 시야에서 제거를 누릅니다.
    5. 같은 물건을 다시 인식하면 체크가 취소됩니다.
    """)

    icons = {
        1: "📱",
        2: "📓",
        3: "✏️"
    }

    for item_id, name in KOREAN_NAMES.items():

        with st.container(border=True):

            a, b, c = st.columns(
                [1.2, 1, 1],
                vertical_alignment="center"
            )

            with a:

                st.write(
                    f"**{icons[item_id]} {name}**"
                )

                if item_id in st.session_state.found:
                    st.success("확인 완료")
                else:
                    st.caption("미확인")

            with b:

                if st.button(
                    "물건 인식",
                    key=f"recognize_{item_id}",
                    use_container_width=True,
                    disabled=(
                        not st.session_state.scanning
                        or not st.session_state.armed[item_id]
                    )
                ):
                    recognize(item_id)
                    st.rerun()

            with c:

                if st.button(
                    "시야에서 제거",
                    key=f"remove_{item_id}",
                    use_container_width=True,
                    disabled=(
                        not st.session_state.scanning
                        or st.session_state.armed[item_id]
                    )
                ):
                    remove_from_camera(item_id)
                    st.rerun()

    # 배경 인식 체험
    with st.expander("⬛ 검정색 가방 배경 인식"):

        st.write("""
        빈 검정색 가방 내부를 ID4로 학습하면
        배경을 준비물과 구분하는 데
        도움이 될 수 있습니다.

        ID4는 필수 준비물에 포함하지 않습니다.
        """)

        if st.button(
            "빈 가방 배경 인식",
            disabled=not st.session_state.scanning
        ):
            add_log(
                "ID4 검정색 배경 - 준비물 집계 제외"
            )
            st.rerun()

    st.divider()

    st.subheader("📝 인식 기록")

    if st.session_state.logs:

        st.dataframe(
            st.session_state.logs,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "검사를 시작하면 기록이 표시됩니다."
        )


# ======================================
# 18. 하드웨어 구성
# ======================================
with tab3:

    st.header("🔌 하드웨어 구성")

    st.subheader("사용 부품")

    hardware = [
        {
            "부품": "Raspberry Pi Pico",
            "역할": "전체 시스템 제어",
            "연결": "Grove Shield"
        },
        {
            "부품": "HUSKYLENS",
            "역할": "AI 물체 인식",
            "연결": "GP6, GP7 / I2C1"
        },
        {
            "부품": "SSD1315 OLED",
            "역할": "준비물 목록과 결과 표시",
            "연결": "GP8, GP9 / SoftI2C"
        },
        {
            "부품": "Grove Dual Button",
            "역할": "검사 시작 및 종료",
            "연결": "GP16, GP17"
        },
        {
            "부품": "WS2813 LED Stick",
            "역할": "가방 내부 조명",
            "연결": "GP18 / LED 10개"
        },
        {
            "부품": "보조배터리",
            "역할": "휴대용 전원 공급",
            "연결": "Pico USB"
        }
    ]

    st.dataframe(
        hardware,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("📚 물체 학습 ID")

    st.table([
        {
            "ID": "ID1",
            "대상": "휴대폰",
            "준비물 검사": "O"
        },
        {
            "ID": "ID2",
            "대상": "공책",
            "준비물 검사": "O"
        },
        {
            "ID": "ID3",
            "대상": "필통",
            "준비물 검사": "O"
        },
        {
            "ID": "ID4 (선택)",
            "대상": "검정색 가방 배경",
            "준비물 검사": "X"
        }
    ])

    st.subheader("🎛️ 버튼 기능")

    st.markdown("""
    - **초록 버튼 짧게:** 검사 시작 또는 이어서 검사
    - **초록 버튼 2초 길게:** 처음부터 새 검사
    - **빨간 버튼:** 검사 종료
    - **같은 물건 두 번째 인식:** 체크 자동 취소
    """)

    st.subheader("🎒 가방 내부 설치")

    st.markdown("""
    - **가방 위쪽:** HUSKYLENS 및 LED 스틱
    - **가방 입구:** OLED와 버튼
    - **가방 등판 쪽:** Pico 및 Grove Shield
    - **가방 옆주머니:** USB 보조배터리
    - **배선 정리:** 지지판과 벨크로 타이 활용
    """)


# ======================================
# 19. 제작 과정
# ======================================
with tab4:

    st.header("🛠️ 제작 과정")

    steps = [
        (
            "1. 아이디어 구상",
            "준비물을 빠뜨리는 문제를 해결하기 위해 "
            "스마트 가방을 기획했습니다."
        ),
        (
            "2. 회로 연결",
            "Pico와 Grove Shield에 "
            "카메라, OLED, 버튼, LED를 연결했습니다."
        ),
        (
            "3. OLED 오류 해결",
            "I2C 통신 오류를 해결하기 위해 "
            "SoftI2C를 적용했습니다."
        ),
        (
            "4. HUSKYLENS 펌웨어 업데이트",
            "Object Classification 기능을 "
            "사용할 수 있도록 업데이트했습니다."
        ),
        (
            "5. LED 제어 개선",
            "WS2813 전용 타이밍을 적용하여 "
            "LED 제어 방식을 수정했습니다."
        ),
        (
            "6. 준비물 인식 기능 구현",
            "물체 ID에 따라 체크리스트가 "
            "갱신되도록 프로그램을 작성했습니다."
        ),
        (
            "7. 가방 설치 설계",
            "보조배터리와 지지판을 이용한 "
            "휴대용 구조를 설계했습니다."
        )
    ]

    for title, description in steps:

        with st.container(border=True):

            st.subheader(title)
            st.write(description)

    st.divider()

    st.subheader("⚠️ 프로젝트의 한계")

    st.markdown("""
    - 물건이 겹쳐 있으면 인식이 어려울 수 있습니다.
    - 조명과 카메라 각도에 따라 정확도가 달라질 수 있습니다.
    - 빈 가방 배경이 준비물로 잘못 인식될 수 있습니다.
    - 물건을 실제로 꺼내는 순간을 자동 감지하지는 않습니다.
    """)

    st.subheader("🚀 향후 발전 방향")

    st.markdown("""
    - 빈 가방 배경 오인식 감소
    - 실제 물체 인식 정확도 측정
    - 요일별 준비물 목록 설정
    - 가방 내부 배선 정리 및 소형화
    - 물건 출입을 자동 판단하는 기능
    """)


# ======================================
# 20. 하단 안내
# ======================================
st.divider()

st.caption(
    "🎒 SMART BAG CHECKER | "
    "Raspberry Pi Pico + HUSKYLENS + Streamlit"
)

st.caption(
    "※ 웹앱의 검사 기능은 시뮬레이션이며, "
    "실제 센서에서 실시간 데이터를 가져오는 것은 아닙니다."
)
