resource "google_service_account" "svc_account_node" {
  account_id = "${var.resources_name}-node"
}

resource "google_storage_bucket_iam_member" "member" {
  bucket = "heapdumps.bucket.rchain-dev.tk"
  role = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.svc_account_node.email}"
}

