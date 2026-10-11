#!/usr/bin/env python3
import hashlib
import random
from pathlib import Path

SEED_GEN = 7
SEED_HOLDOUT = 99
TARGET_TOTAL = 9000
HOLDOUT_N = 200
MIN_TRAIN = 8000

NOMES = [
    "Ana",
    "Bruno",
    "Carla",
    "Diego",
    "Elisa",
    "Felipe",
    "Gabriela",
    "Henrique",
    "Isabela",
    "João",
    "Karla",
    "Lucas",
    "Mariana",
    "Nicolas",
    "Olivia",
    "Paulo",
    "Queila",
    "Rafael",
    "Sofia",
    "Tiago",
    "Ursula",
    "Vinicius",
    "Wanessa",
    "Xavier",
    "Yasmin",
    "Zeca",
    "Alice",
    "Bernardo",
    "Cecilia",
    "Davi",
    "Eduarda",
    "Fabio",
    "Giovana",
    "Heitor",
    "Igor",
    "Julia",
    "Kaique",
    "Larissa",
    "Miguel",
    "Nina",
]

CIDADES = [
    "São Paulo",
    "Rio de Janeiro",
    "Belo Horizonte",
    "Curitiba",
    "Fortaleza",
    "Salvador",
    "Recife",
    "Porto Alegre",
    "Brasília",
    "Goiânia",
    "Manaus",
    "Belém",
    "Florianópolis",
    "Vitória",
    "Natal",
    "João Pessoa",
    "Maceió",
    "Aracaju",
    "Teresina",
    "Campo Grande",
    "Cuiabá",
    "Porto Velho",
    "Macapá",
    "Boa Vista",
    "Palmas",
    "Santos",
    "Campinas",
    "Osasco",
    "Sorocaba",
    "Joinville",
]

TEMAS = [
    "matemática",
    "história",
    "geografia",
    "ciências",
    "português",
    "inglês",
    "biologia",
    "química",
    "física",
    "filosofia",
    "sociologia",
    "artes",
    "música",
    "programação",
    "robótica",
    "astronomia",
    "ecologia",
    "economia",
    "literatura",
    "redação",
    "álgebra",
    "geometria",
    "trigonometria",
    "estatística",
    "informática",
    "desenho",
    "teatro",
    "fotografia",
    "culinária",
    "jardinagem",
]


PAISES = [
    ("Brasil", "Brasília", "do"),
    ("Argentina", "Buenos Aires", "da"),
    ("Chile", "Santiago", "do"),
    ("Uruguai", "Montevidéu", "do"),
    ("Paraguai", "Assunção", "do"),
    ("Peru", "Lima", "do"),
    ("Colômbia", "Bogotá", "da"),
    ("Venezuela", "Caracas", "da"),
    ("Portugal", "Lisboa", "de"),
    ("Espanha", "Madri", "da"),
    ("França", "Paris", "da"),
    ("Itália", "Roma", "da"),
    ("Alemanha", "Berlim", "da"),
    ("Japão", "Tóquio", "do"),
    ("China", "Pequim", "da"),
    ("Índia", "Nova Délhi", "da"),
    ("Egito", "Cairo", "do"),
    ("Marrocos", "Rabat", "de"),
    ("Canadá", "Ottawa", "do"),
    ("México", "Cidade do México", "do"),
    ("Cuba", "Havana", "de"),
    ("Angola", "Luanda", "de"),
    ("Moçambique", "Maputo", "de"),
    ("Austrália", "Camberra", "da"),
    ("Grécia", "Atenas", "da"),
    ("Turquia", "Ancara", "da"),
    ("Holanda", "Amsterdã", "da"),
    ("Suíça", "Berna", "da"),
    ("Noruega", "Oslo", "da"),
    ("Suécia", "Estocolmo", "da"),
]

MESES_DIAS = {
    "janeiro": 31,
    "fevereiro": 28,
    "março": 31,
    "abril": 30,
    "maio": 31,
    "junho": 30,
    "julho": 31,
    "agosto": 31,
    "setembro": 30,
    "outubro": 31,
    "novembro": 30,
    "dezembro": 31,
}

DIAS_SEMANA = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]

