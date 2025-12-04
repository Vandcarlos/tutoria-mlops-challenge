// main.tf
// Creates an ECR repository with scan on push and lifecycle policy.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_ecr_repository" "this" {
  name                 = local.repo_name
  image_tag_mutability = var.image_mutability
  force_delete = true

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  tags = local.merged_tags
}

resource "aws_ecr_lifecycle_policy" "this" {
  repository = aws_ecr_repository.this.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the most recent ${var.lifecycle_max_images} images"
        selection = {
          tagStatus = "any"
          countType = "imageCountMoreThan"
          countNumber = var.lifecycle_max_images
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
