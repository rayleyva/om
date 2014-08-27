![Logo](logo.png)

[![Build Status](https://travis-ci.org/overseer-monitoring/om.svg?branch=master)](https://travis-ci.org/overseer-monitoring/om)
[![PyPI version](https://badge.fury.io/py/om.svg)](http://badge.fury.io/py/om)

## Table of Contents

- [What is om?](#what-is-om)
  - [Features](#features)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
  - [Running om](#running-om-on-a-host)
  - [Running om on Multiple Hosts](#running-om-on-multiple-hosts)
  - [Custom SSH user, password and port](#ssh-username-password-and-port)
  - [Using a Configuration File](#running-om-using-a-configuration-file)
- [Configuration File](#configuration-file)
  - [Quick Reference](#quick-reference)
  - [Monitoring a Process](#processes)
  - [Plugins](#plugins)
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
include ''ssh'' and ''plugins'' sections for global configuration of SSH (username, password, port) and [plugins](#plugins).

Hosts allow host-specific settings for SSH and plugins for more advanced setups.

```json
{
  "hosts": {
    # Hosts go here
    # (required)

    "host1": {

      # IP or hostname goes here
      "host": "179.25.15.2",

      "ssh": {
        # Host-specific SSH settings go here
        # (optional)
      }

      "plugins": {
        # Host specific plugin configurations go here
        # (optional)
      }
    }
  },

  "ssh": {
    # Global SSH settings go here
    # (optional)
  },

  "plugins": {
    # Global plugin configurations go here
    # (optional)
  }
}
```

Remember that having your SSH keys in place for the current user allows you to skip configuring ''ssh''. om can already load them from the local agent

''ssh'' is entirely optional if your local agent is already able to use keys to get to the machine.

### Plugins

The "plugins" section allows you to further customize your monitoring. Our current plugins are:

- disk_usage
- memory_usage
- cpu_load
- process_state

For instance, disk usages are reported as critical when they reach 80% usage. If for a certain box you want to be critical when it reaches 50%, then:

```json
{
  "hosts": {
    "my_rails_app": {
      "host": "125.22.13.12",
      "plugins": {
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
  "hosts": {
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
  "plugins": {
    "disk_usage": {
      "thresholds": {
        "usage": "50%"
      }
    }
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
