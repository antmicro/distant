# Distributed build engine

## Prequisites

1. Coordinator machine in GCP project, with permissions to start other virtual machines within Compute Engine service.
2. Python3 with modules described in requirements.txt
3. Docker, docker-machine, sshfs

## Usage

1. In your project Create/edit machines.txt file, there is example file: machines.txt.example with syntax. This file contains worker machines types with commands to be executed on each worker. 
2. (Optional) Create/edit local.txt file. This file contains command(s) to be executed on coordinator machine.
2. coordinator.py script executed from build project directory - starts execution. It will look for machines.txt and local.txt files in project directory.

After each task has finished logs and performance graphs are accessible in vmoutput subdirectory of <project_dir>.

Engine uses 'antmicro/ubuntu-build-tools' docker image, basically Ubuntu 18.04 with tools: python3 python3-pip build-essential git cmake

Image can be changed in singlejob.py file (pull and run commands).

## Additional tools

./ninjatree.py tool can be useful while dividing tasks between workers and coordinator machine. 
Usage: ./ninjatree.py <build_path> <start_target> <targets_list_file> <depth>
Provide build_path with build.ninja file, initial target, list of targets that will be executed on workers machines and tree search depth. Ninjatree tool will search build tree for those targets and it will output complementary list of targets to be performed on coordinator machine to have complete <start_target> execution.

