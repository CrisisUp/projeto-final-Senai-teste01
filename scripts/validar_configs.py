#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valida consistencia dos arquivos de configuracao do projeto SENAI
(Matriz + Filial — Packet Tracer) contra o plano de enderecoamento.

Uso:
    python scripts/validar_configs.py
    python scripts/validar_configs.py --root "C:\\Users\\...\\projeto-final-Senai-teste01"

Exit code 0 = todas as verificacoes OK; 1 = ha falhas.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Plano de referencia (espelha Documentacao Tecnica.txt / README.md)
# ---------------------------------------------------------------------------
DNS_CORPORATIVO = "192.168.3.10"

ARQUIVOS = {
    "RT-00": "codigo RT-00.txt",
    "RT-01": "codigo RT-01.txt",
    "RT-02": "codigo RT-02.txt",
    "SW-01": "codigo SW-01.txt",
    "SW-02": "codigo SW-02.txt",
    "WIFI": "codigo WIFI-IOT.txt",
    "DOC": "Documentacao Tecnica.txt",
    "DIAG": "Comandos de Diagnosticos e Validacao.txt",
    "README": "README.md",
}

# hosts que nao devem aparecer (regressao de DNS corporativo)
HOSTS_PROIBIDOS = ["8.8.8.8", "8.8.4.4"]


class Resultado:
    def __init__(self) -> None:
        self.ok: list[str] = []
        self.falhas: list[str] = []
        self.avisos: list[str] = []

    def passou(self, msg: str) -> None:
        self.ok.append(msg)

    def falhou(self, msg: str) -> None:
        self.falhas.append(msg)

    def aviso(self, msg: str) -> None:
        self.avisos.append(msg)

    @property
    def exit_code(self) -> int:
        return 1 if self.falhas else 0


