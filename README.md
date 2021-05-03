# Distant - Antmicro's distributed build engine

Copyright (c) 2019-2021 [Antmicro](https://www.antmicro.com)

## Scenario

Distant - distributed cloud build utilizes cloud virtual machines to spread build/test workloads. It assumes there is a preparation phase executed on the coordinator machine (setting envs, executing common jobs), after which test/build execution can be distributed to worker machines.

## Prerequisites

1. Coordinator machine in a GCP project, with permissions to start other virtual machines within a Compute Engine service.
2. Python 3 with modules described in `requirements.txt`
3. `docker`, `docker-machine`, `sshfs`

## Usage

1. In your project Create/edit a `machines.conf` file, there is an example file: `machines.conf.example` file which presents the syntax. This file contains worker machine types with commands to be executed on each worker.
2. (Optional) Create/edit a `local.conf` file. This file contains command(s) to be executed on the coordinator machine.
2. The `coordinator.py` script executed from the build project directory starts the execution. It will look for `machines.conf` and `local.conf` files in the project directory.

The coordinator.py script can work in two modes (GCPSTORAGE setting in config.ini).

1. With worker machines storage spaces mounted to the coordinator machine via sshfs. This mode requires no preparation, just execute `coordinator.py -f build_subdir` in fork phase.
2. With the GCP block storage used to move project content to the worker machines. This mode requires a virtual disk to be mounted in the preparation phase via `coordinator.py -p build_subdir`, then in the fork phase execute `coordinator.py -f build_subdir`.

After each task has finished, logs and performance graphs are accessible in the `vmoutput` subdirectory of `<project_dir>`.

The engine uses the `antmicro/ubuntu-build-measure-tools` docker image, basically Ubuntu 18.04 with the following tools: `python3 python3-pip build-essential git cmake`

The image can be changed in the `singlejob.py` file (the `pull` and `run` commands).

