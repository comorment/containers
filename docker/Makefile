all: hello.sif gwas.sif python3.sif r.sif saige.sif

%.sif: dockerfiles/%/Dockerfile
	scripts/build_docker.sh $* && \
	scripts/convert_docker_image_to_singularity.sh $* && \
	scripts/move_singularity_file.sh $*

# Example commands executed by this make file
# 
# Run "make hello.sif" will trigger this:
# docker scripts/build_docker.sh hello && \  # build docker image
#     scripts/convert_docker_image_to_singularity.sh hello && \         # produces hello.sif
#     scripts/move_singularity_file.sh hello        # moves hello.sif to ../singularity/.
#  
# Run "make gwas.sif" will trigger this:
# docker scripts/build_docker.sh gwas && \  # build docker image
#     scripts/convert_docker_image_to_singularity.sh gwas && \  # produces gwas.sif
#     scripts/move_singularity_file.sh gwas   # moves gwas.sif to ../singularity/.
#
# Build logs are stored in the ./logs/ directory