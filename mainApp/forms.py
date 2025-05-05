from django import forms
from django.forms.widgets import ClearableFileInput


class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True


class ImageForm(forms.Form):
    images = forms.ImageField(
        label="Загрузите изображение",
        widget=MultiFileInput(attrs={'multiple': True})
    )


class CompressionForm(forms.Form):
    image_name = forms.CharField(widget=forms.HiddenInput())
    compression_val = forms.IntegerField(
        label='Уровень сжатия',
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(
            attrs={
                'id': 'compression-value',
                'step': 1,

            }
        )
    )
    compression_slider = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "type": "range",
                "id": "compression-slider",
                "step": 1,
                "min": 20,
                "max": 100,
            }
        )
    )

    def clean(self):
        cleaned = super().clean()
        val_num = cleaned.get('compression_value')
        val_slider = cleaned.get('compression_slider')
        if val_slider is not None and val_num is None:
            cleaned['compression_value'] = val_slider
        level = cleaned.get('compression_value')
        if level is None:
            raise forms.ValidationError('Укажите уровень сжатия')
        if not (20 <= level <= 100):
            raise forms.ValidationError('Диапазон сжатия должен быть от 20 до 100')
        return cleaned


