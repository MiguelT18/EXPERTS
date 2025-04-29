# TODO: Backend

1. Endpoints CRUD básicos: Sucursales
  - [❓] **POST** `/branches/create/` -> Crear una nueva sucursal (solo ADMIN).
  - [❓] **GET** `/branches/` -> Listar todas las sucursales (solo ADMIN y quizás STAFF, filtrable por estado, ciudad, etc).
  - [❓] **GET** `/branches/{id}/` -> Obtener detalles de una sucursal específica.
  - [❓] **PUT** `/branches/{id}/` -> Actualizar una sucursal (solo ADMIN).
  - [❓] **PATCH** `/branches/{id}/status/` -> Cambiar estado (activo/inactivo/mantenimiento) de una sucursal sin tocar otros campos (más eficiente que un PUT completo).
  - [❓] **DELETE** `/branches/{id}/` -> Eliminar una sucursal solo si está vacía (sin usuarios ni recursos activos). (Soft delete recomendado, es decir, marcarla como INACTIVE, no borrar la tabla directamente).
  - [❓] **GET** `/branches/{id}/resources/` -> Listar recursos de una sucursal.
  - [❓] **GET** `/branches/{id}/people/` -> Listar personas asignadas a una sucursal.
  - [❓] **GET** `/branches/{id}/transfer-records/` -> Ver historial de transferencias asociadas (enviadas y recibidas).
  - [❓] **POST** `/branches/transfer-resource/{resource_id}` -> Realizar una transferencia de recursos entre sucursales.
  
---
  
2. Modelos que deben vivir en Redis (totalmente o parcialmente):
  - **Notification:** Guardar en Redis para acceso ultra rápido y replica en PostgreSQL con historial.
  - **Invitation:** Redis como store primario y PostgreSQL para auditar.
  - **ChatMessage** Almacena los mensajes recientes (últimos 100-500 por sala en Redis, luego flushea a PostgreSQL en batch).
  - **ChatRoom y ChatParticipant:** Guarda las salas y participantes activos en Redis mientras están vivos. Persistencia eventual en RDBMS.
  