# Octiv SlotBooker

![Octive Overview](https://github.com/seblum/octiv_booker/blob/d434b11827b830aa7dd0e0614558034dbaabe66f/octiv_overview.png)

Octiv Slotbooker is, as the name says, used to book a slot/class for the fitness app Octiv. I developed it mainly for personal reasons so I can automate the weekly booking of classes. The functionality is based on selenium. 

## Structure 

The repository includes the app itself written in python and a Dockerfile under `slotBooker`. The directory `infrastructure` includes the terraform scripts to deploy the app on AWS ECR and to either run it on an AWS EC2 instance with cron or run it on AWS Lambda using cloudwatch events. The latter is merely an attempt though and is not working properly due to the combination of docker and AWS Lambda. 

Deployment of terraform can be done using Github actions or of course manually on a local environment.

```
OCTIV_BOOKER
│   README.md
│   Makefile
│   .pre-commit-config.yaml
│
└───.github/workflows
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

## Prerequisites

One has to create an S3 Bucket named `octivbookerterraform` previous to run terraform and be able to apply terraform. This is a prerequisite for the backend to store the tf.statefile on AWS. Of course, the bucket can be named otherwise, one has to adjust the backend.tf as well though.

To run locally, one needs to have the AWS CLI, Terraform, and Docker installed and proberly configured. To run the app without docker, one also needs to install chromedriver for selenium.

## Usage

### Github Actions

To run Github actions, one has to set github secrets for the relevant variables in the workflow. This includes `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` for the AWS account to apply the ressources. `OCTIV_PASSWORD` and `OCTIV_USERNAME` of ones octivapp account, and a `PUBLIC_PEM_KEY` from an aws key pair dedicated to ssh into an ec2 instance.

The private and public pem key can be created using the following commands.
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

### Local development

All secrets needed for github actions are needed for local execution as well. `OCTIV_PASSWORD`, `OCTIV_USERNAME`, and `PUBLIC_PEM_KEY` have to be inserted at runtime. `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` need to be configured with the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

In case one wants to only run the python script, two environment variables including the `octiv_username` and `octiv_password` need to be configured previously. This can be done running the included script `source set-credentials.sh`.

Build the image locally needs to have both variables specified either in the `docker build` or the `docker run`. This can be done using following commands.

```
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

## Known issues

- `Error: Error pushing docker image: Error response from daemon: Bad parameters and missing X-Registry-Auth: EOF` This Error can occur during terraform apply in Github Actions during building of the Docker image.. It works running terraform apply locally though.
- `Error: Error building docker image: 0: failed to solve with frontend dockerfile.v0: failed to create LLB definition: no active session for wx08tjz0ezhyc8zt4z1qlmica: context deadline exceeded` This Error can occur during terraform apply in Github Actions during building of the Docker image.. It works running terraform apply locally though.


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
- [ ] refactor AWS_Lambda for github actions
