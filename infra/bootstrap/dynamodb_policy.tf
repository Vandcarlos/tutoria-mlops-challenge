data "aws_iam_policy_document" "lock_table" {
  statement {
    sid    = "AllowLockTFState"
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:DeleteItem",
      "dynamodb:UpdateItem",
      "dynamodb:DescribeTable"
    ]
    resources = [aws_dynamodb_table.tf_lock.arn]
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.oc_infra_deployer.arn]
    }
  }
}

resource "aws_dynamodb_resource_policy" "lock_table" {
  resource_arn = aws_dynamodb_table.tf_lock.arn
  policy       = data.aws_iam_policy_document.lock_table.json
}
