from django.db import models



class Slider(models.Model):

    titulo = models.CharField(
        max_length=200
    )


    descripcion = models.TextField(
        blank=True
    )


    imagen = models.ImageField(
        upload_to="slider/"
    )


    activo = models.BooleanField(
        default=True
    )


    orden = models.PositiveIntegerField(
        default=1
    )


    class Meta:

        ordering = [
            "orden"
        ]


    def __str__(self):

        return self.titulo




class Servicio(models.Model):


    nombre = models.CharField(
        max_length=100
    )


    descripcion = models.TextField()


    icono = models.CharField(
        max_length=100,
        blank=True
    )


    imagen = models.ImageField(
        upload_to="servicios/",
        blank=True,
        null=True
    )


    activo = models.BooleanField(
        default=True
    )


    def __str__(self):

        return self.nombre





class Testimonio(models.Model):


    nombre = models.CharField(
        max_length=100
    )


    comentario = models.TextField()


    foto = models.ImageField(
        upload_to="testimonios/",
        blank=True,
        null=True
    )


    activo = models.BooleanField(
        default=True
    )


    def __str__(self):

        return self.nombre