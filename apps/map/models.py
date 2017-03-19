from django.db import models


class District(models.Model):
    name = models.CharField(max_length=10, verbose_name='Наименование')

    class Meta:
        verbose_name = 'Округ'
        verbose_name_plural = 'Округа'

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование')
    district = models.ForeignKey(District,
                                 on_delete=models.PROTECT,
                                 related_name='regions')

    class Meta:
        verbose_name = 'Район'
        verbose_name_plural = 'Районы'
        ordering = ('name', )

    def __str__(self):
        return self.name

    @property
    def short_name(self):
        return self.name[:4].upper()
