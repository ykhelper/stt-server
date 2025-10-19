from whisper_live.client import TranscriptionClient

if __name__ == "__main__":
    client = TranscriptionClient(
        "127.0.0.1",
        9090,
        lang="en",
        model="Systran/faster-whisper-small",
        use_vad=True,
        save_output_recording=False,
    )
    client()
