# Bitácora de Interacciones y Prompts de Asistencia con IA
## Proyecto: Dulce Arte — Sistema Web de Trazabilidad, Producción, Inventario y Despacho

Este documento registra de forma transparente y auditable el soporte de Inteligencia Artificial utilizado durante las fases del proyecto, cumpliendo con los estándares de integridad académica.

---

### Registro N.º 1 — Fase 1: Análisis Funcional y Diseño de Arquitectura
* **Fecha:** 2026-11-06
* **Rol Asumido:** Arquitecto de Software Senior & Diseñador Fullstack UX/UI.
* **Instrucción del Usuario:**
  > Actúa como un arquitecto de software senior... Vamos a desarrollar desde cero un proyecto académico llamado Dulce Arte... Stack obligatorio: Python, Django, DRF, PostgreSQL, Django Templates, Tailwind CSS, Admin personalizado, sesiones Django, AWS EC2. Comienza únicamente con la FASE 1: Análisis funcional, arquitectura propuesta, estructura de directorios, modelos/relaciones, matriz RBAC, endpoints REST, plan de implementación y criterios de aceptación. No implementes código todavía.
* **Aportes y Soluciones de la IA:**
  1. Diseño del flujo de valor integral (*End-to-End*) desde cotización hasta entrega con firma digital.
  2. Diagrama de arquitectura modular monolítica con desacoplamiento estricto mediante la capa de servicios (`Service Layer Pattern`).
  3. Formulación de las 6 reglas de negocio críticas (*invariants*): identificación única `DA-YYYY-XXXXX`, no negatividad de stock, consumo atómico con `select_for_update()`, protección anti-doble consumo con flag `stock_consumed`, trazabilidad histórica inmutable y entrega con firma digital idempotente.
  4. Especificación del Modelo Entidad-Relación (MER) con 11 entidades y restricciones de integridad (`CheckConstraint`, `UniqueConstraint`).
  5. Matriz RBAC para los 4 roles requeridos: `ADMIN`, `VENTAS`, `COCINA`, `REPARTIDOR`.
  6. Especificación de endpoints REST v1 con estándares de verbos HTTP y códigos de estado.
  7. Plan de desarrollo en 7 fases y criterios de aceptación en formato BDD/Gherkin.

---

### Registro N.º 2 — Fase 2: Ajustes de Arquitectura e Implementación Inicial
* **Fecha:** 2026-11-06
* **Rol Asumido:** Arquitecto de Software Senior y Desarrollador Especializado en Django, DRF y PostgreSQL.
* **Instrucción del Usuario:**
  > Continuemos con Dulce Arte. La Fase 1 queda APROBADA CON AJUSTES: 1. Rutas de despacho mediante DeliveryRoute y paradas ordenadas; 2. Conversión consistente de unidades de medida; 3. Soporte para personalizaciones de pedidos; 4. CRUD con eliminación protegida (Soft Delete); 5. Protección CSRF, autenticación por sesiones y RBAC en API y Web; 6. Validación atómica de stock y bloqueo de filas; 7. Diferenciar estados comerciales de etapas de cocina; 8. Mantener implementación sencilla y académica. Implementar Fase 2: entorno virtual, Django, DRF, PostgreSQL real (no SQLite), modelo Custom User antes de migraciones, Django Admin personalizado, Frontend base con tokens de diseño, documentación y verificación real de inicio.
* **Aportes y Soluciones de la IA:**
  1. **Inspección de Infraestructura:** Detección de PostgreSQL 16 y Python 3.14 en el sistema local.
  2. **Configuración de Base de Datos Real:** Puesta en marcha del servicio PostgreSQL, verificación de credenciales locales y creación de la base de datos `dulce_arte_db`.
  3. **Instalación de Dependencias:** Creación del entorno virtual `.venv` e instalación de `Django 6.1.3`, `djangorestframework 3.18.3`, `psycopg 3.3.8` (adaptador oficial moderno de PostgreSQL), `python-dotenv 1.2.4`, `pillow 13.0.0` y `django-cors-headers 4.9.0`.
  4. **Modularización Limpia:** Estructura de 9 aplicaciones modulares (`core`, `users`, `clients`, `inventory`, `recipes`, `orders`, `production`, `dispatch`, `dashboard`) desacopladas bajo la carpeta `apps/`.
  5. **Modelos Abstractos de Integridad (`core`):** Creación de `TimeStampedModel` y `SoftDeleteModel` para desactivación lógica y auditoría histórica no destructiva.
  6. **Motor de Conversión de Unidades (`core.utils`):** Implementación de utilidades para cálculo entre gramos/kilogramos, mililitros/litros y unidades.
  7. **Modelo Custom User Pre-Migración (`users.models.User`):** Definición del modelo heredado de `AbstractUser` con enumeración `UserRole` (`ADMIN`, `VENTAS`, `COCINA`, `REPARTIDOR`) y propiedades booleanas (`is_admin`, `is_sales`, etc.), evitando errores irreparables en el ciclo de vida del ORM.
  8. **Seguridad y Permisos RBAC (`users.permissions`):** Clases de permisos para DRF (`IsAdminRole`, `IsSalesRole`, etc.) y mixins/decoradores para Django Web (`RoleRequiredMixin`, `@role_required`).
  9. **Frontend Atómico & Tokens Semánticos:**
     - Archivo `static/css/theme.css` con variables CSS para la paleta institucional:
       - Fondo principal: `#FAF7F2`
       - Burdeos principal: `#773344`
       - Rosa pastel: `#F3D6DB`
       - Verde suave: `#DCEBDD`
       - Texto oscuro: `#292524`
     - Plantilla base `templates/base.html`, componentes modulares `sidebar.html` y `topbar.html`, y pantallas operativas `login.html` y `dashboard/index.html`.
  10. **Verificación y Pruebas Reales:** Creación y ejecución de la suite de pruebas automatizadas `tests/test_initial_setup.py` (8 pruebas ejecutadas en 18.36s contra PostgreSQL con resultado exitoso 100%).

