# [Netrics](https://github.com/chicago-cdac/nm-exp-active-netrics)
NetMicroscope Experiment - Active Measurements (AKA Netrics)

## 1. [About Netrics](https://chicago-cdac.github.io/nm-exp-active-netrics)

TBD

### 1.1 Install (umanaged, direct influxfb data ingestion)

1. Checkout the latest pre-releases and releases at [link](https://github.com/chicago-cdac/nm-exp-active-netrics/releases).
2. Copy link and login into your Jetson Nano device, download .deb file:<br>
`wget https://github.com/chicago-cdac/nm-exp-active-netrics/releases/download/v0.1.10-arm64/nm-exp-active-netrics-v0.1.10-arm64.deb`
3. run `sudo apt install ./nm-exp-active-netrics-v0.1.10-arm64.deb` (use `--reinstall` if you have an old version already installed)
4. edit your `/etc/nm-exp-active-netrics/nm-exp-active-netrics.toml` file to include <b>[iperf]</b> target servers:
```
...
[iperf]

   targets = ["server:33001"]
...
```
5. Create .env file with server credentials <b>`sudo vim /etc/nm-exp-active-netrics/.env`</b>:
<pre>
INFLUXDB_SERVER=
INFLUXDB_PORT=
INFLUXDB_USERNAME=
INFLUXDB_PASSWORD=
INFLUXDB_DATABASE=
INSTALL_ID=<b>myid</b> <---- use your lastname here so you can filter out grafana/influxdb queries.
</pre>
6. Restart netrics: <b>`sudo /etc/init.d/nm-exp-active-netrics restart`</b>
7. Check health with `sudo netrics -C` and logs with `sudo netrics -L`

### 1.2 Install (managed, via nm-mgmt-cms-*.deb)

TBD
