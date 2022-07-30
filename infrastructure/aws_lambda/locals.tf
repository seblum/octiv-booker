locals {
  aws_ecr_url              = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com"
  ecr_repository_name      = "octiv-booker-lambda"
  ecr_image_tag            = "latest"
  cron_schedule_expression = "cron(0 20 ? * SAT,MON,TUE *)"
}
