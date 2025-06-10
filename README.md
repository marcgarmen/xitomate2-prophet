# xitomate2-prophet


xitomate2-prophet provides forecasting capabilities using [Facebook Prophet](https://github.com/facebook/prophet). It exposes a FastAPI service that can forecast sales totals or ingredient usage for a week into the future.

## Local development

Install dependencies and run the service with:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The service listens on port `8000` locally and exposes a single `/forecast` endpoint.
Requests that fail during forecasting will now raise an HTTP `500` error with a
JSON body describing the issue.

## Deploying to Cloud Run

When building for Cloud Run use the provided `Dockerfile`. The container reads the `PORT` environment variable and defaults to `8080` if not set. A minimal deployment command would look like:

```bash
gcloud run deploy xitomate2-prophet \
  --source . \
  --platform managed \
  --region <your-region> \
  --allow-unauthenticated
```

Set the environment variable `PROPHET_URL` in your xitomate-2 instance to the deployed service URL so the two services can communicate.
