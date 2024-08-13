#!/bin/sh
set -euo pipefail

wget https://github.com/dougspeed/LDAK/blob/4ee871be17d8ea406494211638a5ead677e7dd47/ldak6.linux
chmod +x ldak6.linux
cp ldak6.linux /bin/ldak
