# api-doc-cache
GETs an API result and serves it up internally.

This one specifically fetches data from the OpenWeatheMap onecall API. You need an API key for that.

## Running

Copy `example.env` to `.env` and fill in your values.

### Start

```bash
docker build -t api-doc-cache:latest .
docker run -d \
  --name api-doc-cache \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  api-doc-cache:latest
```

The `--restart unless-stopped` flag ensures the container restarts automatically after a host reboot or Docker daemon restart.

### Check status / logs

```bash
docker ps
docker logs api-doc-cache
```

### Remove old/dead containers

```bash
docker rm api-doc-cache
```

The API is available at `http://localhost:8080/data`.