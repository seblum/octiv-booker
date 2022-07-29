#!/bin/bash
set -ex

echo "updating system"
sudo yum update -y
sudo yum upgrade -y

echo "Installing docker"
sudo amazon-linux-extras install docker -y
sudo service docker start

sudo usermod -a -G docker ec2-user
sudo curl -L https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "Log into private ecr"
# TODO: install credentials store
aws ecr get-login-password --region "${region}" | docker login --username AWS --password-stdin "${awsid}".dkr.ecr."${region}".amazonaws.com

#sudo docker start
docker pull "${ecr_url}"
sleep 5

# systemctl enable docker
# systemctl start docker
# create cronjobs
# sudo crontab -l > cron_bkp
#sudo echo "0 10 * * * docker run octiv-booker:latest" >> cron_bkp
#sudo crontab cron_bkp
#sudo rm cron_bkp

sudo touch /etc/cron.d/slotbooker-cronjobs
echo " # This file contains cron jobs that runs every day at 18 o'clock.
# run saturday to book for thursday
0 20 ? SAT * docker run octiv-booker:latest" | sudo tee -a /etc/cron.d/slotbooker-cronjobs
echo " # run monday and tuesday to book for weekend
0 12 ? MON,TUE * docker run octiv-booker:latest" | sudo tee -a /etc/cron.d/slotbooker-cronjobs


# Give execution rights on the cron job
sudo chmod 0755 /etc/cron.d/slotbooker-cronjobs
