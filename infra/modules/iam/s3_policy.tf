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

resource "aws_iam_policy" "task_policy" {
  name   = local.policy_name
  policy = data.aws_iam_policy_document.task_s3_policy.json

  tags = local.merged_tags
}

resource "aws_iam_role_policy_attachment" "task_role_policy_attachment" {
  role       = aws_iam_role.task_role.name
  policy_arn = aws_iam_policy.task_policy.arn
}
