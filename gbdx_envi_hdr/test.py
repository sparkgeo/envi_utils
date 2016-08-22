import os
import pytest
import shutil

from envi_hdr import EnviHdr
from constants import DG_SATID_TO_ENVI, DG_BAND_NAMES, DG_WEIGHTED_BAND_CENTERS


@pytest.fixture(scope="function")
def hdr_ctl():
    """
    The EnviHdr object for testing.
    """
    work_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp_test_dir')
    os.makedirs(work_path)

    input_path = os.path.join(work_path, 'input')
    os.makedirs(input_path)
    os.makedirs(os.path.join(input_path, 'image'))

    output_path = os.path.join(work_path, 'output')
    os.makedirs(output_path)
    os.makedirs(os.path.join(output_path, 'output_data'))

    yield EnviHdr(work_path=work_path)

    # Teardown
    shutil.rmtree(work_path)


@pytest.fixture(scope="module")
def imd_filename():
    """
    Name of the test IMD file to use.
    """
    imd_filename = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'imds', '11OCT23192252-M1BS-055168976010_01_ACOMP.imd'
    )
    return imd_filename


def test_get_imd_sensor_id(hdr_ctl, imd_filename):
    """
    Test the IMD parsing performs as expected.
    """
    try:
        sat_id, rows, cols = hdr_ctl.get_sensor_id_imd(imd_filename)
    except Exception as e:
        raise e

    assert sat_id == 'WV02_Multi'
    assert rows == '7100'
    assert cols == '8610'


def test_write_hdr_file_from_sensor(hdr_ctl, imd_filename):
    """
    Test the EnviHdr invoke function using a sensor id. Output is a *.hdr file.
    """

    # Create mock image file with same filename as the IMD file
    filename_no_ext = os.path.splitext(os.path.split(imd_filename)[1])[0]
    image_filename = os.path.join(hdr_ctl.get_input_data_port('image'), '%s.tif' % filename_no_ext)
    with open(image_filename, 'w') as img_f:
        img_f.write('Hello')

    # Set input ports with sensor_id, hack but works.
    hdr_ctl._GbdxTaskInterface__string_input_ports = {"sensor_id": "WV02_Multi"}

    hdr_ctl.invoke()

    hdr_path = os.path.join(hdr_ctl.get_output_data_port('output_data'), os.path.split(imd_filename)[1])
    hdr_filename = '%s.hdr' % os.path.splitext(hdr_path)[0]
    _check_hdr(hdr_filename)


def test_write_hdr_file(hdr_ctl, imd_filename):
    """
    Test the EnviHdr invoke function. Output is a *.hdr file.
    """

    # Create mock image file with same filename as the IMD file
    filename_no_ext = os.path.splitext(os.path.split(imd_filename)[1])[0]
    image_filename = os.path.join(hdr_ctl.get_input_data_port('image'), '%s.tif' % filename_no_ext)
    with open(image_filename, 'w') as img_f:
        img_f.write('Hello')

    # Copy IMD file to output port.
    imd_dest_filename = os.path.join(hdr_ctl.get_input_data_port('image'), os.path.split(imd_filename)[1])
    shutil.copyfile(imd_filename, imd_dest_filename)

    hdr_ctl.invoke()

    hdr_path = os.path.join(hdr_ctl.get_output_data_port('output_data'), os.path.split(imd_filename)[1])
    hdr_filename = '%s.hdr' % os.path.splitext(hdr_path)[0]
    _check_hdr(hdr_filename)


def _check_hdr(hdr_filename):
    assert os.path.isfile(hdr_filename)

    with open(hdr_filename, 'r') as f:
        has_sensor = False
        has_bands = False
        has_band_names = False
        has_wavelength = False
        for line in f:
            # Check sensor type
            if line.startswith('sensor type'):
                value = line.replace(' ', '').split('=')[1].rstrip('\n')
                assert value in DG_SATID_TO_ENVI.values()
                has_sensor = True
            # Check lines
            if line.startswith('lines'):
                value = line.replace(' ', '').split('=')[1].rstrip('\n')
                assert value == '7100'
            # Check Samples
            if line.startswith('samples'):
                value = line.replace(' ', '').split('=')[1].rstrip('\n')
                assert value == '8610'
            # Check bands
            if line.startswith('bands'):
                value = line.replace(' ', '').split('=')[1].rstrip('\n')
                assert value == '8'
                has_bands = True
            # Check band names
            if line.startswith('band names'):
                value = line.replace(' ', '').split('=')[1].rstrip('\n')
                assert value == '{%s}' % ','.join(str(e) for e in DG_BAND_NAMES['WV02_MULTI'])
                has_band_names = True
            # Check wavelengths
            if line.startswith('wavelength') and 'units' not in line:
                value = line.replace(' ', '').split('=')[1].rstrip('\n')
                assert value == '{%s}' % ','.join(str(e) for e in DG_WEIGHTED_BAND_CENTERS['WV02_MULTI'])
                has_wavelength = True

        assert has_wavelength and has_band_names and has_bands and has_sensor
