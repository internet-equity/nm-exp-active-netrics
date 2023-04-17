<a id="vcqoe"></a>

# **vcqoe module**

Module to run vcqoe tests on meet or teams platform

<a id="cli"></a>

# cli

vcqoe command-line interface entry-point

<a id="cli.execute_client"></a>

#### execute\_client

```python
def execute_client(logger=None, trace_filename=None, config_file=None)
```

Execute the auto_call CLI command

<a id="cli.execute_server"></a>

#### execute\_server

```python
def execute_server(logger=None, trace_filename=None, config_file=None)
```

Execute the auto_call CLI command



<a id="vca"></a>

# vca

VCA Class to start test and capture metrics

<a id="vca.VCA"></a>

## VCA Objects

```python
class VCA()
```

<a id="vca.VCA.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config, filename)
```

Initiates a vca object

<a id="vca.VCA.launch_browser"></a>

#### launch\_browser

```python
def launch_browser()
```

Launches browser for running the video conference call

<a id="vca.VCA.dump_webrtc"></a>

#### dump\_webrtc

```python
def dump_webrtc()
```

Downloads webrtc file and copies the file to webrtc dump file in the vca-test module

<a id="vca.VCA.start_call"></a>

#### start\_call

```python
def start_call()
```

Starts a video call after opening browser

<a id="vca.VCA.end_call"></a>

#### end\_call

```python
def end_call(isServer)
```

Ends call once test is done

<a id="vca.VCA.copy_webrtc_stats"></a>

#### copy\_webrtc\_stats

```python
def copy_webrtc_stats(isadmitted)
```

copies webrtc stats file to a dump file in project file system and parses the webrtc to sumamrised metrics

<a id="vca.VCA.parse_webrtc"></a>

#### parse\_webrtc

```python
def parse_webrtc(json_vals)
```

parses webrtc to summarised metrics

<a id="vca.VCA.admit_client"></a>

#### admit\_client

```python
def admit_client()
```

Admits the client by clicking on admit client button

<a id="vca.VCA.wait_until_client_has_left"></a>

#### wait\_until\_client\_has\_left

```python
def wait_until_client_has_left()
```

waits until client has left to end the test



<a id="meet"></a>

# meet

Class for launching Google Meet Calls.

<a id="meet.Meet"></a>

## Meet Objects

```python
class Meet()
```

<a id="meet.Meet.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config)
```

Initiates a meet call object

<a id="meet.Meet.join_call_mac"></a>

#### join\_call\_mac

```python
def join_call_mac()
```

join the meet call by clicking join image

<a id="meet.Meet.join_call_raspi"></a>

#### join\_call\_raspi

```python
def join_call_raspi()
```

Join meet call on raspi

<a id="meet.Meet.join_call_linux"></a>

#### join\_call\_linux

```python
def join_call_linux()
```

Join meet call on linux

<a id="meet.Meet.join_call"></a>

#### join\_call

```python
def join_call()
```

Join a meet call after checking the os

<a id="meet.Meet.admit_client"></a>

#### admit\_client

```python
def admit_client()
```

Admit client on a meet call by clicking admit button on screen

<a id="meet.Meet.wait_until_client_has_left"></a>

#### wait\_until\_client\_has\_left

```python
def wait_until_client_has_left()
```

sleep until there is no client in the call

<a id="meet.Meet.exit_call"></a>

#### exit\_call

```python
def exit_call()
```

exit a meet call by clicking end call button on the screen





<a id="teams"></a>

# teams

Class for initiating the teams calls in client of browser

<a id="teams.Teams"></a>

## Teams Objects

```python
class Teams()
```

