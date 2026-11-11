"""Vistas de gestión y acciones del ciclo operativo."""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Max
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from apps.clients.models import Client
from apps.core.exceptions import BusinessLogicException, InvalidStateTransitionException
from apps.dispatch.models import (
    DeliveryRoute,
    DispatchOrder,
    DispatchStatus,
    RouteStatus,
)
from apps.dispatch.services import DispatchService
from apps.inventory.models import Supply, UnitOfMeasure
from apps.inventory.services import InventoryService
from apps.orders.models import Order, OrderStatus
from apps.orders.services import OrderService
from apps.production.models import ProductionOrder
from apps.production.services import ProductionService
from apps.recipes.models import Product, Recipe
from apps.users.models import UserRole
from apps.users.permissions import RoleRequiredMixin

from .management_forms import (
    AssignDispatchForm,
    ClientForm,
    DeliveryProofForm,
    DeliveryRouteForm,
    OrderCancelForm,
    OrderConfirmationForm,
    OrderForm,
    OrderItemFormSet,
    ProductForm,
    ProductionTransitionForm,
    QualityCheckForm,
    RecipeForm,
    RecipeIngredientFormSet,
    RouteCancelForm,
    StockEntryForm,
    StockWasteForm,
    SupplyForm,
    UnitOfMeasureForm,
)


class SalesManagementMixin(RoleRequiredMixin, LoginRequiredMixin):
    allowed_roles = [UserRole.VENTAS]


class InventoryManagementMixin(RoleRequiredMixin, LoginRequiredMixin):
    allowed_roles = [UserRole.COCINA]


class KitchenManagementMixin(RoleRequiredMixin, LoginRequiredMixin):
    allowed_roles = [UserRole.COCINA]


class DeliveryManagementMixin(RoleRequiredMixin, LoginRequiredMixin):
    allowed_roles = [UserRole.REPARTIDOR]


class AdminManagementMixin(RoleRequiredMixin, LoginRequiredMixin):
    allowed_roles = []


class UnitOfMeasureListView(AdminManagementMixin, ListView):
    model = UnitOfMeasure
    template_name = "dashboard/units.html"
    context_object_name = "units"
    ordering = ("magnitude", "code")


class UnitOfMeasureCreateView(AdminManagementMixin, CreateView):
    model = UnitOfMeasure
    form_class = UnitOfMeasureForm
    template_name = "dashboard/management_form.html"
    success_url = reverse_lazy("dashboard:units")
    extra_context = {"page_title": "Nueva unidad de medida", "module": "inventory"}


class UnitOfMeasureUpdateView(AdminManagementMixin, UpdateView):
    model = UnitOfMeasure
    form_class = UnitOfMeasureForm
    template_name = "dashboard/management_form.html"
    success_url = reverse_lazy("dashboard:units")
    extra_context = {"page_title": "Editar unidad de medida", "module": "inventory"}


