.PHONY: install lint build run compose-up compose-down logs test-compose health evidence

# Install Node dependencies for Newman/Prism/Spectral
install:
	npm install

# Lint OpenAPI contracts with Spectral
lint:
	npx spectral lint contracts/*.yaml

# Build Docker images
build:
	docker compose build

# Run API container standalone (không qua compose, để test nhanh)
run:
	docker run --rm --name fit4110-api-lab05 -p 8000:8000 --env-file .env fit4110/iot-ingestion:v0.1.0-lab05

# ─── Compose commands ────────────────────────────────────────────
compose-up:
	docker compose up -d --build

compose-down:
	docker compose down

compose-down-volumes:
	docker compose down -v

logs:
	docker compose logs -f

# Kiểm tra readiness từng service
health:
	@echo "=== API health ===" && curl -s http://localhost:8000/health | python -m json.tool
	@echo "\n=== AI service health ===" && curl -s http://localhost:9000/health | python -m json.tool
	@echo "\n=== DB readiness ===" && docker exec fit4110-db-lab05 pg_isready -U lab05 -d iotdb
	@echo "\n=== Compose status ===" && docker compose ps

# Chạy Newman test trên compose stack
test-compose:
	npm run test:compose

# Thu thập evidence vào reports/
evidence:
	docker compose logs > reports/logs-compose.txt
	docker compose ps >> reports/logs-compose.txt
	@echo "Evidence saved to reports/logs-compose.txt"