import streamlit as st
import random

st.set_page_config(page_title="Cloze Test Practice", page_icon="✍️")
st.title("✍️ Cloze Test Practice App")

# ===== 打字模式「稱讚語」清單（隨機顯示） =====
PRAISES = [
    "你好棒：)",
    "你真的超強~~",
    "果然是201的學生><",
    "太神啦!!",
    "天啊你是單字魔鬼@@",
    "烏拉烏拉烏拉@#&%",
    "太厲害了^^",
    "不愧是展哥教徒呢!",
    "恭喜尼答對了ㄚㄚㄚ",
    "挖塞又答對了~",
    "太驚人了!!",
    "好扯喔",
]

# ===== 題庫 (含中文翻譯) =====
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

MC_BLANK = "(空白/略過)"  # 選擇題的空白選項

# ===== 初始化 =====
def init_state():
    st.session_state.mode = "選擇題模式"            # 預設：選擇題
    st.session_state.order = list(range(len(QUESTION_BANK)))
    random.shuffle(st.session_state.order)          # 題目順序只洗一次
    st.session_state.idx = 0                        # 目前題目在 order 中的索引
    st.session_state.score = 0
    st.session_state.submitted = False              # 本題是否已送出
    st.session_state.options = {}                   # {真題索引: [四個固定選項(不含空白)]}
    st.session_state.records = []                   # [(sentence, user_ans, correct, correct_ans)]

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

# ===== 主體 =====
if st.session_state.idx < total:
    q_index = st.session_state.order[st.session_state.idx]
    q = QUESTION_BANK[q_index]
    st.markdown(f"**Q{st.session_state.idx + 1}. {q['sentence']}**")

    # 顯示輸入或選項
    if st.session_state.mode == "選擇題模式":
        if q_index not in st.session_state.options:
            correct = q["answer"]
            pool = [x["answer"] for x in QUESTION_BANK if x["answer"] != correct]
            distractors = random.sample(pool, 3)
            opts = [correct] + distractors
            random.shuffle(opts)
            st.session_state.options[q_index] = opts  # 只存四個真選項
        options_display = [MC_BLANK] + st.session_state.options[q_index]
        user_input_value = st.radio("Choose the correct word:", options_display, key=f"mc_{q_index}")
        if user_input_value == MC_BLANK:
            user_input_value = ""
    else:
        user_input_value = st.text_input("Your answer:", key=f"input_{q_index}")

    # 送出答案
    col1, col2 = st.columns([1, 1])
    with col1:
        disabled_submit = st.session_state.submitted
        if st.button("送出答案", disabled=disabled_submit):
            st.session_state.submitted = True
            is_correct = (user_input_value.strip().lower() == q["answer"]) if user_input_value else False
            if is_correct:
                # 打字模式：顯示隨機稱讚語；選擇題維持原樣
                if st.session_state.mode == "打字模式":
                    st.success(random.choice(PRAISES))
                else:
                    st.success("✅ Correct!")
                st.session_state.score += 1
            else:
                st.error(f"❌ Incorrect. Correct answer: {q['answer']}")
                st.warning(f"📘 中文翻譯：{q['translation']}")
            st.session_state.records.append((q["sentence"], user_input_value or "", is_correct, q["answer"]))

    with col2:
        if st.session_state.submitted:
            if st.button("下一題"):
                st.session_state.idx += 1
                st.session_state.submitted = False
                st.rerun()

# ===== 結果頁 =====
else:
    st.subheader("📊 Results")
    score = st.session_state.score
    st.write(f"Total Score: **{score}/{total}**")
    st.write(f"Accuracy: **{(score/total)*100:.1f}%**")

    with st.expander("查看答題紀錄"):
        for i, (sentence, ans, correct, corr) in enumerate(st.session_state.records, 1):
            icon = "✅" if correct else "❌"
            show_ans = ans if ans != "" else "未作答"
            st.write(f"Q{i}: {sentence} → 你的答案：**{show_ans}**；正解：**{corr}** {icon}")

    st.button("🔄 再做一次", on_click=init_state)
