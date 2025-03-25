import unittest
import os
import skconfig


#
# g_test_str = """
# ALTIUS_DATABASE_FOLDER: './Users/nickl/Documents/Work/software/ARG_Packages/skconfig'
# folders:
#     l1pp_datafiles:  $(ALTIUS_DATABASE_FOLDER)$/l1pp_datafiles          # Use the environment variable ALTIUS_DATABASE_FOLDER for location of ALTIUS database files etc. If you prefer you can use an explicit folder, e.g E:/altius_data/l1pp_datafiles
#     sdo_hmii_data: $( ALTIUS_DATABASE_FOLDER)$/sdo_hmii_data             # Location where we store the Solar Dynamics Observatory HMI continuum images, see https://sdo.gsfc.nasa.gov/data/aiahmi/ and http://jsoc.stanford.edu/ajax/lookdata.html?ds=hmi.Ic_720s
#
# orbit:
#     nominal_altitude_km : 691.0                      # nominal altitude of the spacecraft in kilometers
#
# uv:
#     front_aperture_area: 25.0                         # front aperture area in cm2.
#     spectral:
#         wavelength_range: [250.0, 370.0]
#     window:
#         native_size:           [2000,1504]              # Y,X dimensions of the native CMOS detector
#         science_native_size:   [171,171]              # Y,X dimensions of the scienmce window in  native pixels
#         science_native_origin: [0,0]                  # Y,X Origin of bottom left corner of science window in native pixel
#         science_binning:       [3,3]                  # Y,X native pixel binning to make science window
#         fov_degrees:           [2.5917959198092038, 1.948056503444799]       # Y,X field of view in degrees across the native size window
#     altius_oob_spectral_light:
#         data_file_folder: $( folders/l1pp_datafiles )$/uv/oob_spectral_light        # oob spectral light data folder. Either absolute path or join with key folders/fl1pp_datafiles
#
# vis:
#     2020-10-20:
#        psfdata:
#          350.0:
#             - filename: $(ALTIUS_DATABASE_FOLDER)$/file_2020-10-20_350_0.txt
#               center: [0, 0, 45, 78]
#             - filename: $(ALTIUS_DATABASE_FOLDER)$/file_2020-10-20_350_1.txt
#               center: [0, 0, 45, 78]
#          300.0:
#            - $(ALTIUS_DATABASE_FOLDER)$/file_2020-10-20_300_0.txt
#            - $(ALTIUS_DATABASE_FOLDER)$/file_2020-10-20_300_0.txt
#     2021-03-09:
#        psfdata:
#          350.0:
#             - filename: $(ALTIUS_DATABASE_FOLDER)$/file_2021-03-09_350_0.txt
#             - filename: $(ALTIUS_DATABASE_FOLDER)$/file_2021-03-09_350_1.txt
#          300.0:
#             - filename: $(ALTIUS_DATABASE_FOLDER)$/file_2021-03-09_300_0.txt
#             - filename: $(ALTIUS_DATABASE_FOLDER)$/file_2021-03-09_300_0.txt
#
#
#     front_aperture_area: 25.0                         # front aperture area in cm2.
#     spectral:
#         wavelength_range: [400.0, 800.0]
#
#     window:
#         native_size:           [2000,1504]            # Y,X dimensions of the native CMOS detector
#         science_native_size:   [501,  501]            # Y,X dimensions of the scienmce window in  native pixels
#         science_native_origin: [0,0]                  # Y,X Origin of bottom left corner of science window in native pixel
#         science_binning:       [3,3]                  # Y,X native pixel binning to make sceince window
#         fov_degrees:           [2.5917959198092038, 1.948056503444799]       # Y,X field of view in degrees across the native size window
#     spatial_psf:
#         data_file: $( folders/l1pp_datafiles )$/vis/vispsf.mat   # Visible channel point spread function extracted from SPS. Either absolute path or join with key folders/fl1pp_datafiles
#
# nir:
#     front_aperture_area: 25.0                         # front aperture area in cm2.
#     spectral:
#         wavelength_range: [520.0, 1040.0]
#
#     window:
#         native_size:           [2000,1504]            # Y,X dimensions of the native CMOS detector
#         science_native_size:   [501,  501]            # Y,X dimensions of the scienmce window in  native pixels
#         science_native_origin: [0,0]                  # Y,X Origin of bottom left corner of science window in native pixel
#         science_binning:       [3,3]                  # Y,X native pixel binning to make sceince window
#         fov_degrees:           [2.5917959198092038, 1.948056503444799]       # Y,X field of view in degrees across the native size window
# """


