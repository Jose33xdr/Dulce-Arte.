import os
import django
from datetime import date, time, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from apps.clients.models import Client
from apps.users.models import User, UserRole
from apps.recipes.models import Product, ProductCategory
from apps.orders.models import Order, OrderItem, OrderStatus, DeliveryType
from apps.production.models import ProductionOrder, KanbanStage, QualityCheck, QualityResult
from apps.dispatch.models import DispatchOrder, DispatchStatus

def seed_clients_and_orders():
    print("=== 1. POBLANDO 10 CLIENTES NUEVOS ===")
    clients_data = [
        {
            "identification": "15.482.910-3",
            "name": "Valentina Paz Concha Lagos",
            "email": "valentina.concha@gmail.com",
            "phone": "+56984123678",
            "address": "Av. Providencia 1420, Depto 804, Providencia",
            "notes": "Cliente frecuente, prefiere preparaciones bajas en azúcar.",
        },
        {
            "identification": "17.204.659-8",
            "name": "Gonzalo Ignacio Sepúlveda Mora",
            "email": "gonzalo.sepulveda@outlook.com",
            "phone": "+56973569102",
            "address": "Los Militares 5890, Las Condes",
            "notes": "Cumpleaños infantil temático.",
        },
        {
            "identification": "16.892.341-2",
            "name": "Constanza Belén Valenzuela Riquelme",
            "email": "constanza.valenzuela@gmail.com",
            "phone": "+56992345671",
            "address": "Eliodoro Yáñez 2150, Providencia",
            "notes": "Alergia leve a nueces.",
        },
        {
            "identification": "18.520.147-5",
            "name": "Felipe Andrés Muñoz Carrasco",
            "email": "felipe.munoz@yahoo.com",
            "phone": "+56961284793",
            "address": "Av. Andrés Bello 2711, Las Condes",
            "notes": "Retira en tienda siempre de mañana.",
        },
        {
            "identification": "14.739.028-1",
            "name": "María José Larraín Chadwick",
            "email": "mjlarrain@empresaslarrain.cl",
            "phone": "+56989341120",
            "address": "Camino El Alba 8900, Las Condes",
            "notes": "Empresa para eventos corporativos.",
        },
        {
            "identification": "19.382.745-6",
            "name": "Sebastián Eduardo Torres Pezoa",
            "email": "seba.torres@gmail.com",
            "phone": "+56955438901",
            "address": "Manuel Montt 850, Providencia",
            "notes": "Torta para aniversario de matrimonio.",
        },
        {
            "identification": "17.915.430-K",
            "name": "Francisca Javiera Reyes Alarcón",
            "email": "fran.reyes@hotmail.com",
            "phone": "+56978213456",
            "address": "Av. Vitacura 4320, Vitacura",
            "notes": "Decoración minimalista y elegante.",
        },
        {
            "identification": "20.143.892-7",
            "name": "Nicolás Alejandro Silva Gómez",
            "email": "nico.silva@alumnos.uc.cl",
            "phone": "+56944127890",
            "address": "Av. Vicuña Mackenna 4860, Macul",
            "notes": "Graduación universitaria de ingeniería.",
        },
        {
            "identification": "16.340.871-9",
            "name": "Camila Ignacia Rojas Valdés",
            "email": "camila.rojas.v@gmail.com",
            "phone": "+56991236789",
            "address": "Av. Suecia 1250, Providencia",
            "notes": "Diseño con detalles florales naturales.",
        },
        {
            "identification": "18.112.564-4",
            "name": "Joaquín Esteban Donoso Fuentes",
            "email": "joaquin.donoso@gmail.com",
            "phone": "+56986543219",
            "address": "Monseñor Edwards 1020, La Reina",
            "notes": "Despacho a domicilio en horario tarde.",
        },
    ]

    created_clients = []
    for c_data in clients_data:
        client, created = Client.objects.get_or_create(
            identification=c_data["identification"],
            defaults=c_data,
        )
        if not created:
            for k, v in c_data.items():
                setattr(client, k, v)
            client.is_active = True
            client.save()
        created_clients.append(client)
        status = "Creado" if created else "Actualizado"
        print(f"[{status}] Cliente: {client.name} (RUT: {client.identification})")

    print("\n=== 2. POBLANDO PRODUCTOS DE PASTELERÍA ===")
    products_data = [
        {
            "code": "PRD-TOR-002",
            "name": "Torta Tradicional de Manjar y Nuez",
            "category": ProductCategory.TORTA_TRADICIONAL,
            "base_price": 32000,
            "estimated_production_minutes": 90,
            "description": "Bizcochuelo artesanal de vainilla relleno con abundante manjar casero y nueces mariposa.",
        },
        {
            "code": "PRD-PAS-001",
            "name": "Pastel Fondant Personalizado Premium",
            "category": ProductCategory.PASTEL_FONDANT,
            "base_price": 48000,
            "estimated_production_minutes": 180,
            "description": "Modelado temático artístico en pasta de azúcar fondant de alta elasticidad.",
        },
        {
            "code": "PRD-TOR-003",
            "name": "Torta Selva Negra con Chocolate Belga",
            "category": ProductCategory.TORTA_TRADICIONAL,
            "base_price": 36000,
            "estimated_production_minutes": 100,
            "description": "Capas de bizcocho húmedo de cacao con guindas, crema chantilly fresca y virutas de chocolate.",
        },
        {
            "code": "PRD-TOR-004",
            "name": "Torta Mousse de Maracuyá y Chocolate Blanco",
            "category": ProductCategory.TORTA_TRADICIONAL,
            "base_price": 38000,
            "estimated_production_minutes": 120,
            "description": "Refrescante mousse de maracuyá natural con base crocante y ganache suave de chocolate blanco.",
        },
        {
            "code": "PRD-TOR-005",
            "name": "Torta Red Velvet Artesanal con Crema de Queso",
            "category": ProductCategory.TORTA_TRADICIONAL,
            "base_price": 42000,
            "estimated_production_minutes": 110,
            "description": "Clásica masa terciopelo rojo combinada con frosting de queso crema tipo Philadelphia y vainilla.",
        },
    ]

    products_map = {}
    for p_data in products_data:
        p, _ = Product.objects.get_or_create(
            code=p_data["code"],
            defaults=p_data,
        )
        products_map[p.code] = p
        print(f"Producto listo: {p.name} - ${p.base_price}")

    print("\n=== 3. POBLANDO 5 PEDIDOS EN LAS 5 ETAPAS DEL TABLERO KANBAN ===")
    cook_sofia = User.objects.get(username="sofia.pastelera")
    cook_rodrigo = User.objects.get(username="rodrigo.chef")
    cook_valentina = User.objects.get(username="valentina.decoradora")
    admin_user = User.objects.get(username="admin")

    today = date.today()

    orders_config = [
        # 1. RECIBIDO
        {
            "client_idx": 0,
            "order_number": "DA-2026-00002",
            "prod_code": "OP-2026-00002",
            "stage": KanbanStage.RECIBIDO,
            "cook": cook_sofia,
            "stock_consumed": False,
            "product_code": "PRD-TOR-002",
            "qty": 1,
            "deposit": 16000,
            "order_status": OrderStatus.CONFIRMADO,
            "delivery_type": DeliveryType.RETIRO_TIENDA,
            "days_ahead": 3,
            "hour": time(16, 0),
            "custom": "Dedicatoria: '¡Feliz Cumpleaños Mamá!'",
        },
        # 2. EN PREPARACION
        {
            "client_idx": 1,
            "order_number": "DA-2026-00003",
            "prod_code": "OP-2026-00003",
            "stage": KanbanStage.EN_PREPARACION,
            "cook": cook_rodrigo,
            "stock_consumed": True,
            "product_code": "PRD-PAS-001",
            "qty": 1,
            "deposit": 48000,
            "order_status": OrderStatus.EN_PRODUCCION,
            "delivery_type": DeliveryType.DESPACHO_DOMICILIO,
            "days_ahead": 2,
            "hour": time(14, 30),
            "custom": "Temática Dinosaurios Jurásicos, tonos verdes y dorados",
        },
        # 3. HORNEADO Y DECORADO
        {
            "client_idx": 4,
            "order_number": "DA-2026-00004",
            "prod_code": "OP-2026-00004",
            "stage": KanbanStage.HORNEADO_DECORADO,
            "cook": cook_valentina,
            "stock_consumed": True,
            "product_code": "PRD-TOR-003",
            "qty": 1,
            "deposit": 20000,
            "order_status": OrderStatus.EN_PRODUCCION,
            "delivery_type": DeliveryType.DESPACHO_DOMICILIO,
            "days_ahead": 1,
            "hour": time(11, 0),
            "custom": "Evento de directorio corporativo, logo impreso en oblea",
        },
        # 4. CONTROL DE CALIDAD
        {
            "client_idx": 6,
            "order_number": "DA-2026-00005",
            "prod_code": "OP-2026-00005",
            "stage": KanbanStage.CONTROL_CALIDAD,
            "cook": cook_sofia,
            "stock_consumed": True,
            "product_code": "PRD-TOR-004",
            "qty": 1,
            "deposit": 38000,
            "order_status": OrderStatus.EN_PRODUCCION,
            "delivery_type": DeliveryType.RETIRO_TIENDA,
            "days_ahead": 1,
            "hour": time(17, 45),
            "custom": "Decoración de flores comestibles y mariposas",
        },
        # 5. LISTO PARA DESPACHO
        {
            "client_idx": 5,
            "order_number": "DA-2026-00006",
            "prod_code": "OP-2026-00006",
            "stage": KanbanStage.LISTO,
            "cook": cook_rodrigo,
            "stock_consumed": True,
            "product_code": "PRD-TOR-005",
            "qty": 1,
            "deposit": 42000,
            "order_status": OrderStatus.LISTO,
            "delivery_type": DeliveryType.DESPACHO_DOMICILIO,
            "days_ahead": 0,
            "hour": time(19, 0),
            "custom": "Aniversario de bodas de plata: '25 años juntos'",
        },
    ]

    for cfg in orders_config:
        client = created_clients[cfg["client_idx"]]
        product = products_map[cfg["product_code"]]
        unit_price = product.base_price
        total_amount = unit_price * cfg["qty"]
        deposit = cfg["deposit"]
        balance = total_amount - deposit
        delivery_date = today + timedelta(days=cfg["days_ahead"])

        order, _ = Order.objects.get_or_create(
            order_number=cfg["order_number"],
            defaults={
                "client": client,
                "status": cfg["order_status"],
                "delivery_date": delivery_date,
                "delivery_time": cfg["hour"],
                "delivery_type": cfg["delivery_type"],
                "delivery_address": client.address if cfg["delivery_type"] == DeliveryType.DESPACHO_DOMICILIO else "",
                "total_amount": total_amount,
                "deposit_amount": deposit,
                "balance_due": balance,
                "custom_design_notes": cfg["custom"],
            }
        )
        # Asegurar items
        OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={
                "quantity": cfg["qty"],
                "unit_price": unit_price,
                "subtotal": total_amount,
                "custom_dedication": cfg["custom"],
            }
        )

        # Crear o actualizar ProductionOrder
        prod_order, created_p = ProductionOrder.objects.get_or_create(
            order=order,
            defaults={
                "production_code": cfg["prod_code"],
                "kanban_stage": cfg["stage"],
                "assigned_cook": cfg["cook"],
                "stock_consumed": cfg["stock_consumed"],
                "notes": f"Instrucciones: {cfg['custom']}",
            }
        )
        if not created_p:
            prod_order.kanban_stage = cfg["stage"]
            prod_order.assigned_cook = cfg["cook"]
            prod_order.stock_consumed = cfg["stock_consumed"]
            prod_order.notes = f"Instrucciones: {cfg['custom']}"
            prod_order.save()

        # Si es etapa LISTO, registrar control de calidad aprobado
        if cfg["stage"] == KanbanStage.LISTO:
            QualityCheck.objects.get_or_create(
                production_order=prod_order,
                defaults={
                    "inspected_by": admin_user,
                    "result": QualityResult.APROBADO,
                    "observations": "Estructura, presentación y temperatura certificadas conforme a los estándares de Dulce Arte.",
                }
            )

        # Si es despacho a domicilio, asegurar registro de despacho
        if cfg["delivery_type"] == DeliveryType.DESPACHO_DOMICILIO:
            DispatchOrder.objects.get_or_create(
                order=order,
                defaults={
                    "status": DispatchStatus.PENDIENTE,
                    "stop_order": 1,
                }
            )

        print(f"[Kanban: {prod_order.get_kanban_stage_display()}] Pedido: {order.order_number} ({prod_order.production_code}) - Pastelero: {cfg['cook'].username} - Cliente: {client.name}")

    print("\n=== RESUMEN ===")
    print(f"Total Clientes: {Client.objects.count()}")
    print(f"Total Pedidos: {Order.objects.count()}")
    print(f"Total Órdenes de Producción: {ProductionOrder.objects.count()}")

if __name__ == "__main__":
    seed_clients_and_orders()
