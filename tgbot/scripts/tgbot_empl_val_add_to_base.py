from tgbot.models import EmployeeValues 

def run():
    vals = ['Безумие', 'Отвага']

    for val in vals:
        g, create = EmployeeValues.objects.get_or_create(title=val)
        if create:
            g.is_base = True
            g.save()
