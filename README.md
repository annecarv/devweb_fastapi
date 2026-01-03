# Plataforma de Comunidade com API REST - FastAPI + Auth0 + SQLite

API construída com FastAPI, SQLite e autenticação JWT via Auth0.

- **Framework:** FastAPI com estrutura modular (`routers`, `models`, `schemas`, `auth`, `database`)
- **Autenticação:** Auth0 JWT validation usando JWKS
- **Banco de Dados:** SQLite com SQLModel (SQLAlchemy)
- **RBAC:** Sistema de roles (USER/MODERATOR/ADMIN)
- **Features:** Posts, comentários, categorias, tags, likes, paginação, busca e filtros

---

## Instalação e Configuração

### Pré-requisitos

- Python 3.9+
- Conta Auth0

### Instalação

```bash
# Criar ambiente virtual
python -m venv .venv

#  ambiente virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
AUTH0_DOMAIN=seu-dominio.us.auth0.com
AUTH0_AUDIENCE=sua-api-audience
AUTH0_ALGORITHMS=RS256
```

### Executar Servidor

```bash
#  normal
uvicorn app.main:app --reload

# teste
TESTING=1 uvicorn app.main:app --reload
```

O servidor estará disponível em: **http://localhost:8000**

---

## 📚 Documentação da API

### Documentação Interativa

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## 🔐 Autenticação

### Modo Produção

Envie o token JWT do Auth0 no header:

```http
Authorization: Bearer <seu-token-jwt>
```

### Modo de Teste

Com `TESTING=1`, você pode usar tokens no formato:

```
test:user_id|ROLE1,ROLE2
```

**Exemplos:**

```http
Authorization: Bearer test:user123|USER
Authorization: Bearer test:admin456|ADMIN
Authorization: Bearer test:mod789|MODERATOR
```

### Roles Disponíveis

- **USER:** Usuário padrão (criar posts, comentários, likes)
- **MODERATOR:** Pode ocultar/deletar comentários e deletar posts de usuários
- **ADMIN:** Acesso total (gerenciar categorias, deletar qualquer conteúdo)

---

## 📖 Endpoints

### Posts

#### `POST /posts`
Criar novo post.

**Autenticação:** Requerida
**Body:**
```json
{
  "title": "Título do post",
  "content": "Conteúdo do post",
  "category": "Tecnologia",
  "tags": ["python", "fastapi"]
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Título do post",
  "content": "Conteúdo do post",
  "author_sub": "user123",
  "created_at": "2024-01-02T10:30:00",
  "category": "Tecnologia",
  "tags": ["python", "fastapi"],
  "likes": 0
}
```

---

#### `GET /posts`
Listar posts com filtros e paginação.

**Query Parameters:**
- `limit` (int, default: 10) - Quantidade de posts por página
- `offset` (int, default: 0) - Deslocamento para paginação
- `category` (string) - Filtrar por categoria
- `tag` (string) - Filtrar por tag
- `author` (string) - Filtrar por autor (user_sub)
- `order_by` (string) - Ordenação: `created_at` (padrão) ou `popular` (por likes)

**Exemplos:**
```http
GET /posts?limit=20&offset=0
GET /posts?category=Tecnologia
GET /posts?tag=python
GET /posts?author=user123
GET /posts?order_by=popular
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Título",
    "content": "Conteúdo",
    "author_sub": "user123",
    "created_at": "2024-01-02T10:30:00",
    "category": "Tecnologia",
    "tags": ["python"],
    "likes": 5
  }
]
```

---

#### `GET /posts/search`
Buscar posts por texto.

**Query Parameters:**
- `q` (string, required) - Termo de busca
- `limit` (int, default: 10)
- `offset` (int, default: 0)

**Exemplo:**
```http
GET /posts/search?q=python&limit=10
```

---

#### `PUT /posts/{post_id}`
Atualizar post.

**Autenticação:** Requerida
**Permissão:** Dono do post, MODERATOR ou ADMIN

**Body:**
```json
{
  "title": "Novo título",
  "content": "Novo conteúdo",
  "category": "Tech",
  "tags": ["python", "api"]
}
```

---

#### `DELETE /posts/{post_id}`
Deletar post.

