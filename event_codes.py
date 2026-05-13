import secrets

CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def generate_code(prefix, length=6):
    """Return a short invitation code with a fixed prefix and readable characters."""
    return f"{prefix}-" + ''.join(secrets.choice(CODE_ALPHABET) for _ in range(length))


def generate_unique_code(model, field_name, prefix, length=6):
    """Generate a unique code for a Django model field."""
    for _ in range(100):
        code = generate_code(prefix, length)
        if not model.objects.filter(**{field_name: code}).exists():
            return code
    raise RuntimeError(f'Could not generate a unique {field_name}.')