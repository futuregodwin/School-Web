from django import template

register = template.Library()

@register.filter(name='add_style')
def add_style(field, css):
    return field.as_widget(attrs={"class": css})
