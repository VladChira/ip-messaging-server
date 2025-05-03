sudo docker run -d \
  --name chatapp-db \
  --restart unless-stopped \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  --env-file .env \
  postgres:15
