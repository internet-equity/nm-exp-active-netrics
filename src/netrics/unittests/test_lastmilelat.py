import toml
import unittest
from pathlib import Path
import sys
import warnings
import json
sys.path.insert(0, '/home/ubuntu/nm-exp-active-netrics/src')
from netrics.builtin import netrics_test_last_mile_latency as netrics
from mock_measurements import Measurements

class TestLastMileLatency(unittest.TestCase):
    """Class for methods of ookla unit tests"""
    
    def setUp(self):
        self.measurement = Measurements()
        self.last_mile_key = "last_mile_latency"

    def test_lastmile_success(self):
        """
        Test flow correctness if inputs given are correct
        """

        #read config
        conf = self.read_config('nm-exp-active-netrics.toml')
        sites = list(conf['reference_site_dict'].keys())[:2]
        labels = conf['reference_site_dict']
        args = {
            "sites" : sites,
            "labels" : labels
        }

        #run test
        results = {}
        results[self.last_mile_key] = {}
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.test_last_mile_latency(self.last_mile_key, self.measurement, args, results, False)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        self.assertIsNotNone(results)
        self.assertIsNotNone(output)

        #assert output format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/lastmile_output.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(output),dict)
        self.assert_format(json_format, output)

        #assert result format
        json_sample = str(Path(__file__).resolve().parent) + '/samples/lastmile_results.json'
        try:
            with open(json_sample, "rb") as f:
                json_format = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return   
        
        self.assertEqual(type(results),dict)
        self.assert_format(json_format, results)

        return

    def test_lastmile_popen_error(self):
        """
        Test returning error if site is unknown
        """

        #read config
        conf = self.read_config('nm-exp-active-netrics.toml')
        sites = ["ABCD","ABCD","ABCD","ABCD","ABCD"]
        labels = conf['reference_site_dict']
        args = {
            "sites" : sites,
            "labels" : labels
        }

        #run test
        results = {}
        results[self.last_mile_key] = {}
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                output = netrics.test_last_mile_latency(self.last_mile_key, self.measurement, args, results, False)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        self.assertIsNotNone(results)
        self.assertIsNotNone(output)
        
        self.assertTrue(results['last_mile_latency']['error'])
        self.assertIn('failure', output)

        return
    
    def test_parse_trace_output_1(self):
        """
        Test returning error if site is unknown
        """

        #read trace output sample
        file = str(Path(__file__).resolve().parent) + '/test_configs/traceoutput_1'
        try:
            with open(file, "rb") as f:
                out = f.read().decode('utf-8')
        except Exception as e:
            print(e)
        out = out.split('\n')

        conf = self.read_config('nm-exp-active-netrics.toml')
        sites = list(conf['reference_site_dict'].keys())[:2]
        labels = conf['reference_site_dict']
        
        results = {}
        results['last_mile_latency'] = {}

        #run test
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                err = netrics.parse_trace_output(out,{},sites[0],results,self.last_mile_key,labels)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        self.assertIn('google_last_mile_ping_packet_loss_pct',results['last_mile_latency'])
        self.assertIn('google_last_mile_ping_rtt_min_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_ping_rtt_max_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_ping_rtt_avg_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_ping_rtt_mdev_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_tr_rtt_min_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_tr_rtt_median_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_tr_rtt_max_ms',results['last_mile_latency'])
        self.assertIsNone(err)

        return

    def test_parse_trace_output_2(self):
        """
        Test returning error if site is unknown
        """

        #read trace output sample
        file = str(Path(__file__).resolve().parent) + '/test_configs/traceoutput_2'
        try:
            with open(file, "rb") as f:
                out = f.read().decode('utf-8')
        except Exception as e:
            print(e)
        out = out.split('\n')

        conf = self.read_config('nm-exp-active-netrics.toml')
        sites = list(conf['reference_site_dict'].keys())[:2]
        labels = conf['reference_site_dict']
        
        results = {}
        results['last_mile_latency'] = {}

        #run test
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                err = netrics.parse_trace_output(out,{},sites[0],results,self.last_mile_key,labels)
        except Exception as e:
            print("ERROR IN TEST SUITE: ", e)
            return

        self.assertIn('google_last_mile_ping_packet_loss_pct',results['last_mile_latency'])
        self.assertIn('google_last_mile_ping_rtt_min_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_ping_rtt_max_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_ping_rtt_avg_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_ping_rtt_mdev_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_tr_rtt_min_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_tr_rtt_median_ms',results['last_mile_latency'])
        self.assertIn('google_last_mile_tr_rtt_max_ms',results['last_mile_latency'])
        self.assertIsNone(err)
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