---

### Registro N.º 3 — Fase 3: Modelado Relacional, Migraciones y Django Admin
* **Fecha:** 2026-11-06
* **Rol Asumido:** Arquitecto Senior especializado en Django ORM, PostgreSQL, Integridad Referencial y Diseño Administrativo.
* **Instrucción del Usuario:**
  > Continuemos con el proyecto Dulce Arte... Ejecutar la FASE 3: Modelado Relacional, Migraciones y Django Admin... 1. Auditoría previa obligatoria; 2. Modelos del dominio: Clientes (Client), Inventario (Supply, UnitOfMeasure, StockMovement), Productos y Recetas (Product, Recipe, RecipeIngredient), Pedidos (Order, OrderItem, OrderStatusHistory), Producción (ProductionOrder, QualityCheck), Despachos (DeliveryRoute, DispatchOrder, DeliveryProof); 3. Integridad de datos: ForeignKey/OneToOne, UniqueConstraint, CheckConstraint, DecimalField para dinero/cantidades, índices, PROTECT, eliminación lógica, unidades compatibles, no poner consumo en save(); 4. Django Admin profesional: list_display, list_filter, search_fields, inlines tabulares, badges visuales, inmutabilidad de movimientos e historial; 5. Migraciones en PostgreSQL; 6. Pruebas automatizadas completas; 7. Actualización de documentación.
* **Aportes y Soluciones de la IA:**
  1. **Auditoría Previa Exitosa:** Verificación de `check` (0 issues), conexión a PostgreSQL 16 y ejecución de la suite base (8/8 pruebas exitosas).
  2. **Implementación de Modelos del Dominio:**
     - `clients.Client`: Validación de RUT chileno (módulo 11) y DNI internacional, normalización y `SoftDeleteModel`.
     - `inventory.UnitOfMeasure`: Conversión consistente de magnitudes (`MASA`, `VOLUMEN`, `UNIDAD`) con factores hacia unidades base.
     - `inventory.Supply`: Insumos con `CheckConstraint` de no negatividad para stock actual, mínimo y costo unitario.
     - `inventory.StockMovement`: Historial de solo anexado (`ENTRADA`, `SALIDA_MANUAL`, `CONSUMO_PRODUCCION`, `AJUSTE_MERMA`, `DEVOLUCION`) con bloqueo de edición/eliminación en Django Admin.
     - `recipes.Product`: Catálogo de productos con categoría, precio base y tiempo de producción.
     - `recipes.Recipe` & `RecipeIngredient`: BOM con porcentaje de merma, cálculo de cantidad bruta efectiva, conversión a unidad base del insumo y validación estricta de magnitudes compatibles en `clean()`.
     - `orders.Order`: Código único `DA-YYYY-XXXXX`, estados comerciales desacoplados de cocina, cálculo de saldo pendiente y restricción `deposit_amount <= total_amount`.
     - `orders.OrderItem`: Personalización artesanal (porciones, sabor de bizcocho, relleno, cubierta, dedicatoria, detalles) con subtotales en `DecimalField`.
     - `orders.OrderStatusHistory`: Bitácora histórica inmutable vinculada al usuario responsable.
     - `production.ProductionOrder`: Etapas Kanban (`RECIBIDO`, `EN_PREPARACION`, `HORNEADO_DECORADO`, `CONTROL_CALIDAD`, `LISTO`), cocinero asignado y flag de seguridad `stock_consumed` anti-duplicados.
     - `production.QualityCheck`: Evaluación de conformidad previa a entrega.
     - `dispatch.DeliveryRoute`: Rutas programadas por fecha y repartidor.
     - `dispatch.DispatchOrder`: Paradas ordenadas (`stop_order`) con restricción de unicidad de secuencia en ruta (`UniqueConstraint(fields=['route', 'stop_order'])`).
     - `dispatch.DeliveryProof`: Certificación de entrega con firma digital (DataURI) y receptor.
  3. **Compatibilidad Django 6+:** Identificación y adaptación proactiva de `CheckConstraint(condition=Q(...))` reemplazando el argumento deprecado `check=...`.
  4. **Django Admin Profesional:** Inlines tabulares (`RecipeIngredientInline`, `OrderItemInline`, `OrderStatusHistoryInline`, `QualityCheckInline`, `DispatchOrderInline`), badges visuales HTML para estados y bloqueo de edición en tablas de auditoría.
  5. **Migraciones:** Creación y aplicación limpia de 6 archivos de migración inicial en PostgreSQL sin modificar bases de datos existentes.
  6. **Suite de Pruebas Completa:** Creación de 12 pruebas de integridad y ejecución conjunta con las 8 de Fase 2, alcanzando 20 pruebas ejecutadas en 15.91s con 100% de éxito.

