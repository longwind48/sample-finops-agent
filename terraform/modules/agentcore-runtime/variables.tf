variable "project_name" {
  description = "Name prefix for resources"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "container_uri" {
  description = "Full container URI for aws-api-mcp-server"
  type        = string
}

variable "aws_policy_arn" {
  description = "AWS managed policy ARN for runtime permissions (e.g., ReadOnlyAccess)"
  type        = string
  default     = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

variable "cur_bucket_name" {
  description = "S3 bucket name for CUR data (used to scope Athena results write permissions). Defaults to wildcard pattern if empty."
  type        = string
  default     = ""
}

variable "athena_results_bucket_name" {
  description = "S3 bucket name for Athena query results (used to scope write permissions). Defaults to wildcard pattern if empty."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
