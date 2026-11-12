# Local AI frontend

Frontend thuần HTML/CSS/JavaScript cho workflow Local AI của Financial AI Service.

## Chạy

Khởi động Backend FastAPI ở `http://localhost:8000`, sau đó phục vụ thư mục này bằng một static server:

```powershell
python -m http.server 5173 --directory frontend
```

Mở `http://localhost:5173`. Địa chỉ Backend có thể thay đổi ở ô trên cùng.

Frontend gọi đúng các endpoint hiện có:

- `GET /datasets/`
- `POST /datasets/build` (được gọi gián tiếp khi đánh giá Dataset mới)
- `POST /local-ai/evaluations`
- `POST /local-ai/train`

Backend hiện chưa bật CORS và chưa mount static frontend. Vì vậy, khi chạy frontend ở origin khác, trình duyệt có thể chặn request CORS; cần phục vụ frontend cùng origin hoặc bật CORS ở lớp triển khai ứng dụng.
