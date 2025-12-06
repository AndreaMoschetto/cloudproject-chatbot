variable "google_api_key" {
  description = "Google API Key for accessing Google Cloud services."
  type        = string
  sensitive   = true
}

variable "telegram_token" {
  description = "Telegram Bot Token"
  type        = string
  sensitive   = true
}

variable "chainlit_auth_secret" {
  description = "Secret for Chainlit session signing"
  type        = string
  sensitive   = true
}

variable "allowed_telegram_ids" {
  description = "List of allowed Telegram user IDs comma separated"
  type        = string
  default     = "" 
}