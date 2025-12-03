// routes.tf
// Route tables and associations for public and private subnets.

# -------------------------
# Public route table
# -------------------------
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  tags = merge(
    local.merged_tags,
    { Name = "${local.name_prefix}-public-rt" }
  )
}

resource "aws_route" "public_internet_access" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this.id
}

resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# -------------------------
# Private route tables
# -------------------------
resource "aws_route_table" "private" {
  count = length(aws_subnet.private)

  vpc_id = aws_vpc.this.id

  tags = merge(
    local.merged_tags,
    { Name = "${local.name_prefix}-private-rt-${count.index + 1}" }
  )
}

# Route from private subnets to NAT gateway (if enabled)
resource "aws_route" "private_internet_access" {
  count = var.enable_nat_gateway ? length(aws_route_table.private) : 0

  route_table_id         = aws_route_table.private[count.index].id
  destination_cidr_block = "0.0.0.0/0"

  # If single_nat_gateway = true, all private RTs use NAT[0]
  # Otherwise, each private RT uses its own NAT in the same AZ.
  nat_gateway_id = aws_nat_gateway.this[var.single_nat_gateway ? 0 : count.index].id
}

resource "aws_route_table_association" "private" {
  count = length(aws_subnet.private)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
