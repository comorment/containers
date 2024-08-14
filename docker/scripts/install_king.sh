#!/bin/sh
set -euo pipefail

# king
VERSION="232"
wget --debug --no-check-certificate --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/83.0.4103.61 Chrome/83.0.4103.61 Safari/537.36" https://www.kingrelatedness.com/executables/Linux-king$VERSION.tar.gz && \
    tar -xvzf Linux-king$VERSION.tar.gz && \
    rm -rf Linux-king$VERSION.tar.gz

cp king  /bin

rm -rf *