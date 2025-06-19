// Adds our SSH key for Ansible.

resource "aws_lightsail_key_pair" "hci" {
  name       = "ansible-key-${terraform.workspace}"
  public_key = file("~/.ssh/hci_ansible_${terraform.workspace}_ed25519.pub")
}