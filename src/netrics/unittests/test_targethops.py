import toml
import unittest
from pathlib import Path
import sys
import warnings
import json
sys.path.insert(0, '/home/ubuntu/nm-exp-active-netrics/src')
from netrics.builtin import netrics_test_hops_to_target as netrics
from mock_measurements import Measurements


class TestTargetHops(unittest.TestCase):
    """Class for methods of Target hops unit tests"""
    
    def setUp(self):
        self.measurement = Measurements()
        self.key = "hops_to_target"

    def test_dns_success(self):
        """
        Test flow correctness if inputs given are correct
        """

        #read config
        conf = self.read_config('nm-exp-active-netrics.toml')
        sites = list(conf['reference_site_dict'].keys())[:2]
        labels = conf['reference_site_dict']
        args = {
            "conf" : conf,
            "labels" : labels
        }

        #run test
        results = {}
        results[self.key] = {}
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.test_hops_to_target(self.key, self.measurement, args, results, False)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        self.assertIsNotNone(results)
        self.assertIsNotNone(output)

        #assert output format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/hops_output.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(output),dict)
        self.assert_format(json_format, output)

        #assert result format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/hops_results.json'
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
