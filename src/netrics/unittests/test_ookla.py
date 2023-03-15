import toml
import unittest
from pathlib import Path
import sys
import warnings
import json
sys.path.insert(0, '/home/ubuntu/nm-exp-active-netrics/src')
from netrics.builtin import netrics_test_speedtests as netrics
from netrics.unittests.mock_measurements import Measurements

class TestOokla(unittest.TestCase):
    """Class for methods of ookla unit tests"""
    
    def setUp(self):
        self.measurement = Measurements()
        self.ookla_key = "ookla"

    def test_ookla_success(self):
        """
        Test flow correctness if inputs given are correct
        """

        #read config
        conf = self.read_config('nm-exp-active-netrics.toml')

        #config asserts for ookla
        self.assertIsNotNone(conf['ookla']['timeout'])
        self.assertIsNotNone(conf['databases']['tinydb_enable'])

        #run test
        results = {}
        results[self.ookla_key] = {}
        results['total_bytes_consumed'] = 0
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.test_ookla(self.ookla_key, self.measurement, conf, results, False)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        self.assertIsNotNone(results)
        self.assertIsNotNone(output)
        output = json.loads(output)

        #assert output format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/ookla_output_nopacketloss.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(output),dict)
        self.assert_format(json_format, output)

        #assert result format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/ookla_result.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(results),dict)
        self.assert_format(json_format, results)

        return

    def test_ookla_error_in_json(self):
        """
        Test that output is still present if timeout error is present,
        assuming default will timeout (maybe set to 0)
        """

        #read config
        conf = self.read_config('nm-exp-active-netrics-no-timeout.toml')

        #config asserts for ookla
        self.assertNotIn('timeout',conf['ookla'])

        #run test
        results = {}
        results[self.ookla_key] = {}
        results['total_bytes_consumed'] = 0
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.test_ookla(self.ookla_key, self.measurement, conf, results, False)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        self.assertIsNotNone(results)
        self.assertIsNotNone(output)        
        output = json.loads(output)

        #assert output format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/ookla_output_nopacketloss.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(output),dict)
        self.assert_format(json_format, output)

        #assert result format with error present
        json_sample = str(Path(__file__).resolve().parent) + '/samples/ookla_result_timeouterror.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(results),dict)
        self.assertTrue(results["ookla"]["ookla_error"])
        self.assert_format(json_format, results)

        return
    
    def test_ookla_no_output(self):
        """
        Test that output is not present and error is returned
        """

        #read config
        conf = self.read_config('nm-exp-active-netrics.toml')

        #config asserts for ookla
        self.assertIsNotNone(conf['ookla']['timeout'])
        self.assertIsNotNone(conf['databases']['tinydb_enable'])
        conf['ookla']['timeout'] = -1

        #run test
        results = {}
        results[self.ookla_key] = {}
        results['total_bytes_consumed'] = 0
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.test_ookla(self.ookla_key, self.measurement, conf, results, True)
        except Exception as e:
            print(e)
            return
        
        #test that no output present and result is none
        self.assertEqual(output,'') 
        self.assertIsNotNone(results) 
        self.assertEqual(type(results),dict)
        self.assertTrue(results["ookla"]["ookla_error"])
        self.assertIn('ookla_json_error',results["ookla"])

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
