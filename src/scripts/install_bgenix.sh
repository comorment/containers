wget http://code.enkre.net/bgen/tarball/release/bgen.tgz && \
tar -xvzf bgen.tgz && mv bgen.tgz/* . && \
./waf configure && \
./waf && \
cp build/apps/bgenix /bin && \
cp build/apps/cat-bgen /bin && \
cp build/apps/edit-bgen /bin

