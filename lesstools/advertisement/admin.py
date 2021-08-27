from django.contrib import admin
from lesstools.advertisement.models import ADV
from django import forms


class ADVForm(forms.ModelForm):
    class Meta:
        models = ADV
        fields = '__all__'

    def clean(self):
        adv_count = ADV.objects.all()
        old_position = self.initial.get('position') if self.initial else None
        selected_position = self.cleaned_data.get('position')
        if (len(adv_count.filter(position=ADV.TOP)) >= 1 and selected_position == ADV.TOP and old_position != ADV.TOP) \
                or (len(adv_count.filter(position=ADV.MID)) >= 3 and selected_position == ADV.MID
                    and old_position != ADV.MID) \
                or (len(adv_count.filter(position=ADV.BOT)) >= 3 and selected_position == ADV.BOT
                    and old_position != ADV.BOT):
            raise forms.ValidationError(f'Limit of advertisements for {selected_position} is exceeded')

        return self.cleaned_data


class ADVAdmin(admin.ModelAdmin):
    list_display = ('name', 'sub_name', 'position')
    fields = [('name', 'sub_name'), 'icon', 'description', 'position']
    readonly_fields = ('hash',)
    form = ADVForm


admin.site.register(ADV, ADVAdmin)