CURIOSIDADES = {
    "oceano": "o Oceano Pacífico é o maior do planeta, cobrindo cerca de um terço da superfície da Terra",
    "espaço": "um dia em Vênus é mais longo do que um ano em Vênus",
    "corpo humano": "o corpo humano adulto tem 206 ossos",
    "abelhas": "as abelhas se comunicam com uma dança para indicar onde há flores",
    "plantas": "o bambu pode crescer quase um metro em um único dia",
    "história": "a escrita foi inventada há mais de cinco mil anos na Mesopotâmia",
    "geografia": "o deserto do Saara é quase do tamanho do Brasil",
    "ciência": "a água ferve a 100 graus Celsius ao nível do mar",
    "tecnologia": "o primeiro computador eletrônico pesava cerca de 30 toneladas",
    "arte": "a Mona Lisa não tem sobrancelhas, detalhe que intriga estudiosos",
    "música": "ouvir música pode ajudar a memorizar melhor o que se estuda",
    "esportes": "o futebol moderno nasceu na Inglaterra no século dezenove",
    "alimentos": "o mel nunca estraga, arqueólogos já acharam mel comestível em tumbas antigas",
    "clima": "relâmpagos podem aquecer o ar a temperaturas maiores que a superfície do Sol",
    "formigas": "as formigas conseguem carregar muitas vezes o próprio peso",
    "vulcões": "existem mais vulcões embaixo do oceano do que nos continentes",
    "deserto": "no deserto, a temperatura pode variar mais de 30 graus entre o dia e a noite",
    "floresta": "a Amazônia abriga cerca de dez por cento das espécies conhecidas do mundo",
    "rios": "o rio Amazonas despeja tanta água no mar que dá para encher piscinas olímpicas em segundos",
    "montanhas": "o Monte Everest cresce alguns milímetros por ano por causa das placas tectônicas",
}


def t_saud_1(rng):
    n = rng.choice(NOMES)
    q = rng.choice([f"Olá, {n}!", f"Olá! Meu nome é {n}.", f"Oi, sou {n}!"])
    a = rng.choice([f"Olá, {n}! Como posso ajudar hoje?", f"Oi, {n}! Em que posso ser útil?"])
    return q, a


def t_saud_2(rng):
    n = rng.choice(NOMES)
    q = rng.choice([f"Bom dia, {n}!", f"Bom dia! Sou {n}."])
    a = rng.choice([f"Bom dia, {n}! Em que posso ajudar?", f"Bom dia, {n}! Vamos estudar juntos?"])
    return q, a


def t_saud_3(rng):
    n = rng.choice(NOMES)
    c = rng.choice(CIDADES)
    q = rng.choice([f"Boa tarde! Sou {n} de {c}.", f"Boa tarde, sou {n} e moro em {c}."])
    a = rng.choice(
        [
            f"Boa tarde, {n} de {c}! Como posso ajudar?",
            f"Olá, {n}! Que bom ver alguém de {c} por aqui.",
        ]
    )
    return q, a


def t_saud_4(rng):
    n = rng.choice(NOMES)
    q = rng.choice([f"Oi, tudo bem? Me chamo {n}.", f"Oi, tudo bem, {n} por aqui!"])
    a = rng.choice([f"Tudo bem, {n}! Como posso ajudar hoje?", f"Oi, {n}! Tudo ótimo. E com você?"])
    return q, a


def t_saud_5(rng):
    n = rng.choice(NOMES)
    q = rng.choice([f"Olá! Você pode me chamar de {n}.", f"Oi! Pode me chamar de {n}."])
    a = rng.choice(
        [
            f"Prazer, {n}! Sou a Nexusia, uma IA em treinamento.",
            f"Combinado, {n}! Sou a Nexusia. No que ajudo?",
        ]
    )
    return q, a


def t_saud_6(rng):
    n = rng.choice(NOMES)
    c = rng.choice(CIDADES)
    q = rng.choice([f"Boa noite, sou {n} de {c}.", f"Boa noite! Aqui é {n}, de {c}."])
    a = rng.choice(
        [f"Boa noite, {n}! Como posso ajudar?", f"Boa noite, {n} de {c}! Em que sou útil?"]
    )
    return q, a


def t_geral_1(rng):
    n = rng.choice(NOMES)
    q = rng.choice(
        [
            f"O que você é, {n} quer saber?",
            f"O que você é? Pergunta de {n}.",
            f"Sou {n}. O que você é?",
        ]
    )
    a = rng.choice(
        ["Sou a Nexusia, uma IA em treinamento.", f"Sou a Nexusia, {n}, uma IA em treinamento."]
    )
    return q, a