**Autenticação:** Requerida
**Permissão:** Dono do post, MODERATOR ou ADMIN
**Nota:** Moderators não podem deletar posts de ADMIN

**Response:**
```json
{
  "detail": "deleted"
}
```

---

### Comentários

#### `GET /posts/{post_id}/comments`
Listar comentários de um post com paginação.

**Autenticação:** Não requerida

**Query Parameters:**
- `limit` (int, default: 10) - Quantidade de comentários por página
- `offset` (int, default: 0) - Deslocamento para paginação

**Exemplo:**
```http
GET /posts/1/comments?limit=20&offset=0
```

**Response:**
```json
[
  {
    "id": 1,
    "post_id": 1,
    "author_sub": "user123",
    "content": "Ótimo post!",
    "created_at": "2024-01-02T10:35:00",
    "hidden": false,
    "likes": 5
  }
]
```

---

#### `POST /posts/{post_id}/comments`
Criar comentário em um post.

**Autenticação:** Requerida
**Body:**
```json
{
  "content": "Ótimo post!"
}
```

**Response:**
```json
{
  "id": 1,
  "post_id": 1,
  "author_sub": "user123",
  "content": "Ótimo post!",
  "created_at": "2024-01-02T10:35:00",
  "hidden": false,
  "likes": 0
}
```

---

#### `PATCH /comments/{comment_id}/hide`
Ocultar comentário.

**Autenticação:** Requerida
**Permissão:** MODERATOR ou ADMIN

**Response:**
```json
{
  "detail": "hidden"
}
```

---

#### `DELETE /comments/{comment_id}`
Deletar comentário.

**Autenticação:** Requerida
**Permissão:** Dono do comentário, MODERATOR ou ADMIN
**Nota:** Moderators não podem deletar comentários de ADMIN

**Response:**
```json
{
  "detail": "deleted"
}
```

---

### Likes

#### `POST /posts/{post_id}/like`
Curtir um post.

**Autenticação:** Requerida

**Response:**
```json
{
  "likes": 5
}
```

**Nota:** Se já curtiu, retorna:
```json
{
  "detail": "Já curtido"
}
```

---

#### `POST /comments/{comment_id}/like`
Curtir um comentário.

**Autenticação:** Requerida

**Response:**
```json
{
  "likes": 3
}
```

---

### Categorias

#### `POST /categories`
Criar categoria.

**Autenticação:** Requerida
**Permissão:** ADMIN

**Query Parameters:**
- `name` (string, required) - Nome da categoria

**Exemplo:**
```http
POST /categories?name=Tecnologia
```

**Response:**
```json
{
  "id": 1,
  "name": "Tecnologia"
}
```

---

#### `GET /categories`
Listar todas as categorias.

**Autenticação:** Não requerida

**Response:**
```json
[
  {
    "id": 1,
    "name": "Tecnologia"
  },
  {
    "id": 2,
    "name": "Esportes"
  }
]
```

---

#### `PUT /categories/{category_id}`
Atualizar categoria.

**Autenticação:** Requerida
**Permissão:** ADMIN

**Query Parameters:**
- `name` (string, required) - Novo nome da categoria

**Exemplo:**
```http
PUT /categories/1?name=Tech & Inovação
```

---

#### `DELETE /categories/{category_id}`
Deletar categoria.

**Autenticação:** Requerida
**Permissão:** ADMIN

**Response:**
```json
{
  "detail": "deleted"
}
```

---

## Testando a API

### Usando Swagger UI

1. Acesse http://localhost:8000/docs
2. Clique em "Authorize" no topo
3. No modo de teste, use: `test:user123|USER`
4. Clique em qualquer endpoint e "Try it out"
5. Preencha os parâmetros e execute

### Usando cURL

**Criar post:**
```bash
curl -X POST http://localhost:8000/posts \
  -H "Authorization: Bearer test:user123|USER" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Meu primeiro post",
    "content": "Conteúdo do post",
    "category": "Tecnologia",
    "tags": ["python", "fastapi"]
  }'
```

**Listar posts:**
```bash
curl http://localhost:8000/posts
```

