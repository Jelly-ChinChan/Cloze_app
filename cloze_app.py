import streamlit as st
import random

st.set_page_config(page_title="Cloze Test Practice", page_icon="📝", layout="centered")

# ===== 全域字體 & 版面樣式（整體略縮小） =====
st.markdown(
    """
    <style>
    html, body, [class*="css"]  { font-size: 22px !important; }
    h2 { font-size: 26px !important; margin-top: 0.22em !important; margin-bottom: 0.22em !important; }

    .block-container { padding-top: 0.4rem !important; padding-bottom: 0.9rem !important; max-width: 1000px; }

    /* 進度條卡片與題目間距更小 */
    .progress-card { margin-bottom: 0.22rem !important; }

    /* 讓選項緊貼題目（去掉上方多餘空白），移除「選項：」字樣 */
    .stRadio { margin-top: 0 !important; }
    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stRadio"]) { margin-top: 0 !important; }

    /* 單一主要按鈕外觀 */
    .stButton>button{ height: 44px; padding: 0 18px; }

    /* 回饋（小字） */
    .feedback-small { font-size: 17px !important; line-height: 1.4; margin: 6px 0 2px 0; }
    .feedback-correct { color: #1a7f37; font-weight: 700; }
    .feedback-wrong { color: #c62828; font-weight: 700; }
    .feedback-translation { margin-top: 0.2rem; font-size: 17px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== 打字模式「稱讚語」 =====
PRAISES = [
    "你好棒：)", "你真的超強~~", "果然是201的學生><", "太神啦!!", "天啊你是單字魔鬼@@",
    "烏拉烏拉烏拉@#&%", "太厲害了^^", "不愧是展哥教徒呢!", "恭喜尼答對了ㄚㄚㄚ",
    "挖塞又答對了~", "太驚人了!!", "好扯喔",
]

# ===== 題庫 (15 題 + 中文翻譯) =====
QUESTION_BANK = [
    {"sentence": "The picture was hung too low on the wall and needed to be ______.",
     "answer": "adjusted", "translation": "這幅畫掛得太低，需要調整。"},
    {"sentence": "Owing to his leg surgery, Mike has been ______ to bed for a whole week.",
     "answer": "confined", "translation": "由於腿部手術，麥克已經臥床一整週了。"},
    {"sentence": "It was so hot and stuffy in the classroom that many students felt ______ and began to nod off.",
     "answer": "drowsy", "translation": "教室裡又悶又熱，許多學生感到昏昏欲睡，開始打瞌睡。"},
    {"sentence": "The key ______ of a good story is an interesting plot.",
     "answer": "element", "translation": "好故事的關鍵要素是一個有趣的情節。"},
    {"sentence": "The Internet ______ people to exchange information easily.",
     "answer": "enables", "translation": "網際網路讓人們可以輕鬆交換資訊。"},
    {"sentence": "The ghost story Jeremy told us ______ us to death.",
     "answer": "frightened", "translation": "傑里米講的鬼故事把我們嚇得要死。"},
    {"sentence": "After the surface of the lake ______ every winter, an ice-skating contest will be held.",
     "answer": "freezes", "translation": "湖面每年冬天結冰後，將舉辦溜冰比賽。"},
    {"sentence": "Grace wins her friends’ trust by keeping every ______ she makes.",
     "answer": "promise", "translation": "葛蕾絲透過信守每個承諾來贏得朋友的信任。"},
    {"sentence": "The car crashed into a tree. Fortunately, the driver was only ______ injured.",
     "answer": "slightly", "translation": "汽車撞上一棵樹，幸運的是駕駛只有輕傷。"},
    {"sentence": "Many years of hot sun and powerful storms have affected the ______ of this house.",
     "answer": "stability", "translation": "多年炎熱的陽光和猛烈的暴風雨已經影響了這棟房子的穩定性。"},
    {"sentence": "The patient has ______ lung cancer and has trouble breathing on his own.",
     "answer": "terminal", "translation": "這名病人罹患末期肺癌，即使治療後仍難以自行呼吸。"},
    {"sentence": "Some of the prisoners were either beaten or ______ to death.",
     "answer": "tortured", "translation": "有些囚犯被毒打，或被折磨致死。"},
    {"sentence": "All the passengers are asked to return their seats to the ______ position.",
     "answer": "upright", "translation": "所有乘客被要求把座椅調回直立位置。"},
    {"sentence": "The number of ______ in plane crashes has been on the increase.",
     "answer": "victims", "translation": "飛機失事的受害者人數一直在增加。"},
    {"sentence": "She believes only kind words can create ______ in people’s hearts.",
     "answer": "warmth", "translation": "她相信只有善意的話語才能在人心中帶來溫暖。"},
]

# ===== 初始化 =====
def init_state():
    st.session_state.mode = "選擇題模式"
    st.session_state.order = list(range(len(QUESTION_BANK)))
    random.shuffle(st.session_state.order)
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.submitted = False
    st.session_state.options = {}
    st.session_state.records = []
    st.session_state.last_feedback = ""  # 送出後顯示在按鈕上方

if "order" not in st.session_state:
    init_state()

# ===== 側邊欄 =====
with st.sidebar:
    st.markdown("### 設定")
    can_change_mode = (st.session_state.idx == 0 and not st.session_state.submitted)
    st.session_state.mode = st.radio(
        "選擇練習模式",
        ["打字模式", "選擇題模式"],
        index=1,
        disabled=not can_change_mode,
    )
    if st.button("🔄 重新開始"):
        init_state()
        st.rerun()

total = len(st.session_state.order)

# ===== 頂端卡片：進度條（間距更小） =====
current = st.session_state.idx + 1 if st.session_state.idx < total else total
percent = int(current / total * 100)
st.markdown(
    f"""
    <div class="progress-card" style='background-color:#f5f5f5; padding:9px 14px; border-radius:12px;'>
        <div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;'>
            <div style='font-size:18px;'>📘 目前進度：{current} / {total}</div>
            <div style='font-size:16px; color:#555;'>{percent}%</div>
        </div>
        <progress value='{current}' max='{total}' style='width:100%; height:14px;'></progress>
    </div>
    """,
    unsafe_allow_html=True
)

# ===== 題目與作答 =====
if st.session_state.idx < total:
    q_index = st.session_state.order[st.session_state.idx]
    q = QUESTION_BANK[q_index]

    st.markdown(f"<h2>Q{st.session_state.idx + 1}. {q['sentence']}</h2>", unsafe_allow_html=True)

    # 顯示輸入或選項
    if st.session_state.mode == "選擇題模式":
        if q_index not in st.session_state.options:
            correct = q["answer"]
            pool = [x["answer"] for x in QUESTION_BANK if x["answer"] != correct]
            distractors = random.sample(pool, 3)
            opts = [correct] + distractors
            random.shuffle(opts)
            st.session_state.options[q_index] = opts
        options_display = st.session_state.options[q_index]
        # 不顯示「選項：」文字，讓選項緊貼題目
        user_input_value = st.radio("", options_display, key=f"mc_{q_index}", label_visibility="collapsed")
    else:
        user_input_value = st.text_input("請輸入答案：", key=f"input_{q_index}")

    # ===== 主動作按鈕（動態標籤）：未送出=送出答案；已送出=下一題 =====
    # 先顯示訂正/稱讚（若已送出）
    if st.session_state.submitted and st.session_state.last_feedback:
        st.markdown(st.session_state.last_feedback, unsafe_allow_html=True)

    # 單一按鈕，依狀態變更文字
    action_label = "下一題" if st.session_state.submitted else "送出答案"
    if st.button(action_label, key="action_btn"):
        if not st.session_state.submitted:
            # 第一次按：送出並判題
            st.session_state.submitted = True
            is_correct = (user_input_value.strip().lower() == q["answer"]) if user_input_value else False

            if is_correct:
                if st.session_state.mode == "打字模式":
                    msg = random.choice(PRAISES)
                    st.session_state.last_feedback = (
                        f"<div class='feedback-small feedback-correct'>🎉 {msg}</div>"
                    )
                else:
                    st.session_state.last_feedback = (
                        "<div class='feedback-small feedback-correct'>✅ Correct!</div>"
                    )
                st.session_state.score += 1
            else:
                st.session_state.last_feedback = (
                    f"<div class='feedback-small feedback-wrong'>❌ Incorrect. 正確答案：{q['answer']}</div>"
                    f"<div class='feedback-translation'>📘 中文翻譯：{q['translation']}</div>"
                )

            st.session_state.records.append(
                (q["sentence"], user_input_value or "", is_correct, q["answer"])
            )
            st.rerun()  # 立即重繪，讓按鈕文字改成「下一題」並顯示訂正
        else:
            # 第二次按：前往下一題
            st.session_state.idx += 1
            st.session_state.submitted = False
            st.session_state.last_feedback = ""
            st.rerun()

# ===== 結果頁 =====
else:
    st.subheader("📊 Results")
    score = st.session_state.score
    st.markdown(f"<h3>Total Score: {score}/{total}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h3>Accuracy: {(score/total)*100:.1f}%</h3>", unsafe_allow_html=True)

    with st.expander("查看答題紀錄"):
        for i, (sentence, ans, correct, corr) in enumerate(st.session_state.records, 1):
            icon = "✅" if correct else "❌"
            show_ans = ans if ans != "" else "未作答"
            st.write(f"Q{i}: {sentence} → 你的答案：**{show_ans}**；正解：**{corr}** {icon}")

    # ❌ 已移除彩帶效果
    st.button("🔄 再做一次", on_click=init_state)