def t_geral_2(rng):
    t = rng.choice(TEMAS)
    q = rng.choice(
        [
            f"O que você sabe fazer com {t}?",
            f"Você pode me ajudar com {t}?",
            f"Você entende de {t}?",
        ]
    )
    a = rng.choice(
        [
            f"Sim! Posso explicar {t} passo a passo, com exemplos simples.",
            f"Claro! Pergunte sobre {t} que eu explico de forma simples.",
        ]
    )
    return q, a


def t_geral_3(rng):
    n = rng.choice(NOMES)
    q = rng.choice([f"Qual é o seu nome? Sou {n}.", f"Como você se chama? Eu sou {n}."])
    a = rng.choice(
        [
            f"Meu nome é Nexusia, {n}, uma IA em treinamento.",
            "Meu nome é Nexusia, uma IA em treinamento.",
        ]
    )
    return q, a


def t_geral_4(rng):
    n = rng.choice(NOMES)
    q = rng.choice(
        [f"Como você funciona, {n} quer entender?", f"Você pode explicar como funciona? Sou {n}."]
    )
    a = rng.choice(
        [
            f"{n}, eu respondo a partir do que aprendi no treino, sem acessar a internet.",
            "Eu gero respostas a partir do que aprendi no treinamento.",
        ]
    )
    return q, a


def t_geral_5(rng):
    n = rng.choice(NOMES)
    q = rng.choice([f"Você aprende comigo, {n}?", f"Sou {n}. Você aprende com as conversas?"])
    a = rng.choice(
        [
            "Sim, quando a coleta está autorizada e os dados são elegíveis.",
            f"Sim, {n}! Quando a coleta está autorizada, aprendo com conversas elegíveis.",
        ]
    )
    return q, a


def t_geral_6(rng):
    c = rng.choice(CIDADES)
    n = rng.choice(NOMES)
    q = rng.choice([f"Você conhece {c}? Sou {n}.", f"Sou {n} de {c}. Você conhece minha cidade?"])
    a = rng.choice(
        [
            f"Conheço {c} de nome, {n}! Me conte o que você quer saber sobre ela.",
            f"{c} é uma cidade interessante, {n}! O que você quer saber?",
        ]
    )
    return q, a


def t_math_soma(rng):
    a = rng.randint(2, 199)
    b = rng.randint(2, 199)
    q = rng.choice(
        [f"Quanto é {a} mais {b}?", f"Quanto dá {a} + {b}?", f"Me diga o resultado de {a} + {b}."]
    )
    return q, f"{a} mais {b} é igual a {a + b}."


def t_math_sub(rng):
    a = rng.randint(5, 299)
    b = rng.randint(2, a)
    q = rng.choice(
        [
            f"Quanto é {a} menos {b}?",
            f"Quanto dá {a} - {b}?",
            f"Me diga o resultado de {a} menos {b}.",
        ]
    )
    return q, f"{a} menos {b} é igual a {a - b}."


def t_math_mult(rng):
    a = rng.randint(2, 49)
    b = rng.randint(2, 12)
    q = rng.choice(
        [
            f"Quanto é {a} vezes {b}?",
            f"Quanto dá {a} x {b}?",
            f"Me diga o resultado de {a} vezes {b}.",
        ]
    )
    return q, f"{a} vezes {b} é igual a {a * b}."


def t_math_div(rng):
    b = rng.randint(2, 12)
    k = rng.randint(2, 25)
    a = b * k
    q = rng.choice([f"Quanto é {a} dividido por {b}?", f"Quanto dá {a} ÷ {b}?"])
    return q, f"{a} dividido por {b} é igual a {k}."


def t_math_dobro(rng):
    a = rng.randint(2, 499)
    q = rng.choice([f"Qual é o dobro de {a}?", f"Me diga o dobro de {a}."])
    return q, f"O dobro de {a} é {a * 2}."


def t_math_metade(rng):
    a = rng.choice([x for x in range(4, 500, 2)])
    q = rng.choice([f"Qual é a metade de {a}?", f"Me diga a metade de {a}."])
    return q, f"A metade de {a} é {a // 2}."


def t_math_soma3(rng):
    a = rng.randint(2, 99)
    b = rng.randint(2, 99)
    c = rng.randint(2, 99)
    q = rng.choice([f"Quanto é {a} mais {b} mais {c}?", f"Quanto dá {a} + {b} + {c}?"])
    return q, f"{a} + {b} + {c} é igual a {a + b + c}."


