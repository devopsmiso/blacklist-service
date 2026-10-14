# Arquitectura — Blacklist Service

Los diagramas están en [Mermaid](https://mermaid.js.org/), que GitHub muestra
directamente. Las imágenes en `docs/img/` son las mismas, listas para el
documento de la entrega.

## 1. Despliegue en AWS

Despliegue manual sobre AWS Elastic Beanstalk (PaaS), sin CI/CD.

![Despliegue en AWS](img/despliegue-aws.png)

```mermaid
flowchart LR
    client["Postman / apps internas"]

    subgraph aws["AWS"]
        subgraph eb["Elastic Beanstalk — ambiente Load balanced"]
            alb["Application Load Balancer<br/>health check: GET /health"]
            subgraph asg["Auto Scaling Group (mín. 3 — máx. 6 instancias EC2)"]
                ec2a["EC2: Nginx → gunicorn → Flask"]
                ec2b["EC2: Nginx → gunicorn → Flask"]
                ec2c["EC2: Nginx → gunicorn → Flask"]
            end
        end
        rds[("Amazon RDS<br/>PostgreSQL")]
    end

    client -- "HTTP + Bearer Token" --> alb
    alb --> ec2a
    alb --> ec2b
    alb --> ec2c
    ec2a -- "5432" --> rds
    ec2b -- "5432" --> rds
    ec2c -- "5432" --> rds
```

| Componente | Función |
|---|---|
| Application Load Balancer | Reparte el tráfico entre instancias y retira las que fallan el health check (`/health`). Agrega la IP del cliente en `X-Forwarded-For`. |
| Auto Scaling Group | Mantiene entre 3 y 6 instancias. Las estrategias de despliegue actúan sobre este grupo. |
| EC2 (Nginx → gunicorn → Flask) | Nginx es el proxy de la plataforma Python de Beanstalk; gunicorn ejecuta `application:application`. |
| Amazon RDS (PostgreSQL) | Base de datos compartida por todas las instancias. Solo acepta conexiones del security group de Beanstalk. |

La IP del cliente pasa por dos proxies (balanceador y Nginx); por eso en
Beanstalk se configura `PROXY_FIX_X_FOR=2`.

## 2. Capas (Clean Architecture)

Las dependencias apuntan hacia el dominio. El dominio no conoce Flask ni SQLAlchemy.

![Capas](img/capas.png)

```mermaid
flowchart TB
    api["api<br/>Recursos REST, esquemas Marshmallow,<br/>JWT, manejo de errores, logs"]
    uc["use_cases<br/>AddEmailToBlacklist, GetBlacklistStatus"]
    domain["domain<br/>BlacklistEntry, excepciones,<br/>contrato BlacklistRepository"]
    infra["infrastructure<br/>BlacklistModel, SQLAlchemyBlacklistRepository"]
    root["create_app (raíz de composición)<br/>inyecta el repositorio en los casos de uso"]

    api --> uc
    uc --> domain
    infra -- "implementa" --> domain
    root -.-> api
    root -.-> infra
```

## 3. Flujo de `POST /blacklists`

![Flujo POST](img/flujo-post.png)

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as BlacklistCollectionResource
    participant U as AddEmailToBlacklist
    participant P as SQLAlchemyBlacklistRepository
    participant DB as PostgreSQL

    C->>R: POST /blacklists + Bearer Token
    R->>R: Valida el JWT (401 si falla)
    R->>R: Valida el cuerpo con Marshmallow (400 si falla)
    R->>U: AddEmailCommand(email, app_uuid, motivo, IP)
    U->>P: find_by_email(email normalizado)
    P->>DB: SELECT
    alt El email ya existe
        U-->>R: EmailAlreadyBlacklistedError
        R-->>C: 409 Conflict
    else Email nuevo
        U->>P: add(entrada con fecha/hora UTC)
        P->>DB: INSERT
        R-->>C: 201 Created + mensaje de confirmación
    end
```

## 4. Modelo de datos

| Columna | Tipo | Restricción |
|---|---|---|
| `id` | INTEGER | Llave primaria |
| `email` | VARCHAR(255) | Obligatorio, único, indexado, en minúsculas |
| `app_uuid` | VARCHAR(36) | Obligatorio |
| `blocked_reason` | VARCHAR(255) | Opcional |
| `ip_address` | VARCHAR(45) | Obligatorio (admite IPv6) |
| `created_at` | TIMESTAMP WITH TIME ZONE | Obligatorio |
