variable "name" {
  type        = string
  description = "Secret name prefix."
}

variable "recovery_window_in_days" {
  type        = number
  default     = 0
  description = "0 = delete immediately (good for dev); use 7-30 in prod."
}

variable "tags" {
  type    = map(string)
  default = {}
}
