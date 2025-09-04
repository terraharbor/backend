resource "null_resource" "this" {
  triggers = {
    timestamp = timestamp()
  }

  provisioner "local-exec" {
    command = "echo 'Hello, World!'"
  }
}
