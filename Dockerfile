FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN groupadd --system --gid 999 python \
 && useradd --system --gid 999 --uid 999 --create-home python

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

ENV UV_TOOL_BIN_DIR=/usr/local/bin

RUN apt update && apt install -y portaudio19-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

RUN mkdir /app
WORKDIR /app

COPY run_server.py /app

CMD ["python3", "run_server.py",
     "--port", "9090",
     "--backend", "faster_whisper",
     "--omp_num_threads", "4"]
