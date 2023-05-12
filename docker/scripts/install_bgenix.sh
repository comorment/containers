# python appears to be a build time dependency
apt-get update && apt-get install -y  --no-install-recommends python3=3.8.2-0ubuntu2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# /usr/bin/python must exist
update-alternatives --install /usr/bin/python python /usr/bin/python3 10

# build bgen
wget http://code.enkre.net/bgen/tarball/release/bgen.tgz && \
    tar -xvzf bgen.tgz && mv bgen.tgz/* . && \
    ./waf configure && \
    ./waf -v
# copy binaries
cp build/apps/bgenix /bin && \
    cp build/apps/cat-bgen /bin && \
    cp build/apps/edit-bgen /bin

# remove python
apt-get purge \
    python3 -y && \
    apt-get autoremove --purge -y
