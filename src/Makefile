all: hello.sif gwas.sif python3.sif r.sif saige.sif enigma-cnv.sif matlabruntime.sif

%.sif: containers/%/Dockerfile
	docker build -t $* -f containers/$*/Dockerfile . && singularity/from_docker_image.sh $*

# Example commands executed by this make file
# 
# Run "make hello.sif" will trigger this:
# docker build -t hello -f containers/hello/Dockerfile . && singularity/from_docker_image.sh hello          # produces hello.sif
#  
# Run "make gwas.sif" will trigger this:
# docker build -t gwas -f containers/gwas/Dockerfile . && singularity/from_docker_image.sh gwas            # produces gwas.sif
#
#
