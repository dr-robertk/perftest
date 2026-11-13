FROM python:3.12-slim

# git is required by pytest-benchmark to read commit_info (commit sha, branch, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Pin pytest <9.2.0: pytest-benchmark 5.3.0 breaks on it (relies on a private
# pytest attribute removed in 9.2.0) - same pin used in pyproject.toml and CI.
RUN pip install --no-cache-dir \
    numpy scipy psycopg2-binary \
    "pytest>=9.1.1,<9.2.0" "pytest-benchmark>=5.3.0"

COPY run_local_baseline.sh /usr/local/bin/run_local_baseline.sh
RUN chmod +x /usr/local/bin/run_local_baseline.sh

# The actual repo is bind-mounted to /app at runtime (see docker-compose.yml)
# rather than baked in, so `git pull` on the host takes effect on the next
# loop iteration without rebuilding the image, and pytest-benchmark can read
# the real .git history for commit_info.
WORKDIR /app

ENTRYPOINT ["/usr/local/bin/run_local_baseline.sh"]
