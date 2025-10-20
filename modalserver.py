import modal

BASE_MODEL = "Systran/faster-whisper-small"
MINUTES = 60

model_cache = modal.Volume.from_name("whisper-cache", create_if_missing=True)
cache_dir = "/root/.cache/whisper"

app = modal.App("whisper-live")


def download_model(repo_id: str, allow_patterns: list[str]):
    from huggingface_hub import snapshot_download

    snapshot_download(
        repo_id=repo_id,
        local_dir=cache_dir,
        allow_patterns=allow_patterns,
        ignore_patterns=["*.pt"],
    )
    model_cache.commit()


image = (
    modal.Image.from_registry(
        "ghcr.io/collabora/whisperlive-gpu:latest"
    )  # Removed add_python
    .apt_install("portaudio19-dev")
    .run_commands("apt-get clean", "rm -rf /var/lib/apt/lists/*")
    .env(
        {
            "HF_HUB_ENABLE_HF_TRANSFER": "1",
            "LD_LIBRARY_PATH": "/usr/local/lib/python3.10/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.10/site-packages/nvidia/cudnn/lib",  # Fixed to 3.10
        }
    )
    .run_function(
        download_model,
        volumes={cache_dir: model_cache},
        kwargs={"repo_id": BASE_MODEL, "allow_patterns": ["*.gguf", ".bin"]},
    )
)


@app.function(
    image=image,
    volumes={cache_dir: model_cache},
    gpu="T4",
    timeout=30 * MINUTES,
)
@modal.concurrent(max_inputs=256)
@modal.web_server(port=9090)
def serve_whisper():
    from whisper_live.server import TranscriptionServer

    server = TranscriptionServer()
    server.run(
        "0.0.0.0",
        port=9090,
        backend="faster_whisper",
        faster_whisper_custom_model_path=cache_dir,
        single_model=True,
    )
