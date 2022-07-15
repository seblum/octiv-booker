# create ECR repo
resource aws_ecr_repository ecr_repo {
    name = local.ecr_repository_name
}

## Build docker images and push to ECR
resource docker_registry_image docker_ecr_image {
    name = "${aws_ecr_repository.ecr_repo.repository_url}:latest"

    build {
        context = "../slotBooker"
        dockerfile = "Dockerfile"
    }  
}



resource aws_lambda_function terraform_lambda_func {
    timeout          = 300 # change lamda timeout to 15 minutes
    image_uri        = "${aws_ecr_repository.ecr_repo.repository_url}@${docker_registry_image.docker_ecr_image.sha256_digest}"
    package_type     = "Image"
    function_name    = "OctiveBooker_Test_Lambda_Function"
    role             = aws_iam_role.lambda_role.arn
    #handler          = "index.lambda_handler"
    #runtime          = "python3.8"
    depends_on       = [aws_iam_role_policy_attachment.attach_iam_policy_to_iam_role]
}

resource aws_iam_role_policy_attachment attach_iam_policy_to_iam_role {
    role        = aws_iam_role.lambda_role.name
    policy_arn  = aws_iam_policy.iam_policy_for_lambda.arn
}

resource aws_iam_role lambda_role {
    name   = "OctiveBooker_Lambda_Function_Role"
    assume_role_policy = <<EOF
{
   "Version": "2012-10-17",
   "Statement": [
       {
           "Action": "sts:AssumeRole",
           "Principal": {
               "Service": "lambda.amazonaws.com"
           },
           "Effect": "Allow"
       }
   ]
}
 EOF
}

resource aws_iam_policy iam_policy_for_lambda {
    name         = "aws_iam_policy_for_terraform_aws_lambda_role"
    path         = "/"
    description  = "AWS IAM Policy for managing aws lambda role"
    policy = <<EOF
{
"Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*",
            "Effect": "Allow"
        }
    ]
}
 EOF
}