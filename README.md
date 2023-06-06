# Netrics

Netrics - Active Measurement of Network Performance

## 1. About Netrics

<b>What</b>: a software framework to concentrate and run dedicated computer network measurements.<br>
<b>For Whom</b>: internet users, network engineers and the general internet research community.<br>
<b>Why</b>: to troubleshoot impaired computer networks, to understand how the internet is evolving, and to support decisions on internet infrastructure capacity planning.

![Netrics Dashboard](https://user-images.githubusercontent.com/2147779/234374283-e7270619-49a2-40b9-ba0e-e1e50c81d5f2.png)
<p align="center">
    Figure 1. one of the reasons for constantly monitoring your internet performance: it varies over time.
</p>


### 1.1 Software

The software is a simple set of modular wrapper code around standard internet performace measurement tools. It's designed to parse and extract the most crutial information from the output of these tools in order to give to the internet performance observers a critical view over the network. The output from the original commands are preserved as part of the reproducibility of the data pipeline.  

More details in [Code Documentation](#Documentation).


### 1.2 Hardware

Netrics runs on dedicated SBC's (Single Board Computers). It's well tested on Raspberry Pis and NVIDIA Jetson Nanos. The active Netrics package (this repo) is mainly responsible for measurements that actively generate network traffic in order to assess network's performance metrics. 

|![Attached](https://github.com/internet-equity/nm-exp-active-netrics/blob/main/docs/images/attached3.png?raw=true)|
|:---:|
<p align="center">
    Figure 2. a Raspberry Pi running Netrics connected to a modem via Gigabit Ethernet port.
</p>

### 1.3 Data and Data Structure

Different than Ookla and Cloudflare/Mlab, Netrics is designed to collect hyperlocalized data from a region or a city and by doing that your're likely to expose pattens and outliers in the data that can be used to shed a light into the inequities on how the internet infrastructure in being developed. To learn more about the findings of what this software can unlock please visit the [Internet Equity Initiative](https://internetequity.uchicago.edu/) and [Netrics Data](https://github.com/internet-equity/netrics-data).

Next we describe the general structure of the output data of the Netrics that is written in the "pending" directory.
<details>
  <summary>Output JSON (Meta Data)</summary>
  
  ```json
  {
	"Meta": {
		"Extended": {
			"Annotation": null,
			"dataver": "1",
			"debhash": "fa01",
			"gitlog": "docs: README.md update"
		},
		"Id": null,
		"Time": 1682435164.984354
	},
    "Measurement": {
    ...
    }
  }
  ```
</details>

As you can see, the output JSON contains 2 main dictonaries **Meta** and **Measuments**. Meta contains *Time*, a UTC timestamp and *ID* of the device. <b>Important: ID is a placeholder, the backend is responsible to determine the device ID and to move the files from "pending" to "archive" directory when the data files are safely transferred to the data storage (more to this below).</b>


### 1.4 Source Code, Configuration and Data locations

The python source code, after installed resides on:<br>
`/usr/local/src/nm-exp-active-netrics/*`<br>

The local data (SBC storage) is located at:<br>
`/var/nm/nm-exp-active-netrics/upload/pending/*` (pending upload),<br>
`/var/nm/nm-exp-active-netrics/upload/archive/*` (uploaded, safe for deletion)<br>

Configuration can be found at:<br>
`/etc/nm-exp-active-netrics/*`

## 2. Install

[Install](https://www.youtube.com/watch?v=WVhyWWEiqVY)


## 3. Next-Generation Netrics

Please visit [Netrics V2](https://github.com/internet-equity/netrics) as it will become the continuation of this software.  


# Documentation  

The network measurement and experimentation tool is written in Python 3.0+, providing various tests to analyze network performance. This documentation provides an overview of the codebase, its structure, and directions to contributing to the project.

## 1. Overview

The execution flow in `netrics.py` relies on the functionality provided by netson.py to perform built-in network tests. The script delegates the execution of specific tests to the corresponding functions defined in `netson.py`.

By importing test from `netson.py`, `netrics.py` can call functions such as `last_mile_latency`, `dns_latency`, `hops_to_target`, `speed_ookla`, `speed_ndt7`, `speed`, `iperf3_bandwidth`, and `oplat`. These functions encapsulate the logic for conducting the respective network tests.

In addition to the built-in network tests provided by `netson.py`, `netrics.py` also supports the use of plugins to extend its functionality. The script includes a section that enables the discovery and execution of plugin tests.

This dynamic loading and execution of plugins allow developers to create custom tests and extend the capabilities of `netrics.py` without modifying the core functionality of the script. It provides a flexible and modular approach to accommodate additional network tests tailored to specific requirements.



## 2. Builtin Tests

Netrics software provides builtin tests that can be configured to run tests with the provided flags.

The builtin tests integrated with Netrics and their configurations are as shown: 

| Test              | Measures                                                                                                                                  | Configurations           |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|
| Ookla             | Download and upload speeds of the network connection                                                                                      | Test time out (seconds)  |
| NDT7              | Network's capacity for throughput and latency                                                                                             | None                     |
| Ping Latency      | Latency or delay in milliseconds for sending a ping request and receiving a response from a set of specified sites                        | None                     |
| Last Mile Latency | Latency experienced in the last mile of the network connection, which is the portion from the user's location to the nearest network node | Target sites with labels |
| DNS Latency       | Network latency and performance metrics under different load conditions                                                                   | Target sites with labels |
| Oplat Latency     | DNS (Domain Name System) lookup latency for a set of specified sites                                                                      | Target sites with labels |
| Hops To Target    | Number of network hops or routers traversed to reach a target site                                                                        | Target sites with labels |
| Connected Devices | Count of the number of active devices on the network using ARP (Address Resolution Protocol)                                              | None                     |
| iperf bandwidth   | Data transfer rate between a client and server                                                                                            | Target sites with labels |



## 3. Plugin Tests

Netrics supports tests that can be extended as plugins. The plugins discover and run tests in the `nm-exp-active-netrics/src/netrics/plugins/` folder.   

The code performs globbing for plugins and runs plugin tests based on the specified configuration.   

These tests can be run with `-P` or `--plugins`, from a given list eg. `./netrics -P=httping,goresp,vca`.

The plugins tests integrated with Netrics and their configurations are as shown:  

| Test             | Measures                                                      | Configurations                                                                                                                            |
|------------------|---------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Httping          | Availability and response time of HTTP servers                | Target sites with labels, c = Number of times to ping                                                                                     |
| Goresponsiveness | Round-trip time (RTT) of the HTTP requests to a target server | None                                                                                                                                      |
| VCA              | Performance of Video conferencing                             | [Config sample](https://github.com/internet-equity/netrics_vca_test/tree/669132a263310ef7a8637979897d7bb98277f104/vca_automation/configs) |


## 4. Integrating New Tests

If you would like to add your own tests, there is a detailed  guide in [Active Metrics Development Guide](https://github.com/internet-equity/nm-exp-active-netrics/blob/main/docs/active_metrics_dev_guide.md). 

Tests can also be added as python script to be run as a plugin in the `nm-exp-active-netrics/src/netrics/plugins/` folder named as `plugin_<plugin name>.py`.

The general format to add a plugin test file is to have a function formatted as,   

``` python
def test_<test_name>(<json key name>: str, <toml config>: dict, <result json>: dict, quite: bool) -> dict:
    #test logic
    return <dict with raw output from the test>
```

## 5. Unit Testing

Unit tests have been provided to the builtin tests which can be run to isolate the builtin tests code and determine if it works as intended on your device.

> **Note**:
> Before running tests there might be a need to change    
> the permissions of the nm-exp-active-netrics/src/netrics/unittests/ folder   
> to 777 if not already set so that tests can read/write results.  
> sudo chmod -R 777 nm-exp-active-netrics/src/netrics/unittests/

**To run all tests:**    

``` bash
cd nm-exp-active-netrics/src/netrics
python3 -m unittest discover unittests -v
```       
    
**To run individual tests:**   

``` bash
cd nm-exp-active-netrics/src/netrics
python3 -m unittest unittests/<test_filename with .py> -v  
````       

**Unit test options:**
    
`-v` - verbose      
`-h` - help   

**To get coverage:**   
    
``` bash
cd src
```
   
Get coverage of all tests for all files in builtin:   
``` bash
pip install coverage  
cd nm-exp-active-netrics/src/netrics  
coverage run --source=./builtin -m unittest discover -v && coverage report  
```      
Or 
``` bash
cd nm-exp-active-netrics/src/netrics 
coverage run --source=./builtin -m unittest discover -v && coverage xml  
```    

Example:     

``` console
Name                                                                                       Stmts   Miss  Cover
--------------------------------------------------------------------------------------------------------------
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/__init__.py                             0      0   100%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_connected_devices.py      48      4    92%
/home/ubuntu/nm-exp-active-netrics/src/netrics/builtin/netrics_test_speedtests.py            115     11    90%
--------------------------------------------------------------------------------------------------------------
TOTAL                                                                                        163    15    90%
```    

Get coverage of specific test for files in builtin:   
``` bash
cd nm-exp-active-netrics/src/netrics/unittests 
coverage run --source=../builtin <test_filename> -v -v && coverage report 
```     
