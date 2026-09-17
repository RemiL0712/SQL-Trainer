FROM python:3.12-slim

WORKDIR /app
COPY server.py content.py curriculum_extra.py app.js style.css index.html favicon.svg ./
RUN useradd --system --uid 10001 sqlstudio && mkdir /data && chown sqlstudio:sqlstudio /data

USER sqlstudio
ENV HOST=0.0.0.0 PORT=8000 DB_PATH=/data/progress.sqlite3
EXPOSE 8000
CMD ["python", "server.py"]
