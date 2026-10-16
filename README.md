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
| Aplicación en ejecución en AWS Elastic Beanstalk, accesible vía Postman | URL del ambiente (en el documento de la entrega) |
| Repositorio con el código fuente | Este repositorio (GitHub) |
| Colección de Postman con ejemplos de solicitud y respuesta, documentación publicada | `postman/` y URL publicada (ver [Postman](#postman)) |
| Documento "Proyecto 1 entrega 1 – Documento.pdf" | Entrega del curso |
| Video de sustentación (máximo 10 minutos) | Entrega del curso |

## Stack tecnológico

| Tecnología          | Versión | Uso |
|---------------------|---------|-----|
| Python              | 3.11    | Lenguaje de programación |
| Flask               | 1.1.4   | Micro framework web |
| Flask-SQLAlchemy    | 2.5.1   | ORM SQLAlchemy |
| Flask-RESTful       | 0.3.10  | API REST |
| Flask-Marshmallow   | 0.15.0  | Serialización y validación |
| Flask-JWT-Extended  | 4.3.1   | Bearer Token (JWT) |
| Werkzeug            | 1.0.1   | Biblioteca WSGI (`ProxyFix` para la IP real del cliente) |
| PostgreSQL          | 16      | Base de datos (AWS RDS en la nube) |
| psycopg2-binary     | 2.9.10  | Driver de PostgreSQL para SQLAlchemy |
| gunicorn            | 23.0.0  | Servidor WSGI dentro del contenedor Docker |

> Las dependencias transitivas (Jinja2, MarkupSafe, itsdangerous, click) están fijadas
> en `requirements.txt` porque sus versiones recientes no son compatibles con Flask 1.1.x.

## Estructura del proyecto

```
blacklist-service/
├── application.py              # Punto de entrada WSGI (Beanstalk busca `application`)
├── blacklist/                  # Código de la aplicación Flask
│   ├── config.py               # Configuración desde variables de entorno
│   ├── api/                    # Recursos REST, esquemas, rutas y autenticación
│   ├── domain/                 # Entidad y excepciones
│   ├── use_cases/              # Agregar email / consultar estado
│   └── infrastructure/         # Modelo SQLAlchemy y acceso a PostgreSQL
├── tests/                      # Pruebas unitarias y de integración
├── docs/arquitectura.md        # Diagrama de despliegue en AWS y modelo de datos
├── postman/                    # Colección de Postman con los escenarios de prueba
├── CHANGELOG.md                # Historial de versiones
├── Dockerfile                  # Imagen que construye Beanstalk (plataforma Docker)
├── docker-compose.yml
├── Procfile                    # Arranque en la plataforma Python de Beanstalk (con Docker se usa el CMD)
├── requirements.txt            # Dependencias de ejecución
├── requirements-dev.txt        # + pytest y cobertura
├── setup.cfg                   # Configuración de pytest y cobertura
├── .env.example                # Plantilla de variables de entorno
└── .ebextensions/              # Configuración de Beanstalk (health check) incluida en el zip
```

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
- Responden **400**: un email con formato inválido o de más de 255 caracteres, un `app_uuid`
  que no es un UUID, o un `blocked_reason` de más de 255 caracteres.
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

El enunciado permite un token predefinido para toda la aplicación. Por indicación del
tutor, debe ser un JWT válido de Flask-JWT-Extended, no un texto cualquiera. El comando
`flask generate-token` emite un JWT firmado con `JWT_SECRET_KEY` y **sin expiración**:
se genera una vez y se reutiliza en Postman.

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
3. Ejecutar la colección (*Run collection*). Cubre los 3 endpoints con 15 escenarios,
   cada uno con aserciones automáticas y un ejemplo de respuesta:
   - `POST /blacklists`: email agregado, sin motivo (opcional), duplicado (409), duplicado
     con mayúsculas (409), datos inválidos (400), campos obligatorios ausentes (400),
     sin token (401) y token inválido (401).
   - `GET /blacklists/<email>`: email en la lista, con mayúsculas, sin motivo, email que
     no está, sin token (401) y token inválido (401).
   - `GET /health`.
4. Cada endpoint tiene su ejemplo de solicitud y respuesta. Publicar la documentación
   (*View documentation → Publish*) y anexar la URL al documento de la entrega.

## Despliegue manual en AWS Elastic Beanstalk

Despliegue manual (sin CI/CD) del servicio como contenedor Docker en un ambiente
*Load balanced* de AWS Elastic Beanstalk, con PostgreSQL en Amazon RDS. Diagrama en
[`docs/arquitectura.md`](docs/arquitectura.md).

- **Plataforma**: *Docker running on 64bit Amazon Linux 2023*. Cada instancia
  construye la imagen con el `Dockerfile`.
- **Capacidad**: auto scaling de 3 a 6 instancias detrás de un Application Load
  Balancer.
- **Base de datos**: Amazon RDS PostgreSQL sin acceso público; solo acepta el
  puerto 5432 desde el security group de las instancias.
- **Health check**: `GET /health`, definido en `.ebextensions/01-healthcheck.config`.
- **Variables de entorno** (*Environment properties*): las de la tabla
  [Variables de entorno](#variables-de-entorno), con `PROXY_FIX_X_FOR=2`.
- **Verificación**: `GET /health` debe responder 200 y la colección de Postman debe
  pasar contra la URL del ambiente. En la tabla `blacklists` la IP guardada debe ser
  la del cliente, no una privada (`172.31.x.x`).

Paquete de despliegue (los archivos en la raíz del zip, incluida la carpeta oculta
`.ebextensions/`, y **sin** `docker-compose.yml`):

```bash
zip -r blacklist-service-1.0.0.zip Dockerfile .dockerignore .ebextensions application.py requirements.txt blacklist -x "*__pycache__*"
```

En cada despliegue se incrementa la versión en `blacklist/version.py`, se registra
en `CHANGELOG.md` y se verifica con `GET /health`.

### Estrategias de despliegue

Se ejecutan 4 estrategias distintas, todas con más de una instancia (auto scaling de 3 a 6):

| # | Estrategia | Versión | Instancias | Descripción |
|---|---|---|---|---|
| 1 | Traffic splitting | 1.0.1 | Nuevas | Lanza instancias nuevas y les envía un porcentaje del tráfico antes de completar el cambio. |
| 2 | Immutable | 1.0.2 | Nuevas | Lanza instancias nuevas con la versión nueva y elimina las anteriores si pasan el health check. |
| 3 | All at once | 1.0.3 | Las iniciales | Actualiza todas las instancias a la vez; puede haber una breve indisponibilidad. |
| 4 | Rolling | 1.0.4 | Las iniciales | Actualiza por lotes; la capacidad baja durante cada lote y conviven dos versiones. |

Para cada una:

1. Incrementar la versión en `blacklist/version.py`, registrarla en `CHANGELOG.md` y
   generar el `.zip` del paquete de despliegue.
2. Seleccionar la estrategia en *Configuration → Rolling updates and deployments* y
   desplegar el `.zip`.
3. Consultar `GET /health` repetidamente durante el despliegue: cada respuesta indica
   la versión que atiende la instancia (evidencia de que el despliegue está en ejecución).
4. Registrar en el documento de la entrega: cantidad de instancias, cómo se validó el
   despliegue, tiempo total (minutos y segundos, pestaña *Events*), si se hizo sobre
   instancias iniciales o nuevas, capturas de la consola y hallazgos.
