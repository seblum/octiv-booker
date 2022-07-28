# Octiv SlotBooker

![Octive Overview](https://github.com/seblum/octiv_booker/blob/163984791abc0a553de5e33fb548adf6aa07da9c/octiv_overview.png)


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
    │   │ main.tf
        │ ...
```

### slotBooker


### infrastructure



## Usage

### create key pair

```
aws ec2 create-key-pair \
    --key-name octivbooker \
    --key-type rsa \
    --key-format pem \
    --query "KeyMaterial" \
    --output text > octivbooker.pem

chmod 400 octivbooker.pem

ssh-keygen -y -f octivbooker.pem > octivbooker-public.pem

chmod 400 octivbooker-public.pem
```


## run locally

To run locally, one has to specify and ingest some variables which is otherwise handled by github actions.
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

- [ ] pull docker image on ec2 and make it run on cronjobs
- [x] create envs for octiv passwords
- [x] create docker envs for octiv passwords
- [x] pass envs from tf to docker envs for octiv passwords
- [x] move terraform to github actions
- [x] terraform statefile save on aws
- [ ] resolve issue with statefile s3 bucket on deletion
- [ ] write proper documentation
- [ ] enable full network on terraform
- [ ] put tags in infrastructure
- [ ] own network for ec2
- [ ] 
## env variables

run shell script using source set-credentials to set environment variables.

printenv
