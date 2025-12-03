# Grants AdministratorAccess to the oc-infra-deployer role.
# This role will be assumed by GitHub Actions via OIDC during Terraform deployments.
resource "aws_iam_role_policy_attachment" "oc_infra_admin" {
  role       = aws_iam_role.oc_infra_deployer.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
