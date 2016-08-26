# Run atmospheric compensation on WV02 data
from gbdxtools import Interface
gbdx = Interface()

add_hdr = gbdx.Task("ENVI_HDR")
add_hdr.inputs.image = 's3://gbd-customer-data/7d8cfdb6-13ee-4a2a-bf7e-0aff4795d927/kathleen_AComp/AComp2Envi/AComp/'
# add_hdr.inputs.sensor_id = 'WV02_MULTI'  # Example of providing the sensor id as a port value.

envi_ndvi = gbdx.Task("ENVI_SpectralIndex")
envi_ndvi.inputs.input_raster = add_hdr.outputs.output_data.value
envi_ndvi.inputs.file_types = "hdr"
envi_ndvi.inputs.index = "Normalized Difference Vegetation Index"

workflow = gbdx.Workflow([add_hdr, envi_ndvi])

workflow.savedata(
    add_hdr.outputs.output_data,
    location='acomp_envi_test1/output_data'
)
workflow.savedata(
    envi_ndvi.outputs.output_raster_uri,
    location='acomp_envi_test1/output_raster_uri'
)

print workflow.execute()
