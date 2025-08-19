from django import template

register = template.Library()

@register.filter(name='add_styles')
def add_styles(field, css):
    return field.as_widget(attrs={"class": css})
