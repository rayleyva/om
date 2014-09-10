![Logo](logo.png)

[![Build Status](https://travis-ci.org/overseer-monitoring/om.svg?branch=master)](https://travis-ci.org/overseer-monitoring/om)
[![PyPI version](https://badge.fury.io/py/om.svg)](http://badge.fury.io/py/om)

## Table of Contents

- [What is om?](#what-is-om)
  - [Features](#features)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
  - [Running om](#running-om)
  - [Running om on Multiple Hosts](#running-om-on-multiple-hosts)
  - [Custom SSH user, password and port](#custom-ssh-user-password-and-port)
  - [Using a Configuration File](#using-a-configuration-file)
- [Configuration File](#configuration-file)
  - [Quick Reference](#quick-reference)
  - [Monitoring a Process](#processes)
  - [Plugins](#plugins)
    - [CPU, Memory and Disk Usage](#cpu-memory-and-disk-usage)
    - [Check if a Process is Running](#check-if-a-process-is-running)
    - [Check if Disk Usage is Over 50%](#check-if-disk-usage-is-over-50)
    - [Check if Disk Usage is Over 50% for All Hosts](#check-if-disk-usage-is-over-50-for-all-hosts)
  - [Handlers](#handlers)
- [Contributing to om](#contributing-to-om)
- [Hacking on om](#hacking-on-om)
- [License](#license)
- [Copyright](#copyright)

## What is om?

Collect disk usage, memory and cpu load info on remote boxes without having to install any software - as long as you can SSH into it.

### Features

- CPU load, disk and memory usage
- Supports email alerts when resources get to a critical state (e.g. nearly full disk, low free memory, high cpu load, etc)


## Installation

```shell
$ pip install om
```

## Basic Usage

### Running om

```shell
$ om 192.168.0.1
```

### Running om on Multiple Hosts

```shell
$ om 192.168.0.2,box2
```

### Custom SSH user, password and port

```shell
$ om root:mypass@mybox:44445
```

### Using a [Configuration File](#configuration-file)

```shell
$ om -c <config.json>
```

## Configuration File

The configuration file can be used for more advanced setups. Some use cases are monitoring multiple hosts, specifying
alarming values of disk, cpu or memory usage for a host or for all hosts, using custom handlers, monitoring process
status (running/stopped) and etc.

Please note that though the config file allows much customisation and host-specific settings, we suggest you to avoid
most of them. Our goal with om is to have the best defaults so you don't have to configure much.

### Quick Reference

The configuration file must have a ''hosts'' section to indicate which hosts you want to collect from. It can also
include ''ssh'', ''plugins'' and ''handlers'' sections for global configuration of SSH (username, password, port), [plugins](#plugins) and
[handlers](#handlers).

Hosts allow host-specific settings for SSH and plugins for more advanced setups.

```ruby
{
  "hosts": {
    # Hosts go here (required)

    "host1": {
      # IP or hostname goes here (required)
      "host": "179.25.15.2",

      "ssh": {
        # Host-specific SSH settings go here (optional)
      }

      "plugins": {
        # Host specific plugin configurations go here (optional)
      }
    }
  },

  "ssh": {
    # Global SSH settings go here (optional)
  },

  "plugins": {
    # Global plugin configurations go here (optional)
  }

  "handlers": {
    # Handlers configurations go here
  }
}
```

Remember that having your SSH keys in place for the current user allows you to skip configuring ''ssh''. om can already load them from the local agent

''ssh'' is entirely optional if your local agent is already able to use keys to get to the machine.

### Config file example

```ruby
{
  "ssh": {
    "username": "user001"
  },
  "hosts": {
    "webserver01": {
      "host": "webserver01.overseer.om",
      "plugins": [
        {
          "type": "process_state",
          "process_name": "nginx"
        },
        {
          "type": "process_state",
          "process_name": "postgres"
        }
      ]
    }
  },
  "plugins": [
    {
      "type": "disk_usage",
      "thresholds": {
        "usage": 90
      }
    }
  ],
  "handlers": {
    "stdout" : {},
  }
}
```

### Plugins

Plugins are the units that collect the metrics on the designated machines. Plugins are added as an object to the `plugins` list.

```shell
$ om -p
```

#### CPU, Memory and Disk Usage

CPU load, memory and disk usage have builtin plugins and are always collected by om. No further configuration is required.

#### Check if a Process is Running

Checking if a process ''nginx'' is running:

```ruby
{
  "hosts": {
    "my_web_server": {
      "host": "192.168.0.1",

      "plugins": [
        {
          "type": "process_state",
          "process_name" : "nginx"
        },
        {
          "type": "process_state",
          "process_name" : "unicorn"
        }
      ]
    }
  }

  ...
}
```

#### Check if Disk Usage is Over 50%

For instance, disk usages are reported as critical when they reach 80% usage. If for a certain box you want to be critical when it reaches 50%, then:

```json
{
  "hosts": {
    "my_rails_app": {
      "host": "125.22.13.12",

      "plugins": [
        {
          "type": "disk_usage",
          "thresholds": {
            "usage": "50%"
          }
        }
      ]
    }
  }

  ...
}
```

#### Check if Disk Usage is Over 50% for All Hosts

You can also override the default value globally:

```json
{
  "hosts": {
    "my_postgres": {
      "host": "postgresbox",
      "plugins_config": {
        "disk_usage": {
          "thresholds": {
            "usage": "60%"
          }
        }
      }
    }
  },

  "plugins": [
    {
      "type": "disk_usage",
      "thresholds": {
        "usage": "50%"
      }
    }
  ]
}
```

#### Disk Usage
Checks if disk usage is above a percentual threshold.
```ruby
{
  "type": "disk_usage",
  "thresholds": {
    "usage": "50%" #optional, default: 80%
  }
}
```

#### Memory Usage
Checks if memory usage is above a percentual threshold.
```ruby
{
  "type": "memory_usage",
  "thresholds": {
    "usage": "50%" #optional, default: 70%
  }
}
```

#### CPU Load
Checks if the CPU load average is above a percentual threshold for the past 1, 5 and 15 minutes intervals.
```ruby
{
  "type": "cpu_load",
  "thresholds": {
    "avg_1min":  "90%", #optional, default: 25%
    "avg_5min":  "80%", #optional, default: 50%
    "avg_15min": "75%"  #optional, default: 75%
  }
}
```

#### Process state
Checks if a process with a given name is running at the host.
```ruby
{
  "type": "process_state",
  "process_name": "<name of the process>"
}
```

### Handlers

Handlers receive the results of the plugins metrics and act upon them. Handlers can be as simple as the StdOut handler that simply prints the
results to stdout or can save the metrics to a database. Plugins can be configured to have thresholds that are used to detect if the measured value
indicates a risky situation. Handlers have access to this information and it can act only if the value is critical. For example, an Email handler
can be configured to mail sysadmins only if the value reaches a critical or bad value.

#### Standard Output
Simple handler that just dumps the metrics to the standard output
Name: `stdout`
Parameters: none

#### JSON Standard Output
Dumps the metrics to the standard output in JSON format
Name: `json_stdout`
Parameters: none

#### Email handler
Sends email whenever critical values are found for metrics
Name: `email`
Parameters:
```ruby
"handlers": {
  "email": {
    "smtp": "<smtp host>",
    "port": <smtp port>,
    "security": "<security mechanism used>", #optional, accepts starttls
    "login": "<smtp user login>",
    "password": "<smtp user password>",
    "from": "<from mail>",
    "to": ["<list of recipients>"],
    "subject": "<subject for the mail>", #optional
  }
}
```

#### Sqlite3 handler
Saves the metrics to a Sqlite3 database
Name: `sqlite3`
Parameters:
```ruby
"handlers": {
  "sqlite3": {
    "path": "<file path>",
    "expiration_days": <days after a metric is deleted>
  }
}
```

#### Redis handler
Saves the metrics to a Redis database
Name: `redis`
Parameters:
```ruby
"handlers": {
  "redis": {
    "host": "<redis host>",
    "port": <redis port>,
    "max_list_length": <number> #maximum number of metrics stored per instance and plugin
  }
}
```

## Contributing to om

You're encouraged to submit issues, PRs and weigh in with your opinion anywhere. If you want to know how to get started,
feel free to contact the authors either directly or through a new issue. We also love documentation so feel free to extend
this README.

## Hacking on om

Hacking locally is really easy. First clone the repository:

```shell
$ git clone https://github.com/overseer-monitoring/om.git
```

Install the requirements (we provide a quick makefile for that):

```shell
$ make
```

Run the daemon on a host:

```shell
$ cd om
$ PYTHONPATH=. ./bin/om <host>
```

Run tests:

```shell
$ make test
```

## License

LGPLv3 License. See LICENSE for details.

## Copyright

Copyright (c) 2014 André Dieb, Thiago Sousa Santos
