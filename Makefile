############################
#  gbdx_envi_hdr Commands  #
############################

# Build the image
build_envi_hdr:
    docker build -f gbdx_envi_hdr/Dockerfile -t sparkgeo/gbdx_envi_hdr:latest gbdx_envi_hdr/.
