# python appears to be a build time dependency
apt-get update && apt-get install -y  --no-install-recommends python && \
    rm -rf /var/lib/apt/lists/*

# build bgen
wget http://code.enkre.net/bgen/tarball/release/bgen.tgz && \
tar -xvzf bgen.tgz && mv bgen.tgz/* . && \
./waf configure && \
./waf && \
cp build/apps/bgenix /bin && \
cp build/apps/cat-bgen /bin && \
cp build/apps/edit-bgen /bin

# remove python
apt-get purge \
    python -y && \
    apt-get autoremove --purge -y
