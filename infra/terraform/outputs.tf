output "ecr_repo" {
  value = aws_ecr_repository.providerfinder.repository_url
}
