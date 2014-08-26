# om

Collect disk usage, memory and cpu load info on remote boxes without having to install any software - as long as you can SSH into it.


## Features

- Disk and memory usage
- CPU load
- Supports email alerts when resources get to a critical state (e.g. nearly full disk, low free memory, high cpu load, etc)


## Installation

```shell
$ pip install om
```

## Usage

To collect usage for a host:

```shell
$ om 192.168.0.1
```

To collect usage for multiple hosts:

```shell
$ om 192.168.0.2,box2
```

The tool also supports username, password and port if needed:

```shell
$ om root:mypass@mybox:44445
```

## Extra customization (optional)

You can tweak the ssh and metrics settings by saving the configs into a json config file.

Running against a config file:

```shell
$ om -c <config.json>
```

### config.json format

#### Machines

The config file is a JSON and informs which machines are to be monitored.

```json
{
  "machines": {
    "my_rails_app": {
      "host": "125.22.13.12",
      "ssh": {
        "username": "foo",
        "password": "bar"
      }
    }
  }
}
```

The only required field is ''host''. ''ssh'' is entirely optional if your local agent is already able to use keys to get to the machine.

#### Metrics

The "metrics" section allows you to further customize your monitoring. Our current metrics are:

- disk_usage
- memory_usage

For instance, disk usages are reported as critical when they reach 80% usage. If for a certain box you want to be critical when it reaches 50%, then:

```json
{
  "machines": {
    "my_rails_app": {
      "host": "125.22.13.12",
      "metrics": {
        "disk_usage": {
          "thresholds": {
            "usage": "50%"
          }
        }
      }
    }
  }
}
```

You can also override the default value globally:

```json
{
  "machines": {
    "my_rails_app": {
      "host": "125.22.13.12",
    },
    "my_postgres": {
      "host": "postgresbox",
      "disk_usage": {
        "thresholds": {
          "usage": "60%"
        }
      }
    }
  },
  "metrics": {
    "disk_usage": {
      "thresholds": {
        "usage": "50%"
      }
    }
  }
}
```
