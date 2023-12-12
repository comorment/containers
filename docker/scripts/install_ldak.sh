#!/bin/sh
set -euo pipefail

wget --no-check-certificate https://dougspeed.com/wp-content/uploads/ldak5.2.linux_.zip
unzip ldak5.2.linux_.zip
cp ldak5.2.linux /bin/ldak