def t_math_macas(rng):
    n = rng.choice(NOMES)
    a = rng.randint(2, 60)
    b = rng.randint(2, 60)
    q = rng.choice(
        [
            f"Sou {n} e tenho {a} maçãs. Se eu ganhar {b}, com quantas fico?",
            f"Se {n} tem {a} balas e ganha {b}, com quantas fica?",
        ]
    )
    return q, f"Com {a + b}, {n}! Pois {a} + {b} = {a + b}."


def t_cap_1(rng):
    pais, cap, art = rng.choice(PAISES)
    n = rng.choice(NOMES)
    q = rng.choice(
        [f"Qual é a capital {art} {pais}?", f"{n} quer saber: qual é a capital {art} {pais}?"]
    )
    return q, f"A capital {art} {pais} é {cap}."


def t_cap_2(rng):
    pais, cap, _ = rng.choice(PAISES)
    q = rng.choice([f"{cap} é capital de qual país?", f"De qual país {cap} é capital?"])
    return (
        q,
        f"{cap} é a capital {('de ' + pais) if pais in ('Portugal', 'Cuba', 'Angola', 'Moçambique', 'Marrocos') else ('do ' + pais if pais not in ('Colômbia', 'Venezuela', 'Espanha', 'França', 'Itália', 'Alemanha', 'China', 'Índia', 'Austrália', 'Grécia', 'Turquia', 'Holanda', 'Suíça', 'Noruega', 'Suécia', 'Argentina') else ('da ' + pais))}.",
    )


def t_cap_3(rng):
    pais, cap, art = rng.choice(PAISES)
    n = rng.choice(NOMES)
    q = rng.choice(
        [f"Me diga a capital {art} {pais}, por favor.", f"Sou {n}. Me diga a capital {art} {pais}."]
    )
    return q, f"Claro, {n}! A capital {art} {pais} é {cap}."


def t_cap_4(rng):
    pais, cap, _ = rng.choice(PAISES)
    q = rng.choice([f"Em que país fica {cap}?", f"Em qual país fica a cidade de {cap}?"])
    return q, f"{cap} fica em {pais}."


def t_cap_5(rng):
    pais, cap, art = rng.choice(PAISES)
    q = rng.choice(
        [f"Você sabe a capital {art} {pais}?", f"Qual a capital {art} {pais}? Me conta."]
    )
    return q, f"Sei sim! É {cap}."


def t_cap_6(rng):
    pais, cap, _art = rng.choice(PAISES)
    n = rng.choice(NOMES)
    q = rng.choice(
        [
            f"Cite um país e sua capital, para {n} estudar.",
            f"{n} está estudando. Cite um país e a capital.",
        ]
    )
    return q, f"Exemplo para {n}: {pais}, capital {cap}."


def t_data_1(rng):
    mes, dias = rng.choice(list(MESES_DIAS.items()))
    n = rng.choice(NOMES)
    q = rng.choice([f"Quantos dias tem {mes}?", f"Sou {n}. Quantos dias tem {mes}?"])
    extra = " Em anos bissextos, fevereiro tem 29." if mes == "fevereiro" else ""
    return q, f"{mes.capitalize()} tem {dias} dias.{extra}"


def t_data_2(rng):
    n = rng.choice(NOMES)
    q = rng.choice(
        [f"Quantos meses tem um ano, {n} quer saber?", f"Sou {n}. Quantos meses tem um ano?"]
    )
    return q, f"Um ano tem 12 meses, {n}!"


def t_data_3(rng):
    d = rng.choice(DIAS_SEMANA)
    nxt = DIAS_SEMANA[(DIAS_SEMANA.index(d) + 1) % 7]
    n = rng.choice(NOMES)
    q = rng.choice(
        [f"Que dia da semana vem depois de {d}?", f"Sou {n}. Depois de {d} vem qual dia?"]
    )
    return q, f"Depois de {d} vem {nxt}, {n}!"


def t_data_4(rng):
    n = rng.choice(NOMES)
    c = rng.choice(CIDADES)
    q = rng.choice(
        [
            f"Sou {n} de {c}. Quantos dias tem uma semana?",
            f"Quantos dias tem uma semana? Pergunta de {n}.",
        ]
    )
    return q, f"Uma semana tem 7 dias, {n}!"


def t_estudo_1(rng):
    t = rng.choice(TEMAS)
    n = rng.choice(NOMES)
    q = rng.choice(
        [f"Me ajude a estudar {t}. Sou {n}.", f"Sou {n} e quero estudar {t}. Por onde começo?"]
    )
    return (
        q,
        f"Claro, {n}! Para estudar {t}, comece pelo básico, faça resumos curtos e revise em 3 dias.",
    )


