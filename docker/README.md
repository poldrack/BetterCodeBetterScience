# Docker for BetterCodeBetterScience

## Building the image

From the repository root:

```bash
docker build -f docker/Dockerfile -t bettercode .
```

## Running the container

Interactive shell:
```bash
docker run -it bettercode /bin/bash
```

Run tests:
```bash
docker run bettercode pytest
```

Mount local data directory:
```bash
docker run -v /path/to/local/data:/data bettercode python script.py
```