class ClientCreateView(SalesManagementMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "dashboard/management_form.html"
    success_url = reverse_lazy("dashboard:clients")
    extra_context = {"page_title": "Nuevo cliente", "module": "clients"}

    def form_valid(self, form):
        messages.success(self.request, "El cliente se creó correctamente.")
        return super().form_valid(form)


class ClientUpdateView(SalesManagementMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "dashboard/management_form.html"
    success_url = reverse_lazy("dashboard:clients")
    extra_context = {"page_title": "Editar cliente", "module": "clients"}

    def form_valid(self, form):
        messages.success(self.request, "Los datos del cliente se actualizaron.")
        return super().form_valid(form)


class ClientDeactivateView(SalesManagementMixin, View):
    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        client.soft_delete()
        messages.success(request, "El cliente se desactivó sin borrar su historial.")
        return redirect("dashboard:clients")


class ClientRestoreView(SalesManagementMixin, View):
    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        client.restore()
        messages.success(request, "El cliente se reactivó.")
        return redirect("dashboard:clients")


class OrderCreateView(SalesManagementMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "dashboard/order_form.html"
    success_url = reverse_lazy("dashboard:orders")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "item_formset" not in context:
            context["item_formset"] = OrderItemFormSet(instance=self.object, prefix="items")
        context.update({"page_title": "Nuevo pedido o cotización", "module": "orders"})
        return context

    def form_valid(self, form):
        item_formset = OrderItemFormSet(self.request.POST, prefix="items")
        if not item_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, item_formset=item_formset)
            )

        items_data = []
        for item_form in item_formset:
            data = item_form.cleaned_data
            if not data or data.get("DELETE"):
                continue
            items_data.append({
                key: data.get(key, "")
                for key in (
                    "product",
                    "quantity",
                    "unit_price",
                    "cake_size",
                    "flavor_sponge",
                    "flavor_filling",
                    "flavor_cover",
                    "custom_dedication",
                    "customizations",
                )
            })

        try:
            with transaction.atomic():
                order = OrderService.create_order(
                    client=form.cleaned_data["client"],
                    delivery_date=form.cleaned_data["delivery_date"],
                    delivery_time=form.cleaned_data["delivery_time"],
                    items_data=items_data,
                    delivery_type=form.cleaned_data["delivery_type"],
                    delivery_address=form.cleaned_data["delivery_address"],
                    deposit_amount=form.cleaned_data["deposit_amount"],
                    custom_design_notes=form.cleaned_data["custom_design_notes"],
                    user=self.request.user,
                )
                if form.cleaned_data.get("reference_image"):
                    order.reference_image = form.cleaned_data["reference_image"]
                    order.save(update_fields=["reference_image", "updated_at"])
        except (BusinessLogicException, ValueError) as exc:
            form.add_error(None, str(exc))
            return self.render_to_response(
                self.get_context_data(form=form, item_formset=item_formset)
            )

        messages.success(self.request, f"El pedido {order.order_number} se registró correctamente.")
        return HttpResponseRedirect(self.get_success_url())


class OrderUpdateView(SalesManagementMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "dashboard/order_form.html"
    success_url = reverse_lazy("dashboard:orders")

    def get_queryset(self):
        return Order.objects.filter(status=OrderStatus.COTIZACION).select_related("client")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "item_formset" not in context:
            context["item_formset"] = OrderItemFormSet(instance=self.object, prefix="items")
        context.update({"page_title": f"Editar cotización {self.object.order_number}", "module": "orders"})
        return context

    def form_valid(self, form):
        item_formset = OrderItemFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object,
            prefix="items",
        )
        if not item_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, item_formset=item_formset)
            )

        total = sum(
            (
                int(data["quantity"]) * int(data["unit_price"])
                for data in item_formset.cleaned_data
                if data and not data.get("DELETE")
            ),
            0,
        )
        if form.cleaned_data["deposit_amount"] > total:
            form.add_error("deposit_amount", "El abono no puede superar el total de los productos.")
            return self.render_to_response(
                self.get_context_data(form=form, item_formset=item_formset)
            )

        try:
            with transaction.atomic():
                order = form.save(commit=False)
                order.total_amount = total
                order.balance_due = total - order.deposit_amount
                order.full_clean()
                order.save()
                item_formset.save()
        except (ValueError, ProtectedError) as exc:
            form.add_error(None, str(exc))
            return self.render_to_response(
                self.get_context_data(form=form, item_formset=item_formset)
            )

        messages.success(self.request, "La cotización se actualizó correctamente.")
        return HttpResponseRedirect(self.get_success_url())


