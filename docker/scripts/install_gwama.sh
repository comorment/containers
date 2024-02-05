#!/bin/sh
set -euo pipefail

apt-get update && apt-get install -y --no-install-recommends \
    gwama=2.2.2+dfsg-2build1 \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
