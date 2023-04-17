<a id="main_client"></a>

# main\_client

vcqoe command-line interface entry-point

<a id="main_client.start_virtual_display"></a>

#### start\_virtual\_display

```python
def start_virtual_display(config)
```

Starts a virtual display with the given resolutions in config file.

**Arguments**:

- `config` - dictionary containing config information
  

**Returns**:

  None

<a id="main_client.stop_virtual_display"></a>

#### stop\_virtual\_display

```python
def stop_virtual_display()
```

Stops virtual display

<a id="main_client.get_vca"></a>

#### get\_vca

```python
def get_vca(config)
```

Get the vca meeting to run (teams/meet)

<a id="main_client.connect_to_server"></a>

#### connect\_to\_server

```python
def connect_to_server(vca, host, port)
```

Connect to host server at the end point http://{host}:{port}/run-test?vca={vca}

**Arguments**:

- `vca` - vca name (meet/teams)
- `host` - url to connect to host
- `port` - port to connect to with the host url
  

**Returns**:

  response as a json

<a id="main_client.start_test"></a>

#### start\_test

```python
def start_test(config_file)
```

Start the vca test. Calls the corresponding code for client/server

**Arguments**:

- `config_file` - dictionary containing config information
  

**Returns**:

  None

<a id="main_client.set_logger"></a>

#### set\_logger

```python
def set_logger(config)
```

Creates the logger file to output test log information

**Arguments**:

- `config` - dictionary containing config information
  

**Returns**:

  None

<a id="main_client.connect_and_set_vca"></a>

#### connect\_and\_set\_vca

```python
def connect_and_set_vca(config_file)
```

Tries to connect to host after getting the vca conference to run

**Arguments**:

- `config_file` - dictionary containing config information
  

**Returns**:

- `Boolean` - True is successfully connected to host. Else, False.

## vcqoe module

[Module to run vcqoe tests on meet or teams platform](https://github.com/tarunmangla/netrics-vca-test/blob/main/vca_automation/vcqoe/README.md)
