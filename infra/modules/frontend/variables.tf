variable "bucket_name" {
  type        = string
  description = "Globally-unique S3 bucket name for the SPA."
}

variable "force_destroy" {
  type    = bool
  default = true
}

variable "price_class" {
  type    = string
  default = "PriceClass_100"
}

variable "aliases" {
  type    = list(string)
  default = []
}

variable "acm_certificate_arn" {
  type        = string
  default     = ""
  description = "ACM cert (us-east-1) for a custom domain. Empty = CloudFront default cert."
}

variable "tags" {
  type    = map(string)
  default = {}
}
