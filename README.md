# envi_utils

Some utilities for working with ENVI.

## Header file Creation

The `gbdx_envi_hdr` contains a gbdx task that will take a raster input and create an ENVI header file with the associated wavelength data.

The function will proceed in this order:

- If \*.IMD or \*.XML file exists with same name as \*.TIF, parse to find satellite id
- Else, the task port `satellite_name` must be provided.

Valid satellites and band names are:

```
DG_BAND_NAMES = {
    'QB02_MULTI' :  ['B','G','R','N1'],
    'QB02_P' :      ['P'],
    'IK02_MULTI' :  ['B','G','R','N1'],
    'IK02_P' :      ['P'],
    'GE01_MULTI' :  ['B','G','R','N1'],
    'GE01_P' :      ['P'],
    'WV01_P' :      ['P'],
    'WV02_MULTI' :  ['C','B','G','Y','R','RE','N1','N2'],
    'WV02_MS1' :    ['B','G','R','N1'],
    'WV02_MS2' :    ['C','Y','RE','N2'],
    'WV02_P' :      ['P'],
    'WV03_MULTI' :  ['C','B','G','Y','R','RE','N1','N2'],
    'WV03_MS1' :    ['B','G','R','N1'],
    'WV03_MS2' :    ['C','Y','RE','N2'],
    'WV03_P' :      ['P'],
    'WV03_ALL-S' :  ['S1','S2','S3','S4','S5','S6','S7','S8']
}
```

Valid satellites and band centers are:

```
DG_WEIGHTED_BAND_CENTERS = {
    'QB02_MULTI' : [478.40,542.89,650.45,803.41],
    'QB02_P' :     [674.58],
    'IK02_MULTI' : [483.07,550.62,663.25,794.37],
    'IK02_P' :     [723.00],
    'GE01_MULTI' : [484.52,547.87,675.20,836.52],
    'GE01_P' :     [631.79],
    'WV01_P' :     [670.17],
    'WV02_MULTI' : [428.58,479.35,548.07,607.78,658.92,723.27,825.06,914.55],
    'WV02_MS1' :   [479.35,548.07,658.92,825.06],
    'WV02_P' :     [651.05],
    'WV03_MULTI' : [427.38,481.92,547.14,604.28, \
                    660.11,722.73,824.04,913.65],
    'WV03_MS1' :   [481.92,547.14, \
                    660.11,824.04],
    'WV03_P' :     [649.36],
    'WV03_ALL-S' : [1209.06,1571.61,1661.10,1729.54, \
                    2163.69,2202.16,2259.32,2329.22]
}
```

These values are from the gbdx geoio library, https://github.com/DigitalGlobe/geoio/blob/master/geoio/constants.py.
