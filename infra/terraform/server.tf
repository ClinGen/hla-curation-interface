// Configures the server we use for the HCI.

resource "aws_lightsail_instance" "hci" {
  name              = "hci-lightsail-${terraform.workspace}"
  provider          = aws.stanford-clingen-projects
  availability_zone = "us-west-2a"
  blueprint_id      = "ubuntu_24_04"
  bundle_id         = terraform.workspace == "prod" ? "medium_3_0" : "small_3_0"

  // Lightsail takes a snapshot of the whole instance every day and keeps the last
  // 7. The time is in UTC: 10 or 11 PM Pacific, before the midnight Pacific
  // database backup.
  add_on {
    type          = "AutoSnapshot"
    snapshot_time = "06:00"
    status        = "Enabled"
  }
}

resource "aws_lightsail_instance_public_ports" "hci" {
  provider      = aws.stanford-clingen-projects
  instance_name = aws_lightsail_instance.hci.name

  port_info {
    protocol  = "tcp"
    from_port = 22
    to_port   = 22
  }

  port_info {
    protocol  = "tcp"
    from_port = 80
    to_port   = 80
  }

  port_info {
    protocol  = "tcp"
    from_port = 443
    to_port   = 443
  }
}
