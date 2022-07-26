
# build the image

docker build -t seblum/slotbooker:v1 .

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