---

### Registro N.º 4 — Fase 4: Capa de Servicios y Reglas de Negocio
* **Fecha:** 2026-11-08
* **Rol Asumido:** Arquitecto de Software Senior & Especialista en Lógica de Dominio y Concurrencia en Django.
* **Instrucción del Usuario:**
  > Implementar la lógica de negocio desacoplada en la capa de servicios (`Service Layer Pattern`) para los módulos operativos de Dulce Arte: creación, confirmación y cancelación de pedidos con generación automática de órdenes de producción y despacho; máquina de estados para el flujo Kanban de cocina con control de calidad obligatorio; descuento transaccional y atómico de insumos por receta (BOM) previniendo condiciones de carrera y doble consumo; y gestión completa de rutas de despacho con certificación de entrega mediante firma digital.
* **Aportes y Soluciones de la IA:**
  1. `OrderService`: creación transaccional de pedidos con cálculo de ítems, confirmación comercial (genera automáticamente `ProductionOrder` en etapa `RECIBIDO` y `DispatchOrder` pendiente de ruta) y cancelación controlada con registro en `OrderStatusHistory`.
  2. `ProductionService`: máquina de estados para transiciones de etapa Kanban (`RECIBIDO` -> `EN_PREPARACION` -> `HORNEADO_DECORADO` -> `CONTROL_CALIDAD` -> `LISTO`), validación de control de calidad aprobado (`QualityCheck`) antes de pasar a `LISTO` y asignación de pastelero con rol `COCINA`.
  3. `InventoryService`: verificación previa de disponibilidad de stock convirtiendo unidades de receta a unidad base del insumo, registro de entradas/mermas y descuento atómico de insumos con bloqueo pesimista (`select_for_update()`); uso del flag `stock_consumed` para garantizar idempotencia y evitar el doble descuento.
  4. `DispatchService`: creación de hojas de ruta (`DeliveryRoute`), asignación ordenada de paradas (`stop_order`), inicio de ruta y confirmación de entrega idempotente con firma digital (`DeliveryProof`) y actualización del pedido a `ENTREGADO`.

---

### Registro N.º 5 — Fase 5: API REST v1 y Permisos por Rol
* **Fecha:** 2026-11-08
* **Rol Asumido:** Desarrollador Backend Senior especializado en Django REST Framework y Seguridad RBAC.
* **Instrucción del Usuario:**
  > Exponer los módulos operativos y la capa de servicios mediante una API RESTful versionada bajo `/api/v1/`, implementando serializadores de lectura y entrada validados, autenticación por sesiones de Django, protección CSRF y control de acceso basado en roles (RBAC) para `ADMIN`, `VENTAS`, `COCINA` y `REPARTIDOR`.
* **Aportes y Soluciones de la IA:**
  1. Serializers de lectura y validación de entrada (`InputSerializer`) junto con `ViewSets` y acciones personalizadas (`@action`) en DRF para clientes, inventario, recetas, pedidos, producción Kanban, despacho y métricas de dashboard.
  2. Autenticación por sesión (`SessionAuthentication`) y permiso `IsAuthenticated` global por defecto, aplicando permisos granulares por rol (`IsAdminRole`, `IsSalesRole`, `IsKitchenRole`, `IsDriverRole`) según la matriz RBAC.
  3. Validación estricta de identificadores UUID, paginación estándar y manejo uniforme de excepciones de dominio (`ValidationError` / `BusinessLogicError`) traducidas a respuestas HTTP `400 Bad Request` y `403 Forbidden`.

---

