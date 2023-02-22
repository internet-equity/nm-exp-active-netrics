import toml
import unittest
from pathlib import Path
import sys
import warnings
import json
sys.path.insert(0, '/home/ubuntu/nm-exp-active-netrics/src')
from netrics.builtin import netrics_test_speedtests as netrics
from mock_measurements import Measurements

#TO EDIT
class TestNdt7(unittest.TestCase):
    """Class for methods of ndt7 unit tests"""
    
    def setUp(self):
        self.measurement = Measurements()
        self.key = "ndt7"

    def test_ndt7_success(self):
        """
        Test flow correctness if inputs given are correct
        """

        #read config
        conf = self.read_config('nm-exp-active-netrics.toml')

        #run test
        results = {}
        results[self.key] = {}
        results['total_bytes_consumed'] = 0
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.test_ndt7(self.key, self.measurement, conf, results, False)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        output = json.loads(output)
        self.assertIsNotNone(results)
        self.assertIsNotNone(output)

        #assert output format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/ndt7_output.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(output),dict)
        self.assert_format(json_format, output)

        #assert result format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/ndt7_results.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(results),dict)
        self.assert_format(json_format, results)

        return

    def test_ndt7_success_quiet(self):
        """
        Test quiet mode
        """

        #read config
        conf = self.read_config('nm-exp-active-netrics.toml')

        #run test
        results = {}
        results[self.key] = {}
        results['total_bytes_consumed'] = 0
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.test_ndt7(self.key, self.measurement, conf, results, True)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        output = json.loads(output)
        self.assertIsNotNone(results)
        self.assertIsNotNone(output)

        #assert output format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/ndt7_output.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(output),dict)
        self.assert_format(json_format, output)

        #assert result format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/ndt7_results.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(results),dict)
        self.assert_format(json_format, results)

        return
    
    def test_ndt7_parse_output(self):
        """
        Test output parsing of ndt7
        """

        #read output sample
        sample = str(Path(__file__).resolve().parent) + '/samples/ndt7_output.json'
        try:
            with open(sample, "r") as f:
                output_sample = f.read()
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return
        
        #run test
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.parse_ndt7_output(output_sample)
        except Exception as e:
            print(e)
            return
        
        print(output)

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
