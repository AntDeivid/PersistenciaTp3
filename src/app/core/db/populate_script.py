from datetime import datetime, timedelta
from random import Random

from bson import ObjectId

from src.app.core.db.database import database
from src.app.models.contrato import Contrato
from src.app.models.manutencao import Manutencao
from src.app.models.pagamento import Pagamento
from src.app.models.usuario import Usuario
from src.app.models.veiculo import Veiculo
from src.app.models.veiculo_manutencao import VeiculoManutencao
import asyncio

# Move collection definitions inside main()
# COLLECTION_CONTRATO = database.get_collection("contratos")
# COLLECTION_MANUTENCAO = database.get_collection("manutencoes")
# COLLECTION_PAGAMENTO = database.get_collection("pagamentos")
# COLLECTION_USUARIO = database.get_collection("usuarios")
# COLLECTION_VEICULO = database.get_collection("veiculos")
# COLLECTION_VEICULO_MANUTENCAO = database.get_collection("veiculo_manutencoes")

def generate_random_data(n=15, random_generator=None):
    """Gera dados aleatórios para as coleções."""

    if random_generator is None:
        random_generator = Random()

    usuarios = []
    for i in range(n):
        usuarios.append(
            Usuario(
                nome=f"Usuario {i}",
                email=f"usuario{i}@email.com",
                celular=f"1199999{str(i).zfill(4)}",
                cpf=f"{str(i).zfill(3)}.{str(i+1).zfill(3)}.{str(i+2).zfill(3)}-{str(i%10).zfill(2)}"
            ).model_dump(exclude={"id"}, by_alias=True) #converte o modelo pydantic em um dicionario, necessário para inserir no mongoDB
        )

    veiculos = []
    marcas = ["Fiat", "Volkswagen", "Ford", "Chevrolet", "Hyundai"]
    modelos = ["Uno", "Gol", "Ka", "Onix", "HB20"]
    for i in range(n):
        veiculos.append(
            Veiculo(
                modelo=modelos[i % len(modelos)],
                marca=marcas[i % len(marcas)],
                placa=f"ABC{str(i).zfill(3)}",
                ano=2010 + (i % 13)
            ).model_dump(exclude={"id"}, by_alias=True)
        )

    pagamentos = []
    formas_pagamento = ["Crédito", "Débito", "Boleto", "PIX"]
    for i in range(n):
        pagamentos.append(
            Pagamento(
                valor=random_generator.uniform(50.0, 500.0),
                forma_pagamento=formas_pagamento[i % len(formas_pagamento)],
                vencimento=datetime.now() + timedelta(days=random_generator.randint(1, 30)),
                pago=random_generator.choice([True, False])
            ).model_dump(exclude={"id"}, by_alias=True)
        )

    manutencoes = []
    tipos_manutencao = ["Revisão", "Troca de óleo", "Pneus", "Freios"]
    for i in range(n):
        manutencoes.append(
            Manutencao(
                data=datetime.now() - timedelta(days=random_generator.randint(0, 365)),
                tipo_manutencao=tipos_manutencao[i % len(tipos_manutencao)],
                custo=random_generator.uniform(100.0, 1000.0),
                observacao=f"Manutenção de rotina {i}"
            ).model_dump(exclude={"id"}, by_alias=True)
        )


    # contratos = []
    # for i in range(n):
    #     data_inicio = datetime.now() - timedelta(days=random.randint(1, 365))
    #     data_fim = data_inicio + timedelta(days=random.randint(30, 365))
    #     contratos.append(
    #         Contrato(
    #             usuario_id=str(ObjectId()),  # Substituir por IDs reais
    #             veiculo_id=str(ObjectId()),  # Substituir por IDs reais
    #             pagamento_id=str(ObjectId()),  # Substituir por IDs reais (pode ser None)
    #             data_inicio=data_inicio,
    #             data_fim=data_fim
    #         ).dict(by_alias=True)
    #     )
    #
    # veiculo_manutencoes = []
    # for i in range(n):
    #     veiculo_manutencoes.append(
    #         VeiculoManutencao(
    #             veiculo_id=str(ObjectId()),  # Substituir por IDs reais
    #             manutencao_id=str(ObjectId())  # Substituir por IDs reais
    #         ).dict(by_alias=True)
    #     )

    return usuarios, veiculos, pagamentos, manutencoes

async def populate_database(COLLECTION_USUARIO, COLLECTION_VEICULO, COLLECTION_PAGAMENTO, COLLECTION_MANUTENCAO, usuarios, veiculos, pagamentos, manutencoes):
    """Popula o banco de dados MongoDB com os dados gerados."""

    # Inserir dados em lote
    if usuarios:
        for usuario in usuarios:
            await COLLECTION_USUARIO.insert_one(usuario)
        print(f"Inseridos {len(usuarios)} documentos em {COLLECTION_USUARIO.name}")

    if veiculos:
        for veiculo in veiculos:
            await COLLECTION_VEICULO.insert_one(veiculo)
        print(f"Inseridos {len(veiculos)} documentos em {COLLECTION_VEICULO.name}")

    if pagamentos:
        for pagamento in pagamentos:
            await COLLECTION_PAGAMENTO.insert_one(pagamento)
        print(f"Inseridos {len(pagamentos)} documentos em {COLLECTION_PAGAMENTO.name}")

    if manutencoes:
        for manutencao in manutencoes:
            await COLLECTION_MANUTENCAO.insert_one(manutencao)
        print(f"Inseridos {len(manutencoes)} documentos em {COLLECTION_MANUTENCAO.name}")

