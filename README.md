# Bộ lọc SMS Spam bằng Multinomial Naive Bayes

Web demo Streamlit phân loại tin nhắn SMS là spam hay tin thường (ham), dùng mô hình Multinomial Naive Bayes kết hợp Bag-of-Words (`CountVectorizer`, unigram + bigram). Model được huấn luyện trên bộ dữ liệu SMS Spam Collection (UCI, 5.572 tin nhắn tiếng Anh đã gán nhãn), đạt F1 = 0,9444 trên tập test.

**Lưu ý quan trọng:** đây là công cụ hỗ trợ lọc sơ bộ tin nhắn tiếng Anh, không đảm bảo chính xác tuyệt đối và không nên dùng làm cơ chế bảo mật/chặn tin nhắn duy nhất.

## Chạy cục bộ

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-notebook.txt
jupyter notebook sms_spam_naive_bayes.ipynb   # tuỳ chọn: chạy lại để tái tạo spam_model.pkl, file này đã có sẵn
streamlit run app.py
```

## Chạy bằng Docker

```
docker compose up --build
```

Model **đã được huấn luyện sẵn và commit trong repo** (`spam_model.pkl`), không train lại lúc build image — Dockerfile chỉ cài đúng phiên bản thư viện đã ghim (`requirements.txt`, khớp scikit-learn 1.9.0) rồi copy model vào. Mở `http://localhost:8501`.

## Dữ liệu đầu vào / đầu ra

Ứng dụng nhận **văn bản SMS tiếng Anh** nhập trực tiếp trên giao diện web (không qua API JSON). Pipeline tự động vector hoá văn bản thô, không cần tiền xử lý thủ công trước khi đưa vào model.

Đầu ra:

- Nhãn `SPAM` hoặc `HAM`, so theo ngưỡng xác suất (mặc định 0,5, chỉnh được ở thanh trượt sidebar).
- Xác suất là spam (`predict_proba`).
- Bảng các từ/cụm từ ảnh hưởng mạnh nhất tới quyết định (log-odds dương → nghiêng spam, âm → nghiêng ham).

## Giao diện

- **Kiểm tra một tin nhắn**: chọn ví dụ có sẵn hoặc tự nhập, bấm "Phân loại" để xem nhãn, xác suất và các từ ảnh hưởng.
- **Kiểm tra hàng loạt**: dán nhiều dòng, mỗi dòng một tin nhắn, phân loại cùng lúc.
- Sidebar: chỉnh ngưỡng gán nhãn spam, xem sẵn Precision/Recall/F1 đo trên tập test (0,9835 / 0,9084 / 0,9444).

Mỗi kết quả chỉ nên xem là gợi ý phân loại sơ bộ, tin nghi ngờ nên được người dùng tự kiểm tra lại trước khi xoá.

## Kiểm thử

Dự án hiện chưa có bộ test tự động (pytest). Việc đánh giá model được thực hiện trong notebook (Bước 8–9): `classification_report`, ma trận nhầm lẫn, đường cong Precision-Recall/ROC, và so sánh với baseline (`DummyClassifier`) trên tập test giữ riêng khỏi quá trình huấn luyện.
