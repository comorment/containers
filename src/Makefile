all: hello.sif gwas.sif python3.sif r.sif saige.sif

%.sif: dockerfiles/%/Dockerfile
	docker build -t $* -f dockerfiles/$*/Dockerfile . && \
	singularity/from_docker_image.sh $* && \
	singularity/update_image_in_repo.sh $*

# Example commands executed by this make file
# 
# Run "make hello.sif" will trigger this:
# docker build -t hello -f dockerfiles/hello/Dockerfile . && \  # build docker container
#     singularity/from_docker_image.sh hello \         # produces hello.sif
#     singularity/update_image_in_repo.sh hello        # moves hello.sif to ../singularity/.
#  
# Run "make gwas.sif" will trigger this:
# docker build -t gwas -f dockerfiles/gwas/Dockerfile . && \
#     singularity/from_docker_image.sh gwas && \       # produces gwas.sif
#     singularity/update_image_in_repo.sh gwas         # moves gwas.sif to ../singularity/.
#
