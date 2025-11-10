from django.core.exceptions import ValidationError
import re

def validate_password_complexity(value):
    """
    Valida se a senha tem no mínimo 8 caracteres,
    pelo menos uma letra maiúscula e pelo menos um número.
    """
    # 1. Checa o comprimento mínimo
    if len(value) < 8:
        raise ValidationError(
            'A senha deve ter no mínimo 8 caracteres.',
            code='password_too_short'
        )

    # 2. Checa se contém letra maiúscula
    # O modificador r'[A-Z]' verifica se há pelo menos uma letra maiúscula.
    if not re.search(r'[A-Z]', value):
        raise ValidationError(
            'A senha deve conter pelo menos uma letra maiúscula.',
            code='password_no_uppercase'
        )

    # 3. Checa se contém número
    # O modificador r'\d' verifica se há pelo menos um dígito (número).
    if not re.search(r'\d', value):
        raise ValidationError(
            'A senha deve conter pelo menos um número.',
            code='password_no_number'
        )
