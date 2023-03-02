import toml
from tinydb import TinyDB
import unittest
from pathlib import Path
import sys
import warnings
import json
sys.path.insert(0, '/home/ubuntu/nm-exp-active-netrics/src')
from netrics.builtin import netrics_test_iperf3 as netrics
from mock_measurements import Measurements

speeddb = TinyDB(Path(str(Path(__file__).resolve().parent)+'/samples/speedtest.json'))

class TestIperf(unittest.TestCase):
    """Class for methods of iperf unit tests"""
    
    def setUp(self):
        self.measurement = Measurements()
        self.key = "iperf"

    def test_iperf_success(self):
        """
        Test flow correctness if inputs given are correct
        """

        measured_down = 5
        max_monthly_consumption_gb = 200
        max_monthly_tests = 200
    
        #read config
        conf = self.read_config('nm-exp-active-netrics.toml')
        conf['databases']['tinydb_enable'] = False
        args = {
            "speed_db" : speeddb,
            'limit' : False,
            "client" : "abbott.cs.uchicago.edu",
            "port" : "33301",
            "bandwidth_test_stochastic_limit": self.measurement.bandwidth_test_stochastic_limit,
            "measured_down" : measured_down,
            "max_monthly_consumption_gb" : max_monthly_consumption_gb,
            "max_monthly_tests" : max_monthly_tests,
            "conf" : conf,
            "update_max_speed" : self.measurement.update_max_speed
        }

        #run test
        results = {}
        results[self.key] = {}
        results['total_bytes_consumed'] = 0

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.test_iperf3(self.key, self.measurement, args, results, False)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        self.assertIsNotNone(results)
        self.assertIsNotNone(output)

        #assert output format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/iperf_output.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(output),dict)
        self.assert_format(json_format, output)

        #assert result format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/iperf_results.json'
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
