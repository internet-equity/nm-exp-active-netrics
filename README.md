# [Netrics](https://chicago-cdac.github.io/nm-exp-active-netrics)

Netrics - Active Measurement of Network Performance

## 1. About Netrics

<b>What</b>: a software framework to concentrate and run dedicated computer network measurements.<br>
<b>For Whom</b>: internet users, network engineers and the general internet research community.<br>
<b>Why</b>: to troubleshoot impaired computer networks, to understand how the internet is evolving, and to support decisions on internet infrastructure capacity planning.

![Netrics Dashboard](https://github.com/internet-equity/nm-exp-active-netrics/blob/main/docs/images/dashboard.png?raw=true)

### 1.1 Software

The software is a simple set of modular wrapper code around standard internet performace measurement tools. It's designed to parse and extract the most crutial information from the output of these tools in order to give to the internet performance observers a critical view over the network. The output from the original commands are preserved as part of the reproducibility of the data pipeline.   


### 1.2 Hardware

Netrics runs on dedicated SBC's (Single Board Computers). It's well tested on Raspberry Pis and NVIDIA Jetson Nanos. The active Netrics package (this repo) is mainly responsible for measurements that actively generate network traffic in order to assess network's performance metrics. 

|![Attached](https://github.com/internet-equity/nm-exp-active-netrics/blob/main/docs/images/attached3.png?raw=true)|
|:---:|
<p align="center">
    Figure 1. a Raspberry Pi connected to the modem's Ethernet port.
</p>

### 1.3 Data Structure
Here we describe the general structure of the output data of the Netrics that is written in the "pending" directory.
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

As you can see, the output JSON contains 2 main dictonaries **Meta** and **Measuments**. Meta contains *Time*, a UTC timestamp and *ID* of the device. <b>Important: ID is a placeholder, the backend is responsible to determine the device ID and to move the files from "pending" to "archive" directory when the data files are safely transferred to the data storage (more to this below).



### 1.4 Source Code, Configuration and Data locations

The python source code, after installed resides on:<br>
`/usr/local/src/nm-exp-active-netrics/*`<br>

The local data (SBC storage) is located at:<br>
`/var/nm/nm-exp-active-netrics/upload/pending/*` (pending upload),<br>
`/var/nm/nm-exp-active-netrics/upload/archive/*` (uploaded, safe for deletion)<br>

Configuration can be found at:<br>
`/etc/nm-exp-active-netrics/*`

## 2. Install

Please use the _unmanaged_ installation with direct influxdb data ingestion if you're a developer or researcher planning to contribute with code, testing and building of NetMicroscope/Netrics Open Source software. For all other cases, please use the _managed_ installation method.

### 2.1 Install (umanaged, direct influxfb data ingestion)

1. Checkout the latest pre-releases and releases at [link](https://github.com/chicago-cdac/nm-exp-active-netrics/releases).
2. Copy link and login into your Jetson Nano device, download .deb file:<br>
`wget https://github.com/chicago-cdac/nm-exp-active-netrics/releases/download/v0.1.10-arm64/nm-exp-active-netrics-v0.1.10-arm64.deb`
3. run `sudo apt install ./nm-exp-active-netrics-v0.1.10-arm64.deb`<br>
(To reinstall run):<br>`sudo apt remove --purge nm-exp-active-netrics`<br>`sudo apt install --reinstall ./nm-exp-active-netrics-v0.1.10-arm64.deb`, and if necessary run:<br>`sudo rm -Rf /usr/local/src/nm-exp-active-netrics`
4. edit your `/etc/nm-exp-active-netrics/nm-exp-active-netrics.toml` file to include <b>[iperf]</b> target servers:
```
...
[iperf]

   targets = ["server:33001"]
...
```
5. Create .env.netrics file with server credentials <b>`sudo vim /etc/nm-exp-active-netrics/.env.netrics`</b>:
<pre>
INFLUXDB_SERVER=
INFLUXDB_PORT=
INFLUXDB_USERNAME=
INFLUXDB_PASSWORD=
INFLUXDB_DATABASE=
INSTALL_ID=<b>myid</b> <---- use your lastname here so you can filter out grafana/influxdb queries.
</pre>
6. Restart netrics: <b>`sudo /etc/init.d/nm-exp-active-netrics restart`</b>
7. Check health with `netrics -C` and logs with `netrics -L`

### 1.2 Install (managed, via nm-mgmt-cms-*.deb)

TBD

[Install](https://www.youtube.com/watch?v=WVhyWWEiqVY)
