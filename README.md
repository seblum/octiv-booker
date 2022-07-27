
# Structure

|
|--
# build the image

docker build -t seblum/slotbooker:v1 .

docker build \
--build-arg OCTIV_USERNAME=??? \
--build-arg OCTIV_PASSWORD=??? \
-t seblum/slotbooker:v1 \
--no-cache .

or

docker run \
-e OCTIV_USERNAME \ 
-e OCTIV_PASSWORD \
seblum/slotbooker:v1

# create key pair

aws ec2 create-key-pair \
    --key-name octivbooker \
    --key-type rsa \
    --key-format pem \
    --query "KeyMaterial" \
    --output text > octivbooker.pem

chmod 400 octivbooker.pem

ssh-keygen -y -f octivbooker.pem > octivbooker-public.pem

chmod 400 octivbooker-public.pem

# terraform

1. set your terraform backend
2. login to cloud
3. does not work with docker...
# TODO

- [ ] pull docker image on ec2 and make it run on cronjobs
- [x] create envs for octiv passwords
- [x] create docker envs for octiv passwords
- [x] pass envs from tf to docker envs for octiv passwords
- [ ] move terraform to github actions
- [ ] terraform statefile save on aws
- [-] add terraform cloud to save statefile
- [ ] write proper documentation
- [ ] put tags in infrastructure
# env variables

run shell script using source set-credentials to set environment variables.

printenv
