
resource "aws_iam_role" "ec2_role_octiv_booker" {
  name = "ec2_role_octiv_booker"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF

  tags = {
    project = "octive-booker"
  }
}


resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2_profile_hello_world"
  role = aws_iam_role.ec2_role_octiv_booker.name
}


resource "aws_iam_role_policy" "ec2_policy" {
  name = "ec2_policy"
  role = aws_iam_role.ec2_role_octiv_booker.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchImportUpstreamImage",
        "ecr:CreatePullThroughCacheRule"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}
