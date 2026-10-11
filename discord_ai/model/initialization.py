from __future__ import annotations

from torch import nn


def init_weights_autoral(module: nn.Module, std: float = 0.02) -> None:
    if isinstance(module, (nn.Linear, nn.Embedding)):
        module.weight.data.normal_(mean=0.0, std=std)
        if isinstance(module, nn.Linear) and module.bias is not None:
            module.bias.data.zero_()
    elif isinstance(module, nn.LayerNorm):
        module.bias.data.zero_()
        module.weight.data.fill_(1.0)


def verify_random_init(model: nn.Module) -> dict:

    params = list(model.parameters())
    assert params, "modelo sem parâmetros"
    trainable = sum(p.numel() for p in params if p.requires_grad)
    assert trainable > 0, "nenhum parâmetro treinável"
    all_const = all(bool((p.data == p.data.flatten()[0]).all()) for p in params if p.numel())
    return {
        "num_params": sum(p.numel() for p in params),
        "trainable": trainable,
        "all_constant": all_const,
    }
