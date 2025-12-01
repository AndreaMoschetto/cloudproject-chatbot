resource "aws_cognito_user_pool" "users" {
  name = "cloud-nlp-user-pool"

  # --- AGGIUNTA FONDAMENTALE 1 ---
  # Dice a Cognito: "L'utente usa l'email come username per il login"
  username_attributes = ["email"]
  # -------------------------------

  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  # --- AGGIUNTA FONDAMENTALE 2 ---
  # Obbliga l'utente a inserire l'email durante la registrazione
  schema {
    attribute_data_type = "String"
    name                = "email"
    required            = true
    mutable             = true
  }
}

# ... Il resto (client, domain) rimane uguale ...


resource "aws_cognito_user_pool_client" "client" {
  name = "cloud-nlp-frontend-client"
  user_pool_id = aws_cognito_user_pool.users.id
  
  generate_secret = true # Chainlit supports client secret
  
  # OAuth Configuration (Standard for Chainlit)
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  supported_identity_providers         = ["COGNITO"]
  
  read_attributes = ["email", "email_verified", "name", "preferred_username"]
  
  callback_urls = ["http://localhost:8001/auth/oauth/aws-cognito/callback"]
}

# 3. Dominio per la pagina di login ospitata da AWS
resource "aws_cognito_user_pool_domain" "main" {
  domain       = "cloud-nlp-project-${random_string.suffix.result}" # Nome unico random
  user_pool_id = aws_cognito_user_pool.users.id
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}