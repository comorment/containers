#!/bin/sh
set -euo pipefail

# gcta
VERSION="1.94.1"
curl -O -J -L https://github.com/jianyangqt/gcta/releases/download/v$VERSION/gcta-$VERSION-linux-x86_64-static && \
    mv gcta-$VERSION-linux-x86_64-static /bin/gcta64 && \
    chmod +x /bin/gcta64

