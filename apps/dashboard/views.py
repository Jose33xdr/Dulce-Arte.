"""
Vistas web del Dashboard administrativo de Dulce Arte.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.clients.models import Client
from apps.dispatch.models import DeliveryRoute, DispatchOrder
from apps.inventory.models import StockMovement, Supply
from apps.orders.models import Order
from apps.production.models import KanbanStage, ProductionOrder
from apps.recipes.models import Product, Recipe
from apps.users.models import User, UserRole

from .services import DashboardService


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    """Vista principal del panel administrativo con indicadores ejecutivos."""
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Panel de Control"
        context["metrics"] = DashboardService.get_operational_metrics()
        return context


class OperationsView(LoginRequiredMixin, TemplateView):
    """Pantallas web operativas para los módulos de Dulce Arte."""

    template_name = "dashboard/module.html"
    module = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["module"] = self.module
        return context


class ClientsView(OperationsView):
    module = "clients"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Clientes",
            "clients": Client.objects.order_by("name"),
        })
        return context


class OrdersView(OperationsView):
    module = "orders"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Pedidos y cotizaciones",
            "orders": Order.objects.select_related("client").prefetch_related("items").order_by("-delivery_date", "-delivery_time"),
        })
        return context


class InventoryView(OperationsView):
    module = "inventory"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Inventario de insumos",
            "supplies": Supply.objects.select_related("unit_of_measure").order_by("name"),
            "movements": StockMovement.objects.select_related("supply", "user")[:8],
        })
        return context


class RecipesView(OperationsView):
    module = "recipes"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Recetas y BOM",
            "products": Product.objects.prefetch_related(
                "recipe__ingredients__supply",
                "recipe__ingredients__unit",
            ).order_by("category", "name"),
            "recipes": Recipe.objects.select_related("product").prefetch_related(
                "ingredients__supply",
                "ingredients__unit",
            ),
        })
        return context


class ProductionView(OperationsView):
    module = "production"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = ProductionOrder.objects.select_related(
            "order__client",
            "assigned_cook",
            "quality_check",
        ).order_by("-created_at")
        context.update({
            "page_title": "Producción Kanban",
            "stages": [
                (code, label, [item for item in orders if item.kanban_stage == code])
                for code, label in KanbanStage.choices
            ],
            "cooks": User.objects.filter(role=UserRole.COCINA, is_active=True).order_by("username"),
        })
        return context


class DispatchView(OperationsView):
    module = "dispatch"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Despachos y rutas",
            "routes": DeliveryRoute.objects.select_related("assigned_driver").prefetch_related("dispatches").order_by("-scheduled_date"),
            "dispatches": DispatchOrder.objects.select_related("order__client", "route", "assigned_driver").order_by("-created_at")[:15],
        })
        return context
