# Hosted demo

The app is container-ready. No paid infrastructure has been provisioned.

1. Obtain an approved Qloo hackathon key. The key request is pending and may take a few business days.
2. Connect this repository to a Python/container host with an existing authorized account, managed HTTPS, secret environment variables and edge rate limiting.
3. Use the Dockerfile or Render blueprint. Keep one instance/process while using process-local quotas. Add QLOO_API_KEY through the host's secret settings; never put it into frontend code, build arguments or Git.
4. Open /api/status. `live_configured` means a key exists; it does not mean it was verified.
5. Search real movies for two participants, run both policies, inspect source positions and failure handling, and record a redacted verification note. Never commit raw Qloo data.
6. Verify a judge can open the public app without supplying a paid account or key. Put its URL in README and the Devpost entry before final submission.

Local build:
```
docker build -t commonground .
docker run --rm -p 8790:8790 -e QLOO_API_KEY commonground
```
The container uses Python's standard-library HTTP server for a bounded demo behind the host's HTTPS proxy. This is not a hardened production server. Configure a hard cloud spending cap and provider quotas before exposing live calls. The application has no persistent data volume.
