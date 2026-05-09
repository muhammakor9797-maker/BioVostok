from django import forms
from .models import Order, ShippingMethod


class OrderCreateForm(forms.ModelForm):
    shipping_method = forms.ModelChoiceField(
        queryset=ShippingMethod.objects.filter(active=True),
        widget=forms.RadioSelect(),
        label='Способ доставки'
    )

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 
                  'country', 'city', 'address', 'postal_code', 'shipping_method']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ❗ УДАЛЯЕМ SELECT И ДЕЛАЕМ ОБЫЧНОЕ ПОЛЕ ВВОДА ДЛЯ СТРАНЫ
        self.fields['country'].widget = forms.TextInput()
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
