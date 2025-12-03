// locals.tf
// Derived values and naming helpers.

locals {
  task_family  = "${var.name_prefix}-task"
  service_name = "${var.name_prefix}-service"
}
