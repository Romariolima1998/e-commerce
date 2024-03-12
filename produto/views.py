from django.shortcuts import render
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse

from . import models


class ListaProduto(ListView):
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 9


class DetalheProduto(View):
    ...


class AdicionarAoCarrinho(View):
    ...


class RemoverDoCarrinho(View):
    ...


class Carrinho(View):
    ...


class Finalizar(View):
    ...