def t_estudo_2(rng):
    t = rng.choice(TEMAS)
    q = rng.choice([f"Como posso aprender {t}?", f"Qual o jeito mais fácil de aprender {t}?"])
    return q, f"Divida {t} em partes pequenas, pratique um pouco todo dia e teste-se com perguntas."


def t_estudo_3(rng):
    t = rng.choice(TEMAS)
    n = rng.choice(NOMES)
    q = rng.choice(
        [f"Dê uma dica para estudar {t}, {n} pede.", f"Sou {n}. Uma dica rápida para {t}?"]
    )
    return q, f"Dica para {n}: estude {t} em blocos de 25 minutos com pausas de 5."


def t_estudo_4(rng):
    t = rng.choice(TEMAS)
    q = rng.choice(
        [f"Como organizar meus estudos de {t}?", f"Como montar um plano para estudar {t}?"]
    )
    return q, f"Liste os tópicos de {t}, defina metas semanais e revise o que errou."


def t_estudo_5(rng):
    t = rng.choice(TEMAS)
    n = rng.choice(NOMES)
    q = rng.choice(
        [
            f"Qual a melhor forma de revisar {t}? Sou {n}.",
            f"Sou {n}. Como reviso {t} na véspera da prova?",
        ]
    )
    return q, f"{n}, releia seus resumos de {t}, refaça exercícios e durma bem antes da prova."


def t_estudo_6(rng):
    t = rng.choice(TEMAS)
    n = rng.choice(NOMES)
    q = rng.choice(
        [
            f"Tenho dificuldade em {t}. Sou {n}, o que faço?",
            f"{n} tem dificuldade em {t}. Algum conselho?",
        ]
    )
    return q, f"{n}, tente exemplos mais simples de {t}, peça ajuda e pratique sem pressa."


def t_curio_1(rng):
    tema = rng.choice(list(CURIOSIDADES.keys()))
    fato = CURIOSIDADES[tema]
    n = rng.choice(NOMES)
    q = rng.choice(
        [
            f"Me conte uma curiosidade sobre {tema}.",
            f"Sou {n}. Me conte uma curiosidade sobre {tema}.",
        ]
    )
    return q, f"Você sabia que {fato}, {n}?"


def t_curio_2(rng):
    tema = rng.choice(list(CURIOSIDADES.keys()))
    fato = CURIOSIDADES[tema]
    q = rng.choice([f"O que você sabe sobre {tema}?", f"Me ensine algo sobre {tema}."])
    return q, f"Sobre {tema}: {fato}."


def t_curio_3(rng):
    tema = rng.choice(list(CURIOSIDADES.keys()))
    fato = CURIOSIDADES[tema]
    n = rng.choice(NOMES)
    q = rng.choice(
        [f"{n} quer uma curiosidade de {tema}.", f"Conte um fato curioso sobre {tema} para {n}."]
    )
    return q, f"{n}, aqui vai: {fato}!"


def t_curio_4(rng):
    a = rng.randint(2, 99)
    b = rng.randint(2, 99)
    q = rng.choice(
        [
            f"Você sabia que {a} mais {b} é {a + b}? Me conta outra curiosidade com números.",
            f"Me diga uma conta fácil com {a} e {b}.",
        ]
    )
    return q, f"Claro! {a} + {b} = {a + b}. E {a} x 2 = {a * 2}!"


def t_curio_5(rng):
    c = rng.choice(CIDADES)
    n = rng.choice(NOMES)
    q = rng.choice(
        [f"Sou {n} de {c}. Me conte uma curiosidade.", f"{n}, de {c}, quer uma curiosidade."]
    )
    tema = rng.choice(list(CURIOSIDADES.keys()))
    return q, f"Para {n} de {c}: você sabia que {CURIOSIDADES[tema]}?"


def t_curio_6(rng):
    t = rng.choice(TEMAS)
    n = rng.choice(NOMES)
    q = rng.choice(
        [f"Por que estudar {t} é legal, {n} pergunta?", f"Sou {n}. Por que {t} é interessante?"]
    )
    return q, f"{t.capitalize()} é interessante porque ajuda a entender o mundo, {n}!"


def t_desp_1(rng):
    n = rng.choice(NOMES)
    q = rng.choice([f"Obrigado, sou {n}!", f"Obrigado pela ajuda, {n} agradece."])
    return q, f"Por nada, {n}! Precisando, é só chamar."


