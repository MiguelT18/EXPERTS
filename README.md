# EXPERTS

Este es un proyecto que utiliza Docker y Docker Compose para crear y gestionar los entornos de desarrollo y producción. A continuación se proporciona una guía paso a paso sobre cómo configurar y ejecutar el proyecto, así como cómo construir y levantar los contenedores tanto para desarrollo como para producción.

## Requisitos Previos

- [Docker](https://www.docker.com/get-started) (incluyendo Docker Compose) debe estar instalado en tu máquina. Puedes verificar si tienes Docker instalado ejecutando el siguiente comando:

```bash
docker --version
```

Si no tienes Docker instalado, por favor sigue las instrucciones en la [documentación oficial de Docker](https://docs.docker.com/get-started/).

### 1. Descargar Docker

Si no tienes Docker instalado en tu máquina, sigue estos pasos:

#### Para Linux:

1. Ejecuta el siguiente comando para instalar Docker:

```bash
sudo apt install docker.io
```

2. Verifica que Docker esté instalado correctamente:

```bash
docker --version
```

#### Para Mac y Windows:

Descarga Docker Desktop desde la página oficial de Docker: [Link oficial aquí](https://www.docker.com/products/docker-desktop).

### 2. Instalar Docker Compose

Docker Compose es una herramienta que facilita la administración de múltiples contenedores Docker. A partir de Docker 1.27.0, Docker Compose viene incluido como parte de la instalación de Docker, pero si no lo tienes, puedes instalarlo por separado:

#### Para Linux:

1. Descarga Docker Compose ejecutando el siguiente comando:

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

2. Dale permisos de ejecución:

```bash
sudo chmod +x /usr/local/bin/docker-compose
```

3. Verifica que Docker Compose se haya instalado correctamente:

```bash
docker-compose --version
```

#### Para Mac y Windows:

Docker Compose viene incluido en Docker Desktop, por lo que solo necesitas instalar Docker Desktop como se explicó anteriormente.

### 3. Configuración del Proyecto

#### Crear el archivo `.env`

En la raíz del proyecto, crea un nuevo archivo `.env` y agrega la siguiente configuración:

```bash
DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{database}
REDIS_URL=redis://redis:6379
ENV=development

PGADMIN_DEFAULT_EMAIL={random_name}@{random_domain}.{random_tld}
PGADMIN_DEFAULT_PASSWORD={random_password}
POSTGRES_USER={random_name}
POSTGRES_PASSWORD={random_password}
```

**Explicación de las variables:**

- `DATABASE_URL`: La URL de conexión a la base de datos PostgreSQL.
- `REDIS_URL`: La URL de conexión al servicio de Redis.
- `ENV`: El entorno de ejecución, que puede ser '_development_' o '_production_'.
- `PGADMIN_DEFAULT_EMAIL`: El correo electrónico por defecto para el usuario administrador de pgAdmin.
- `PGADMIN_DEFAULT_PASSWORD`: La contraseña para acceder a pgAdmin.
- `POSTGRES_USER`: El nombre de usuario de la base de datos PostgreSQL.
- `POSTGRES_PASSWORD`: La contraseña de la base de datos PostgreSQL.

#### Configuración de Alembic en el Backend

1. En la ruta `/core/backend`, ejecuta el siguiente comando para inicializar el directorio de migración con Alembic:

```bash
alembic init migrations
```

2. En el archivo `alembic.ini`, busca la línea que comienza con:

```bash
sqlalchemy.url = driver://user:pass@localhost/dbname
```

Y reemplázala con:

```bash
sqlalchemy.url = postgresql://{user}:{password}@{host}:{port}/{database}
```

Asegúrate de que los valores de `{user}`, `{password}`, `{host}`, `{port}`, y `{database}` coincidan con los valores definidos en tu archivo `.env`.

3. Para generar la primera migración de la base de datos, ejecuta:

```bash
alembic revision --autogenerate -m "Initial migration"
```

4. Finalmente, para aplicar las migraciones y sincronizar la base de datos con el modelo actual, ejecuta:

```bash
alembic upgrade head
```

5. Crea un archivo `.env` en la ruta `/core/backend` con las siguientes variables de entorno:

```bash
DATABASE_URL=postgresql://{user}:{password}@{host}:{5432}/{database}
REDIS_URL=redis://redis:6379

SMTP_USER=miguel.teranj02@gmail.com
SMTP_PASSWORD="neiq crxg wkol jhrt"

SECRET_KEY={secret_key}
ALGORITHM=HS256
```

6. Para crear el secret key, ejecuta el siguiente comando:

```bash
openssl rand -base64 32
```

### 4. Construcción y Levantamiento de los Contenedores

#### Entorno de Desarrollo

Para levantar los contenedores en modo de desarrollo, utiliza el siguiente comando:

```bash
docker compose up --build
```

Este comando construirá las imágenes necesarias y levantará los contenedores definidos en `docker-compose.yml`. Para detener los contenedores, puedes usar:

```bash
docker compose down
```

#### Entorno de Producción

Para levantar los contenedores en modo de producción, utiliza el siguiente comando:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

Este comando utiliza el archivo `docker-compose.prod.yml` para configurar el entorno de producción. Para detener los contenedores en producción, usa:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### 5. Acceder a la Aplicación

Una vez que los contenedores estén en funcionamiento, podrás acceder a las siguientes aplicaciones:

- **Backend:** [http://localhost:8000](http://localhost:8000)
- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **pgAdmin:** [http://localhost:5050](http://localhost:5050)
- **RedisInsight:** [http://localhost:5540](http://localhost:5540)
- **Nginx:** [http://localhost:80](http://localhost:80)

#### Credenciales de pgAdmin

Puedes acceder a pgAdmin usando las siguientes credeciales definidas en el archivo `.env`:
- **Email:** `{random_name}@{random_domain}.{random_tld}`
- **Contraseña:** `{random_password}`

### 6. Notas Adicionales

- Asegúrate de tener configuradas correctamente las variables de entorno en el archivo `.env`.
- Si experimentas problemas con los contenedores, revisa los logs usando `docker compose logs` o `docker compose logs -f` para obtener más detalles.

¡Con eso, tu entorno de desarrollo y producción debe estar listo para usarse!

Este README proporciona instrucciones completas para instalar Docker, configurar el proyecto, y ejecutar los contenedores tanto en desarrollo como en producción, además de los pasos específicos para configurar Alembic y las migraciones de la base de datos.

### 7. Usar Postman con las Rutas del Proyecto

¡Te invitamos a probar las rutas de la API usando [Postman](https://www.postman.com/). Simplemente haz clic en el siguiente enlace para unirte a nuestro equipo de Postman y empezar a interactuar con las rutas ya definidas en el proyecto.

[Unirse al equipo de Postman.](https://app.getpostman.com/join-team?invite_code=6ea484591a0f03c1a3df8b590f2e4b0b769183a13b3d62466991c7f10479e8e6&target_code=5411b12b5f4b8269d709f073a8aafd57)

¡Comienza a explorar y hacer pruebas de las funcionalidades de la API directamente desde Postman!

---

¡Con eso, tu entorno de desarrollo y producción debe estar listo para usarse!

Este README proporciona instrucciones completas para instalar Docker, configurar el proyecto, y ejecutar los contenedores tanto en desarrollo como en producción, además de los pasos específicos para configurar Alembic y las migraciones de la base de datos.