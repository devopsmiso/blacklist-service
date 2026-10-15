# Blacklist Service — Entrega 1

Microservicio para gestionar la **lista negra global de emails** de la organización.
Proyecto del curso **DevOps** — Universidad de los Andes.

## Equipo

| Apellidos           | Nombres        | Email Uniandes               | Usuario GitHub |
|---------------------|----------------|------------------------------|----------------|
| Arango Chavarria    | Wendy Maria    | w.arangoc@uniandes.edu.co    | warango4       |
| Echeverry Bohorquez | Andres Felipe  | a.echeverryb@uniandes.edu.co | afecheverryb10 |
| Vega Guarin         | Juan Sebastian | js.vega1@uniandes.edu.co     | jsebasvegag    |
| Urian Villamil      | Julio Cesar    | j.urianv@uniandes.edu.co     | jurianvilla    |

## Entregables de la Entrega 1

| Entregable | Dónde |
|---|---|
| Código fuente | Este repositorio |
| Aplicación desplegada en AWS Elastic Beanstalk | URL del ambiente (en el documento de la entrega) |
| Documentación del API publicada en Postman | Se publica desde el workspace del equipo (ver [Postman](#postman)) |
| Documento "Proyecto 1 entrega 1 – Documento.pdf" | Coursera |
| Video de sustentación (máximo 10 minutos) | Enlace (YouTube, Vimeo o cuenta de la universidad) en Coursera |

## Stack tecnológico

| Tecnología          | Versión | Uso |
|---------------------|---------|-----|
| Python              | 3.11    | Lenguaje (el enunciado exige 3.8+) |
| Flask               | 1.1.4   | Framework web (exigido: 1.1.x) |
| Flask-SQLAlchemy    | 2.5.1   | ORM |
| Flask-RESTful       | 0.3.10  | Recursos REST |
| Flask-Marshmallow   | 0.15.0  | Validación y serialización |
| Flask-JWT-Extended  | 4.3.1   | Bearer Token (JWT) |
| Werkzeug            | 1.0.1   | WSGI y `ProxyFix` para la IP real del cliente |
| PostgreSQL          | 16      | Base de datos (AWS RDS en la nube) |
| psycopg2-binary     | 2.9.10  | Driver de PostgreSQL para SQLAlchemy |
| gunicorn            | 23.0.0  | Servidor WSGI que usa AWS Beanstalk para Python |

> **¿Por qué Python 3.11?** Las pruebas pasan en Python 3.8 a 3.13, pero desde
> 3.12 Werkzeug 1.0.1 (la versión que exige Flask 1.1.x) usa APIs de Python
> obsoletas que se eliminan en 3.14. Python 3.11 ejecuta el stack sin
> advertencias y está disponible en AWS Beanstalk como plataforma
> **Python 3.11 running on 64bit Amazon Linux 2023**.
> Las dependencias transitivas (Jinja2, MarkupSafe, itsdangerous, click) están
> fijadas porque sus versiones recientes rompen Flask 1.1.x.

## Arquitectura

Se aplica **Clean Architecture**: las dependencias apuntan hacia el dominio,
que no conoce Flask ni la base de datos. Los diagramas de despliegue en AWS,
capas, flujo del POST y modelo de datos están en
[`docs/arquitectura.md`](docs/arquitectura.md) (imágenes en `docs/img/`).

```
api  ──►  use_cases  ──►  domain  ◄──  infrastructure
(HTTP)    (reglas de la     (entidades,    (SQLAlchemy +
           aplicación)       contratos)     PostgreSQL)
```

```
blacklist-service/
├── application.py              # Punto de entrada WSGI (Beanstalk busca `application`)
├── blacklist/
│   ├── __init__.py             # create_app: raíz de composición (inyección de dependencias)
│   ├── config.py               # Configuración desde variables de entorno
│   ├── extensions.py           # Instancias de db, ma y jwt
│   ├── logging_config.py       # Formato de logs
│   ├── version.py              # Versión del microservicio (se expone en /health)
│   ├── domain/                 # Entidad, excepciones y contrato del repositorio
│   ├── use_cases/              # Agregar email / consultar estado
│   ├── infrastructure/         # Modelo ORM, repositorio SQLAlchemy, creación del esquema
│   └── api/                    # Recursos REST, esquemas, rutas, auth, errores, logs, CLI
├── tests/
│   ├── unit/                   # Dominio, casos de uso y configuración (sin BD)
│   └── integration/            # API, repositorio, autenticación, arranque y comandos
├── docs/                       # Arquitectura y diagramas
├── postman/                    # Colección de Postman con los escenarios de prueba
├── CHANGELOG.md                # Historial de versiones
├── Dockerfile                  # Imagen que construye Beanstalk (plataforma Docker)
├── docker-compose.yml
├── Procfile                    # Arranque en Beanstalk plataforma Python (en Docker se usa el CMD del Dockerfile)
├── requirements.txt            # Dependencias de ejecución
├── requirements-dev.txt        # + pytest y cobertura
├── setup.cfg                   # Configuración de pytest y cobertura
├── .env.example                # Plantilla de variables de entorno
└── .ebextensions/              # Configuración de Beanstalk (health check) incluida en el zip
```

**Principios SOLID aplicados**

- **S** — Cada clase tiene una responsabilidad: los recursos traducen HTTP, los casos de uso aplican reglas, el repositorio persiste.
- **O** — Se puede cambiar la persistencia agregando otra implementación de `BlacklistRepository` sin modificar los casos de uso.
- **L** — Cualquier implementación del repositorio (SQLAlchemy o el doble de pruebas en memoria) es intercambiable.
- **I** — El contrato del repositorio solo expone las dos operaciones que se necesitan.
- **D** — Los casos de uso dependen de la abstracción `BlacklistRepository`; `create_app` inyecta la implementación concreta.

## API REST

Ambos endpoints de negocio requieren `Authorization: Bearer <token>`.

### `POST /blacklists` — Agregar un email a la lista negra

| Campo            | Tipo   | Obligatorio | Regla |
|------------------|--------|-------------|-------|
| `email`          | String | Sí          | Email válido, máximo 255 caracteres |
| `app_uuid`       | String | Sí          | UUID válido |
| `blocked_reason` | String | No          | Máximo 255 caracteres |

El servicio guarda internamente la **IP de origen** y la **fecha/hora** de la solicitud.

```json
// Request
{
  "email": "cliente@example.com",
  "app_uuid": "9f1c3a52-7d4b-4c1e-9a3f-2b8e6d0c1a77",
  "blocked_reason": "Solicitud del cliente"
}

// 201 Created
{
  "message": "El email fue agregado a la lista negra global.",
  "id": 1,
  "email": "cliente@example.com",
  "created_at": "2026-10-13T23:47:11.734808+00:00"
}
```

| Código | Caso |
|--------|------|
| 201 | Email agregado |
| 400 | Datos inválidos (`errors` indica el detalle por campo) |
| 401 | Token ausente o inválido |
| 409 | El email ya está en la lista negra |

### `GET /blacklists/<email>` — Consultar si un email está en la lista negra

```json
// 200 OK — está en la lista negra
{ "email": "cliente@example.com", "is_blacklisted": true, "blocked_reason": "Solicitud del cliente" }

// 200 OK — no está en la lista negra
{ "email": "otro@example.com", "is_blacklisted": false, "blocked_reason": null }
```

| Código | Caso |
|--------|------|
| 200 | Consulta realizada (el email puede estar o no en la lista negra) |
| 401 | Token ausente o inválido |

### Reglas de negocio (confirmadas por el tutor)

- Un email está o no está en la lista negra: un email repetido se rechaza con **409**.
- Los emails no distinguen mayúsculas: `Juan@Mail.com` y `juan@mail.com` son el mismo.
  Se guardan y consultan en minúsculas.
- Datos inválidos (email inválido o > 255, `app_uuid` o `blocked_reason` > 255) responden **400**.
- El token es un JWT generado con Flask-JWT-Extended, que la librería valida en cada solicitud.

### `GET /health` — Health check

No requiere token. Responde `{"status": "ok", "version": "1.0.0"}` y es la ruta que
se configura en los health checks del balanceador de AWS Beanstalk. No consulta la
base de datos a propósito: una falla momentánea de RDS no debe hacer que Beanstalk
reemplace todas las instancias.

## Variables de entorno

| Variable          | Ejemplo            | Descripción |
|-------------------|--------------------|-------------|
| `DB_USER`         | `postgres`         | Usuario de PostgreSQL |
| `DB_PASSWORD`     | `postgres`         | Contraseña de PostgreSQL |
| `DB_HOST`         | `localhost`        | Host (en AWS: endpoint de RDS) |
| `DB_PORT`         | `5432`             | Puerto (opcional, 5432 por defecto) |
| `DB_NAME`         | `blacklist`        | Nombre de la base de datos |
| `JWT_SECRET_KEY`  | `clave-segura`     | Clave con la que se firma el Bearer Token |
| `LOG_LEVEL`       | `INFO`             | Nivel de logs (opcional) |
| `PROXY_FIX_X_FOR` | `1`                | Proxies delante de la app: `1` local, `2` en Beanstalk |

## Ejecución local

### Opción A — Docker Compose (recomendada)

```bash
cp .env.example .env
docker compose up --build
```

El API queda en `http://localhost:5000` y PostgreSQL en `localhost:5432`.
La tabla `blacklists` se crea automáticamente al iniciar.

Generar el Bearer Token:

```bash
docker compose exec api flask generate-token
```

### Opción B — Entorno virtual de Python

Requiere Python 3.11 y un PostgreSQL disponible (se puede levantar solo la base de
datos con `docker compose up -d db`).

Linux / macOS:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
set -a; source .env; set +a
export FLASK_APP=blacklist

flask generate-token              # Bearer Token
python application.py             # API en http://localhost:5000
```

Windows (PowerShell):

```powershell
py -3.11 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
Get-Content .env | Where-Object { $_ -match '^[A-Z_]+=' } | ForEach-Object {
    $name, $value = $_ -split '=', 2; Set-Item "env:$name" $value
}
$env:FLASK_APP = "blacklist"

flask generate-token
python application.py
```

## Bearer Token

El enunciado permite un token estático y el tutor confirmó que debe ser un JWT
de Flask-JWT-Extended. El comando `flask generate-token` emite un JWT firmado con
`JWT_SECRET_KEY` y **sin expiración**: se genera una vez y se reutiliza en Postman.

El comando **no se conecta a la base de datos**: solo necesita las variables de
entorno cargadas. Un token sirve para cualquier ambiente que tenga el mismo
`JWT_SECRET_KEY`.

**Token para AWS:**

1. Definir un `JWT_SECRET_KEY` seguro y configurarlo en Beanstalk
   (todas las instancias lo comparten).
2. En local, poner ese mismo valor en `.env`, cargar las variables y ejecutar
   `flask generate-token`.
3. Usar ese token en la variable `token` de Postman.

Si el `JWT_SECRET_KEY` de Beanstalk cambia, los tokens anteriores dejan de ser
válidos y hay que generar uno nuevo.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest
```

Las pruebas usan SQLite en memoria (no requieren PostgreSQL) y el comando falla
si la cobertura baja de **100%**.

## Postman

1. Importar `postman/Blacklist-Service.postman_collection.json` en el workspace del equipo.
2. En las variables de la colección definir `base_url` (local o URL de Beanstalk) y `token`.
3. Ejecutar la colección completa (*Run collection*). Incluye escenarios de éxito,
   email duplicado, datos inválidos, ausencia de token y token inválido, cada uno
   con aserciones automáticas.
4. Publicar la documentación (*View documentation → Publish*) y anexar la URL al
   documento de la entrega.

## Logs

Los logs se escriben en la salida estándar (visibles en Docker y en los logs de
Beanstalk). Cada solicitud registra método, ruta, código de respuesta e IP:

```
2026-10-13 18:47:11,739 INFO [blacklist.access] POST /blacklists -> 201 (ip=181.49.12.7)
2026-10-13 18:47:11,754 INFO [blacklist.access] GET /blacklists/<string:email> -> 200 (ip=127.0.0.1)
```

Por privacidad, la ruta se registra como plantilla y los emails no se escriben en los logs.

## Despliegue manual en AWS Elastic Beanstalk

El servicio se despliega como contenedor Docker en un ambiente *Load balanced* de
AWS Elastic Beanstalk, con PostgreSQL en Amazon RDS.

- **Plataforma**: *Docker running on 64bit Amazon Linux 2023*. Cada instancia
  construye la imagen con el `Dockerfile`.
- **Capacidad**: auto scaling de 3 a 6 instancias detrás de un Application Load
  Balancer.
- **Base de datos**: Amazon RDS PostgreSQL sin acceso público; solo acepta el
  puerto 5432 desde el security group de las instancias.
- **Health check**: `GET /health`, definido en `.ebextensions/01-healthcheck.config`.
- **Variables de entorno** (*Environment properties*): las de la tabla
  [Variables de entorno](#variables-de-entorno), con `PROXY_FIX_X_FOR=2`.

Paquete de despliegue (los archivos en la raíz del zip, incluida la carpeta oculta
`.ebextensions/`, y **sin** `docker-compose.yml`):

```bash
zip -r blacklist-service-1.0.0.zip Dockerfile .dockerignore .ebextensions application.py requirements.txt blacklist -x "*__pycache__*"
```

En cada despliegue se incrementa la versión en `blacklist/version.py`, se registra
en `CHANGELOG.md` y se verifica con `GET /health`.