# ------------------------------------------------------------------------------
#           SkconfigTests
# ------------------------------------------------------------------------------
class SkconfigTests(unittest.TestCase):

    def setUp(self):
        basedir, name = os.path.split(__file__)
        self._yamlfile = os.path.join(basedir, 'test_configuration.yaml')
        # self.locator_info = skconfig.ConfigurationLocatorInfo(packagename='python_skconfig_testing', groupname='usask-arg', yamlname='testconfig.yaml', location='user')
        # values = yaml.load(g_test_str, Loader=yaml.FullLoader)
        # for i in range(3):
        #     config = skconfig.Configuration()
        #    config.save_registry(self.locator_info, values=values)

    def tearDown(self):
        pass
        # config = skconfig.Configuration(file_locator=self.locator_info)
        # filename = config.filename
        # if os.path.exists(filename):
        #    os.unlink(filename)
        # basedir, name = os.path.split(filename)
        # if os.path.exists(basedir):
        #    os.rmdir(basedir)

    # ------------------------------------------------------------------------------
    #           test_read
    # ------------------------------------------------------------------------------
    def test_precedence_read(self):
        """
        Tests reading a yaml file and then accessing a key after changing the macro precedence order.
        """
        os.environ['ALTIUS_DATABASE_FOLDER'] = './Users/nickl/Documents'
        config = skconfig.Configuration(self._yamlfile)
        w4 = config.subkey('vis/psfdata/2020-10-20/350.0/0')
        name = w4.as_pathname('filename')
        w5 = config.subkey('vis/psfdata/2020-10-20/300.0')
        aname = w5.as_pathname(1)
        w1 = config['nir']['window']['native_size']
        w2 = config['nir/window/native_size']
        w3 = config['nir/window/native_size']
        filename1 = config.as_pathname('vis/spatial_psf/data_file')
        config.set_macros_precedence_order(('int', 'env'))
        filename2 = config.as_pathname('vis/spatial_psf/data_file')

        filename1 = filename1.replace('\\', '/')
        filename2 = filename2.replace('\\', '/')
        self.assertEqual(w1[0], 2000)
        self.assertEqual(w2[0], 2000)
        self.assertEqual(w3[0], 2000)
        self.assertEqual(w1[1], 1504)
        self.assertEqual(w2[1], 1504)
        self.assertEqual(w3[1], 1504)
        self.assertEqual(filename2, 'default/folder/inside/yamlfile/l1pp_datafiles/vis/vispsf.mat')
        self.assertEqual(filename1, 'Users/nickl/Documents/l1pp_datafiles/vis/vispsf.mat')

    # ------------------------------------------------------------------------------
    #           test_subkey_read
    # ------------------------------------------------------------------------------
    def test_subkey_read(self):
        """
        Tests reading a yaml file and accessing a subkey. The trick in this test is to ensure the macro expansion is still valid
        as it must use the entire yaml file, not just the subkey section.
        """

        config = skconfig.Configuration(self._yamlfile, subkey='vis')
        config.set_macros_precedence_order(('int', 'env'))
        w1 = config['window']['native_size']
        w2 = config['window/native_size']
        w3 = config['window/native_size']
        filename1 = config.as_pathname('spatial_psf/data_file')
        filename1 = filename1.replace('\\', '/')
        self.assertEqual(w1[0], 2000)
        self.assertEqual(w2[0], 2000)
        self.assertEqual(w3[0], 2000)
        self.assertEqual(w1[1], 1504)
        self.assertEqual(w2[1], 1504)
        self.assertEqual(w3[1], 1504)
        self.assertEqual(filename1, 'default/folder/inside/yamlfile/l1pp_datafiles/vis/vispsf.mat')


if __name__ == "__main__":
    tests = SkconfigTests()
    unittest.main()
