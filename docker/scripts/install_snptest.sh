#!/bin/sh
set -euo pipefail

# snptest
wget --no-check-certificate http://www.well.ox.ac.uk/~gav/resources/snptest_v2.5.6_CentOS_Linux7.8-x86_64_dynamic.tgz
tar -xvzf snptest_v2.5.6_CentOS_Linux7.8-x86_64_dynamic.tgz
cp snptest_v2.5.6_CentOS_Linux7.8.2003-x86_64_dynamic/snptest_v2.5.6 /bin/snptest
