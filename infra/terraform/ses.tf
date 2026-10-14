// Lets the server send email through Amazon SES, from addresses on its own
// subdomain (hci.clinicalgenome.org or hci-test.clinicalgenome.org).

locals {
  email_domain = "${terraform.workspace == "prod" ? "hci" : "hci-test"}.clinicalgenome.org"
}

resource "aws_sesv2_email_identity" "hci" {
  provider       = aws.stanford-clingen-projects
  email_identity = local.email_domain
}

// Easy DKIM gives three tokens. Each needs a CNAME record in our DNS zone, which
// lives in the Route 53 account, before SES will verify the domain.
resource "aws_route53_record" "ses_dkim" {
  count    = 3
  provider = aws.route-53
  zone_id  = data.aws_route53_zone.hci.id
  name     = "${aws_sesv2_email_identity.hci.dkim_signing_attributes[0].tokens[count.index]}._domainkey.${local.email_domain}"
  type     = "CNAME"
  ttl      = 600
  records  = ["${aws_sesv2_email_identity.hci.dkim_signing_attributes[0].tokens[count.index]}.dkim.amazonses.com"]
}

//==============================================================================
// Configure the sender.
// -----------------------------------------------------------------------------
// The server sends email over SMTP as this user. While SES is in the sandbox,
// it checks the policy against each recipient's identity too, so the policy
// allows every identity but only from addresses on the server's subdomain.
//==============================================================================

resource "aws_iam_user" "email_sender" {
  provider = aws.stanford-clingen-projects
  name     = "hci-ses-${terraform.workspace}"
}

resource "aws_iam_user_policy" "email_sender" {
  provider = aws.stanford-clingen-projects
  name     = "hci-ses-${terraform.workspace}"
  user     = aws_iam_user.email_sender.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ses:SendRawEmail"]
        Resource = "arn:aws:ses:us-west-2:${data.aws_caller_identity.current.account_id}:identity/*"
        Condition = {
          StringLike = {
            "ses:FromAddress" = "*@${local.email_domain}"
          }
        }
      },
    ]
  })
}

resource "aws_iam_access_key" "email_sender" {
  provider = aws.stanford-clingen-projects
  user     = aws_iam_user.email_sender.name
}

// The SMTP username is the access key ID. The SMTP password is derived from the
// secret key for us-west-2. Read it with:
// terraform output -raw email_smtp_password
output "email_smtp_username" {
  value = aws_iam_access_key.email_sender.id
}

output "email_smtp_password" {
  value     = aws_iam_access_key.email_sender.ses_smtp_password_v4
  sensitive = true
}
