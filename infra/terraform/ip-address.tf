// Attaches a static IP address to the Lightsail instance.

resource "aws_lightsail_static_ip_attachment" "hci" {
  provider       = aws.stanford-clingen-projects
  instance_name  = aws_lightsail_instance.hci.id
  static_ip_name = aws_lightsail_static_ip.hci.id
}

resource "aws_lightsail_static_ip" "hci" {
  name     = "hci-ip-${terraform.workspace}"
  provider = aws.stanford-clingen-projects
}
