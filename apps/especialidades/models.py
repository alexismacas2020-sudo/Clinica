from django.db import models



class Especialidad(models.Model):

    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre"
    )


    descripcion = models.TextField(
        verbose_name="Descripción",
        blank=True
    )


    imagen = models.ImageField(
        upload_to="especialidades/",
        blank=True,
        null=True,
        verbose_name="Imagen"
    )


    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )


    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )



    class Meta:

        verbose_name = "Especialidad"

        verbose_name_plural = "Especialidades"

        ordering = [
            "nombre"
        ]



    def __str__(self):

        return self.nombre