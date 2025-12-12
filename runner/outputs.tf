output "runner_public_ip" {
  value = aws_instance.self_runner.public_ip
}
output "runner_instance_id" {
  value = aws_instance.self_runner.id
}