class OrderCancelView(SalesManagementMixin, FormView):
    form_class = OrderCancelForm
    template_name = "dashboard/confirm_action.html"
    extra_context = {"page_title": "Cancelar pedido", "submit_label": "Cancelar pedido"}

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["description"] = f"Se cancelará el pedido {self.order.order_number} y se registrará el motivo en su historial."
        context["cancel_url"] = reverse("dashboard:orders")
        return context

    def form_valid(self, form):
        try:
            OrderService.cancel_order(
                self.order,
                user=self.request.user,
                reason=form.cleaned_data["reason"],
            )
        except (BusinessLogicException, InvalidStateTransitionException) as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, f"El pedido {self.order.order_number} fue cancelado.")
        return redirect("dashboard:orders")


class OrderConfirmView(SalesManagementMixin, FormView):
    form_class = OrderConfirmationForm
    template_name = "dashboard/confirm_action.html"
    extra_context = {"page_title": "Confirmar cotización", "submit_label": "Confirmar pedido"}

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["total_amount"] = self.order.total_amount
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "description": f"Confirmar {self.order.order_number} por ${self.order.total_amount}. Esta acción crea automáticamente la orden de producción y, si corresponde, el despacho.",
            "cancel_url": reverse("dashboard:orders"),
        })
        return context

    def form_valid(self, form):
        try:
            OrderService.confirm_order(
                self.order,
                deposit_amount=form.cleaned_data.get("deposit_amount"),
                user=self.request.user,
            )
        except (BusinessLogicException, InvalidStateTransitionException) as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, f"El pedido {self.order.order_number} fue confirmado.")
        return redirect("dashboard:orders")


class SupplyCreateView(AdminManagementMixin, CreateView):
    model = Supply
    form_class = SupplyForm
    template_name = "dashboard/supply_form.html"
    success_url = reverse_lazy("dashboard:inventory")
    extra_context = {"page_title": "Nuevo insumo", "module": "inventory", "cancel_url": reverse_lazy("dashboard:inventory")}

    def form_valid(self, form):
        messages.success(self.request, "El insumo se registró con stock inicial cero. Registra una entrada para cargar existencias.")
        return super().form_valid(form)


class SupplyUpdateView(AdminManagementMixin, UpdateView):
    model = Supply
    form_class = SupplyForm
    template_name = "dashboard/supply_form.html"
    success_url = reverse_lazy("dashboard:inventory")
    extra_context = {"page_title": "Editar insumo", "module": "inventory", "cancel_url": reverse_lazy("dashboard:inventory")}

    def form_valid(self, form):
        messages.success(self.request, "Los datos del insumo se actualizaron.")
        return super().form_valid(form)


class SupplyDeactivateView(InventoryManagementMixin, View):
    def post(self, request, pk):
        supply = get_object_or_404(Supply, pk=pk)
        supply.soft_delete()
        messages.success(request, "El insumo se desactivó y su historial de movimientos se conservó.")
        return redirect("dashboard:inventory")


class StockMovementCreateView(AdminManagementMixin, FormView):
    form_class = StockEntryForm
    template_name = "dashboard/management_form.html"
    extra_context = {"page_title": "Registrar entrada de stock", "module": "inventory"}

    def dispatch(self, request, *args, **kwargs):
        self.supply = get_object_or_404(Supply, pk=kwargs["pk"], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Entrada de stock: {self.supply.name}"
        context["cancel_url"] = reverse("dashboard:inventory")
        return context

    def form_valid(self, form):
        try:
            InventoryService.register_entry(
                supply=self.supply,
                quantity=form.cleaned_data["quantity"],
                user=self.request.user,
                reference=form.cleaned_data["reference"],
                notes=form.cleaned_data["notes"],
            )
        except BusinessLogicException as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "La entrada se registró y el stock fue actualizado.")
        return redirect("dashboard:inventory")


