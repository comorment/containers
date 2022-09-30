all: hello.sif gwas.sif python3.sif r.sif saige.sif

%.sif: dockerfiles/%/Dockerfile
	docker build -t $* -f dockerfiles/$*/Dockerfile . && \
	scripts/convert_docker_image_to_singularity.sh $* && \
	scripts/scripts/move_singularity_file.sh.sh $*

# Example commands executed by this make file
# 
# Run "make hello.sif" will trigger this:
# docker build -t hello -f dockerfiles/hello/Dockerfile . && \  # build docker container
#     scripts/convert_docker_image_to_singularity.sh hello \         # produces hello.sif
#     scripts/scripts/move_singularity_file.sh.sh hello        # moves hello.sif to ../singularity/.
#  
# Run "make gwas.sif" will trigger this:
# docker build -t gwas -f dockerfiles/gwas/Dockerfile . && \
#     scripts/convert_docker_image_to_singularity.sh gwas && \       # produces gwas.sif
#     scripts/scripts/move_singularity_file.sh.sh gwas         # moves gwas.sif to ../singularity/.
#
