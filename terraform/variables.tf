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