def t_desp_2(rng):
    n = rng.choice(NOMES)
    q = rng.choice([f"Tchau! Sou {n}.", f"Tchau, até mais! {n} se despede."])
    return q, f"Tchau, {n}! Até a próxima."


def t_desp_3(rng):
    n = rng.choice(NOMES)
    t = rng.choice(TEMAS)
    q = rng.choice(
        [f"Até logo! Vou estudar {t}. Sou {n}.", f"Vou nessa estudar {t}. Até logo! {n}."]
    )
    return q, f"Até logo, {n}! Bons estudos de {t}."


def t_desp_4(rng):
    n = rng.choice(NOMES)
    q = rng.choice([f"Boa noite e obrigado! Sou {n}.", f"Boa noite! {n} vai dormir."])
    return q, f"Boa noite, {n}! Descanse bem."


TEMPLATES = [
    t_saud_1,
    t_saud_2,
    t_saud_3,
    t_saud_4,
    t_saud_5,
    t_saud_6,
    t_geral_1,
    t_geral_2,
    t_geral_3,
    t_geral_4,
    t_geral_5,
    t_geral_6,
    t_math_soma,
    t_math_sub,
    t_math_mult,
    t_math_div,
    t_math_dobro,
    t_math_metade,
    t_math_soma3,
    t_math_macas,
    t_cap_1,
    t_cap_2,
    t_cap_3,
    t_cap_4,
    t_cap_5,
    t_cap_6,
    t_data_1,
    t_data_2,
    t_data_3,
    t_data_4,
    t_estudo_1,
    t_estudo_2,
    t_estudo_3,
    t_estudo_4,
    t_estudo_5,
    t_estudo_6,
    t_curio_1,
    t_curio_2,
    t_curio_3,
    t_curio_4,
    t_curio_5,
    t_curio_6,
    t_desp_1,
    t_desp_2,
    t_desp_3,
    t_desp_4,
]

assert len(TEMPLATES) >= 40, f"preciso de >=40 templates, tenho {len(TEMPLATES)}"


def build_lines():
    rng = random.Random(SEED_GEN)
    seen = set()
    lines = []
    attempts = 0
    max_attempts = 300000
    idx = 0
    while len(lines) < TARGET_TOTAL and attempts < max_attempts:
        tpl = TEMPLATES[idx % len(TEMPLATES)]
        idx += 1
        attempts += 1
        try:
            q, a = tpl(rng)
        except Exception:  # noqa: BLE001, S112 — template ruim é descartado; asserts cobrem
            continue
        line = f"<bos><usr>{q}<sep><asst>{a}<eos>"
        if len(line) < 8:
            continue
        if not line.startswith("<bos>") or not line.endswith("<eos>"):
            continue
        h = hashlib.sha256(line.encode("utf-8")).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        lines.append(line)
    assert len(lines) >= TARGET_TOTAL, (
        f"falha: geradas {len(lines)} unicas, esperado >={TARGET_TOTAL}"
    )
    return lines


def main():
    root = Path(__file__).resolve().parent.parent
    out_train = root / "datasets" / "incoming" / "mega_seed_ptbr.txt"
    out_hold = root / "datasets" / "evaluation" / "holdout_seed.txt"

    lines = build_lines()

    rng_h = random.Random(SEED_HOLDOUT)
    hold_idx = set(rng_h.sample(range(len(lines)), HOLDOUT_N))
    holdout = [lines[i] for i in sorted(hold_idx)]
    train = [ln for i, ln in enumerate(lines) if i not in hold_idx]

    assert len(holdout) == HOLDOUT_N, f"holdout={len(holdout)}"
    assert len(train) >= MIN_TRAIN, f"treino={len(train)} < {MIN_TRAIN}"

    assert not (set(holdout) & set(train)), "vazamento holdout->treino!"

    assert len(set(train)) == len(train), "duplicadas no treino!"
    assert len(set(holdout)) == len(holdout), "duplicadas no holdout!"

    out_train.parent.mkdir(parents=True, exist_ok=True)
    out_hold.parent.mkdir(parents=True, exist_ok=True)
    out_train.write_text("\n".join(train) + "\n", encoding="utf-8")
    out_hold.write_text("\n".join(holdout) + "\n", encoding="utf-8")

    print(f"templates: {len(TEMPLATES)}")
    print(f"total gerado: {len(lines)} unicas")
    print(f"treino: {len(train)} linhas -> {out_train}")
    print(f"holdout: {len(holdout)} linhas -> {out_hold}")


if __name__ == "__main__":
    main()
