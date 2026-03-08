# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "Main-IGW" }
}

# Route Table for public subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "Public-RT" }
}

# Default route to Internet Gateway
resource "aws_route" "internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

# Associate public subnet with route table
resource "aws_route_table_association" "app_inet" {
  subnet_id      = aws_subnet.app_inet.id
  route_table_id = aws_route_table.public.id
}

# Private Interface (Interface 2)
resource "aws_network_interface" "private_eni" {
  subnet_id       = aws_subnet.app_db_a.id
  security_groups = [aws_security_group.db_client_sg.id]
  tags            = { Name = "App-DB-Interface" }
}

# Attach Private Interface to the EC2 Instance
resource "aws_network_interface_attachment" "private_eni_attach" {
  instance_id          = aws_instance.wordpress.id
  network_interface_id = aws_network_interface.private_eni.id
  device_index         = 1
}

# Associate Elastic IP with the Instance's primary interface
resource "aws_eip" "wp_eip" {
  instance = aws_instance.wordpress.id
  domain   = "vpc"
}
