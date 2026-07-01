# 🎓 Hướng Dẫn Deploy Dashboard Phân Tích Khảo Sát AI

Thư mục này chứa toàn bộ mã nguồn tinh giản, các file cấu hình và tài nguyên cần thiết để chạy Dashboard trên các máy chủ hosting, VPS hoặc nền tảng đám mây (Cloud) mà không bị lẫn dữ liệu thử nghiệm nội bộ hoặc file rác.

---

## 📂 Danh sách các file trong thư mục:
- `dashboard/app.py`: File code chính của Dashboard.
- `src/`: Thư mục mã nguồn xử lý logic pipeline, AI agents và điền Excel template.
- `Form.xlsx`: File template báo cáo chuẩn của FPT Education.
- `.streamlit/config.toml`: File cấu hình giao diện (dark mode) và bảo mật cho Streamlit.
- `requirements.txt`: Danh sách các thư viện Python cần cài đặt.
- `Dockerfile`: Cấu hình Docker phục vụ deploy tự động lên các Cloud host hoặc VPS hỗ trợ Docker.

---

## 🚀 Các Phương Án Deploy (Lên Host)

### Phương án 1: Deploy lên Streamlit Community Cloud (Miễn phí & Dễ nhất)
Nền tảng chính chủ của Streamlit hỗ trợ deploy trực tiếp từ Github hoàn toàn miễn phí.
1. Đưa toàn bộ nội dung của thư mục `survey_analytics_deploy` này lên một **GitHub Repository** mới của bạn.
2. Truy cập [share.streamlit.io](https://share.streamlit.io/) và đăng nhập bằng tài khoản Github.
3. Nhấp **"Create app"**, chọn repository vừa tạo, nhánh `main`.
4. Nhập đường dẫn file chạy chính: `dashboard/app.py`.
5. Nhấp **"Deploy!"** và đợi hệ thống tự chạy. Bạn sẽ nhận được đường dẫn dạng `https://[your-app-name].streamlit.app/` để chia sẻ cho mọi người.

### Phương án 2: Deploy bằng Docker (Khuyên dùng cho VPS / Cloud Server)
Nếu bạn có VPS riêng (như DigitalOcean, AWS, Google Cloud) hoặc các dịch vụ Hosting hỗ trợ Docker (như Render, Railway, CapRover):
1. Upload thư mục này lên server.
2. Build Docker image:
   ```bash
   docker build -t survey-analytics-app .
   ```
3. Chạy container:
   ```bash
   docker run -d -p 8501:8501 --name survey-dashboard survey-analytics-app
   ```
4. Truy cập qua địa chỉ: `http://[IP_CUA_VPS]:8501`

### Phương án 3: Deploy thủ công trên VPS (Ubuntu/Debian) sử dụng Virtualenv
Nếu bạn muốn chạy trực tiếp bằng Python trên VPS:
1. Cài đặt Python 3.10+ và Pip:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv -y
   ```
2. Di chuyển vào thư mục dự án và tạo virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Cài đặt các thư viện yêu cầu:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Chạy Dashboard dưới dạng nền (background process) bằng `nohup` hoặc công cụ quản lý tiến trình `pm2` / `systemd`:
   ```bash
   nohup streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 > app.log 2>&1 &
   ```
