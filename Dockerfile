# Ảnh nền: Python 3.11 bản slim — nhẹ hơn bản đầy đủ khoảng 700MB
FROM python:3.11-slim

# Không ghi file .pyc, log in thẳng ra terminal (không bị giữ trong buffer)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Cài thư viện TRƯỚC khi copy code: Docker cache lại lớp này,
# nên sửa app.py về sau sẽ build lại trong vài giây thay vì cài lại từ đầu.
COPY requirements.txt requirements-notebook.txt ./
RUN pip install --upgrade pip && pip install -r requirements-notebook.txt

# Copy code, mô hình đã huấn luyện, dữ liệu và notebook
COPY app.py spam_model.pkl spam.csv sms_spam_naive_bayes.ipynb ./

EXPOSE 8501

# Kiểm tra container còn sống không (Docker tự gọi định kỳ)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8501/_stcore/health')"

# Mặc định chạy web demo. server.address=0.0.0.0 là bắt buộc,
# nếu để mặc định localhost thì bên ngoài container không truy cập được.
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
