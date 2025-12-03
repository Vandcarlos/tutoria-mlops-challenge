// main.tf
// Creates IAM roles and policies for ECS tasks:
// - Task role: assumed by the application container (app permissions, e.g. S3).
// - Execution role: used by the ECS agent (pull images, push logs).

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# -------------------------------------------------------------------
# Execution role (ECS agent: pull image, write logs)
# -------------------------------------------------------------------
resource "aws_iam_role" "execution_role" {
  name               = local.execution_role_name
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "execution_role_policy" {
  role       = aws_iam_role.execution_role.name
  # AWS managed policy used for ECS task execution (ECR pull, CloudWatch Logs, etc.)
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# -------------------------------------------------------------------
# Task role (application: S3, etc.)
# -------------------------------------------------------------------

# S3 access policy for the given bucket
data "aws_iam_policy_document" "task_s3_policy" {
  statement {
    sid = "AllowS3AccessToArtifactsBucket"

    actions = [
      "s3:ListBucket",
      "s3:GetBucketLocation"
    ]

    resources = [
      var.s3_bucket_arn
    ]
  }

  statement {
    sid = "AllowS3ObjectsAccessToArtifactsBucket"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      "${var.s3_bucket_arn}/*"
    ]
  }
}

resource "aws_iam_role" "task_role" {
  name               = local.task_role_name
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = local.merged_tags
}

resource "aws_iam_policy" "task_policy" {
  name   = local.policy_name
  policy = data.aws_iam_policy_document.task_s3_policy.json

  tags = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "task_role_policy_attachment" {
  role       = aws_iam_role.task_role.name
  policy_arn = aws_iam_policy.task_policy.arn
}
