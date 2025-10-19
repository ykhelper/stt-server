import os

if __name__ == "__main__":
    if "OMP_NUM_THREADS" not in os.environ:
        os.environ["OMP_NUM_THREADS"] = str(8)

    from whisper_live.server import TranscriptionServer

    server = TranscriptionServer()
    server.run(
        "0.0.0.0",
        port=9090,
        backend="faster_whisper",
        faster_whisper_custom_model_path="/home/duk/code/stt-server/models",
        single_model=True,
    )
