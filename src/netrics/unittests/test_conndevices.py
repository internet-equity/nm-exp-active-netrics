
from tinydb import TinyDB
from pathlib import Path
import toml
import unittest
from pathlib import Path
import sys
import warnings
import json
sys.path.insert(0, '/home/ubuntu/nm-exp-active-netrics/src')
from netrics.builtin import netrics_test_connected_devices as netrics
from mock_measurements import Measurements

devdb = TinyDB(Path(str(Path(__file__).resolve().parent)+'/samples/devdb.json'))

class TestConnDevices(unittest.TestCase):
    """Class for methods of connected devices unit tests"""
    
    def setUp(self):
        self.measurement = Measurements()
        self.key = "connected_devices"

    def test_latunderload_success(self):
        """
        Test flow correctness if inputs given are correct
        """
    
        #read config
        conf = self.read_config('nm-exp-active-netrics.toml')

        #run test
        results = {}
        results[self.key] = {}

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.test_connected_devices(self.key, self.measurement, devdb, conf, results, False)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        self.assertIsNotNone(results)
        self.assertIsNotNone(output)
        
        self.assertEqual(type(output),dict)

        #assert result format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/conndevices_results.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(results),dict)
        self.assert_format(json_format, results)

        return

    def assert_format(self, format_dict, check_dict):
        """
        checks if keys are matching ina format dict to 
        a refernce dict
        """
        for key in format_dict:
            self.assertIn(key,check_dict)
            if type(key) is dict:
                self.assert_format(format_dict[key],check_dict[key])
        return

    def read_config(self, filename):
        config_file = str(Path(__file__).resolve().parent) + '/test_configs/'+filename
        try:
            with open(config_file, "rb") as f:
                conf = toml.loads(f.read().decode('utf-8'))
        except Exception as e:
            print(e)
        return conf

    
if __name__ == "__main__":
    unittest.main()
