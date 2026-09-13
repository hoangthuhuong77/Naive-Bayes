# -*- coding: utf-8 -*-
"""Web demo bộ lọc SMS Spam — chạy bằng: streamlit run app.py"""

import os

import joblib
import numpy as np
import pandas as pd
import streamlit as st

MODEL_PATH = "spam_model.pkl"

st.set_page_config(page_title="Bộ lọc SMS Spam", page_icon="📩", layout="wide")


# B1 — Nạp mô hình (cache để không phải đọc lại file ở mỗi lần bấm nút)
@st.cache_resource
def nap_mo_hinh():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


model = nap_mo_hinh()
if model is None:
    st.error(f"Chưa tìm thấy `{MODEL_PATH}`. Hãy chạy hết notebook `sms_spam_naive_bayes.ipynb` để tạo file này.")
    st.stop()


# B2 — Hàm dự đoán: nhận text thô, pipeline tự vector hoá bên trong
def du_doan(tin_nhan, nguong):
    p = float(model.predict_proba([tin_nhan])[0, 1])
    return ("SPAM" if p >= nguong else "HAM"), p


# B3 — Lấy các từ có ảnh hưởng mạnh nhất tới quyết định
def tu_anh_huong(tin_nhan, top_n=8):
    vect, nb = model.named_steps["vect"], model.named_steps["nb"]
    x = vect.transform([tin_nhan])
    if x.nnz == 0:
        return pd.DataFrame(columns=["Từ / cụm từ", "Số lần", "Log-odds"])
    ten = np.array(vect.get_feature_names_out())
    log_odds = nb.feature_log_prob_[1] - nb.feature_log_prob_[0]
    idx = x.indices
    df = pd.DataFrame({"Từ / cụm từ": ten[idx], "Số lần": x.data, "Log-odds": log_odds[idx]})
    df["abs"] = df["Log-odds"].abs()
    return df.sort_values("abs", ascending=False).head(top_n).drop(columns="abs").reset_index(drop=True)


# ---------------------------------------------------------------- giao diện
st.title("📩 Bộ lọc tin nhắn SMS Spam")
st.caption("Multinomial Naive Bayes + Bag-of-Words (1-2 gram) · F1 lớp spam = 0,9444 trên tập test")

with st.sidebar:
    st.header("Cài đặt")
    nguong = st.slider("Ngưỡng gắn nhãn spam", 0.05, 0.95, 0.50, 0.05,
                       help="Ngưỡng cao = ít chặn nhầm hơn nhưng bỏ lọt nhiều spam hơn")
    st.divider()
    st.subheader("Hiệu năng trên tập test")
    st.metric("Precision (spam)", "0,9835")
    st.metric("Recall (spam)", "0,9084")
    st.metric("F1 (spam)", "0,9444")
    st.caption("1.034 tin: bắt đúng 119/131 spam, chặn nhầm 2/903 tin thường.")

VI_DU = {
    "— Tự nhập —": "",
    "Spam: trúng thưởng": "Congratulations! You have WON a FREE iPhone 15. Click http://bit.ly/claim-now to claim your prize NOW!",
    "Spam: tổng đài tính phí": "URGENT! Your mobile number has been awarded a 2000 pound cash prize. Call 09061701461 to claim. T&C apply.",
    "Ham: hẹn ăn trưa": "Hey, are we still meeting for lunch at 12? Let me know if you're running late.",
    "Ham: việc nhà": "Mom said she'll pick up the kids today, so don't worry about leaving work early.",
}

tab1, tab2 = st.tabs(["Kiểm tra một tin nhắn", "Kiểm tra hàng loạt"])

# --- Tab 1: một tin nhắn ---
with tab1:
    chon = st.selectbox("Chọn ví dụ có sẵn hoặc tự nhập", list(VI_DU.keys()))
    tin_nhan = st.text_area("Nội dung tin nhắn (tiếng Anh)", value=VI_DU[chon], height=130,
                            placeholder="Nhập nội dung tin nhắn...")

    if st.button("Phân loại", type="primary"):
        if not tin_nhan.strip():
            st.warning("Hãy nhập nội dung tin nhắn.")
        else:
            nhan, prob = du_doan(tin_nhan, nguong)
            c1, c2 = st.columns([1, 2])
            with c1:
                if nhan == "SPAM":
                    st.error(f"### 🚫 {nhan}")
                else:
                    st.success(f"### ✅ {nhan}")
                st.metric("Xác suất là spam", f"{prob:.2%}")
            with c2:
                st.write("**Mức độ nghi ngờ**")
                st.progress(prob)
                st.caption(f"Ngưỡng hiện tại: {nguong:.2f} · xác suất ≥ ngưỡng thì gắn nhãn SPAM")
                st.write("**Những từ ảnh hưởng mạnh nhất tới quyết định**")
                bang = tu_anh_huong(tin_nhan)
                if bang.empty:
                    st.caption("Không có từ nào nằm trong từ vựng của mô hình.")
                else:
                    st.dataframe(bang.style.format({"Log-odds": "{:+.2f}"}), hide_index=True,
                                 width="stretch")
                    st.caption("Log-odds dương → nghiêng về spam, âm → nghiêng về ham.")

# --- Tab 2: nhiều tin nhắn ---
with tab2:
    st.write("Mỗi dòng là một tin nhắn.")
    nhieu = st.text_area("Danh sách tin nhắn", height=180,
                         value="\n".join(v for k, v in VI_DU.items() if v))
    if st.button("Phân loại tất cả"):
        dong = [d.strip() for d in nhieu.splitlines() if d.strip()]
        if not dong:
            st.warning("Chưa có tin nhắn nào.")
        else:
            probs = model.predict_proba(dong)[:, 1]
            kq = pd.DataFrame({
                "Tin nhắn": [d[:90] + ("..." if len(d) > 90 else "") for d in dong],
                "Xác suất spam": probs,
                "Nhãn": np.where(probs >= nguong, "SPAM", "HAM"),
            })
            st.dataframe(kq.style.format({"Xác suất spam": "{:.2%}"}), hide_index=True,
                         width="stretch")
            st.caption(f"{(kq['Nhãn'] == 'SPAM').sum()}/{len(kq)} tin bị gắn nhãn spam ở ngưỡng {nguong:.2f}.")