async def generate_contratos(COLLECTION_USUARIO, COLLECTION_VEICULO, COLLECTION_PAGAMENTO, random_generator, n=15):
    """Gera dados aleatórios para a coleção contratos, buscando IDs existentes."""

    usuarios = await COLLECTION_USUARIO.find({}, {"_id": 1}).to_list(length=None)
    veiculos = await COLLECTION_VEICULO.find({}, {"_id": 1}).to_list(length=None)
    pagamentos = await COLLECTION_PAGAMENTO.find({}, {"_id": 1}).to_list(length=None)

    if not usuarios or not veiculos or not pagamentos:
        print("Atenção: As coleções usuario, veiculo ou pagamento estão vazias. Não é possível criar contratos.")
        return []

    contratos = []
    for i in range(n):
        data_inicio = datetime.now() - timedelta(days=random_generator.randint(1, 365))
        data_fim = data_inicio + timedelta(days=random_generator.randint(30, 365))

        usuario_id = random_generator.choice(usuarios)['_id']
        veiculo_id = random_generator.choice(veiculos)['_id']
        pagamento_id = random_generator.choice(pagamentos)['_id']  # Assume que todos os pagamentos são válidos

        contratos.append(
            Contrato(
                usuario_id=str(usuario_id),
                veiculo_id=str(veiculo_id),
                pagamento_id=str(pagamento_id),
                data_inicio=data_inicio,
                data_fim=data_fim
            ).model_dump(exclude={"id"}, by_alias=True)
        )
    return contratos

async def generate_veiculo_manutencoes(COLLECTION_VEICULO, COLLECTION_MANUTENCAO, random_generator, n=15):
    """Gera dados para veiculo_manutencoes, buscando IDs existentes."""

    veiculos = await COLLECTION_VEICULO.find({}, {"_id": 1}).to_list(length=None)
    manutencoes = await COLLECTION_MANUTENCAO.find({}, {"_id": 1}).to_list(length=None)

    if not veiculos or not manutencoes:
        print("Atenção: As coleções veiculo ou manutencao estão vazias. Não é possível criar veiculo_manutencoes.")
        return []

    veiculo_manutencoes = []
    for i in range(n):
        veiculo_id = random_generator.choice(veiculos)['_id']
        manutencao_id = random_generator.choice(manutencoes)['_id']

        veiculo_manutencoes.append(
            VeiculoManutencao(
                veiculo_id=str(veiculo_id),
                manutencao_id=str(manutencao_id)
            ).model_dump(exclude={"id"}, by_alias=True)
        )
    return veiculo_manutencoes


async def populate_collection(collection_name, data):
    """Popula uma coleção com dados."""

    if data:
        #É necessário converter as datas para ISODate antes de inserir em contratos
        if(collection_name == database.get_collection("contratos")): #COLLECTION_CONTRATO):
            for item in data:
                item['data_inicio'] = item['data_inicio']
                item['data_fim'] = item['data_fim']

        for item in data:
            await collection_name.insert_one(item)
        print(f"Inseridos {len(data)} documentos em {collection_name.name}")
    else:
        print(f"Nenhum dado para inserir em {collection_name.name}")


async def main():
    await database.connect()
    random_generator = Random() # Create random generator

    # Get collections *after* connecting
    COLLECTION_CONTRATO = database.get_collection("contratos")
    COLLECTION_MANUTENCAO = database.get_collection("manutencoes")
    COLLECTION_PAGAMENTO = database.get_collection("pagamentos")
    COLLECTION_USUARIO = database.get_collection("usuarios")
    COLLECTION_VEICULO = database.get_collection("veiculos")
    COLLECTION_VEICULO_MANUTENCAO = database.get_collection("veiculo_manutencoes")

    # usuarios, veiculos, pagamentos, manutencoes = generate_random_data(15, random_generator)

    # await populate_database(COLLECTION_USUARIO, COLLECTION_VEICULO, COLLECTION_PAGAMENTO, COLLECTION_MANUTENCAO, usuarios, veiculos, pagamentos, manutencoes)

    contratos = await generate_contratos(COLLECTION_USUARIO, COLLECTION_VEICULO, COLLECTION_PAGAMENTO, random_generator, 15)
    veiculo_manutencoes = await generate_veiculo_manutencoes(COLLECTION_VEICULO, COLLECTION_MANUTENCAO, random_generator, 15)

    await populate_collection(COLLECTION_CONTRATO, contratos)
    await populate_collection(COLLECTION_VEICULO_MANUTENCAO, veiculo_manutencoes)

    print("Dados inseridos com sucesso!")
    await database.disconnect()


if __name__ == "__main__":
    asyncio.run(main())