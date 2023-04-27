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
