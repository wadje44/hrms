variable "name" {
  type        = string
  description = "Name prefix for resources."
}

variable "cidr_block" {
  type    = string
  default = "10.0.0.0/16"
}

variable "azs" {
  type        = list(string)
  description = "Availability zones to spread subnets across."
}

variable "one_nat_per_az" {
  type        = bool
  default     = false
  description = "Set true in prod for HA NAT; false (single NAT) keeps dev cheap."
}

variable "tags" {
  type    = map(string)
  default = {}
}