**Listar comentários de um post:**
```bash
curl http://localhost:8000/posts/1/comments?limit=10&offset=0
```

**Criar comentário:**
```bash
curl -X POST http://localhost:8000/posts/1/comments \
  -H "Authorization: Bearer test:user456|USER" \
  -H "Content-Type: application/json" \
  -d '{"content": "Ótimo post!"}'
```

**Curtir post:**
```bash
curl -X POST http://localhost:8000/posts/1/like \
  -H "Authorization: Bearer test:user789|USER"
```

### Usando Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"
headers = {"Authorization": "Bearer test:user123|USER"}

response = requests.post(
    f"{BASE_URL}/posts",
    headers=headers,
    json={
        "title": "Título",
        "content": "Conteúdo",
        "category": "Tech",
        "tags": ["python"]
    }
)
print(response.json())

response = requests.get(f"{BASE_URL}/posts")
print(response.json())
```

---

## Estrutura do Projeto

```
backend_ex3/
├── app/
│   ├── __init__.py
│   ├── main.py           # Aplicação FastAPI principal
│   ├── auth.py           # Autenticação Auth0 e RBAC
│   ├── database.py       # Configuração SQLModel/SQLite
│   ├── models.py         # Modelos do banco de dados
│   ├── schemas.py        # Schemas Pydantic
│   └── routers/
│       ├── __init__.py
│       ├── posts.py      # Endpoints de posts
│       ├── comments.py   # Endpoints de comentários
│       ├── likes.py      # Endpoints de likes
│       └── categories.py # Endpoints de categorias
├── .env                  # Variáveis de ambiente
├── requirements.txt      # Dependências
└── README.md            # Esta documentação
```

---

## Permissões

### Posts
- **Criar:** Qualquer usuário autenticado
- **Editar:** Dono, MODERATOR ou ADMIN
- **Deletar:** Dono, MODERATOR ou ADMIN
  - Moderators **não podem** deletar posts de ADMIN

### Comentários
- **Criar:** Qualquer usuário autenticado
- **Listar:** Público (sem autenticação), com paginação
- **Ocultar:** MODERATOR ou ADMIN
- **Deletar:** Dono, MODERATOR ou ADMIN
  - Moderators **não podem** deletar comentários de ADMIN

### Likes
- **Curtir:** Qualquer usuário autenticado
- **Limitação:** Um like por usuário por post/comentário

### Categorias
- **Criar/Editar/Deletar:** Apenas ADMIN
- **Listar:** Público (sem autenticação)

---

## Modelos de Dados

### Post
```python
{
  "id": int,
  "title": str,
  "content": str,
  "author_sub": str,
  "author_role": str | None,
  "created_at": datetime,
  "category_id": int | None,
  "tags": List[Tag],
  "comments": List[Comment],
  "likes": List[PostLike]
}
```

### Comment
```python
{
  "id": int,
  "post_id": int,
  "author_sub": str,
  "content": str,
  "created_at": datetime,
  "hidden": bool,
  "likes": List[CommentLike]
}
```

### Category
```python
{
  "id": int,
  "name": str,
  "posts": List[Post]
}
```

### Tag
```python
{
  "id": int,
  "name": str,
  "posts": List[Post]
}
```

---

## Desenvolvimento

### Adicionar Novos Endpoints

1. Crie/edite um router em `app/routers/`
2. Importe e registre no `app/main.py`:
   ```python
   from app.routers import seu_router
   app.include_router(seu_router.router)
   ```

### Adicionar Novos Modelos

1. Defina o modelo em `app/models.py` usando SQLModel
2. Crie schemas correspondentes em `app/schemas.py`
3. O banco será criado automaticamente no startup

---

## Avisos

- O modo de teste (`TESTING=1`) **não deve** ser usado em produção
- Tags e categorias são criadas automaticamente ao criar/editar posts
- O banco de dados SQLite é criado automaticamente em `database.db`
- Todos os timestamps estão em UTC

---

## Dependências 

- **FastAPI** - Framework web
- **SQLModel** - ORM com Pydantic
- **Uvicorn** - ASGI server
- **python-jose** - JWT handling
- **httpx** - Cliente HTTP (para JWKS)

---

## 🤝 

---
