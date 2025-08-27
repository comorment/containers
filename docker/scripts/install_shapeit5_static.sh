#!/bin/sh
set -euo pipefail

URL=https://github.com/odelaneau/shapeit5/releases/download/v5.1.1
wget ${URL}/ligate_static
mv ligate_static /usr/bin/ligate

wget ${URL}/phase_common_static
mv phase_common_static /usr/bin/phase_common

wget ${URL}/phase_rare_static
mv phase_rare_static /usr/bin/phase_rare

wget ${URL}/simulate_static
mv simulate_static /usr/bin/simulate

wget ${URL}/switch_static
mv switch_static /usr/bin/switch

wget ${URL}/xcftools_static
mv xcftools_static /usr/bin/xcftools

