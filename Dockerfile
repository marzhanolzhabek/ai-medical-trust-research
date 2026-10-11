FROM python:3.12.8-slim-bookworm
WORKDIR /app
COPY . /app
RUN python -m compileall -q src
CMD ["python", "src/benchmark.py", "--config", "configs/config.json"]
