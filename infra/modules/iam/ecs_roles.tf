########################################
# ECS task and execution roles
########################################

# Assume role policy for ECS tasks (generic)
data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

# Execution role: used by ECS agent to pull images and write logs
resource "aws_iam_role" "execution_role" {
  name               = local.execution_role_name
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = local.merged_tags
}

# Attach default AWS managed policy for ECS execution role
resource "aws_iam_role_policy_attachment" "execution_role_default" {
  role       = aws_iam_role.execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Task role: assumed by your application container
resource "aws_iam_role" "task_role" {
  name               = local.task_role_name
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = local.merged_tags
}
