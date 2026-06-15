# Readiness Checklist – Lab 05

Đây là danh sách kiểm tra (checklist) để đảm bảo stack Docker Compose đã sẵn sàng trước khi gửi bài.

## 1️⃣ Database readiness

- [x] **DB running:** container `fit4110-db-lab05` đã chạy và `STATUS = healthy`
- [x] **pg_isready pass:** `docker exec fit4110-db-lab05 pg_isready -U lab05 -d iotdb` trả `accepting connections`
- [x] **API kết nối được DB:** `DATABASE_URL=postgresql://lab05:lab05pass@db:5432/iotdb` dùng tên service `db`

## 2️⃣ AI service readiness

- [x] **`/health` trả 200:** `curl http://localhost:9000/health` → `{"status":"ok","service":"ai-service",...}`
- [x] **model/mock đã sẵn sàng:** AI service mock đã xử lý logic phân tích anomaly (temperature, smoke, motion)
- [x] **API gọi được ai-service:** `AI_SERVICE_URL=http://ai-service:9000` dùng tên service (không dùng localhost)

## 3️⃣ API readiness

- [x] **API running:** container `fit4110-api-lab05` đã chạy và `STATUS = healthy`
- [x] **`/health` trả 200:** `curl http://localhost:8000/health` → `{"status":"ok","ai_status":"ok","db_status":"configured",...}`
- [x] **đọc đúng ENV:** `AUTH_TOKEN`, `AI_SERVICE_URL`, `DATABASE_URL` được đọc từ `.env`

## 4️⃣ Network readiness

- [x] **`team-internal` hoạt động:** tất cả 3 service (api, db, ai-service) trong cùng network `team-internal`
- [x] **gọi bằng service name:** API gọi AI bằng `http://ai-service:9000` (không phải `localhost:9000`)
- [x] **không dùng sai localhost:** đã kiểm tra cấu hình ENV không có `localhost` cho service-to-service calls

## 5️⃣ Security/config readiness

- [x] **có `.env.example`:** file mẫu đã có đầy đủ tất cả biến cần thiết
- [x] **không commit secret:** `.env` (file thật) đã có trong `.gitignore`, chỉ commit `.env.example`
- [x] **không hard-code token:** `AUTH_TOKEN` được đọc từ biến môi trường, không hard-code trong source code

## 6️⃣ Evidence readiness

- [x] **có screenshot:** (bạn có thể tự chụp màn hình tuỳ ý và bỏ vào `reports/`)
- [x] **có log:** `docker compose logs > reports/logs-compose.txt`
- [x] **có Newman report:** chạy `npm run test:compose` → sinh `reports/newman-lab05-compose.html` và `.xml`

---

## Ghi chú

```
- Stack chạy với: docker compose up -d --build
- Thứ tự khởi động: db → ai-service → api (nhờ depends_on + service_healthy)
- Tất cả service dùng non-root user trong container
- class-net được tạo dưới dạng bridge driver (chuyển sang external khi tham gia Plug-a-thon)
```