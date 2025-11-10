from django.contrib.auth.decorators import user_passes_test

def is_nutricionista(user):
    return user.tipo == 'NUTRI'

@user_passes_test(is_nutricionista)
def dashboard_nutricionista(request):
    ...
