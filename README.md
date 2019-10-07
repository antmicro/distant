# Distributed build engine

## Prequisites

1. Coordinator machine in a GCP project, with permissions to start other virtual machines within a Compute Engine service.
2. Python3 with modules described in `requirements.txt`
3. `docker`, `docker-machine`, `sshfs`

## Usage

1. In your project Create/edit a `machines.txt` file, there is an example file: `machines.txt.example` file which presents the syntax. This file contains worker machine types with commands to be executed on each worker. 
2. (Optional) Create/edit a `local.txt` file. This file contains command(s) to be executed on the coordinator machine.
2. The `coordinator.py` script executed from the build project directory starts the execution. It will look for `machines.txt` and `local.txt` files in the project directory.

After each task has finished, logs and performance graphs are accessible in the `vmoutput` subdirectory of `<project_dir>`.

The engine uses the `antmicro/ubuntu-build-tools` docker image, basically Ubuntu 18.04 with the following tools: `python3 python3-pip build-essential git cmake`

The image can be changed in the `singlejob.py` file (the `pull` and `run` commands).

## Additional tools

The `./ninjatree.py` tool can be useful while dividing tasks between the workers and the coordinator machine. 
Usage: `./ninjatree.py <build_path> <start_target> <targets_list_file> <depth>`
Provide thr `build_path` with the `build.ninja` file, the initial target, a list of targets that will be executed on workers machines and the tree search depth. The Ninjatree tool will search the build tree for those targets and it will output a complementary list of targets to be performed on coordinator machine to have a complete `<start_target>` execution.
