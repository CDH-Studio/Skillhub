resource "google_compute_address" "primary" {
    name = "${var.ip_name}"
}

resource "google_dns_managed_zone" "prod" {
    depends_on = ["google_compute_address.primary"]

    name = "${var.dns_zone_name}"
    dns_name = "${var.domain}."
    description = "Production DNS Zone"
}

resource "google_dns_record_set" "base" {
    managed_zone = "${google_dns_managed_zone.prod.name}"

    name = "${google_dns_managed_zone.prod.dns_name}"
    type = "A"
    ttl = 300
    rrdatas = ["${google_compute_address.primary.address}"]
}

resource "google_dns_record_set" "wildcard" {
    managed_zone = "${google_dns_managed_zone.prod.name}"

    name = "*.${google_dns_managed_zone.prod.dns_name}"
    type = "A"
    ttl = 300
    rrdatas = ["${google_compute_address.primary.address}"]
}