### Registro N.º 6 — Fase 6: Interfaz Web (Templates)
* **Fecha:** 2026-11-09
* **Rol Asumido:** Desarrollador Fullstack Django & Diseñador de Interfaces Operativas con Tailwind CSS.
* **Instrucción del Usuario:**
  > Construir la interfaz web operativa utilizando Django Templates y Tailwind CSS: pantalla de autenticación, layout base con navegación lateral según rol, panel de control principal con KPIs en tiempo real y vistas de consulta para los módulos de pedidos, producción, inventario y despacho.
* **Aportes y Soluciones de la IA:**
  1. Estructura de plantillas `base.html` con componentes modulares `sidebar.html` y `topbar.html`, integrando la paleta institucional de Dulce Arte (`#FAF7F2`, `#773344`, `#DCEBDD`) y pantallas `login.html`, `dashboard/index.html` y vistas operativas por módulo.
  2. Vistas basadas en clases protegidas con `LoginRequiredMixin` y control de acceso por rol, alimentadas por consultas agregadas desde `DashboardService` (pedidos del día, órdenes en cocina, alertas de stock crítico y entregas en ruta).

---

### Registro N.º 7 — Fase 7: Pruebas y Documentación
* **Fecha:** 2026-11-09
* **Rol Asumido:** Ingeniero QA de Automatización en Python/Django & Arquitecto Documental.
* **Instrucción del Usuario:**
  > Desarrollar una suite exhaustiva de pruebas unitarias y de integración que valide los modelos, restricciones de base de datos, servicios de dominio, consumo atómico de inventario, permisos RBAC en API REST y flujo completo End-to-End (alcanzando 55 pruebas automatizadas), además de documentar la arquitectura, el MER y las instrucciones de ejecución en `README.md`.
* **Aportes y Soluciones de la IA:**
  1. Implementación y verificación de la suite de 55 pruebas automatizadas distribuidas en validación de configuración inicial, integridad relacional y restricciones (`CheckConstraint`/`UniqueConstraint`), reglas de negocio en la capa de servicios (`OrderService`, `ProductionService`, `InventoryService`, `DispatchService`), endpoints de la API REST v1 con matriz RBAC y flujo integral *End-to-End* desde el pedido hasta la entrega con firma digital.
  2. Actualización integral de `README.md` con la arquitectura del sistema, Modelo Entidad-Relación (MER), invariantes de negocio, matriz de permisos y comandos de ejecución de pruebas sobre PostgreSQL y SQLite en memoria (`config.settings.test`).

---

### Registro N.º 8 — Django Admin con Templates
* **Fecha:** 2026-11-10
* **Instrucción del Usuario:**
  > Mantengámoslo simple, que tenga lo esencial de la rúbrica.
* **Aportes y Soluciones de la IA:**
  1. Revisión del proyecto contra la rúbrica de la Evaluación 3.
  2. Se propuso personalizar el Admin; en la revisión posterior se detectó que las plantillas estaban guardadas con extensión `.txt` y una estaba vacía, y se corrigieron en el Registro N.º 9.

---

### Registro N.º 9 — Revisión de la Evaluación y Preparación de Despliegue
* **Fecha:** 2026-11-10
* **Instrucción del Usuario:**
  > El proyecto está basado en la actividad; completar lo necesario para cumplir la rúbrica y mantener el código sencillo.
* **Aportes y Soluciones de la IA:**
  1. Comparación de la implementación con la pauta, comprobación de migraciones y ejecución de las 55 pruebas con una configuración aislada de SQLite en memoria.
  2. Activación de las plantillas de marca e índice del Django Admin con los nombres que Django reconoce (`admin/base_site.html` y `admin/index.html`).
  3. Preparación de Gunicorn, Nginx y un servicio systemd para EC2, más instrucciones de configuración PostgreSQL.
  4. Despliegue en Ubuntu 26.04 con PostgreSQL 18, Gunicorn y Nginx; migraciones y archivos estáticos aplicados, y página de inicio de sesión del Admin verificada por HTTP 200 en `http://100.48.94.162/admin/login/`.
  5. Configuración de acceso HTTP por IP pública, sin HTTPS ni DNS, según la decisión del usuario. Los secretos de producción se generaron en la instancia y no se incluyeron en el repositorio ni en el paquete desplegado.

---

### Registro N.º 10 — Simplificación de la Interfaz
* **Fecha:** 2026-11-11
* **Instrucción del Usuario:**
  > Dejar el diseño visualmente simple y conservar lo importante.
* **Aportes y Soluciones de la IA:**
  1. Se simplificaron la navegación, el inicio de sesión y el resumen principal, conservando las métricas y enlaces operativos.
  2. Se retiraron elementos visuales y controles sin función para facilitar el uso y mantenimiento.
