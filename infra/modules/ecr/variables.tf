variable "name" {
  type = string
}

variable "keep_last" {
  type    = number
  default = 10
}

variable "force_delete" {
  type        = bool
  default     = true
  description = "Allow destroy even if images remain (handy for dev teardown)."
}

variable "tags" {
  type    = map(string)
  default = {}
}
