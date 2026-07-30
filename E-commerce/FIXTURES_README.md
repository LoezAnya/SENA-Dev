# Datos de prueba (fixtures) — Sprint 1 + Sprint 2

## ⚠️ Si el login con los fixtures JSON no te funcionó

Los hashes de contraseña en `02_users.json` los calculé a mano en este
sandbox (sin Django instalado para generarlos de forma nativa). Si el
login te dio 401, usa en su lugar el **comando de seeding** de abajo —
crea los mismos usuarios pero hasheando la contraseña con tu propia
instalación de Django (`set_password()`), así que es infalible.

## Opción recomendada: comando de management (usa el ORM real)

```bash
python manage.py seed_demo_data
```

Esto crea exactamente los mismos datos que los fixtures JSON de abajo
(mismas categorías, usuarios, sellers, productos, variantes), pero
usando `User.objects.get_or_create()` + `set_password()` — el mismo
mecanismo que usa `/api/v1/auth/register/` — así que la contraseña
**va a funcionar sí o sí** con tu versión de Django/hashers instalados.

Es idempotente: puedes correrlo varias veces sin duplicar datos. Si
quieres empezar de cero:

```bash
python manage.py seed_demo_data --flush
```

Las credenciales resultantes son las mismas que las de la tabla más
abajo (usuario / `StrongPass123!`).

---

## Opción alternativa: fixtures JSON (`loaddata`)

```
fixtures/
├── 01_categories.json        # 7 categorías (5 raíz + 2 subcategorías)
├── 02_users.json              # 6 usuarios: 2 buyers, 3 sellers (3P/FBP/OEM), 1 admin
├── 03_seller_profiles.json    # SellerProfile de cada seller
├── 04_products.json           # 10 productos (1 inactivo, a propósito, para probar filtros)
├── 05_variants.json           # 7 variantes (color/talla) sobre 3 productos
└── api_examples/              # Bodies de ejemplo para cada endpoint (no son fixtures de Django)
    ├── register_buyer.json
    ├── register_seller.json
    ├── login.json
    ├── update_me.json
    ├── create_product.json
    ├── update_product.json
    └── create_variant.json
```

## 1. Cargar los datos

Con las migraciones ya aplicadas (`python manage.py migrate`):

```bash
python manage.py loaddata \
  fixtures/01_categories.json \
  fixtures/02_users.json \
  fixtures/03_seller_profiles.json \
  fixtures/04_products.json \
  fixtures/05_variants.json
```

> El orden no es estrictamente necesario — `loaddata` desactiva las
> validaciones de foreign key mientras carga y las reactiva al final —
> pero mantenerlo así hace más fácil leer qué depende de qué.

Si algo falla a mitad de carga (por ejemplo corriste el comando dos
veces), puedes limpiar y reintentar:

```bash
python manage.py flush          # borra TODOS los datos de la BD (pide confirmación)
python manage.py loaddata fixtures/0*.json
```

## 2. Credenciales de las cuentas semilla

**Todas las cuentas usan la misma contraseña:** `StrongPass123!`

| username       | rol    | seller_type | notas                                  |
|----------------|--------|-------------|------------------------------------------|
| `buyer1`       | buyer  | —           | comprador de prueba                      |
| `buyer2`       | buyer  | —           | comprador de prueba                      |
| `seller_3p`    | seller | 3P          | Style Boutique — verificado               |
| `seller_fbp`   | seller | FBP         | Fast Fashion Fulfilled — verificado       |
| `seller_oem`   | seller | OEM         | Global Manufacturing Co — **sin verificar** |
| `admin_demo`   | admin  | —           | `is_staff=True`, `is_superuser=True` — entra a `/admin/` |

Los hashes de contraseña en el fixture son `pbkdf2_sha256` reales
(generados con el mismo algoritmo que usa Django), así que el login
funciona tal cual, sin pasos adicionales.

## 3. Datos que trae el seed

- **7 categorías**: Tops, Bottoms, Dresses, Shoes, Accessories, y dos
  subcategorías (T-Shirts bajo Tops, Jeans bajo Bottoms) para probar
  la relación `parent`.
- **10 productos** repartidos entre los 3 sellers y las 7 categorías,
  con precios entre $9.99 y $45.00 — a propósito variados para poder
  probar `min_price`/`max_price`. Incluye imágenes de ejemplo
  (`picsum.photos`, tamaño 1340x1785 para simular el canvas del
  Sprint 2) y **dos productos sin imágenes** para ver ese caso también.
- **1 producto inactivo** (`Chaqueta Denim Oversize`, `is_active=false`)
  para verificar que el catálogo público lo excluye.
- **7 variantes** (color/talla) sobre 3 productos, incluyendo una con
  `price_override` distinto al `base_price` del producto padre.

## 4. Recorrido por cada endpoint (curl)

Los archivos en `api_examples/` se pueden pasar directo con `-d @archivo.json`.

### Auth

```bash
# Registro (usa los JSON de ejemplo — no colisionan con las cuentas semilla)
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d @fixtures/api_examples/register_buyer.json

curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d @fixtures/api_examples/register_seller.json

# Login con una cuenta semilla
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d @fixtures/api_examples/login.json
# -> guarda el "access" token de la respuesta en $TOKEN

export TOKEN="pega_aqui_el_access_token"

# Perfil propio
curl http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer $TOKEN"

curl -X PATCH http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d @fixtures/api_examples/update_me.json

# Refresh token
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "pega_aqui_el_refresh_token"}'
```

### Catálogo público (sin auth)

```bash
curl "http://localhost:8000/api/v1/products/"
curl "http://localhost:8000/api/v1/products/?category=jeans"
curl "http://localhost:8000/api/v1/products/?category=4"           # por id (Shoes)
curl "http://localhost:8000/api/v1/products/?min_price=10&max_price=30"
curl "http://localhost:8000/api/v1/products/?search=vestido"
curl "http://localhost:8000/api/v1/products/?ordering=-base_price"
curl "http://localhost:8000/api/v1/products/?page=1"
curl "http://localhost:8000/api/v1/products/1/"                     # detalle
```

### CRUD de seller (usa el token de `seller_3p`, login arriba)

```bash
curl http://localhost:8000/api/v1/products/mine/ \
  -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:8000/api/v1/products/mine/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d @fixtures/api_examples/create_product.json

curl -X PATCH http://localhost:8000/api/v1/products/mine/1/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d @fixtures/api_examples/update_product.json

curl -X DELETE http://localhost:8000/api/v1/products/mine/5/ \
  -H "Authorization: Bearer $TOKEN"

# Variantes
curl http://localhost:8000/api/v1/products/mine/variants/ \
  -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:8000/api/v1/products/mine/variants/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d @fixtures/api_examples/create_variant.json

# Subida de imagen (multipart, no JSON) — usa cualquier .jpg/.png local
curl -X POST http://localhost:8000/api/v1/products/mine/1/images/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@/ruta/a/tu/foto.jpg"
```

### Probar el aislamiento por seller (ownership)

```bash
# Login como seller_fbp y trata de tocar un producto de seller_3p (pk=1) -> 404
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "seller_fbp", "password": "StrongPass123!"}'

export TOKEN_FBP="pega_aqui_el_access_token"

curl http://localhost:8000/api/v1/products/mine/1/ \
  -H "Authorization: Bearer $TOKEN_FBP"
# -> 404 Not Found (el producto 1 es de seller_3p, no de seller_fbp)
```

### Admin de Django

Entra a `http://localhost:8000/admin/` con `admin_demo` / `StrongPass123!`
para ver/editar todo (usuarios, seller profiles, categorías, productos,
variantes) desde la UI.
