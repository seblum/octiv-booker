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




resource "aws_cloudwatch_event_rule" "octiv_scheduler" {
    name = "octiv_scheduler"
    description = "Fires Saturday, Monday, and Tuesday at 8pm five minutes"
    schedule_expression = "cron(0 20 ? * SAT,MON,TUE *)" #"rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "check_octiv_scheduler" {
    rule = aws_cloudwatch_event_rule.octiv_scheduler.name
    target_id = "terraform_lambda_func"
    arn = aws_lambda_function.terraform_lambda_func.arn
}



resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_octiv" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.terraform_lambda_func.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.octiv_scheduler.arn
}