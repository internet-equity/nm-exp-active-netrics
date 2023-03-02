## Running Unittests
     
* * * * * * * * * * * * *

Author: Fathima Maha

### To run all tests:    

```
python3 -m unittest discover unittests -v
```       
    
### To run individual tests:   

```  
python3 -m unittest <test_filename> -v  
````       

### Unit test options:
    
-v - verbose      
-h - help   

## To get coverage:   
    
``` 
cd src
```
   
Get coverage of all tests for all files in builtin:   
```
pip install coverage    
coverage run --source=../builtin -m unittest discover -v && coverage report  
```      
Or 
```
coverage run --source=../builtin -m unittest discover -v && coverage report  
```    

Example:     

```
Name                                                                                       Stmts   Miss  Cover
--------------------------------------------------------------------------------------------------------------
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/__init__.py                             0      0   100%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_connected_devices.py      48      4    92%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_dns_latency.py            50     11    78%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_hops_to_target.py         44     11    75%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_iperf3.py                 87     23    74%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_last_mile_latency.py      80     22    72%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_latunderload.py           54      9    83%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_oplat.py                  80     46    42%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_ping_latency.py           61     13    79%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_speedtests.py            115     11    90%
--------------------------------------------------------------------------------------------------------------
TOTAL                                                                                        619    150    76%

```    

Get coverage of specific test for files in builtin:   
```
coverage run --source=../builtin <test_filename> -v -v && coverage report 
```     
   
### Reference:   

https://docs.python.org/3/library/unittest.html#unittest.main

https://coverage.readthedocs.io/en/7.1.0/