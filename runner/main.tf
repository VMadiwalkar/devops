resource "aws_instance" "self_runner" {
  ami           = var.os
  instance_type = var.type
  security_groups = [aws_security_group.allow_ssh.name]
  key_name = "runner"

  tags = {
    Name = "Self_Hosted-Runner"
  }
  


}


resource "null_resource" "post_apply" {
  depends_on = [aws_instance.self_runner]  # Ensure EC2 fully created

  provisioner "local-exec" {
    # command = "ls"
    command = "echo ${aws_instance.self_runner.public_ip} > ./ansible/terraform-output.txt"
  }


 
provisioner "local-exec" {
  
  command = <<EOF
echo [runner] > ./ansible/inventory.ini
EOF
}


 provisioner "local-exec" {
    
command = <<EOF
echo ${aws_instance.self_runner.public_ip} ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/runner.pem >> ./ansible/inventory.ini
  EOF
  }




#   provisioner "local-exec" {
#     command = "cd ansible && ansible-playbook github-runner.yml"
#   }
}

resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "Allow SSH inbound traffic"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
 

}