<a id="teams.Teams.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config)
```

Initiates a teams call object

<a id="teams.Teams.join_call_mac"></a>

#### join\_call\_mac

```python
def join_call_mac()
```

Join teams call on mac

<a id="teams.Teams.join_call_raspi"></a>

#### join\_call\_raspi

```python
def join_call_raspi()
```

Join teams call on raspi

<a id="teams.Teams.join_call_linux"></a>

#### join\_call\_linux

```python
def join_call_linux()
```

Join teams call on linux

<a id="teams.Teams.join_call"></a>

#### join\_call

```python
def join_call()
```

Join a teams call after checking the os

<a id="teams.Teams.exit_call"></a>

#### exit\_call

```python
def exit_call()
```

exit a teams call by clicking end call button on the screen

<a id="teams.Teams.admit_client"></a>

#### admit\_client

```python
def admit_client()
```

Admit client on a teams call by clicking admit button on screen

<a id="teams.Teams.wait_until_client_has_left"></a>

#### wait\_until\_client\_has\_left

```python
def wait_until_client_has_left()
```

sleep until there is no client in the call







<a id="capture"></a>

# capture

Functions for capturing network traffic

<a id="capture.CaptureTraffic"></a>

## CaptureTraffic Objects

```python
class CaptureTraffic(threading.Thread)
```

<a id="capture.CaptureTraffic.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config, filename)
```

Initiates a CaptureTraffic object

<a id="capture.CaptureTraffic.run"></a>

#### run

```python
def run()
```

calls function to run capture thread

<a id="capture.CaptureTraffic.stop_capture"></a>

#### stop\_capture

```python
def stop_capture(proc)
```

Stops capture thread

<a id="capture.CaptureTraffic.capture_traffic"></a>

#### capture\_traffic

```python
def capture_traffic()
```

Capture network traffic using input filter

<a id="pipe_video"></a>

# pipe\_video

functions for piping a video stream

<a id="pipe_video.PipeVideo"></a>

## PipeVideo Objects

```python
class PipeVideo()
```

<a id="pipe_video.PipeVideo.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config)
```

Initiates pipe video object

<a id="pipe_video.PipeVideo.start_pipe"></a>

#### start\_pipe

```python
def start_pipe()
```

Starts the piping of video in a separate thread

<a id="pipe_video.PipeVideo.end_pipe"></a>

#### end\_pipe

```python
def end_pipe()
```

ends process which is piping the video



<a id="webrtc"></a>

# webrtc

functions for parsing a webrtc json file to summarised metrics

<a id="webrtc.get_active_stream"></a>

#### get\_active\_stream

```python
def get_active_stream(webrtc_stats, pref)
```

Get most active stream in webrtc

**Arguments**:

- `webrtc_stats` - webrtc stats as a dict
- `pref` - prefix to search
  

**Returns**:

  List of active streams

<a id="webrtc.get_most_active"></a>

#### get\_most\_active

```python
def get_most_active(webrtc_stats, id_list, prefix)
```

Get most active stream in webrtc

**Arguments**:

- `webrtc_stats` - webrtc stats as a dict
- `prefix` - prefix from key prefixes dict
- `id_list` - list of active streams
  

**Returns**:

  returns the is of most active stream

<a id="webrtc.get_ts"></a>

#### get\_ts

```python
def get_ts(dt_str)
```

parse date string and to date object

<a id="webrtc.get_webrtc"></a>

#### get\_webrtc

```python
def get_webrtc(filename, logger, vca_name)
```

Get parsed webrtc with summarised metrics

**Arguments**:

- `filename` - webrtc file name
- `logger` - logger file object
- `vca_name` - name of vca conference
  

**Returns**:

  returns dict of parsed webrtc metrics

<a id="utility"></a>

# utility

Contains generic utility functions

<a id="utility.make_dir"></a>

#### make\_dir

```python
def make_dir(new_dir)
```

Creates a directory if it does not exists including the
parent directories

<a id="utility.time_diff"></a>

#### time\_diff

```python
def time_diff(st)
```

returns time difference with current time and st

<a id="utility.image_search"></a>

#### image\_search

```python
def image_search(image_name, haystack=None, threshold=0.8, grayscale=False)
```

searcges for an image on screen with pyautogui module

<a id="utility.click_image"></a>

#### click\_image

```python
def click_image(png_name,
                grayscale=False,
                confidence=0.9,
                max_num_tries=5,
                wait_interval=1)
```

locates and clicks an image on screen using pyautogui

<a id="utility.get_trace_filename"></a>

#### get\_trace\_filename

```python
def get_trace_filename(config, endpoint="client")
```

produce trace file name with current time and return the name

<a id="utility.locate_on_screen"></a>

#### locate\_on\_screen

```python
def locate_on_screen(png_file)
```

locate a png file image on screen with pyautogui