def ler(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def tem(texto: str, trecho: str) -> bool:
    return trecho in texto


def nao_tem(texto: str, trecho: str) -> bool:
    return trecho not in texto


def extrair_pools(texto: str) -> list[str]:
    """Retorna blocos ip dhcp pool ... ate a proxima linha de nivel 0 ou '!'."""
    blocos: list[str] = []
    linhas = texto.splitlines()
    i = 0
    while i < len(linhas):
        if linhas[i].strip().lower().startswith("ip dhcp pool"):
            bloco = [linhas[i]]
            i += 1
            while i < len(linhas):
                linha = linhas[i]
                if not linha.strip():
                    break
                if linha.strip().startswith("!"):
                    # comentário pode virar quebra se for de seção; ainda assim
                    # mantém se indentação indicar que estamos no pool
                    if len(linha) - len(linha.lstrip()) == 0 and i + 1 < len(linhas) and not linhas[i + 1].startswith(" "):
                        break
                    bloco.append(linha)
                    i += 1
                    continue
                if not linha.startswith(" ") and not linha.startswith("\t"):
                    break
                bloco.append(linha)
                i += 1
            blocos.append("\n".join(bloco))
        else:
            i += 1
    return blocos


def validar_rt00(texto: str, res: Resultado) -> None:
    nome = "RT-00"
    for ip in [
        "200.100.50.1",
        "10.0.0.1",
        "10.100.0.1",
        "hostname RT-00",
        "ip nat outside",
        "ip nat inside",
        "ip nat inside source list 1 interface gigabitEthernet 0/0 overload",
        "ip route 0.0.0.0 0.0.0.0 200.100.50.2",
        "ip route 192.168.3.0 255.255.255.0 10.0.0.2",
        "ip route 192.168.5.0 255.255.255.0 10.0.0.2",
        "ip route 192.168.8.0 255.255.255.0 10.0.0.2",
        "ip route 192.168.10.0 255.255.255.0 10.0.0.2",
        "ip route 192.168.15.0 255.255.255.0 10.0.0.2",
        "ip route 192.168.55.0 255.255.255.0 10.100.0.2",
        "ip route 192.168.56.0 255.255.255.0 10.100.0.2",
        "ip route 192.168.57.0 255.255.255.0 10.100.0.2",
    ]:
        if tem(texto, ip):
            res.passou(f"{nome}: contem '{ip}'")
        else:
            res.falhou(f"{nome}: falta '{ip}'")


def validar_rt01(texto: str, res: Resultado) -> None:
    nome = "RT-01"
    obrigatorios = [
        "hostname RT-01",
        "encapsulation dot1Q 1",
        "ip address 192.168.55.1 255.255.255.0",
        "encapsulation dot1Q 10",
        "ip address 192.168.56.1 255.255.255.0",
        "ip address 10.100.0.2 255.255.255.252",
        "ip route 0.0.0.0 0.0.0.0 10.100.0.1",
        f"dns-server {DNS_CORPORATIVO}",
        "network 192.168.55.0 255.255.255.0",
        "network 192.168.56.0 255.255.255.0",
        "default-router 192.168.55.1",
        "default-router 192.168.56.1",
    ]
    for item in obrigatorios:
        if tem(texto, item):
            res.passou(f"{nome}: contem '{item}'")
        else:
            res.falhou(f"{nome}: falta '{item}'")

    for host in HOSTS_PROIBIDOS:
        if host in texto:
            res.falhou(f"{nome}: DNS proibido '{host}' presente (deve ser {DNS_CORPORATIVO})")
        else:
            res.passou(f"{nome}: sem DNS publico '{host}'")

    # pelo menos um dns-server deve ser o corporativo
    dns_encontrados = re.findall(r"dns-server\s+(\S+)", texto)
    if not dns_encontrados:
        res.falhou(f"{nome}: nenhum 'dns-server' configurado")
    else:
        for d in dns_encontrados:
            if d != DNS_CORPORATIVO:
                res.falhou(f"{nome}: dns-server '{d}' difere de {DNS_CORPORATIVO}")
            else:
                res.passou(f"{nome}: dns-server {DNS_CORPORATIVO}")


def validar_rt02(texto: str, res: Resultado) -> None:
    nome = "RT-02"
    obrigatorios = [
        "hostname RT-02",
        "encapsulation dot1Q 3",
        "ip address 192.168.3.1 255.255.255.0",
        "encapsulation dot1Q 5",
        "ip address 192.168.5.1 255.255.255.0",
        "encapsulation dot1Q 8",
        "ip address 192.168.8.1 255.255.255.0",
        "encapsulation dot1Q 10",
        "ip address 192.168.10.1 255.255.255.0",
        "ip address 10.0.0.2 255.255.255.252",
        "ip route 0.0.0.0 0.0.0.0 10.0.0.1",
        "ip dhcp excluded-address 192.168.3.1 192.168.3.20",
        "ip dhcp excluded-address 192.168.5.1 192.168.5.20",
        "ip dhcp excluded-address 192.168.8.1 192.168.8.20",
        "ip dhcp excluded-address 192.168.10.1 192.168.10.20",
        "network 192.168.5.0 255.255.255.0",
        "network 192.168.8.0 255.255.255.0",
        "network 192.168.10.0 255.255.255.0",
        "default-router 192.168.5.1",
        "default-router 192.168.8.1",
        "default-router 192.168.10.1",
        f"dns-server {DNS_CORPORATIVO}",
    ]
    for item in obrigatorios:
        if tem(texto, item):
            res.passou(f"{nome}: contem '{item}'")
        else:
            res.falhou(f"{nome}: falta '{item}'")

    pools = extrair_pools(texto)
    if len(pools) < 3:
        res.falhou(f"{nome}: esperava >= 3 pools DHCP, achou {len(pools)}")
    else:
        res.passou(f"{nome}: {len(pools)} pools DHCP encontrados")

    for host in HOSTS_PROIBIDOS:
        if host in texto:
            res.falhou(f"{nome}: host proibido '{host}'")


def validar_sw01(texto: str, res: Resultado) -> None:
    nome = "SW-01"
    obrigatorios = [
        "hostname SW-01",
        "vlan 10",
        "name IOT_WIRELESS",
        "switchport mode trunk",
        "switchport trunk allowed vlan 1,10",
        "description UPLINK_TRUNK_RT-01",
        "switchport access vlan 1",
        "switchport access vlan 10",
        "spanning-tree bpduguard enable",
    ]
    for item in obrigatorios:
        if tem(texto, item):
            res.passou(f"{nome}: contem '{item}'")
        else:
            res.falhou(f"{nome}: falta '{item}'")

    # porta Wi-Fi deve estar na VLAN 10
    # extrai bloco da interface f0/6
    m = re.search(
        r"interface fastEthernet 0/6\b(.*?)(?:\ninterface |\Z)",
        texto,
        re.S | re.I,
    )
    if not m:
        res.falhou(f"{nome}: interface fastEthernet 0/6 nao encontrada")
    else:
        bloco = m.group(1)
        if "switchport access vlan 10" in bloco:
            res.passou(f"{nome}: f0/6 na VLAN 10")
        else:
            res.falhou(f"{nome}: f0/6 deve estar em switchport access vlan 10")


def validar_sw02(texto: str, res: Resultado) -> None:
    nome = "SW-02"
    obrigatorios = [
        "hostname SW-02",
        "vlan 3",
        "name SERVIDORES",
        "vlan 5",
        "name COLABORADORES",
        "vlan 8",
        "name TI",
        "vlan 10",
        "name IOT",
        "switchport mode trunk",
        "switchport trunk allowed vlan 3,5,8,10",
        "switchport access vlan 3",
        "switchport access vlan 5",
        "switchport access vlan 8",
        "switchport access vlan 10",
        "spanning-tree bpduguard enable",
    ]
    for item in obrigatorios:
        if tem(texto, item):
            res.passou(f"{nome}: contem '{item}'")
        else:
            res.falhou(f"{nome}: falta '{item}'")

    m = re.search(
        r"interface gigabitEthernet 0/2\b(.*?)(?:\ninterface |\Z)",
        texto,
        re.S | re.I,
    )
    if not m:
        res.falhou(f"{nome}: interface g0/2 nao encontrada")
    else:
        if "switchport access vlan 3" in m.group(1):
            res.passou(f"{nome}: g0/2 na VLAN 3 (servidor)")
        else:
            res.falhou(f"{nome}: g0/2 deve estar em switchport access vlan 3")


def validar_wifi(texto: str, res: Resultado) -> None:
    nome = "WIFI-IOT"
    obrigatorios = [
        "192.168.10.2",
        "192.168.10.1",
        "192.168.15.1",
        "192.168.15.100",
        "192.168.56.2",
        "192.168.56.1",
        "192.168.57.1",
        "192.168.57.100",
        "REDE_IOT_MATRIZ",
        "REDE_IOT_FILIAL",
        DNS_CORPORATIVO,
        "WPA2-Personal",
    ]
    for item in obrigatorios:
        if tem(texto, item):
            res.passou(f"{nome}: contem '{item}'")
        else:
            res.falhou(f"{nome}: falta '{item}'")


def validar_doc_e_readme(doc: str, readme: str, diag: str, res: Resultado) -> None:
    for rotulo, texto in (("DOC", doc), ("README", readme)):
        for item in [
            DNS_CORPORATIVO,
            "192.168.55.1",
            "192.168.56.1",
            "192.168.15.1",
            "192.168.57.1",
            "REDE_IOT_MATRIZ",
            "REDE_IOT_FILIAL",
            "200.100.50.2",
        ]:
            if item in texto:
                res.passou(f"{rotulo}: contem '{item}'")
            else:
                res.falhou(f"{rotulo}: falta '{item}'")

        for host in HOSTS_PROIBIDOS:
            # README/doc podem citar 8.8.8.8 apenas como exemplo de teste Internet
            if host in texto:
                res.avisos.append(
                    f"{rotulo}: contem '{host}' (ok se for exemplo de ping Internet, "
                    f"nao como DNS corporativo)"
                )

    # comando de diagnostico: singular
    if "show ip interface" in diag and "show ip interfaces" not in diag:
        res.passou("DIAG: usa 'show ip interface' (singular)")
    else:
        if "show ip interfaces" in diag:
            res.falhou("DIAG: 'show ip interfaces' invalido — use 'show ip interface'")
        else:
            res.avisos.append("DIAG: nao encontrei o comando 'show ip interface'")

    if "REDE_IOT_FILIAL" in diag:
        res.passou("DIAG: menciona REDE_IOT_FILIAL")
    else:
        res.falhou("DIAG: falta cenario com REDE_IOT_FILIAL")

    # alinhamento de faixa DHCP na doc (preferir .21+)
    if re.search(r"\.21\+", doc) or "Sim (.21+)" in doc:
        res.passou("DOC: faixa DHCP documentada como .21+")
    else:
        res.avisos.append("DOC: confira se a faixa DHCP documentada e .21+ (excludes .1-.20)")


def rodar(root: Path) -> Resultado:
    res = Resultado()
    caminhos: dict[str, Path] = {}
    for chave, nome in ARQUIVOS.items():
        p = root / nome
        caminhos[chave] = p
        if not p.is_file():
            res.falhou(f"Arquivo ausente: {nome}")
        else:
            res.passou(f"Arquivo presente: {nome}")

    # se faltar algo critico de config, aborta validacao de conteudo
    configs = ["RT-00", "RT-01", "RT-02", "SW-01", "SW-02", "WIFI"]
    if any(not caminhos[c].is_file() for c in configs):
        res.falhou("Pula validacao de conteudo: falta arquivo(s) de configuracao")
        return res

    validar_rt00(ler(caminhos["RT-00"]), res)
    validar_rt01(ler(caminhos["RT-01"]), res)
    validar_rt02(ler(caminhos["RT-02"]), res)
    validar_sw01(ler(caminhos["SW-01"]), res)
    validar_sw02(ler(caminhos["SW-02"]), res)
    validar_wifi(ler(caminhos["WIFI"]), res)

    if caminhos["DOC"].is_file() and caminhos["README"].is_file():
        diag = ler(caminhos["DIAG"]) if caminhos["DIAG"].is_file() else ""
        validar_doc_e_readme(ler(caminhos["DOC"]), ler(caminhos["README"]), diag, res)

    return res


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida configs do projeto SENAI")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Diretorio raiz do projeto (padrao: pasta do script/..)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Mostra apenas falhas e aviso final",
    )
    args = parser.parse_args(argv)

    if args.root is not None:
        root = args.root.resolve()
    else:
        # scripts/validar_configs.py -> raiz e o pai de scripts/
        root = Path(__file__).resolve().parent.parent

    if not root.is_dir():
        print(f"ERRO: diretorio nao encontrado: {root}", file=sys.stderr)
        return 1

    res = rodar(root)

    if not args.quiet:
        for m in res.ok:
            print(f"  OK  {m}")
    for m in res.avisos:
        print(f"  AVISO {m}")
    for m in res.falhas:
        print(f"  FALHA {m}")

    print()
    print(
        f"Resultado: {len(res.ok)} OK | {len(res.avisos)} aviso(s) | "
        f"{len(res.falhas)} falha(s)"
    )
    if res.exit_code == 0:
        print("PASSOU — configs consistentes com o plano de enderecoamento.")
    else:
        print("FALHOU — corrija as falhas acima antes de commitar/entregar.")
    return res.exit_code


if __name__ == "__main__":
    sys.exit(main())
