# Video Conferencing Performance Measurement Tool
 
Video Conferencing Automation and Performance Measurement Tool for Netrics

## 1. Brief

[**Netrics**](https://github.com/chicago-cdac/nm-exp-active-netrics) is UChicago DSI's open-source software for active measurement of Internet performance. This **Video Conferencing Automation and Performance Measurement Tool** collects video calling performance metrics for the Netrics software, particularly
 - WebRTC data
 - PCAP data

 The test requires two devices, 
 1. **Server**: Hosts the video conference, streams a video and admits the device from which we want to test the Network performance.
 2. **Client**: The device for which we want to measure the network performance by joining a video conference call hosted by the above said server and collects relevent data (WebRTC, PCAP, etc.).

## 2. Installation

### 2.1 Server Device

1. Install Google Chrome
2. Install Python 3
3. Install Node.js
4. Clone the [repository](https://github.com/tarunmangla/netrics-vca-test/blob/main/README.md) to the system local
6. Instal Node.js dependencies
```
cd <path to local repository>/controller
npm install
```
7. Install the requirements in requirements.txt to set up python dependancies
```
cd <path to local repository>
pip install -r requirements
```

### 2.2 Client Device
0. If the client is running Ubuntu, make sure that Wayland display is disabled. This can be done by uncommenting the line `WaylandEnable=False` in `/etc/gdm3/custom.conf`.
1. Install Chromium browser (For raspberry pi Netrics devices)
2. Install Python 3
3. Clone the [repository](https://github.com/tarunmangla/netrics-vca-test/blob/main/README.md) to the system local
7. Install the requirements in requirements.txt to set up python dependancies
```
cd <path to local repository>
pip install -r requirements
```

## 3. Running Tests

### 3.1 Server Device

1. Place the video to pipe in the system local
2. Modify the vca-automation/config.toml (Paste contents from config-backup/config-server.toml) with edits as needed. Refer the config file for specific edits according to the system and paths to file dependencies.
3. Run the following commands
```
cd <path to local repository>/controller
node app.js
```
4. If and when a client joins, the server outputs a log file, webRTC file, and pcap file in vca-automation/Data/<\platform name\>. Once the client leaves, the call is exited and the run ends.

### 3.2 Client Device

1. Modify the vca-automation/config.toml (Paste contents from config-backup/config-client.toml) with edits as needed. Refer the config file for specific edits according to the system and paths to file dependencies.
3. Run the following commands
```
cd <path to local repository>/vca-automation
python main_client.py
```
4. The test when done running successfully outputs 4 files in vca-automation/Data/\<platform name\>:
- webRTC data as a json file in client-\<vca name\>-\<timestamp\>.json
- Summarised metrics for netrics in client-\<vca name\>-\<timestamp\>-netrics.json
- Log of the run in client-\<vca name\>-\<timestamp\>.log
- pcap dat in client-\<vca name\>-\<timestamp\>.pcap

## Dependencies

- Browser (Chromium/Google Chrome) 
- Python 3
- Pip
- Node.js
- [Link to required Python Modules](https://github.com/tarunmangla/netrics-vca-test/blob/main/requirements.txt)


## Documentation

- [Link](https://github.com/tarunmangla/netrics-vca-test/blob/main/vca_automation/README.md)


## Github

- [Repository Link](https://github.com/tarunmangla/netrics-vca-test/blob/main/README.md)

## Version

0.0.1
