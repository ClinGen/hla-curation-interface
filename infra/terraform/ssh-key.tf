// Adds our SSH key for Ansible.

resource "aws_lightsail_key_pair" "hci" {
  name       = "ansible-key"
  public_key = file("~/.ssh/ansible_ed25519.pub")
}