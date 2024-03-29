# Distant distributed build engine tutorial

## Prequisites

1. Working GCP account with full access to the Compute Engine API within the test project.
2. Google Cloud SDK installed, according to this instruction: `https://cloud.google.com/sdk/install`
3. Google Cloud vCPUs quota adequate to your needs. 

## Steps


### Authenticate in Google Cloud Platform

1. Use `gcloud auth login` to authenticate.
2. Use `gcloud config set project <project_name>` to switch to the test project.


### Create coordinator machine

1. Zone 'europe-west-4a' for the coordinator machine is now hardcoded in the coordinator engine - it will be changed in the upcoming releases.
2. Execute `gcloud compute instances create <instance_name> --machine-type=<machine_type> --image-family=ubuntu-1804-lts --image-project=ubuntu-os-cloud --zone=europe-west4-a --scopes=default,compute-rw`. It will assume a disk size of 10 GB, this size can be changed by using the `--boot-disk-size` flag. This machine will have permissions to create worker machines within the current project.
3. Login via ssh to the newly created machine with `gcloud compute ssh <your_GCP_username_without_domain>@<machine_name>`. If it fails - wait a few seconds, this can happen due to the fact that GCP finishes creating a virtual machine in the background. 

### Install necessary components

1. git & sshfs:
```
sudo apt update && sudo apt -y install git sshfs
```
2. docker: 
```
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

```
3. docker-machine: 
```
base=https://github.com/docker/machine/releases/download/v0.16.0 
curl -L $base/docker-machine-$(uname -s)-$(uname -m) >/tmp/docker-machine 
sudo mv /tmp/docker-machine /usr/local/bin/docker-machine
chmod +x /usr/local/bin/docker-machine

```

Add user to docker group: `sudo usermod -aG docker $USER` and relog so that your docker group membership becomes valid.

4. Clone repository: `git clone https://github.com/antmicro/distant.git && cd distant`
5. Install requirements: `sudo apt-get install -y python3-pip && pip3 install -r requirements.txt`
6. Copy `config.ini.example` to `config.ini` and review the settings.

### Usage

The machine is now ready to perform distributed builds/testing. It can be tested by using this simple example:

Create a project dir and inside it create a `machines.conf` file with worker definitions, like:

```
n1-standard-4 echo worker1 here!
c2-standard-8 echo worker2 here!
```

Start the coordinator process from this project directory, by executing `<distributed_engine_dir>/coordinator.py`

The coordinator will spin the machines, perform the tasks, gather the results and dispose of the worker machines. 

After the tasks have been completed, the `vmoutput` subdirectory in project directory will present output logs and generate performance graphs for each worker.
