from django.db import migrations

ESPECIALIDADES = (
    ("Cardiología", "Prevención, diagnóstico y tratamiento de enfermedades del corazón y la circulación, con seguimiento personalizado."),
    ("Neurología", "Evaluación de migrañas, trastornos del sueño, memoria y afecciones del cerebro y los nervios periféricos."),
    ("Odontología", "Prevención, higiene, restauración y estética dental para conservar una sonrisa sana en todas las edades."),
    ("Pediatría", "Control de crecimiento, vacunación, prevención y tratamiento de enfermedades durante la infancia y adolescencia."),
    ("Ginecología", "Controles preventivos, salud reproductiva, planificación y acompañamiento integral en cada etapa de la mujer."),
    ("Traumatología", "Diagnóstico y recuperación de lesiones en huesos, músculos y articulaciones para recuperar la movilidad."),
    ("Oftalmología", "Exámenes visuales, detección temprana y tratamiento de alteraciones que afectan los ojos y la visión."),
    ("Neumología", "Atención de asma, alergias respiratorias y enfermedades pulmonares con seguimiento especializado."),
    ("Dermatología", "Diagnóstico y tratamiento de afecciones de la piel, el cabello y las uñas, con orientación preventiva."),
)

def crear_especialidades(apps, schema_editor):
    Especialidad = apps.get_model("especialidades", "Especialidad")
    for nombre, descripcion in ESPECIALIDADES:
        Especialidad.objects.update_or_create(nombre=nombre, defaults={"descripcion": descripcion, "activo": True})

def eliminar_especialidades_iniciales(apps, schema_editor):
    Especialidad = apps.get_model("especialidades", "Especialidad")
    Especialidad.objects.filter(nombre__in=[item[0] for item in ESPECIALIDADES]).delete()

class Migration(migrations.Migration):
    dependencies = [("especialidades", "0001_initial")]
    operations = [migrations.RunPython(crear_especialidades, eliminar_especialidades_iniciales)]
