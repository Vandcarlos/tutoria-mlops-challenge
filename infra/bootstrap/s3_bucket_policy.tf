data "aws_iam_policy_document" "tf_state_bucket_policy" {
  statement {
    sid    = "AllowInfraRoleList"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.oc_infra_deployer.arn]
    }

    actions = ["s3:ListBucket"]
    resources = [
      aws_s3_bucket.tf_state.arn,
    ]
  }

  statement {
    sid    = "AllowInfraRoleCrudObjects"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.oc_infra_deployer.arn]
    }

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:AbortMultipartUpload",
    ]

    resources = [
      "${aws_s3_bucket.tf_state.arn}/*",
    ]
  }
}

resource "aws_s3_bucket_policy" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id
  policy = data.aws_iam_policy_document.tf_state_bucket_policy.json
}
