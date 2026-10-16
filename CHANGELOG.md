# Changelog

Cambios relevantes del microservicio. El formato sigue
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el versionamiento
[SemVer](https://semver.org/lang/es/).

La versión vive en `blacklist/version.py` y se expone en `GET /health`.
Para cada despliegue (por ejemplo, cada estrategia de la Entrega 1) se incrementa
la versión y se registra aquí.

## [1.0.4] - 2026-10-15

### Cambiado

- Despliegue en AWS Elastic Beanstalk con la estrategia *Rolling* (lote fijo de 1 instancia).

## [1.0.3] - 2026-10-15

### Cambiado

- Despliegue en AWS Elastic Beanstalk con la estrategia *All at once*.

## [1.0.2] - 2026-10-15

### Cambiado

- Despliegue en AWS Elastic Beanstalk con la estrategia *Immutable*.

## [1.0.1] - 2026-10-14

### Cambiado

- Despliegue en AWS Elastic Beanstalk con la estrategia *Traffic splitting*.

## [1.0.0] - 2026-10-13

### Agregado

- `POST /blacklists`: agrega un email a la lista negra global. Guarda la IP de
  origen y la fecha/hora de la solicitud.
- `GET /blacklists/<email>`: indica si el email está en la lista negra y el motivo.
- Autenticación con Bearer Token (JWT de Flask-JWT-Extended, sin expiración).
- Comando `flask generate-token`, que no requiere conexión a la base de datos.
- `GET /health` con la versión desplegada, para los health checks de AWS Beanstalk.
- Validaciones: email válido, `app_uuid` UUID y `blocked_reason` de máximo 255 caracteres (400).
- Email duplicado rechazado con 409; emails tratados sin distinguir mayúsculas.
- Persistencia en PostgreSQL con creación automática de la tabla al iniciar.
- Logs de cada solicitud y de los eventos del negocio.
- Dockerfile, Docker Compose, colección de Postman y pruebas con cobertura del 100%.
