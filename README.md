# overseer-mini

Minimal monitoring system. Monitors any machine without having to install any software - as long as you can SSH into it.


## Features

- Monitoring multiple machines
- Metrics: disk and memory usage
- Email alerts


## Usage

To collect metrics for a host:

```shell
$ ./om 192.168.0.1
```

To collect metrics for multiple hosts (also supports hostnames):

```shell
$ ./om 192.168.0.2,box2
```

Hostname also supports username, password and port if needed:

```shell
$ ./om root:mypass@mybox:44445
```

## Installation

No packages have been released yet. For a development preview, please fetch the code:

```shell
$ git clone https://github.com/overseer-monitoring/overseer-mini.git
$ cd overseer-mini
$ pip install -r requirements.txt
$ ./om
```

## Usage

### Using a config file

```shell
$ ./om -c <config.json>
```

## Configuration

### Machines

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

### Metrics

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
          "critical": "50%"
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
        "critical": "60%"
      }
    }
  },
  "metrics": {
    "disk_usage": {
      "critical": "50%"
    }
  }
}
```
