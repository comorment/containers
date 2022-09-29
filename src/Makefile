all: hello.sif gwas.sif python3.sif r.sif saige.sif enigma-cnv.sif matlabruntime.sif

%.sif: dockerfiles/%/Dockerfile
	docker build -t $* -f dockerfiles/$*/Dockerfile . && \
	singularity/from_docker_image.sh $* \
	mv $*.sif ../singularity/$*/.

# Example commands executed by this make file
# 
# Run "make hello.sif" will trigger this:
# docker build -t hello -f dockerfiles/hello/Dockerfile . && singularity/from_docker_image.sh hello          # produces hello.sif
#  
# Run "make gwas.sif" will trigger this:
# docker build -t gwas -f dockerfiles/gwas/Dockerfile . && singularity/from_docker_image.sh gwas            # produces gwas.sif
#
#
