## Constructure App

Backend and mobile app for the Home Building Companion MVP, implemented according to `project.md`.

### Local development

- **API + Postgres**: `docker compose up --build`
  - API: `http://localhost:8000/health`
  - DB: `postgres://app:app@localhost:5432/app`

### Required environment variables

These are used in local dev, Docker, and AWS:

- **DATABASE_URL**: SQLAlchemy connection string for Postgres (e.g. `postgresql+psycopg://app:app@db:5432/app`)
- **AWS_REGION**: AWS region (e.g. `eu-west-1`)
- **S3_BUCKET**: Private S3 bucket for media uploads
- **JWT_*** / **COGNITO_***: Auth configuration (dev can start with simple JWT; prod with Cognito)
- **AI_PROVIDER_KEY**: API key for the AI provider used by `/ai/ask`

See `infra/` for Terraform-based AWS infrastructure (VPC, ECS Fargate, RDS, S3, IAM, ALB).

