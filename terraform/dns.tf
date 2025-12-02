# --- Reads Route53 Zone ---
data "aws_route53_zone" "main" {
  name         = "am-cloudnlpchatbot.site" # Personal domain purchased on Namecheap
  private_zone = false
}

# --- Requests SSL Certificate (ACM) ---
resource "aws_acm_certificate" "cert" {
  domain_name       = data.aws_route53_zone.main.name
  validation_method = "DNS"

  # We also add the wildcard *.domain for future safety
  subject_alternative_names = ["*.${data.aws_route53_zone.main.name}"]

  tags = {
    Name = "cloud-nlp-cert"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# --- CREATES DNS RECORDS TO VALIDATE THE CERTIFICATE ---
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => dvo
  }

  allow_overwrite = true
  name            = each.value.resource_record_name
  records         = [each.value.resource_record_value]
  ttl             = 60
  type            = each.value.resource_record_type
  zone_id         = data.aws_route53_zone.main.zone_id
}

# --- WAITS FOR THE CERTIFICATE TO BE READY ---
resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

# --- CREATES THE HTTPS LISTENER ON THE LOAD BALANCER ---
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate_validation.cert.certificate_arn

  # If someone arrives via HTTPS, send them to the Frontend
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}

# --- HTTPS ROUTING RULE FOR THE BACKEND ---
# If the HTTPS request is for /query or /docs, send it to the Backend
resource "aws_lb_listener_rule" "https_backend_rule" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  condition {
    path_pattern {
      values = ["/query", "/history/*", "/docs", "/openapi.json"]
    }
  }
}

# --- 7. POINTS THE DOMAIN TO THE LOAD BALANCER (Record A) ---
# This says: "Whoever types am-cloudnlpchatbot.site goes to the ALB address"
resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = data.aws_route53_zone.main.name
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}