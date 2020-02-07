resource "google_compute_address" "node_ext_addr" {
  count = var.node_count
  name = "${var.resources_name}-node${count.index}"
  address_type = "EXTERNAL"
}

resource "google_dns_record_set" "node_dns_record" {
  count = var.node_count
  name = "node${count.index}${var.dns_suffix}."
  managed_zone = "rchain-dev"
  type = "A"
  ttl = 3600
  rrdatas = [google_compute_address.node_ext_addr[count.index].address]
}

resource "google_compute_instance" "node_host" {
  count = var.node_count
  name = "${var.resources_name}-node${count.index}"
  hostname = "node${count.index}${var.dns_suffix}"
  machine_type = "e2-standard-8"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-1804-lts"
      size = 500
      type = "pd-standard"
    }
  }

  tags = [
    "${var.resources_name}-node",
    "collectd-out",
    "elasticsearch-out",
    "logstash-tcp-out",
    "logspout-http",
  ]

  service_account {
    email = google_service_account.svc_account_node.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  network_interface {
    network = data.google_compute_network.default_network.self_link
    access_config {
      nat_ip = google_compute_address.node_ext_addr[count.index].address
      //public_ptr_domain_name = "node${count.index}${var.dns_suffix}."
    }
  }

  depends_on = [google_dns_record_set.node_dns_record]

  connection {
    type = "ssh"
    host = self.network_interface[0].access_config[0].nat_ip
    user = "root"
    private_key = file("~/.ssh/google_compute_engine")
  }

  provisioner "file" {
    source = var.rshard-secret-key
    destination = "/root/rshard-secret.key"
  }

  provisioner "remote-exec" {
    script = "../bootstrap"
  }
}

