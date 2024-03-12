from django.db import models
from PIL import Image
from pathlib import Path
from django.conf import settings
from django.utils.text import slugify
from utils import utils


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao_curta = models.TextField(max_length=255)
    descricao_longa = models.TextField()
    imagem = models.ImageField(
        upload_to='produto_imagens/%Y/%m/', blank=True, null=True
    )
    slug = models.SlugField(unique=True, blank=True, null=True)
    preco_marketing = models.FloatField(verbose_name='preço')
    preco_marketing_promocional = models.FloatField(
        default=0, verbose_name='preço promocional'
        )
    tipo = models.CharField(
        default='V',
        max_length=1,
        choices=(
            ('V', 'Variavel'),
            ('S', 'Simples')
        )
    )

    def get_preco_formatado(self):
        return utils.formata_preco(self.preco_marketing)
    get_preco_formatado.short_description = 'Preço'

    def get_preco_promocional_formatado(self):
        return utils.formata_preco(self.preco_marketing_promocional)
    get_preco_promocional_formatado.short_description = 'Preço'

    @staticmethod
    def resize_image(image_django, new_width=800, optimize=True, quality=60):
        image_path = Path(settings.MEDIA_ROOT / image_django.name).resolve()
        print(image_path)
        image_pillow = Image.open(image_path)

        width, height = image_pillow.size
        # exif = pil_image.info['exif']
        # print(pil_image.info)
        if width <= new_width:
            image_pillow.close()
            return image_pillow

        new_height = round((new_width * height) / width)

        new_image = image_pillow.resize((new_width, new_height), Image.LANCZOS)
        new_image.save(
            image_path,
            optimize=optimize,
            quality=quality
        )

        return new_image

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)

        super_save = super().save(*args, **kwargs)
        if self.imagem:
            self.resize_image(self.imagem, 800)
        return super_save

    def __str__(self) -> str:
        return self.nome


class Variacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    nome = models.CharField(max_length=90, blank=True, null=True)
    preco = models.FloatField()
    preco_promocional = models.FloatField(default=0)
    estoque = models.PositiveBigIntegerField(default=1)

    class Meta:
        verbose_name = 'variação'
        verbose_name_plural = 'variações'

    def __str__(self) -> str:
        return self.nome or self.produto.nome
