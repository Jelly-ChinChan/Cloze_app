import streamlit as st
import random
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="Cloze Test Practice", page_icon="✍️")
st.title("✍️ Cloze Test Practice App (One Question at a Time)")

# --- 內建「每秒自動重繪」：用 JS 輕量刷新父頁（無需外掛）
components.html(
    "<script>setTimeout(function(){window.parent.postMessage({type:'streamlit:rerun'},'*');},1000);</script>",
    height=0,
)

# ===== 題庫 (15 題) =====
QUESTION_BANK = [
    {"sentence": "The picture was hung too low on the wall and needed to be ______.", "answer": "adjusted"},
    {"sentence": "Owing to his leg surgery, Mike has been ______ to bed for a whole week.", "answer": "confined"},
    {"sentence": "It was so hot and stuffy in the classroom that many students felt ______ and began to nod off.", "answer": "drowsy"},
    {"sentence": "The key ______ of a good story is an interesting plot.", "answer": "element"},
    {"sentence": "The Internet ______ people to exchange information easily.", "answer": "enables"},
    {"sentence": "The ghost story Jeremy told us ______ us to death.", "answer": "frightened"},
    {"sentence": "After the surface of the lake ______ every winter, an ice-skating contest will be held.", "answer": "freezes"},
    {"sentence": "Grace wins her friends’ trust by keeping every ______ she makes.", "answer": "promise"},
    {"sentence": "The car crashed into a tree. Fortunately, the driver was only ______ injured.", "answer": "slightly"},
    {"sentence": "Many years of hot sun and powerful storms have affected the ______ of this house.", "answer": "stability"},
    {"sentence": "The patient has ______ lung cancer and has trouble breathing on his own.", "answer": "terminal"},
    {"sentence": "Some of the prisoners were either beaten or ______ to death.", "answer": "tortured"},
    {"sentence": "All the passengers are asked to return their seats to the ______ position.", "answer": "upright"},
    {"sentence": "The number of ______ in plane crashes has been on the increase.", "answer": "victims"},
    {"sentence": "She believes only kind words can create ______ in people’s hearts.", "answer": "warmth"},
]

PER_QUESTION_SECONDS = 10  # 每題固定 10 秒
MC_BLANK = "(空白/略過)"  # 選擇題的「未作答」選項

# ===== 初始化 =====
def init_state():
    st.session_state.mode = "選擇題模式"            # 預設：選擇題
    st.session_state.order = list(range(len(QUESTION_BANK)))
    random.shuffle(st.session_state.order)          # 題目順序只洗一次
    st.session_state.idx = 0                        # 目前題目在 order 中的索引
    st.session_state.score = 0
    st.session_state.submitted = False              # 本題是否已送出
    st.session_state.options = {}                   # {真題索引: [四個固定選項(不含空白)]}
    st.session_state.records = []                   # [(sentence, user_ans, correct, correct_ans, timeout_bool)]
    st.session_state.deadline = None                # 本題截止時間 (unix)

if "order" not in st.session_state:
    init_state()

# ===== 側邊欄：模式與重置 =====
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

# ===== 是否仍有題目 =====
if st.session_state.idx < total:
    q_index = st.session_state.order[st.session_state.idx]
    q = QUESTION_BANK[q_index]
    st.markdown(f"**Q{st.session_state.idx + 1}. {q['sentence']}**")

    # 建立/取得固定選項（選擇題模式）
    if st.session_state.mode == "選擇題模式":
        if q_index not in st.session_state.options:
            correct = q["answer"]
            pool = [x["answer"] for x in QUESTION_BANK if x["answer"] != correct]
            distractors = random.sample(pool, 3)
            opts = [correct] + distractors
            random.shuffle(opts)
            st.session_state.options[q_index] = opts  # 只存四個真選項
        # 顯示時在最上方加上「空白/略過」
        options_display = [MC_BLANK] + st.session_state.options[q_index]
        user_input = st.radio("Choose the correct word:", options_display, key=f"mc_{q_index}")
        # 把空白選項轉成空字串以便統一處理
        if user_input == MC_BLANK:
            user_input_value = ""
        else:
            user_input_value = user_input
    else:
        user_input_value = st.text_input("Your answer:", key=f"input_{q_index}")

    # 設定本題截止時間（第一次進到此題）
    if st.session_state.deadline is None:
        st.session_state.deadline = time.time() + PER_QUESTION_SECONDS

    # 顯示倒數（每秒自動重繪）
    remaining = max(0, int(st.session_state.deadline - time.time()))
    st.info(f"⏳ 倒數：{remaining} 秒")

    # 時間到且尚未送出 → 自動判題並跳下一題
    if (remaining == 0) and (not st.session_state.submitted):
        is_correct = (user_input_value.strip().lower() == q["answer"]) if user_input_value else False
        if is_correct:
            st.session_state.score += 1
        st.session_state.records.append((q["sentence"], user_input_value, is_correct, q["answer"], True))
        st.session_state.idx += 1
        st.session_state.submitted = False
        st.session_state.deadline = None
        st.rerun()

    # 送出答案（就算沒填也可送出）
    col1, col2 = st.columns([1, 1])
    with col1:
        disabled_submit = st.session_state.submitted  # 不再依賴是否有輸入
        if st.button("送出答案", disabled=disabled_submit):
            st.session_state.submitted = True
            is_correct = (user_input_value.strip().lower() == q["answer"]) if user_input_value else False
            if is_correct:
                st.success("✅ Correct!")
                st.session_state.score += 1
            else:
                st.error(f"❌ Incorrect. Correct answer: {q['answer']}")
            st.session_state.records.append((q["sentence"], user_input_value or "", is_correct, q["answer"], False))

    with col2:
        if st.session_state.submitted:
            if st.button("下一題"):
                st.session_state.idx += 1
                st.session_state.submitted = False
                st.session_state.deadline = None  # 下題重新 10 秒
                st.rerun()

# ===== 結果頁 =====
else:
    st.subheader("📊 Results")
    score = st.session_state.score
    st.write(f"Total Score: **{score}/{total}**")
    st.write(f"Accuracy: **{(score/total)*100:.1f}%**")

    with st.expander("查看答題紀錄"):
        for i, (sentence, ans, correct, corr, timeout) in enumerate(st.session_state.records, 1):
            icon = "✅" if correct else "❌"
            tag = "（時間到自動跳題）" if timeout else ""
            show_ans = ans if ans != "" else "未作答"
            st.write(f"Q{i}{tag}: {sentence} → 你的答案：**{show_ans}**；正解：**{corr}** {icon}")

    st.button("🔄 再做一次", on_click=init_state)
