resource "aws_s3_bucket" "media" {
  bucket = "${var.project_name}-${var.environment}-media"

  tags = {
    Name        = "${var.project_name}-${var.environment}-media"
    Environment = var.environment
  }
}

output "bucket_name" {
  value = aws_s3_bucket.media.bucket
}

