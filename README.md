# Octiv SlotBooker

![Octive Overview](https://github.com/seblum/octiv_booker/blob/d434b11827b830aa7dd0e0614558034dbaabe66f/octiv_overview.png)


## Structure

```
OCTIV_BOOKER
│   README.md
│   Makefile
│   .pre-commit-config.yaml
│
└───slotBooker
│   │   Dockerfile
│   │   poetry.Dockerfile
│   │   ...
│   │
│   └───slotbooker
│       │   booker.py
│       │   config.yaml
│       │   ...
│
└───infrastructure
    └───aws_EC2
    │   │ main.tf
    │   │ ...
    │
    └───aws_lambda
        │ main.tf
        │ ...
```

### slotBooker


### infrastructure



## Usage
## Prerequesits

### Create Bucket for tf.state

create bucket octivbookerterraform to store state file.
### create key pair

```
# create a private key pair to ssh into ec2
aws ec2 create-key-pair \
    --key-name octivbooker \
    --key-type rsa \
    --key-format pem \
    --query "KeyMaterial" \
    --output text > octivbooker.pem

# make it executable for local development
chmod 400 octivbooker.pem

# create a public key based on the private one
ssh-keygen -y -f octivbooker.pem > octivbooker-public.pem

# make it executable for local development
chmod 400 octivbooker-public.pem
```

```

ssh -i "octivbooker-public.pem" ec2-user@ec2-3-66-213-246.eu-central-1.compute.amazonaws.com
````

## run locally

To run locally, one has to specify and ingest some variables which is otherwise handled by github actions.

You need to have AWS CLI, Terraform, and Docker installed and proberly configured
### Set environment variables

run shell script using source set-credentials to set environment variables.

printenv

### build the image

```bash
docker build -t seblum/slotbooker:v1 .

docker build \
--build-arg OCTIV_USERNAME=??? \
--build-arg OCTIV_PASSWORD=??? \
-t seblum/slotbooker:v1 \
--no-cache .

docker run \
-e OCTIV_USERNAME \
-e OCTIV_PASSWORD \
seblum/slotbooker:v1
```

## TODO

- [x] create envs for octiv passwords
- [x] create docker envs for octiv passwords
- [x] pass envs from tf to docker envs for octiv passwords
- [x] move terraform to github actions
- [x] terraform statefile save on aws
- [x] resolve issue with statefile s3 bucket on deletion
- [x] enable full network on terraform
- [x] put tags in infrastructure
- [x] own network for ec2
- [ ] pull docker image on ec2 and make it run on cronjobs
- [ ] write proper documentation
- [ ] refactor AWS_Lambda for github actions
