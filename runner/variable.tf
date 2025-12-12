variable "type" {
    description = "Type of instance to launch"
    type        = string
    default     = "t3.micro"
  
}
variable "os" {
    type    = string
    default = "ami-0ecb62995f68bb549"
    description = "The AMI ID for the ubuntu operating system"
  
}
