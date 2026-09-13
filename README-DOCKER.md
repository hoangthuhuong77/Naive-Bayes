# Đóng gói và chuyển sang máy khác bằng Docker

Toàn bộ project (code, mô hình đã huấn luyện, dữ liệu, notebook, thư viện) nằm gọn trong một image Docker.
Máy nhận **không cần cài Python hay thư viện gì**, chỉ cần có Docker.

## Các file phục vụ đóng gói

| File | Vai trò |
|---|---|
| `Dockerfile` | Công thức dựng image |
| `.dockerignore` | Loại file rác khỏi image (`__pycache__`, `.ipynb_checkpoints`, `*.tar`...) |
| `requirements.txt` | Thư viện chạy web demo, đã ghim phiên bản |
| `requirements-notebook.txt` | Thêm matplotlib, seaborn, wordcloud, JupyterLab để chạy lại notebook |
| `docker-compose.yml` | Chạy bằng một lệnh, không cần nhớ tham số |

> **Vì sao phải ghim phiên bản?** `spam_model.pkl` được lưu bằng scikit-learn 1.9.0. Nạp lại bằng phiên bản
> khác có thể cảnh báo hoặc cho kết quả sai, nên `requirements.txt` ghim đúng số phiên bản.

---

## 1. Build image (trên máy hiện tại)

```bash
cd F:\Naive_Bayes
docker build -t sms-spam-nb:1.1 .
```

Lần đầu mất khoảng 3 phút (chủ yếu tải thư viện). Image nặng **1,44 GB**.

## 2. Chạy thử

```bash
docker run -d --name sms-spam -p 8501:8501 sms-spam-nb:1.1
```

Mở <http://localhost:8501>. Hoặc dùng compose cho gọn:

```bash
docker compose up -d        # chạy
docker compose down         # dừng và xoá container
```

Lệnh hữu ích:

```bash
docker ps                   # xem container đang chạy và trạng thái healthy
docker logs -f sms-spam     # xem log
docker stop sms-spam        # dừng
docker rm -f sms-spam       # xoá container
```

## 3. Chạy notebook trong container (tuỳ chọn)

Image đã có sẵn JupyterLab:

```bash
docker run -d --name sms-lab -p 8888:8888 sms-spam-nb:1.1 \
  jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.token=''
```

Mở <http://localhost:8888> để chạy lại `sms_spam_naive_bayes.ipynb`.

Muốn file sửa trong container được lưu ra máy thật thì gắn thêm volume:

```bash
docker run -d --name sms-lab -p 8888:8888 -v "%cd%:/app" sms-spam-nb:1.1 \
  jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.token=''
```

---

## 4. Gửi sang máy khác — 3 cách

### Cách A: file `.tar` (không cần Internet, không cần tài khoản)

Trên máy gửi:

```bash
docker save sms-spam-nb:1.1 -o sms-spam-nb.tar     # ra file 310 MB, mất ~9 giây
```

Chép `sms-spam-nb.tar` qua USB / Google Drive / mạng LAN. Trên máy nhận:

```bash
docker load -i sms-spam-nb.tar                     # ~20 giây
docker run -d --name sms-spam -p 8501:8501 sms-spam-nb:1.1
```

Mở <http://localhost:8501>. Xong — không cài Python, không `pip install` gì cả.

### Cách B: Docker Hub (máy nhận chỉ cần một lệnh)

```bash
# Máy gửi
docker login
docker tag sms-spam-nb:1.1 <tên-tài-khoản>/sms-spam-nb:1.1
docker push <tên-tài-khoản>/sms-spam-nb:1.1

# Máy nhận
docker run -d -p 8501:8501 <tên-tài-khoản>/sms-spam-nb:1.1
```

Lưu ý: repository miễn phí trên Docker Hub là **công khai**, ai cũng tải được.

### Cách C: gửi source code, máy nhận tự build

Chép cả thư mục (hoặc đẩy lên Git) rồi ở máy nhận:

```bash
docker build -t sms-spam-nb:1.1 .
docker compose up -d
```

Nhẹ khi truyền (vài MB) nhưng máy nhận cần Internet để tải thư viện.

**So sánh nhanh:**

| | Dung lượng truyền | Máy nhận cần Internet | Chắc chắn chạy giống hệt |
|---|---|---|---|
| A — file `.tar` | 310 MB | Không | Có |
| B — Docker Hub | 310 MB (tự tải) | Có | Có |
| C — source code | ~3 MB | Có | Gần như (phiên bản đã ghim) |

---

## 5. Lỗi hay gặp

| Triệu chứng | Nguyên nhân / cách xử lý |
|---|---|
| `failed to connect to the docker API` | Docker Desktop chưa chạy. Mở Docker Desktop rồi thử lại. |
| Mở `localhost:8501` không lên | Thiếu `-p 8501:8501`, hoặc port đã bị chiếm. Đổi sang `-p 8600:8501` rồi mở `localhost:8600`. |
| Web trắng trang trong container | Thiếu `--server.address=0.0.0.0` (Dockerfile đã có sẵn). |
| Máy nhận dùng chip ARM (Mac M1/M2/M3) | Image build trên x86 sẽ chạy chậm qua giả lập. Build đa kiến trúc: `docker buildx build --platform linux/amd64,linux/arm64 -t sms-spam-nb:1.1 .` |
| Muốn image nhẹ hơn | Bỏ `requirements-notebook.txt` trong Dockerfile, chỉ cài `requirements.txt` — image còn khoảng 700 MB nhưng không chạy được notebook. |

---

## Đã kiểm chứng

Toàn bộ quy trình dưới đây đã chạy thật trên máy này:

- `docker build` → thành công, image 1,44 GB.
- `docker run` → web lên sau 2 giây, healthcheck báo `healthy`.
- Dự đoán trong container: tin spam → 1,0000; tin thường → 0,0002. scikit-learn trong container đúng 1.9.0.
- `docker save` → file 310 MB (9 giây). Xoá sạch image → `docker load` (19 giây) → chạy lại → web lên bình thường.
