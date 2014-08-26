# om

## Table of Contents

- [What is om?](#what-is-om)
  - [Features](#features)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Configuration File](#configuration-file)
  - [Specifying Machines](#specifying-machines)
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

## Configuration File

### Specifying Machines

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

### Plugins

The "plugins" section allows you to further customize your monitoring. Our current plugins are:

- disk_usage
- memory_usage
- cpu_load
- process_state

For instance, disk usages are reported as critical when they reach 80% usage. If for a certain box you want to be critical when it reaches 50%, then:

```json
{
  "machines": {
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
