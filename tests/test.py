#!/usr/bin/env python3

import os
import requests
import json

os.environ["TESTING"] = "1"

BASE_URL = "http://localhost:8000"

ADMIN_TOKEN = "test:admin123|ADMIN"
MODERATOR_TOKEN = "test:mod456|MODERATOR"
USER_TOKEN = "test:user789|USER"
USER2_TOKEN = "test:user999|USER"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_result(method, endpoint, status, response):
    print(f"\n{method} {endpoint}")
    print(f"Status: {status}")
    print(f"Resposta: {json.dumps(response, indent=2, default=str)}")

print_section("TESTANDO CATEGORIAS (APENAS ADMIN)")

headers_admin = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
headers_mod = {"Authorization": f"Bearer {MODERATOR_TOKEN}"}
headers_user = {"Authorization": f"Bearer {USER_TOKEN}"}

resp = requests.post(f"{BASE_URL}/categories", params={"name": "Technology"}, headers=headers_admin)
print_result("POST", "/categories", resp.status_code, resp.json())

resp = requests.post(f"{BASE_URL}/categories", params={"name": "Sports"}, headers=headers_admin)
print_result("POST", "/categories", resp.status_code, resp.json())

resp = requests.get(f"{BASE_URL}/categories")
print_result("GET", "/categories", resp.status_code, resp.json())

resp = requests.put(f"{BASE_URL}/categories/1", params={"name": "Tech & Innovation"}, headers=headers_admin)
print_result("PUT", "/categories/1", resp.status_code, resp.json())

print_section("TESTANDO POSTS")

dados_post = {
    "title": "primeiro post",
    "content": "Este é um post sobre tecnologia",
    "category": "Tech & Innovation",
    "tags": ["python", "fastapi"]
}
resp = requests.post(f"{BASE_URL}/posts", json=dados_post, headers=headers_user)
print_result("POST", "/posts", resp.status_code, resp.json())

dados_post2 = {
    "title": "Segundo post",
    "content": "Outro post sobre a hello kitty",
    "category": "Sports",
    "tags": ["futebol", "soccer"]
}
resp = requests.post(f"{BASE_URL}/posts", json=dados_post2, headers=headers_user)
print_result("POST", "/posts", resp.status_code, resp.json())

dados_post3 = {
    "title": "Post do usuário 2",
    "content": "Post sobre comidas",
    "category": "Sports",
    "tags": ["tenis"]
}
headers_user2 = {"Authorization": f"Bearer {USER2_TOKEN}"}
resp = requests.post(f"{BASE_URL}/posts", json=dados_post3, headers=headers_user2)
print_result("POST", "/posts", resp.status_code, resp.json())

resp = requests.get(f"{BASE_URL}/posts")
print_result("GET", "/posts", resp.status_code, resp.json())

resp = requests.get(f"{BASE_URL}/posts", params={"category": "Sports"})
print_result("GET", "/posts?category=Sports", resp.status_code, resp.json())

resp = requests.get(f"{BASE_URL}/posts", params={"tag": "python"})
print_result("GET", "/posts?tag=python", resp.status_code, resp.json())

resp = requests.get(f"{BASE_URL}/posts", params={"author": "user789"})
print_result("GET", "/posts?author=user789", resp.status_code, resp.json())

resp = requests.get(f"{BASE_URL}/posts/search", params={"q": "technology"})
print_result("GET", "/posts/search?q=technology", resp.status_code, resp.json())

update_data = {
    "title": "Updated title",
    "content": "Updated content",
    "category": "Tech & Innovation",
    "tags": ["python", "fastapi", "sqlmodel"]
}
resp = requests.put(f"{BASE_URL}/posts/1", json=update_data, headers=headers_user)
print_result("PUT", "/posts/1", resp.status_code, resp.json())

print_section("TESTANDO COMENTÁRIOS")

comment_data = {"content": "Ótimo post!"}
resp = requests.post(f"{BASE_URL}/posts/1/comments", json=comment_data, headers=headers_user2)
print_result("POST", "/posts/1/comments", resp.status_code, resp.json())

comment_data2 = {"content": "Aceito!"}
resp = requests.post(f"{BASE_URL}/posts/1/comments", json=comment_data2, headers=headers_user)
print_result("POST", "/posts/1/comments", resp.status_code, resp.json())

resp = requests.patch(f"{BASE_URL}/comments/1/hide", headers=headers_mod)
print_result("PATCH", "/comments/1/hide", resp.status_code, resp.json())

resp = requests.patch(f"{BASE_URL}/comments/2/hide", headers=headers_user)
print_result("PATCH", "/comments/2/hide (deve falhar)", resp.status_code, resp.json())

print_section("TESTANDO CURTIDAS")

resp = requests.post(f"{BASE_URL}/posts/1/like", headers=headers_user)
print_result("POST", "/posts/1/like", resp.status_code, resp.json())

resp = requests.post(f"{BASE_URL}/posts/1/like", headers=headers_user2)
print_result("POST", "/posts/1/like", resp.status_code, resp.json())

resp = requests.post(f"{BASE_URL}/posts/1/like", headers=headers_user)
print_result("POST", "/posts/1/like (duplicado)", resp.status_code, resp.json())

resp = requests.post(f"{BASE_URL}/comments/1/like", headers=headers_user)
print_result("POST", "/comments/1/like", resp.status_code, resp.json())

resp = requests.post(f"{BASE_URL}/comments/1/like", headers=headers_user2)
print_result("POST", "/comments/1/like", resp.status_code, resp.json())

print_section("TESTANDO ORDENAÇÃO DE POSTS")

resp = requests.get(f"{BASE_URL}/posts", params={"order_by": "popular"})
print_result("GET", "/posts?order_by=popular", resp.status_code, resp.json())

print_section("TESTANDO PERMISSÕES")

resp = requests.delete(f"{BASE_URL}/posts/3", headers=headers_user)
print_result("DELETE", "/posts/3 (deve falhar)", resp.status_code, resp.json())

resp = requests.delete(f"{BASE_URL}/posts/3", headers=headers_mod)
print_result("DELETE", "/posts/3 (moderador)", resp.status_code, resp.json())

resp = requests.delete(f"{BASE_URL}/comments/2", headers=headers_user)
print_result("DELETE", "/comments/2 (dono)", resp.status_code, resp.json())

resp = requests.delete(f"{BASE_URL}/categories/2", headers=headers_admin)
print_result("DELETE", "/categories/2 (admin)", resp.status_code, resp.json())

resp = requests.post(f"{BASE_URL}/categories", params={"name": "Music"}, headers=headers_user)
print_result("POST", "/categories (deve falhar)", resp.status_code, resp.json())

print_section("TESTES CONCLUÍDOS")
