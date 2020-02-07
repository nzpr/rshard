data "google_compute_network" "default_network" {
  name = "default"
}

resource "google_compute_firewall" "fw_public_node" {
  name = "${var.resources_name}-node-public"
  network = data.google_compute_network.default_network.self_link
  priority = 530
  target_tags = ["${var.resources_name}-node"]
  allow {
    protocol = "tcp"
    ports = [22, 40403, 18080]
  }
}

resource "google_compute_firewall" "fw_public_node_rpc" {
  name = "${var.resources_name}-node-rpc"
  network = data.google_compute_network.default_network.self_link
  priority = 540
  target_tags = ["${var.resources_name}-node"]
  allow {
    protocol = "tcp"
    ports = [40401]
  }
}

resource "google_compute_firewall" "fw_node_p2p" {
  name = "${var.resources_name}-node-p2p"
  network = data.google_compute_network.default_network.self_link
  priority = 550
  source_ranges = ["0.0.0.0/0"]
  target_tags = ["${var.resources_name}-node"]
  allow {
    protocol = "tcp"
    ports = [40400, 40404]
  }
}

resource "google_compute_firewall" "fw_node_deny" {
  name = "${var.resources_name}-node-deny"
  network = data.google_compute_network.default_network.self_link
  priority = 5010
  target_tags = ["${var.resources_name}-node"]
  deny {
    protocol = "tcp"
  }
  deny {
    protocol = "udp"
  }
}

