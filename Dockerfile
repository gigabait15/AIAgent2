FROM python:3.12-slim

# 1) Рабочая директория
WORKDIR /app
ENV PYTHONPATH=/app
ENV PATH="/opt/venv/bin:$PATH"

# 2) Системные утилиты + venv + pip
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg \
      curl \
      nano\
 && python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && rm -rf /var/lib/apt/lists/*

# 3) Устанавливаем Python-зависимости
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

# 4) Копируем всё приложение
COPY . .

# 6) Экспонируем порт
EXPOSE 80

# 7) Команда старта
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]