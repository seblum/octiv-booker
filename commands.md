Exemplary commands for local delevolment

```bash

sudo cat /var/log/cloud-init-output.log 

aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin <account-number>.dkr.ecr.eu-central-1.amazonaws.com

aws ecr list-images --repository-name octiv-booker --region eu-central-1

aws ecr batch-delete-image --repository-name octiv-booker-lambda --image-ids imageTag=latest --region eu-central-1

docker run -v /home/ec2-user/tmp:/app/tmp/ <account-number>.dkr.ecr.eu-central-1.amazonaws.com/octiv-booker

systemctl status crond.service

sudo cat /etc/cron.d/slotbooker-cronjobs

echo "Europe/Berlin" | sudo tee /etc/timezone
sudo timedatectl set-timezone Europe/Berlin
```