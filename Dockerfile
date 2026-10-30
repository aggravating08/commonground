FROM python:3.12-slim
WORKDIR /app
COPY engine.py server.py ./
COPY web ./web
RUN useradd --uid 10001 --create-home app
USER app
ENV HOST=0.0.0.0 PORT=8790
EXPOSE 8790
CMD ["python", "server.py"]
