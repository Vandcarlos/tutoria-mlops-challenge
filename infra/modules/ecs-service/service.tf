// service.tf
// ECS Fargate Service associated with the task definition and ALB target group.

resource "aws_ecs_service" "this" {
  name            = local.service_name
  cluster         = var.cluster_arn
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  platform_version = var.platform_version

  deployment_minimum_healthy_percent = var.deployment_minimum_healthy_percent
  deployment_maximum_percent         = var.deployment_maximum_percent

  network_configuration {
    subnets         = var.subnet_ids
    security_groups = var.security_group_ids
    assign_public_ip = var.assign_public_ip
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = var.container_name
    container_port   = var.container_port
  }

  lifecycle {
    // Ignore changes to task_definition so that external deployments
    // (e.g. using CodeDeploy or blue/green strategies) are not blocked by Terraform.
    ignore_changes = [task_definition]
  }
}
