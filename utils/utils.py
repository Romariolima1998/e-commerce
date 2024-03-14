
def formata_preco(val):
    print(val)
    return f'R$ {"{:.2f}".format(val)}'.replace('.', ',')


def cart_total_qtd(carrinho):
    return sum([item['quantidade'] for item in carrinho.values()])
