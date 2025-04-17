sudo docker run -d \
  --name chatapp-db \
  --restart unless-stopped \
  -e POSTGRES_USER="${POSTGRES_USER}" \
  -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  -e POSTGRES_DB="${POSTGRES_DB}" \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15
