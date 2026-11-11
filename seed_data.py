import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from apps.users.models import User, UserRole
from apps.inventory.models import UnitOfMeasure, Supply

def populate():
    print("--- 1. POBLANDO USUARIOS (7 NUEVOS) ---")
    users_data = [
        # Ventas (2)
        {
            "username": "camila.ventas",
            "first_name": "Camila",
            "last_name": "Morales Castro",
            "email": "camila.morales@dulcearte.cl",
            "role": UserRole.VENTAS,
            "identification": "18.345.678-9",
            "phone": "+56987654321",
        },
        {
            "username": "matias.ventas",
            "first_name": "Matías",
            "last_name": "Valenzuela Lagos",
            "email": "matias.valenzuela@dulcearte.cl",
            "role": UserRole.VENTAS,
            "identification": "19.456.789-0",
            "phone": "+56976543210",
        },
        # Cocina / Pastelería (3)
        {
            "username": "sofia.pastelera",
            "first_name": "Sofía",
            "last_name": "Herrera Pinto",
            "email": "sofia.herrera@dulcearte.cl",
            "role": UserRole.COCINA,
            "identification": "17.654.321-K",
            "phone": "+56965432109",
        },
        {
            "username": "rodrigo.chef",
            "first_name": "Rodrigo",
            "last_name": "Araya Fuentes",
            "email": "rodrigo.araya@dulcearte.cl",
            "role": UserRole.COCINA,
            "identification": "16.543.210-4",
            "phone": "+56954321098",
        },
        {
            "username": "valentina.decoradora",
            "first_name": "Valentina",
            "last_name": "Soto Rivas",
            "email": "valentina.soto@dulcearte.cl",
            "role": UserRole.COCINA,
            "identification": "18.987.654-3",
            "phone": "+56943210987",
        },
        # Repartidores / Despacho (2)
        {
            "username": "diego.repartidor",
            "first_name": "Diego",
            "last_name": "Navarro Bravo",
            "email": "diego.navarro@dulcearte.cl",
            "role": UserRole.REPARTIDOR,
            "identification": "19.876.543-2",
            "phone": "+56932109876",
        },
        {
            "username": "felipe.despacho",
            "first_name": "Felipe",
            "last_name": "Castillo Toledo",
            "email": "felipe.castillo@dulcearte.cl",
            "role": UserRole.REPARTIDOR,
            "identification": "17.890.123-5",
            "phone": "+56921098765",
        },
    ]

    default_password = "admin123"

    for u_info in users_data:
        user, created = User.objects.get_or_create(
            username=u_info["username"],
            defaults={
                "first_name": u_info["first_name"],
                "last_name": u_info["last_name"],
                "email": u_info["email"],
                "role": u_info["role"],
                "identification": u_info["identification"],
                "phone": u_info["phone"],
                "is_active": True,
            }
        )
        user.set_password(default_password)
        user.first_name = u_info["first_name"]
        user.last_name = u_info["last_name"]
        user.email = u_info["email"]
        user.role = u_info["role"]
        user.identification = u_info["identification"]
        user.phone = u_info["phone"]
        user.is_active = True
        user.save()
        status = "Creado" if created else "Actualizado"
        print(f"[{status}] Usuario: {user.username} ({user.get_role_display()}) - {user.get_full_name()}")

    print("\n--- 2. POBLANDO INSUMOS (31 INSUMOS COMPLETOS) ---")
    u_kg = UnitOfMeasure.objects.get(code="KG")
    u_lt = UnitOfMeasure.objects.get(code="LT")
    u_und = UnitOfMeasure.objects.get(code="UND")

    supplies_data = [
        # Harinas y polvos base
        {
            "sku": "INS-HAR-001",
            "name": "Harina de Trigo Especial 000",
            "unit": u_kg,
            "current_stock": 120,
            "minimum_stock": 25,
            "cost_per_unit": 1200,
        },
        {
            "sku": "INS-HAR-002",
            "name": "Harina Integral Fina de Grano Entero",
            "unit": u_kg,
            "current_stock": 45,
            "minimum_stock": 10,
            "cost_per_unit": 1550,
        },
        {
            "sku": "INS-HAR-003",
            "name": "Fécula de Maíz (Maicena Extra Fina)",
            "unit": u_kg,
            "current_stock": 30,
            "minimum_stock": 8,
            "cost_per_unit": 2100,
        },
        {
            "sku": "INS-POL-001",
            "name": "Polvo de Hornear Doble Acción",
            "unit": u_kg,
            "current_stock": 15,
            "minimum_stock": 4,
            "cost_per_unit": 3900,
        },
        {
            "sku": "INS-POL-002",
            "name": "Bicarbonato de Sodio Grado Alimentario",
            "unit": u_kg,
            "current_stock": 10,
            "minimum_stock": 3,
            "cost_per_unit": 2400,
        },
        {
            "sku": "INS-POL-003",
            "name": "Levadura Seca Instantánea Panadera",
            "unit": u_kg,
            "current_stock": 8,
            "minimum_stock": 3,
            "cost_per_unit": 6800,
        },

        # Azúcares y endulzantes
        {
            "sku": "INS-AZU-001",
            "name": "Azúcar Blanca Granulada Refinada",
            "unit": u_kg,
            "current_stock": 90,
            "minimum_stock": 20,
            "cost_per_unit": 1100,
        },
        {
            "sku": "INS-AZU-002",
            "name": "Azúcar Flor / Glaseada Repostería",
            "unit": u_kg,
            "current_stock": 50,
            "minimum_stock": 12,
            "cost_per_unit": 1600,
        },
        {
            "sku": "INS-AZU-003",
            "name": "Azúcar Rubio / Mascabado Natural",
            "unit": u_kg,
            "current_stock": 25,
            "minimum_stock": 6,
            "cost_per_unit": 2200,
        },
        {
            "sku": "INS-AZU-004",
            "name": "Miel Pura de Ulmo y Multifloral",
            "unit": u_kg,
            "current_stock": 18,
            "minimum_stock": 5,
            "cost_per_unit": 7500,
        },
        {
            "sku": "INS-AZU-005",
            "name": "Glucosa Líquida en Pasta",
            "unit": u_kg,
            "current_stock": 12,
            "minimum_stock": 4,
            "cost_per_unit": 4300,
        },

        # Lácteos y materias grasas
        {
            "sku": "INS-LAC-001",
            "name": "Mantequilla Sin Sal 82% Materia Grasa",
            "unit": u_kg,
            "current_stock": 60,
            "minimum_stock": 15,
            "cost_per_unit": 7800,
        },
        {
            "sku": "INS-LAC-002",
            "name": "Crema de Leche para Batir 35% MG",
            "unit": u_lt,
            "current_stock": 40,
            "minimum_stock": 10,
            "cost_per_unit": 4200,
        },
        {
            "sku": "INS-LAC-003",
            "name": "Leche Entera Larga Vida UHT",
            "unit": u_lt,
            "current_stock": 55,
            "minimum_stock": 15,
            "cost_per_unit": 1150,
        },
        {
            "sku": "INS-LAC-004",
            "name": "Leche Condensada Tradicional",
            "unit": u_kg,
            "current_stock": 35,
            "minimum_stock": 8,
            "cost_per_unit": 3600,
        },
        {
            "sku": "INS-LAC-005",
            "name": "Queso Crema Tipo Filadelfia Profesional",
            "unit": u_kg,
            "current_stock": 28,
            "minimum_stock": 8,
            "cost_per_unit": 6900,
        },
        {
            "sku": "INS-GRA-001",
            "name": "Aceite Vegetal de Maravilla Puro",
            "unit": u_lt,
            "current_stock": 30,
            "minimum_stock": 8,
            "cost_per_unit": 1950,
        },

        # Chocolates y cacaos
        {
            "sku": "INS-CHO-001",
            "name": "Cobertura de Chocolate Semiamargo 55% Cacao",
            "unit": u_kg,
            "current_stock": 40,
            "minimum_stock": 10,
            "cost_per_unit": 9200,
        },
        {
            "sku": "INS-CHO-002",
            "name": "Chocolate Blanco Puro para Ganache y Relleno",
            "unit": u_kg,
            "current_stock": 25,
            "minimum_stock": 6,
            "cost_per_unit": 9800,
        },
        {
            "sku": "INS-CHO-003",
            "name": "Cacao Amargo Puro en Polvo Alcalinizado",
            "unit": u_kg,
            "current_stock": 20,
            "minimum_stock": 5,
            "cost_per_unit": 8400,
        },
        {
            "sku": "INS-CHO-004",
            "name": "Gotas de Chocolate Termoestables Horneables",
            "unit": u_kg,
            "current_stock": 22,
            "minimum_stock": 5,
            "cost_per_unit": 6500,
        },

        # Rellenos y frutos secos
        {
            "sku": "INS-FRU-001",
            "name": "Manjar Artesanal de Campo para Repostería",
            "unit": u_kg,
            "current_stock": 50,
            "minimum_stock": 12,
            "cost_per_unit": 4100,
        },
        {
            "sku": "INS-FRU-002",
            "name": "Relleno Confitura de Frambuesa Austral",
            "unit": u_kg,
            "current_stock": 30,
            "minimum_stock": 8,
            "cost_per_unit": 4800,
        },
        {
            "sku": "INS-FRU-003",
            "name": "Pulpa de Maracuyá 100% Natural sin Pepas",
            "unit": u_kg,
            "current_stock": 15,
            "minimum_stock": 4,
            "cost_per_unit": 5900,
        },
        {
            "sku": "INS-FRU-004",
            "name": "Nueces Mariposa Seleccionadas Peladas",
            "unit": u_kg,
            "current_stock": 16,
            "minimum_stock": 4,
            "cost_per_unit": 11500,
        },
        {
            "sku": "INS-FRU-005",
            "name": "Almendras Fileteadas Laminadas Naturales",
            "unit": u_kg,
            "current_stock": 14,
            "minimum_stock": 4,
            "cost_per_unit": 12900,
        },

        # Huevos, esencias y aditivos
        {
            "sku": "INS-ADI-001",
            "name": "Huevos de Gallina Libres Extra Grandes",
            "unit": u_und,
            "current_stock": 360,
            "minimum_stock": 60,
            "cost_per_unit": 220,
        },
        {
            "sku": "INS-ADI-002",
            "name": "Extracto Natural de Vainilla Bourbon Madagascar",
            "unit": u_lt,
            "current_stock": 5,
            "minimum_stock": 1,
            "cost_per_unit": 18500,
        },
        {
            "sku": "INS-ADI-003",
            "name": "Pasta Concentrada de Vainilla con Semillas",
            "unit": u_kg,
            "current_stock": 4,
            "minimum_stock": 1,
            "cost_per_unit": 24000,
        },
        {
            "sku": "INS-ADI-004",
            "name": "Sal Fina Marina Yodada Purificada",
            "unit": u_kg,
            "current_stock": 15,
            "minimum_stock": 3,
            "cost_per_unit": 650,
        },
        {
            "sku": "INS-ADI-005",
            "name": "Gelatina Neutra en Polvo 200 Bloom",
            "unit": u_kg,
            "current_stock": 8,
            "minimum_stock": 2,
            "cost_per_unit": 14200,
        },
    ]

    for s_info in supplies_data:
        supply, created = Supply.objects.get_or_create(
            sku=s_info["sku"],
            defaults={
                "name": s_info["name"],
                "unit_of_measure": s_info["unit"],
                "current_stock": s_info["current_stock"],
                "minimum_stock": s_info["minimum_stock"],
                "cost_per_unit": s_info["cost_per_unit"],
                "is_active": True,
            }
        )
        if not created:
            supply.name = s_info["name"]
            supply.unit_of_measure = s_info["unit"]
            supply.current_stock = s_info["current_stock"]
            supply.minimum_stock = s_info["minimum_stock"]
            supply.cost_per_unit = s_info["cost_per_unit"]
            supply.is_active = True
            supply.save()
        status = "Creado" if created else "Actualizado"
        print(f"[{status}] Insumo: [{supply.sku}] {supply.name} - Stock: {supply.current_stock} {supply.unit_of_measure.code} - Costo: ${supply.cost_per_unit}")

    print("\n--- RESUMEN FINAL ---")
    print(f"Total Usuarios en BD: {User.objects.count()}")
    print(f"Total Insumos en BD: {Supply.objects.count()}")

if __name__ == "__main__":
    populate()
