#!/bin/bash
set -ex

echo "UPDATING SYSTEM"
sudo yum update -y
sudo yum upgrade -y

echo "INSTALLING DOCKER"
sudo amazon-linux-extras install docker -y
sudo service docker start
# systemctl enable docker
# systemctl start docker

sudo usermod -a -G docker ec2-user
sudo curl -L https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "LOG INTO PRIVATE ECR"
# TODO: install credentials store
aws ecr get-login-password --region "${region}" | docker login --username AWS --password-stdin "${awsid}".dkr.ecr."${region}".amazonaws.com

# pull image
docker pull "${ecr_url}"

echo "LIST DOCKER IMAGES"
docker images

echo "CREATE CRONJOBS"
sudo touch /etc/cron.d/slotbooker-cronjobs
echo "
# This file contains cron jobs that runs every day at 18 o'clock.
# run saturday to book for thursday
0 20 * * 6 root sudo docker run -v /home/ec2-user/tmp:/app/tmp/ 855372857567.dkr.ecr.eu-central-1.amazonaws.com/octiv-booker

# run monday and tuesday to book for weekend
0 12 * * 1,2 root sudo docker run -v /home/ec2-user/tmp:/app/tmp/ 855372857567.dkr.ecr.eu-central-1.amazonaws.com/octiv-booker

# test to run it every 3 minutes
# */3 * * * * root sudo docker run -v /home/ec2-user/tmp:/app/tmp/ 855372857567.dkr.ecr.eu-central-1.amazonaws.com/octiv-booker
" | sudo tee -a /etc/cron.d/slotbooker-cronjobs

# Give execution rights on the cron job
sudo chmod 0644 /etc/cron.d/slotbooker-cronjobs


# create cronjobs
# sudo crontab -l > cron_bkp
#sudo echo "0 10 * * * docker run octiv-booker:latest" >> cron_bkp
#sudo crontab cron_bkp
#sudo rm cron_bkp
