"""Formularios de gestión para las vistas operativas del dashboard."""

from decimal import Decimal

from django import forms
from django.forms import inlineformset_factory

from apps.clients.models import Client
from apps.dispatch.models import DeliveryProof, DeliveryRoute, DispatchOrder
from apps.inventory.models import Supply, UnitOfMeasure
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.production.models import KanbanStage, QualityResult
from apps.recipes.models import Product, Recipe, RecipeIngredient
from apps.users.models import User, UserRole


FIELD_CLASS = (
    "mt-1 block w-full rounded-xl border border-stone-300 bg-white px-3 py-2 "
    "text-sm text-stone-900 shadow-sm focus:border-[#773344] focus:outline-none "
    "focus:ring-2 focus:ring-[#773344]/20"
)

CHECKBOX_CLASS = (
    "h-4 w-4 rounded border-stone-300 text-[#773344] "
    "focus:ring-2 focus:ring-[#773344]/20"
)


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = CHECKBOX_CLASS
            elif not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs["class"] = FIELD_CLASS


class ClientForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ("identification", "name", "email", "phone", "address", "notes")


class OrderForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "client",
            "delivery_date",
            "delivery_time",
            "delivery_type",
            "delivery_address",
            "deposit_amount",
            "custom_design_notes",
            "reference_image",
        )
        widgets = {
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
            "delivery_time": forms.TimeInput(attrs={"type": "time"}),
            "custom_design_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.filter(is_active=True).order_by("name")

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("delivery_type") == "DESPACHO_DOMICILIO"
            and not cleaned_data.get("delivery_address")
            and cleaned_data.get("client")
            and cleaned_data["client"].address
        ):
            cleaned_data["delivery_address"] = cleaned_data["client"].address
            self.instance.delivery_address = cleaned_data["delivery_address"]
        return cleaned_data

    def _post_clean(self):
        if self.instance.pk and self.instance.status == OrderStatus.COTIZACION:
            total, balance = self.instance.total_amount, self.instance.balance_due
            self.instance.total_amount = 999999999
            try:
                super()._post_clean()
            finally:
                self.instance.total_amount = total
                self.instance.balance_due = balance
            return
        super()._post_clean()


class OrderItemForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = (
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True).order_by("name")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("product") and cleaned_data.get("quantity") and cleaned_data.get("unit_price") is not None:
            self.instance.subtotal = int(cleaned_data["quantity"]) * int(cleaned_data["unit_price"])
        return cleaned_data


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class SupplyForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Supply
        fields = ("sku", "name", "unit_of_measure", "minimum_stock", "cost_per_unit", "is_active")
        widgets = {
            "minimum_stock": forms.NumberInput(attrs={"min": 0, "step": 1}),
            "cost_per_unit": forms.NumberInput(attrs={"min": 0, "step": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["unit_of_measure"].queryset = UnitOfMeasure.objects.filter(is_active=True)


class StockEntryForm(StyledFormMixin, forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={"min": 1, "step": 1}),
    )
    reference = forms.CharField(
        max_length=100,
        required=False,
        label="Referencia / N° Documento",
    )
    notes = forms.CharField(
        required=False,
        label="Observaciones / Justificación",
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class StockWasteForm(StockEntryForm):
    pass


class UnitOfMeasureForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = UnitOfMeasure
        fields = ("code", "name", "magnitude", "conversion_factor", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["code"].disabled = True


class ProductForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "code",
            "name",
            "category",
            "base_price",
            "estimated_production_minutes",
            "description",
            "is_active",
        )
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class RecipeForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ("product", "name", "yield_portions", "instructions", "is_active")
        widgets = {"instructions": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True).order_by("name")

class RecipeIngredientForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ("supply", "quantity_required", "unit", "waste_percentage")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supply"].queryset = Supply.objects.filter(is_active=True).select_related("unit_of_measure")
        self.fields["unit"].queryset = UnitOfMeasure.objects.filter(is_active=True)


RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=1,
    can_delete=True,
)


class DeliveryRouteForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DeliveryRoute
        fields = ("assigned_driver", "scheduled_date", "notes")
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_driver"].queryset = User.objects.filter(
            role=UserRole.REPARTIDOR,
            is_active=True,
        ).order_by("username")
        self.fields["assigned_driver"].required = False


class AssignDispatchForm(StyledFormMixin, forms.Form):
    dispatches = forms.ModelMultipleChoiceField(
        queryset=DispatchOrder.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Despachos pendientes",
    )

    def __init__(self, *args, route, **kwargs):
        super().__init__(*args, **kwargs)
        self.route = route
        self.fields["dispatches"].queryset = DispatchOrder.objects.filter(
            route__isnull=True,
            status="PENDIENTE",
            order__delivery_type="DESPACHO_DOMICILIO",
        ).select_related("order__client").order_by("order__delivery_date")


class ProductionTransitionForm(StyledFormMixin, forms.Form):
    target_stage = forms.ChoiceField(choices=KanbanStage.choices)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def __init__(self, *args, production_order, **kwargs):
        super().__init__(*args, **kwargs)
        allowed = {
            "RECIBIDO": "EN_PREPARACION",
            "EN_PREPARACION": "HORNEADO_DECORADO",
            "HORNEADO_DECORADO": "CONTROL_CALIDAD",
            "CONTROL_CALIDAD": "LISTO",
        }
        next_stage = allowed.get(production_order.kanban_stage)
        self.fields["target_stage"].choices = [
            (value, label) for value, label in KanbanStage.choices if value == next_stage
        ]
        if next_stage:
            self.fields["target_stage"].initial = next_stage


class QualityCheckForm(StyledFormMixin, forms.Form):
    result = forms.ChoiceField(choices=QualityResult.choices)
    observations = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))


class DeliveryProofForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DeliveryProof
        fields = ("recipient_name", "recipient_id", "signature_data", "proof_photo")
        widgets = {
            "signature_data": forms.Textarea(attrs={"rows": 5, "placeholder": "Pega los datos de la firma capturada"}),
        }

    def clean_signature_data(self):
        signature = self.cleaned_data["signature_data"].strip()
        if not signature:
            raise forms.ValidationError("Se requiere la firma digital del receptor.")
        return signature

    def clean_recipient_name(self):
        name = self.cleaned_data["recipient_name"].strip()
        if not name:
            raise forms.ValidationError("Ingresa el nombre de quien recibe el pedido.")
        return name


class OrderCancelForm(StyledFormMixin, forms.Form):
    reason = forms.CharField(
        label="Motivo de cancelación",
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class OrderConfirmationForm(StyledFormMixin, forms.Form):
    deposit_amount = forms.IntegerField(
        label="Abono ($)",
        required=False,
        min_value=0,
    )

    def __init__(self, *args, total_amount, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_amount = total_amount
        self.fields["deposit_amount"].max_value = total_amount

    def clean_deposit_amount(self):
        amount = self.cleaned_data.get("deposit_amount")
        if amount is not None and amount > self.total_amount:
            raise forms.ValidationError("El abono no puede superar el total del pedido.")
        return amount


class RouteCancelForm(StyledFormMixin, forms.Form):
    confirm = forms.BooleanField(label="Confirmo cancelar esta ruta")
