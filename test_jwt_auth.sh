#!/bin/bash

# Setăm URL-ul de bază
BASE_URL="http://localhost:5000"

# Culori pentru output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funcție pentru separare vizuală
separator() {
  echo -e "\n${BLUE}========================================${NC}\n"
}

# Testăm dacă serverul funcționează
echo -e "${BLUE}Testăm conexiunea la server...${NC}"
RESPONSE=$(curl -s "${BASE_URL}/messaging-api")
echo "Răspuns: $RESPONSE"

separator

# 1. Înregistrarea unui utilizator nou
echo -e "${BLUE}Înregistrarea unui utilizator nou:${NC}"
REGISTER_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/messaging-api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword"
  }')
echo "Răspuns la înregistrare: $REGISTER_RESPONSE"

separator

# 2. Login cu utilizatorul nou creat
echo -e "${BLUE}Autentificarea cu utilizatorul nou:${NC}"
LOGIN_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/messaging-api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword"
  }')
echo "Răspuns la autentificare: $LOGIN_RESPONSE"

# Extragem token-ul din răspuns (necesită jq)
if command -v jq &> /dev/null; then
  TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.token')
  echo -e "${GREEN}Token extras: ${TOKEN:0:20}...${NC}"
else
  echo -e "${RED}jq nu este instalat. Te rugăm să extragi manual token-ul din răspunsul de mai sus.${NC}"
  echo "Introduceți token-ul manual:"
  read TOKEN
fi

separator

# 3. Testăm o rută protejată (lista utilizatorilor)
echo -e "${BLUE}Testarea unei rute protejate (lista utilizatorilor):${NC}"
PROTECTED_RESPONSE=$(curl -s -X GET \
  "${BASE_URL}/messaging-api/users" \
  -H "Authorization: Bearer $TOKEN")
echo "Răspuns la ruta protejată: $PROTECTED_RESPONSE"

separator

# 4. Testăm ruta /me pentru a obține informații despre utilizatorul autentificat
echo -e "${BLUE}Testarea rutei /me pentru informații despre utilizatorul autentificat:${NC}"
ME_RESPONSE=$(curl -s -X GET \
  "${BASE_URL}/messaging-api/me" \
  -H "Authorization: Bearer $TOKEN")
echo "Răspuns la ruta /me: $ME_RESPONSE"

separator

# 5. Testăm accesul fără token (ar trebui să primim eroare)
echo -e "${BLUE}Testarea accesului fără token (ar trebui să primim eroare):${NC}"
UNAUTHORIZED_RESPONSE=$(curl -s -X GET \
  "${BASE_URL}/messaging-api/users")
echo "Răspuns fără token: $UNAUTHORIZED_RESPONSE"

echo -e "\n${GREEN}Testarea completă! Verificați răspunsurile de mai sus.${NC}"