class StockWasteCreateView(InventoryManagementMixin, FormView):
    form_class = StockWasteForm
    template_name = "dashboard/management_form.html"
    extra_context = {"page_title": "Registrar merma", "module": "inventory"}

    def dispatch(self, request, *args, **kwargs):
        self.supply = get_object_or_404(Supply, pk=kwargs["pk"], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Merma: {self.supply.name}"
        context["cancel_url"] = reverse("dashboard:inventory")
        return context

    def form_valid(self, form):
        try:
            InventoryService.register_waste(
                supply=self.supply,
                quantity=form.cleaned_data["quantity"],
                user=self.request.user,
                reference=form.cleaned_data["reference"],
                notes=form.cleaned_data["notes"],
            )
        except BusinessLogicException as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "La merma se registró en el historial.")
        return redirect("dashboard:inventory")


class ProductCreateView(AdminManagementMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/management_form.html"
    success_url = reverse_lazy("dashboard:recipes")
    extra_context = {"page_title": "Nuevo producto", "module": "recipes"}


class ProductUpdateView(AdminManagementMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/management_form.html"
    success_url = reverse_lazy("dashboard:recipes")
    extra_context = {"page_title": "Editar producto", "module": "recipes"}


class ProductDeactivateView(AdminManagementMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.soft_delete()
        messages.success(request, "El producto se desactivó conservando las recetas e historial.")
        return redirect("dashboard:recipes")


class RecipeCreateView(AdminManagementMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "dashboard/recipe_form.html"
    success_url = reverse_lazy("dashboard:recipes")

    def get_initial(self):
        initial = super().get_initial()
        if self.request.GET.get("product"):
            initial["product"] = self.request.GET["product"]
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "ingredient_formset" not in context:
            context["ingredient_formset"] = RecipeIngredientFormSet(instance=self.object, prefix="ingredients")
        context["page_title"] = "Nueva receta"
        context["cancel_url"] = reverse("dashboard:recipes")
        return context

    def form_valid(self, form):
        formset = RecipeIngredientFormSet(
            self.request.POST,
            instance=form.instance,
            prefix="ingredients",
        )
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, ingredient_formset=formset))
        try:
            with transaction.atomic():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
        except (ValueError, ProtectedError) as exc:
            form.add_error(None, str(exc))
            return self.render_to_response(self.get_context_data(form=form, ingredient_formset=formset))
        messages.success(self.request, "La receta y sus ingredientes se guardaron.")
        return HttpResponseRedirect(self.get_success_url())


class RecipeUpdateView(AdminManagementMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "dashboard/recipe_form.html"
    success_url = reverse_lazy("dashboard:recipes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "ingredient_formset" not in context:
            context["ingredient_formset"] = RecipeIngredientFormSet(
                instance=self.object,
                prefix="ingredients",
            )
        context["page_title"] = f"Editar receta: {self.object.name}"
        context["cancel_url"] = reverse("dashboard:recipes")
        return context

    def form_valid(self, form):
        formset = RecipeIngredientFormSet(
            self.request.POST,
            instance=self.object,
            prefix="ingredients",
        )
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, ingredient_formset=formset))
        try:
            with transaction.atomic():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
        except (ValueError, ProtectedError) as exc:
            form.add_error(None, str(exc))
            return self.render_to_response(self.get_context_data(form=form, ingredient_formset=formset))
        messages.success(self.request, "La receta y sus ingredientes se actualizaron.")
        return HttpResponseRedirect(self.get_success_url())


class RecipeDeactivateView(AdminManagementMixin, View):
    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe.soft_delete()
        messages.success(request, "La receta se desactivó conservando su historial.")
        return redirect("dashboard:recipes")


class ProductionTransitionView(KitchenManagementMixin, FormView):
    form_class = ProductionTransitionForm
    template_name = "dashboard/management_form.html"
    success_url = reverse_lazy("dashboard:production")

    def dispatch(self, request, *args, **kwargs):
        self.production_order = get_object_or_404(
            ProductionOrder.objects.select_related("order"),
            pk=kwargs["pk"],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["production_order"] = self.production_order
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": f"Avanzar {self.production_order.production_code}",
            "module": "production",
            "cancel_url": reverse("dashboard:production"),
        })
        return context

    def form_valid(self, form):
        try:
            ProductionService.transition_stage(
                production_order=self.production_order,
                target_stage=form.cleaned_data["target_stage"],
                user=self.request.user,
                notes=form.cleaned_data["notes"],
            )
        except (BusinessLogicException, InvalidStateTransitionException) as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "La etapa de producción se actualizó.")
        return redirect(self.success_url)


