resource "aws_ecs_task_definition" "this" {
  family                   = var.name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu                = tostring(var.cpu)
  memory             = tostring(var.memory)
  execution_role_arn = var.execution_role_arn
  task_role_arn      = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = var.name
      image     = var.container_image
      essential = true

      command = length(var.command) > 0 ? var.command : null

      environment = [
        for k, v in var.environment : {
          name  = k
          value = v
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = var.log_group_name
          awslogs-region        = local.aws_region
          awslogs-stream-prefix = var.name
        }
      }
    }
  ])
}
