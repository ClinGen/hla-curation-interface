// Manages subdomains for the HCI.

data "aws_route53_zone" "hci" {
  provider     = aws.route-53
  name         = "clinicalgenome.org"
  private_zone = false
}

resource "aws_route53_record" "hci" {
  provider = aws.route-53
  zone_id  = data.aws_route53_zone.hci.id
  name     = "${terraform.workspace == "prod" ? "hci" : "hci-test"}.clinicalgenome.org"
  type     = "A"
  ttl      = 300

  records = [
    aws_lightsail_static_ip.hci.ip_address
  ]
}
