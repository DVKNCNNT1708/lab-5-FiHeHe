# RUN_COMPOSE.md – Hướng dẫn chạy Lab 05

Tài liệu này hướng dẫn người khác **clone repo sạch và chạy lại toàn bộ stack** Compose của Lab 05 từ đầu đến cuối.

---

## Yêu cầu cài đặt

| Công cụ | Phiên bản tối thiểu | Kiểm tra |
|---|---|---|
| Docker Desktop (hoặc Docker Engine) | 24.x + Compose v2 | `docker compose version` |
| Git | Bất kỳ | `git --version` |
| Node.js (để chạy Newman) | 20.x LTS | `node --version` |

---

## Bước 1 – Clone repo

```bash
git clone <repo-url>
cd lab-5-docker-compose
```

---

## Bước 2 – Cấu hình môi trường

```bash
# Sao chép file cấu hình mẫu
cp .env.example .env
```

> ⚠️ **QUAN TRỌNG:** Không thay đổi `AI_SERVICE_URL` và `DATABASE_URL` thành `localhost`.
> Các service giao tiếp qua **tên service** trong Docker network:
> - `AI_SERVICE_URL=http://ai-service:9000` ✅
> - `DATABASE_URL=postgresql://lab05:lab05pass@db:5432/iotdb` ✅

---

## Bước 3 – Cài Node.js dependencies (để chạy Newman)

```bash
npm install
```

---

## Bước 4 – Build & chạy stack Docker Compose

```bash
docker compose up -d --build
```

Lệnh này sẽ:
1. Build image `fit4110/iot-ingestion:v0.1.0-lab05` cho API
2. Build image `fit4110/ai-service:v0.1.0-lab05` cho AI service
3. Pull image `postgres:15-alpine` cho DB
4. Khởi động theo thứ tự: **`db` → `ai-service` → `api`** (nhờ `depends_on` + `service_healthy`)

Theo dõi log real-time:

```bash
docker compose logs -f
```

---

## Bước 5 – Kiểm tra trạng thái containers

```bash
docker compose ps
```

Tất cả service phải có `STATUS = healthy`:

```
NAME                    STATUS
fit4110-db-lab05        Up (healthy)
fit4110-ai-lab05        Up (healthy)
fit4110-api-lab05       Up (healthy)
```

---

## Bước 6 – Kiểm tra readiness từng service

```bash
# API readiness
curl http://localhost:8000/health
# Kỳ vọng: {"status":"ok","service":"iot-ingestion","ai_status":"ok","db_status":"configured",...}

# AI service readiness
curl http://localhost:9000/health
# Kỳ vọng: {"status":"ok","service":"ai-service",...}

# DB readiness
docker exec fit4110-db-lab05 pg_isready -U lab05 -d iotdb
# Kỳ vọng: /var/run/postgresql:5432 - accepting connections

# Thử AI predict endpoint
curl -X POST http://localhost:9000/predict \
  -H "Content-Type: application/json" \
  -d '{"device_id":"ESP32-TEST","metric":"temperature","value":75.0}'
```

---

## Bước 7 – Chạy Newman test

```bash
npm run test:compose
```

Report tự động sinh ra tại:
- `reports/newman-lab05-compose.html` (HTML đẹp)
- `reports/newman-lab05-compose.xml` (JUnit XML)

---

## Lệnh nhanh bằng Makefile

```bash
make compose-up      # build & chạy stack
make compose-down    # dừng và xoá containers
make logs            # xem log real-time
make test-compose    # chạy Newman test
```

---

## Dừng stack

```bash
# Dừng containers (giữ nguyên volume DB)
docker compose down

# Dừng và xoá volume DB (reset hoàn toàn)
docker compose down -v
```

---

## Mẹo gỡ lỗi

| Vấn đề | Cách xử lý |
|---|---|
| API không start được | Kiểm tra `db` và `ai-service` đã `healthy` chưa bằng `docker compose ps` |
| Lỗi "Connection refused" đến DB | Đảm bảo `DATABASE_URL` dùng `db:5432` không phải `localhost:5432` |
| AI service không phản hồi | Kiểm tra log: `docker compose logs ai-service` |
| Newman test fail | Đảm bảo stack đang chạy trước khi chạy Newman |
| `class-net` error | `class-net` đã được cấu hình là bridge driver – không cần tạo thủ công |

---

## Lưu log để làm evidence

```bash
docker compose logs > reports/logs-compose.txt
docker compose ps >> reports/logs-compose.txt
```