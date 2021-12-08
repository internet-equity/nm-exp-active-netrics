## Extending or adding tests to nm-exp-active-netrics

The best place to start developing new code for the nm-exp-active-netrics package is on a
Raspberry Pi device that you have connected to your home network.

If you need a Raspberry Pi device to use for development, email mtrichardson@uchicago.edu.
Follow the steps below to develop code locally.

1. SSH into your local device or a device that you have set up in the lab:
   ```
   ssh ubuntu@{device_ip_address}
   ```
   Ask a member of the team for the password.
   If you are using a "managed" device, this _should_ also show up as `netrics.local`.
   If that does not work or you are using an unmanaged devce, you'll have to do some `nmap` sleuthing.
   
   * If developing on a device at home, you will need to be connected to your home network to ssh to the device.
   * Developing in the IoT lab is not recommended, because we have measurements running on that devices.
     However, you can _do_ test on that device, you will need to first `ssh` to tigerteam and then ssh to the testing device in the lab.
     using tigerteam's auxiliary ethernet interface.  Ask us about IP addresses.
2. Next, pull the `nm-exp-active-netrics` source code from github by your preferred method.
   This repo is public and does not require special access to pull, but you'll have to ask Marc (mtrichardson) for commit rights.
3. Most development for this package involves two files:
   * **[netrics.py](https://github.com/chicago-cdac/nm-exp-active-netrics/blob/main/src/netrics.py)**: You need to
     (a) add arguments to the [parser](https://github.com/chicago-cdac/nm-exp-active-netrics/blob/9ff6291c783f93c30dd6eaf1855ed19c5a71845f/src/netrics.py#L51)
     (b) ensure that, later on, the test actually runs.  Note that if there is no connectivity / the device is offline,
         then you or we may not want the test to run.  If the code takes too long to attempt, it can muck up other tests
         that we _do_ want to maintain on schedule.
   * **[netson.py](https://github.com/chicago-cdac/nm-exp-active-netrics/blob/main/src/netrics/netson.py)**:
     Here, you must create a function that actually runs your test.  Have a look at
     [ping_latency](https://github.com/chicago-cdac/nm-exp-active-netrics/blob/9ff6291c783f93c30dd6eaf1855ed19c5a71845f/src/netrics/netson.py#L309)
     for inspiration.
     Most of these are simply calling a command line tool and parsing its output. 
     The functions set two things:
     (a) The raw output of the tool is returned, and passed into a dictionary, that gets zipped up, so that we retain all raw files.
     (b) The processed output is loaded into the `self.results` dictionary, which is shared across all tests in that instance,
         and dumped as a json, for upload by the management code.
4. Once you have your changes, you **must** test one-off cases, edge-cases, and continuous performance.
   For initial tests, you may want to just do `./netrics --your_test`.
   

   There are a few ways of doing this You may need to build the package to be able to test your changes. Change directories to the git repository and run make help. Follow the steps in make help to build the package.
Make changes to the files in the cloned git repository
Add new testing functions to netson.py located at ./src/netrics/netson.py
Add new argument flag and function call to netrics.py located at ./src/netrics.py
Test locally
Once you are ready to deploy the changes to the beta testers, commit your changes/open a pull request

After testing changes on your local device, push the changes to the master github branch and notify Marc to deploy the new package to testing devices

Update toml file at nm-exp-active-netrics/conf/toml with new line in cron for the added test
Add any necessary conf parameters to the configuration templates at nm-mgmt-cms/templates/*
Run deploy.tigerteam.sh
From tigerteam, run ssx a un

Local the source code on the device at /usr/local/src/nm-exp-active-netrics/
Add test function to netson.py located at /usr/local/src/nm-exp-active-netrics/src/netrics/
Add new argument flag and function call to netrics.py located at /usr/local/src/nm-exp-active-netrics/src/
Update cron file (‘cron-nm-exp-active-netrics’) located at /etc/cron.d/cron-nm-exp-active-netrics with new netrics command
