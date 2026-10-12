#!/usr/bin/env bash
# Builds a self-contained backup of MoodQueue that can be restored years
# from now, even if npm / PyPI / Docker Hub no longer have these versions.
#
#   ./scripts/make-archive.sh            (Linux, macOS, or Git Bash on Windows)
#
# Produces archive/<date>/ with:
#   moodqueue-image.tar.gz   the complete Docker image (web + API + all dependencies)
#   moodqueue-source.tar.gz  the source code at the current commit
#   RESTORE.txt              how to bring it back to life
set -euo pipefail
cd "$(dirname "$0")/.."

DATE=$(date +%Y-%m-%d)
OUT="archive/$DATE"
mkdir -p "$OUT"

echo "==> Building image"
docker build -t "moodqueue:$DATE" -t moodqueue:latest .

echo "==> Saving image (this is the important file)"
docker save "moodqueue:$DATE" | gzip > "$OUT/moodqueue-image.tar.gz"

echo "==> Saving source code"
git archive --format=tar.gz -o "$OUT/moodqueue-source.tar.gz" HEAD

cat > "$OUT/RESTORE.txt" <<TXT
MoodQueue backup — $DATE — commit $(git rev-parse --short HEAD)

1. Install Docker (or any OCI-compatible runtime such as Podman).
2. docker load -i moodqueue-image.tar.gz
3. docker run -p 8000:8000 -v moodqueue-data:/app/data moodqueue:$DATE
4. Open http://localhost:8000

No account or API key is needed. The image is linux/$(docker version -f '{{.Server.Arch}}' 2>/dev/null || echo amd64);
on another CPU architecture use emulation (docker run --platform linux/amd64 ...).
Source code: moodqueue-source.tar.gz (see README.md inside).
TXT

echo "==> Done: $OUT"
ls -lh "$OUT"
echo "Copy this folder somewhere safe (external drive + cloud)."
