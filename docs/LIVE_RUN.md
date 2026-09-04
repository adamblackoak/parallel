# SetWatch live-run gate

The submission needs one end-to-end run in which Google ADK/Gemini calls Parallel Search at runtime. A labelled demo run is useful for UI work but does not satisfy this gate.

## Local qualification

Set the following values in `.env`:

```text
GOOGLE_CLOUD_PROJECT=<project id with billing enabled>
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=true
GEMINI_MODEL=gemini-2.5-flash
PARALLEL_API_KEY=<secret>
SETWATCH_DEMO_MODE=false
```

Authenticate Application Default Credentials and run the complete smoke test:

```powershell
gcloud auth application-default login
python .\scripts\live_agent_smoke.py
```

The gate passes only when the output contains:

- `mode: live`;
- at least one `LIVE_PARALLEL_SEARCH` trace;
- a real Parallel `search_id`;
- schema-validated findings;
- no model-cited URL that was absent from the captured Parallel results.

## Cloud Run deployment

From the repository root on Windows:

```powershell
.\scripts\deploy_cloud_run.ps1 -ProjectId <your-project-id>
```

The script enables the required APIs, stores the Parallel key in Secret Manager, creates a dedicated runtime service account, grants only Vertex AI User and secret-access roles to that account, deploys from source, and prints the service URL.

The Google hackathon voucher is not consumed by the code. It is billing credit applied to the selected Google Cloud billing account. The project must therefore have billing enabled even if the voucher is still pending.

## Submission evidence

Preserve the successful smoke-test output and capture the product's Runtime evidence panel in the video. Before submission, confirm `/health` reports `mode: live` and `live_ready: true`.
