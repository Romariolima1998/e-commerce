from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.contrib import messages
from django.db.models import Q

from . import models
from perfil.models import Perfil


class ListaProduto(ListView):
    model = models.Produto
    template_name = 'produto/lista.html'
    context_object_name = 'produtos'
    paginate_by = 10
    ordering = ['-id']


class Busca(ListaProduto):
    def get_queryset(self, *args, **kwargs):
        termo = self.request.GET.get('termo') or self.request.session['termo']
        qs = super().get_queryset(*args, **kwargs)

        if not termo:
            return qs
        
        self.request.session['termo'] = termo

        qs = qs.filter(
            Q(nome__icontains=termo) |
            Q(descricao_curta__icontains=termo) |
            Q(descricao_longa__icontains=termo)
        )
        return qs


class DetalheProduto(DetailView):
    model = models.Produto
    template_name = 'produto/detalhe.html'
    context_object_name = 'produto'
    slug_url_kwarg = 'slug'


class AdicionarAoCarrinho(View):
    def get(self, *args, **kwargs):

        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('produto:lista')
        )

        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            messages.error(
                self.request,
                'Produto não existe'
            )
            return redirect(http_referer)

        variacao = get_object_or_404(models.Variacao, id=variacao_id)
        produto = variacao.produto
        variacao_estoque = variacao.estoque

        produto_id = produto.id
        produto_nome = produto.nome
        variacao_nome = variacao.nome or ''
        preco_unitario = variacao.preco
        preco_unitario_promocional = variacao.preco_promocional
        quantidade = 1
        slug = produto.slug
        imagem = produto.imagem

        if imagem:
            imagem = imagem.url
        else:
            imagem = ''

        if variacao.estoque < 1:
            messages.error(
                self.request,
                'Estoque insuficiente'
            )

        if not self.request.session.get('carrinho'):
            self.request.session['carrinho'] = {}
            self.request.session.save()

        carrinho = self.request.session['carrinho']

        if variacao_id in carrinho:
            quantidade_carrinho = carrinho[variacao_id]['quantidade']
            quantidade_carrinho += 1

            if variacao_estoque < quantidade_carrinho:
                messages.warning(
                        self.request,
                        f'Estoque insuficiente para {quantidade_carrinho}x no '
                        f'produto {produto_nome}. Adicionamos '
                        f'{variacao_estoque}x no seu carrinho '
                )
                quantidade_carrinho = variacao_estoque

            carrinho[variacao_id]['quantidade'] = quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo'] = preco_unitario * \
                quantidade_carrinho
            carrinho[variacao_id]['preco_quantitativo_promocional'] = \
                preco_unitario_promocional * quantidade_carrinho

        else:
            carrinho[variacao_id] = {
                'produto_id': produto_id,
                'produto_nome': produto_nome,
                'variacao_nome': variacao_nome,
                'variacao_id': variacao_id,
                'preco_unitario': preco_unitario,
                'preco_unitario_promocional': preco_unitario_promocional,
                'quantidade': quantidade,
                'slug': slug,
                'imagem': imagem,
                'preco_quantitativo_promocional': preco_unitario_promocional,
                'preco_quantitativo': preco_unitario,
            }

        self.request.session.save()
        messages.success(
            self.request,
            f'Produto {produto_nome} {variacao_nome}'
            f'adicionado ao seu carrinho {carrinho[variacao_id]["quantidade"]}'
        )
        return redirect(http_referer)


class RemoverDoCarrinho(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
                'HTTP_REFERER',
                reverse('produto:lista')
            )

        variacao_id = self.request.GET.get('vid')

        if not variacao_id:
            return redirect(http_referer)

        if not self.request.session.get('carrinho'):
            return redirect(http_referer)

        if variacao_id not in self.request.session.get('carrinho'):
            return redirect(http_referer)

        carrinho = self.request.session['carrinho'][variacao_id]

        messages.success(
            self.request,
            f'Produto {carrinho["produto_nome"]} {carrinho["variacao_nome"]}'
            f'removido do seu carrinho'
        )
        del self.request.session['carrinho'][variacao_id]
        self.request.session.save()

        return redirect(http_referer)


class Carrinho(View):
    def get(self, *args, **kwargs):
        context = {
            'carrinho': self.request.session.get('carrinho')
        }
        return render(self.request, 'produto/carrinho.html', context)


class ResumoDaCompra(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        perfil = Perfil.objects.filter(usuario=self.request.user).exists()

        if not perfil:
            messages.error(
                self.request,
                'Perfil do usuário incompleto'
            )
            return redirect('perfil:criar')

        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Seu carrinho esta vazio'
            )
            return redirect('produto:lista')

        context = {
            'usuario': self.request.user,
            'carrinho': self.request.session['carrinho']
        }
        return render(self.request, 'produto/resumodacompra.html', context)
