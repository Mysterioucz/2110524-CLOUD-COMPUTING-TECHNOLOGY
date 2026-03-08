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
