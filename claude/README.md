
# Claude SDK 
- [https://code.claude.com/docs/en/agent-sdk/quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart)
- [https://platform.claude.com/dashboard](https://platform.claude.com/dashboard)
- [https://www.youtube.com/watch?v=TqC1qOfiVcQ](https://www.youtube.com/watch?v=TqC1qOfiVcQ)
- [https://www.youtube.com/watch?v=ChaQ_tZDBFg](https://www.youtube.com/watch?v=ChaQ_tZDBFg)

## MongoDB session storage

The custom store used by `examples/tool-custom-calls.py` persists SDK session
transcripts in MongoDB. Start the local replica set before running the example:

```bash
docker compose up -d
uv run python examples/tool-custom-calls.py
```

The compose file binds MongoDB only to `127.0.0.1:27017`. The defaults are in
`.env.example`; copy the variables to `.env` or export them when using another
MongoDB deployment. The replica set is required for atomic transcript and
summary updates.
