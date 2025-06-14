import requests

username = "admin"
password = "admin"
server_url = "http://127.0.0.1:3080/"

# Etapa 1: obter token
auth_response = requests.post(f"{server_url}/v3/access/users/login", json={
    "username": username,
    "password": password
})

if auth_response.status_code == 200:
    token = auth_response.json().get("token")
    print("✓ Token obtido com sucesso")

    headers = {"Authorization": f"Bearer {token}"}

    # Etapa 2: fazer requisições autenticadas
    project_response = requests.get(f"{server_url}/v3/projects", headers=headers)
    print("Projetos disponíveis:", project_response.json())
else:
    print("❌ Falha na autenticação:", auth_response.json())
