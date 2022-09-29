wget --no-check-certificate https://mathgen.stats.ox.ac.uk/genetics_software/shapeit/shapeit.v2.r904.glibcv2.17.linux.tar.gz && \
    tar -xzvf shapeit.v2.r904.glibcv2.17.linux.tar.gz && \
    mv shapeit.v2.904.3.10.0-693.11.6.el7.x86_64/* . && \
    mv bin/shapeit bin/shapeit2 && \
    chmod +x bin/shapeit2 && \
    cp bin/shapeit2 /bin


