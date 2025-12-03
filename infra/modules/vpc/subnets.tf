// subnets.tf
// Public and private subnets for the VPC.

resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.azs[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    local.merged_tags,
    {
      Name = "${local.name_prefix}-public-${count.index + 1}"
      Tier = "public"
    }
  )
}

resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.this.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.azs[count.index]

  tags = merge(
    local.merged_tags,
    {
      Name = "${local.name_prefix}-private-${count.index + 1}"
      Tier = "private"
    }
  )
}

# NAT EIPs (optional)
resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(aws_subnet.public)) : 0

  domain = "vpc"

  tags = merge(
    local.merged_tags,
    { Name = "${local.name_prefix}-nat-eip-${count.index + 1}" }
  )
}

# NAT Gateways (optional)
resource "aws_nat_gateway" "this" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(aws_subnet.public)) : 0

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    local.merged_tags,
    { Name = "${local.name_prefix}-nat-${count.index + 1}" }
  )

  depends_on = [aws_internet_gateway.this]
}