class QualityCheckCreateView(KitchenManagementMixin, FormView):
    form_class = QualityCheckForm
    template_name = "dashboard/management_form.html"
    success_url = reverse_lazy("dashboard:production")

    def dispatch(self, request, *args, **kwargs):
        self.production_order = get_object_or_404(ProductionOrder, pk=kwargs["pk"])
        if self.production_order.kanban_stage != "CONTROL_CALIDAD":
            messages.error(request, "El control solo se registra cuando la orden está en etapa de calidad.")
            return redirect("dashboard:production")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": f"Control de calidad: {self.production_order.production_code}",
            "module": "production",
            "cancel_url": reverse("dashboard:production"),
        })
        return context

    def form_valid(self, form):
        try:
            ProductionService.record_quality_check(
                production_order=self.production_order,
                inspector_user=self.request.user,
                result=form.cleaned_data["result"],
                observations=form.cleaned_data["observations"],
            )
        except (BusinessLogicException, ValueError) as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "El control de calidad se registró.")
        return redirect(self.success_url)


class AssignCookView(AdminManagementMixin, View):
    def post(self, request, pk):
        production_order = get_object_or_404(ProductionOrder, pk=pk)
        cook_id = request.POST.get("cook_id")
        from apps.users.models import User

        cook = get_object_or_404(User, pk=cook_id, role=UserRole.COCINA, is_active=True)
        ProductionService.assign_cook(production_order, cook)
        messages.success(request, f"Se asignó a {cook.get_full_name() or cook.username}.")
        return redirect("dashboard:production")


class DeliveryRouteCreateView(SalesManagementMixin, CreateView):
    form_class = DeliveryRouteForm
    model = DeliveryRoute
    template_name = "dashboard/management_form.html"
    success_url = reverse_lazy("dashboard:dispatch")
    extra_context = {"page_title": "Nueva ruta", "module": "dispatch"}

    def form_valid(self, form):
        self.object = DispatchService.create_route(
            scheduled_date=form.cleaned_data["scheduled_date"],
            driver_user=form.cleaned_data["assigned_driver"],
            notes=form.cleaned_data["notes"],
        )
        messages.success(self.request, f"Se creó la ruta {self.object.code}.")
        return HttpResponseRedirect(self.get_success_url())


class DeliveryRouteUpdateView(SalesManagementMixin, UpdateView):
    model = DeliveryRoute
    form_class = DeliveryRouteForm
    template_name = "dashboard/management_form.html"
    success_url = reverse_lazy("dashboard:dispatch")
    extra_context = {"page_title": "Editar ruta", "module": "dispatch"}

    def get_queryset(self):
        return DeliveryRoute.objects.filter(status=RouteStatus.PROGRAMADA)

    def form_valid(self, form):
        messages.success(self.request, "La ruta se actualizó.")
        return super().form_valid(form)


