import re

from django.core.exceptions import ValidationError


def normalizar_telefono_ecuador(valor):
    telefono = re.sub(r"[\s\-()]", "", (valor or "").strip())
    if telefono.startswith("0") and len(telefono) == 10:
        telefono = "+593" + telefono[1:]
    elif telefono.startswith("593"):
        telefono = "+" + telefono
    if not re.fullmatch(r"\+593\d{9}", telefono):
        raise ValidationError("Ingresa un número válido de Ecuador, por ejemplo +593987654321.")
    return telefono


def validar_cedula_ecuatoriana(valor):
    cedula = re.sub(r"\D", "", (valor or "").strip())
    if len(cedula) != 10:
        raise ValidationError("La cédula debe contener 10 dígitos.")
    return cedula
