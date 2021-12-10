# Adding a new experiment to Netrics by creating an independent package

## Creating a New Package

If you want to create a new package to deploy on our testbed, follow these steps below.

1. Create a .deb file (Check to see if we have the user "netrics." Otherwise, create the user "netrics"). See example [here](https://github.com/chicago-cdac/nm-exp-active-netrics/blob/main/package/deb/nm-exp-active-netrics/DEBIAN/postinst).
2. Create a file in `/etc/init.d/` to manage the life cycle of your experiment. See example [here](https://github.com/chicago-cdac/nm-exp-active-netrics/blob/main/etc/init.d/nm-exp-active-netrics).
3. Create a cron job at `/etc/cron.d/` using crontab to schedule your testing frequency. See example [here](https://github.com/chicago-cdac/nm-exp-active-netrics/blob/main/conf/nm-exp-active-netrics.toml#L20).
4. Create a configuration file at `/etc/{your_test_package_xxxx}/` to centralize all of your configuration parameters. See example [here](https://github.com/chicago-cdac/nm-exp-active-netrics/blob/main/conf/nm-exp-active-netrics.toml).

## Data Collection

Our software ([nm-mgmd-collect](https://github.com/chicago-cdac/nm-mgmt-collect)) should automatically collect any data dumped in the directory below and upload it to the S3 storage in the cloud.
```
/var/nm/{your_test_package_name}/upload/pending/{topic}/{file_format}/{your_data_file_timestamp.json}
```
In the example above, the file format is JSON. However, you could use any file format that you want (csv, zip, tgz, etc.). Furthermore, the topic name can be anything that you want as well. The topic name just serves as a tag for you to segment your data.

**IMPORTANT**: Please write data with one operation. Avoid appending to files and writing data with partial, multi-part writes to files in `pending`.

Once files in `pending` are uploaded, they are automatically moved to `archive`.

```
ubuntu@netrics:~/nm-exp-active-netrics$ ls -lh /var/nm
total 12K
drwxr-xr-x 5 netrics netrics 4.0K Jul 20 19:25 nm-exp-active-netrics
drwxr-xr-x 3 netrics netrics 4.0K Sep 15 23:11 nm-exp-local-dashboard
drwxr-xr-x 3 netrics netrics 4.0K Jul 20 19:28 nm-mgmt-collectd-http
```
```
ubuntu@netrics:~/nm-exp-active-netrics$ ls -lh /var/nm/nm-exp-active-netrics/upload/
total 8.0K
drwxrwxr-x 3 netrics netrics 4.0K Jul 20 19:30 archive
drwxrwxr-x 3 netrics netrics 4.0K Jul 20 19:30 pending
```
