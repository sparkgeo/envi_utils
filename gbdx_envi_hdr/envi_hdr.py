import os
import sys
import logging
import glob2
import collections
from glob import glob
from shutil import copyfile

from constants import DG_SATID_TO_ENVI, DG_BAND_NAMES, DG_WEIGHTED_BAND_CENTERS, DG_WAVELENGTH_UNITS, RGB_BANDS
from gbdx_task_interface import GbdxTaskInterface


class MetaDataError(Exception):
    # An exception for when proper metadata is not provided.
    pass


class EnviHdr(GbdxTaskInterface):

    # Set-up logger
    logger = logging.getLogger('envi_hdr')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # Log to stdout
    std_out = logging.StreamHandler(sys.stdout)
    std_out.setLevel(logging.DEBUG)
    std_out.setFormatter(formatter)
    logger.addHandler(std_out)

    def invoke(self):
        image_port_path = self.get_input_data_port('image')
        output_port_path = self.get_output_data_port('output_data')

        try:
            os.makedirs(output_port_path)
        except OSError as e:
            self.logger.exception(e)
            if 'file exists' not in e.strerror.lower():
                raise e
            else:
                pass

        # Log to file
        hdlr = logging.FileHandler(os.path.join(output_port_path, 'envi_hdr.log'))
        hdlr.setLevel(logging.DEBUG)
        hdlr.setFormatter(self.formatter)
        self.logger.addHandler(hdlr)

        self.logger.debug("Start Log: ")

        all_files_lower = glob2.glob('%s/**/*.tif' % image_port_path)
        all_files_upper = glob2.glob('%s/**/*.TIF' % image_port_path)
        all_files = all_files_lower + all_files_upper

        if len(all_files) == 0:
            msg = "No image files found in image port."
            self.logger.error(msg)
            raise ValueError(msg)

        self.logger.debug("%s Images found" % len(all_files))

        for img_file in all_files:
            self.logger.debug('Input Image: %s' % img_file)
            new_output_port_path = os.path.join(output_port_path, os.path.split(img_file)[0][len(image_port_path)+1:])
            self.logger.debug('Output_path: %s' % new_output_port_path)
            try:
                self.create_hdr(
                    img_file,
                    new_output_port_path
                )
            except Exception as e:
                self.logger.exception(e)

        self.reason = 'Successfully created Header files'

    def create_hdr(self, img_path, output_port_path):
        # img_path must be a path to the .tif file of an image product
        filename = os.path.split(img_path)[1]
        new_filename = '%s.hdr' % os.path.splitext(filename)[0]

        try:
            os.makedirs(output_port_path)
        except:
            pass

        imd_filename = None
        xml_filename = None

        # Copy input files to output
        for fname in glob('%s.*' % os.path.splitext(img_path)[0]):
            # Save the IMD filename
            if os.path.splitext(fname)[1].lower() == '.imd':
                imd_filename = fname
                self.logger.debug('IMD: %s' % imd_filename)
            # Save the XML filename
            elif os.path.splitext(fname)[1].lower() == '.xml':
                xml_filename = fname
                self.logger.debug('XML: %s' % xml_filename)

            dest = os.path.join(output_port_path, os.path.split(fname)[1])
            copyfile(fname, dest)
            self.logger.debug('%s -> %s' % (fname, dest))

        # Check if sensor id has been provided
        sensor_port_value = self.get_input_string_port('sensor_id')

        # create empty hdr file
        hdr_file = open(os.path.join(output_port_path, new_filename), "w+")
        self.logger.debug('New hdr file: %s' % hdr_file)

        if sensor_port_value is None:
            # Read from IMD first
            if imd_filename is not None:
                sat_id, rows, cols = self.get_sensor_id_imd(imd_filename)
                self.write_header_data(sat_id, rows, cols, hdr_file)
            elif xml_filename is not None:
                sat_id, rows, cols = self.get_sensor_id_xml(xml_filename)
                self.write_header_data(sat_id, rows, cols, hdr_file)
            else:
                raise MetaDataError(
                    """Proper MetaData was not provided. The image must have IMD or XML file of the same name
                    with the statellite id. Or the satellite id can be provided as a port value."""
                )
        else:
            self.write_header_data(sensor_port_value, None, None, hdr_file)

    def get_sensor_id_imd(self, filename):
        # Keys for IMD data
        sat_id = 'satId'
        band_id = 'bandId'
        row_key = 'numRows'
        col_key = 'numColumns'

        sat_id_value = None
        band_id_value = None
        rows = None
        cols = None

        with open(filename, 'r') as f:
            count = 0
            for line in f:
                count += 1
                raw_str = line.replace(' ', '').replace('\t', '')\
                    .replace('\n', '').replace(';', '').replace('\"', '')
                if raw_str.startswith(sat_id):
                    sat_id_value = raw_str.split('=')[1]
                    self.logger.debug('satId: %s' % sat_id_value)
                if raw_str.startswith(band_id):
                    band_id_value = raw_str.split('=')[1]
                    self.logger.debug('bandId: %s' % band_id_value)
                if raw_str.startswith(row_key):
                    rows = raw_str.split('=')[1]
                    self.logger.debug('Rows: %s' % rows)
                if raw_str.startswith(col_key):
                    cols = raw_str.split('=')[1]
                    self.logger.debug('Cols: %s' % cols)
            self.logger.debug('Total lines in IMD: %s' % count)

        if not all([sat_id_value, band_id_value, rows, cols]):
            raise MetaDataError('Proper metadata not found in IMD file.')

        return '%s_%s' % (sat_id_value, band_id_value), rows, cols

    def get_sensor_id_xml(self, filename):
        # return file_obj
        raise NotImplementedError()

    def write_header_data(self, sat_id, rows, cols, hdr_file):

        # Get Band names and wavelengths
        band_names = DG_BAND_NAMES[sat_id.upper()]
        band_centers = DG_WEIGHTED_BAND_CENTERS[sat_id.upper()]

        self.logger.debug('Band Names: %s' % band_names)
        self.logger.debug('Band centers: %s' % band_centers)

        # Add fixed values hdr line
        hdr_file.write('ENVI\n')

        # Create ordered dict to have some control over writing order
        envi_dict = collections.OrderedDict()

        # Add elements to the ODict
        envi_dict['description'] = '{Creating ENVI hdr file from image data}'
        envi_dict['sensor type'] = DG_SATID_TO_ENVI[sat_id.split('_')[0]]

        if rows is not None and cols is not None:
            envi_dict['lines'] = str(rows)
            envi_dict['samples'] = str(cols)

        envi_dict['bands'] = str(len(band_names))

        if envi_dict['bands'] == '3':  # Condition for RGB images??
            band_indexes = [i for i, v in enumerate(band_names) if v in RGB_BANDS]
            band_wavelengths = [band_centers[index] for index in band_indexes]
            envi_dict['band names'] = '{%s}' % ', '.join(RGB_BANDS)
            envi_dict['wavelength'] = '{%s}' % ', '.join(str(e) for e in band_wavelengths)
        else:
            envi_dict['band names'] = '{%s}' % ', '.join(str(e) for e in band_names)
            envi_dict['wavelength'] = '{%s}' % ', '.join(str(e) for e in band_centers)

        envi_dict['wavelength units'] = DG_WAVELENGTH_UNITS

        for entry, value in envi_dict.iteritems():
            # iterate through elements to write them out to file
            hdr_file.write('%s = %s\n' % (entry, value))

        # close file
        hdr_file.close()


if __name__ == "__main__":
    with EnviHdr() as task:
        task.invoke()