class DeliveryRouteDetailView(SalesManagementMixin, DetailView):
    model = DeliveryRoute
    template_name = "dashboard/route_detail.html"
    context_object_name = "route"

    def get_queryset(self):
        return DeliveryRoute.objects.select_related("assigned_driver").prefetch_related(
            "dispatches__order__client",
            "dispatches__proof",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assign_form"] = AssignDispatchForm(route=self.object)
        context["cancel_form"] = RouteCancelForm()
        context["cancel_url"] = reverse("dashboard:dispatch")
        return context


class DeliveryRouteAssignView(SalesManagementMixin, FormView):
    form_class = AssignDispatchForm
    template_name = "dashboard/assign_dispatch.html"

    def dispatch(self, request, *args, **kwargs):
        self.route = get_object_or_404(DeliveryRoute, pk=kwargs["pk"], status=RouteStatus.PROGRAMADA)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["route"] = self.route
        return kwargs

    def get_success_url(self):
        return reverse("dashboard:route_detail", args=[self.route.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get("form") or self.get_form()
        context.update({
            "page_title": f"Asignar despachos a {self.route.code}",
            "route": self.route,
            "module": "dispatch",
            "cancel_url": self.get_success_url(),
            "pending_dispatches": form.fields["dispatches"].queryset,
        })
        return context

    def form_valid(self, form):
        selected = form.cleaned_data["dispatches"]
        current_max = self.route.dispatches.aggregate(value=Max("stop_order"))["value"] or 0
        stops = [
            {"dispatch_id": dispatch.pk, "stop_order": current_max + index}
            for index, dispatch in enumerate(selected, start=1)
        ]
        try:
            DispatchService.assign_dispatches_to_route(self.route, stops)
        except BusinessLogicException as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, f"Se asignaron {len(stops)} parada(s) a la ruta.")
        return redirect(self.get_success_url())


class DeliveryRouteStartView(SalesManagementMixin, View):
    def post(self, request, pk):
        route = get_object_or_404(DeliveryRoute, pk=pk)
        try:
            DispatchService.start_route(route, user=request.user)
        except BusinessLogicException as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "La ruta comenzó y sus pedidos pasaron a despacho.")
        return redirect("dashboard:route_detail", pk=route.pk)


class DeliveryRouteCancelView(SalesManagementMixin, FormView):
    form_class = RouteCancelForm
    template_name = "dashboard/confirm_action.html"

    def dispatch(self, request, *args, **kwargs):
        self.route = get_object_or_404(DeliveryRoute, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("dashboard:dispatch")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": "Cancelar ruta",
            "submit_label": "Cancelar ruta",
            "description": f"Se cancelará la ruta {self.route.code}. Sus despachos volverán a quedar sin ruta.",
            "cancel_url": reverse("dashboard:route_detail", args=[self.route.pk]),
        })
        return context

    def form_valid(self, form):
        if self.route.status != RouteStatus.PROGRAMADA:
            form.add_error(None, "Solo se pueden cancelar rutas programadas.")
            return self.form_invalid(form)
        if self.route.dispatches.filter(status=DispatchStatus.ENTREGADO).exists():
            form.add_error(None, "No se puede cancelar una ruta que ya contiene entregas certificadas.")
            return self.form_invalid(form)
        with transaction.atomic():
            self.route.dispatches.update(route=None, stop_order=1)
            self.route.status = RouteStatus.CANCELADA
            self.route.save(update_fields=["status", "updated_at"])
        messages.success(self.request, "La ruta se canceló y sus despachos quedaron disponibles.")
        return redirect(self.get_success_url())


class DispatchConfirmView(DeliveryManagementMixin, FormView):
    form_class = DeliveryProofForm
    template_name = "dashboard/management_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.dispatch_order = get_object_or_404(
            DispatchOrder.objects.select_related("order", "assigned_driver"),
            pk=kwargs["pk"],
        )
        if not request.user.is_admin and self.dispatch_order.assigned_driver_id != request.user.pk:
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("dashboard:dispatch")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_title": f"Certificar entrega {self.dispatch_order.order.order_number}",
            "module": "dispatch",
            "cancel_url": self.get_success_url(),
        })
        return context

    def form_valid(self, form):
        try:
            DispatchService.confirm_delivery(
                dispatch_order=self.dispatch_order,
                recipient_name=form.cleaned_data["recipient_name"],
                recipient_id=form.cleaned_data["recipient_id"],
                signature_data=form.cleaned_data["signature_data"],
                proof_photo=form.cleaned_data.get("proof_photo"),
                user=self.request.user,
            )
        except (BusinessLogicException, ValueError) as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "La entrega quedó certificada.")
        return redirect(self.get_success_url())
