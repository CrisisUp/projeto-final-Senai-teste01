# Projeto Final SENAI — Redes (Matriz + Filial)

Projeto acadêmico de redes corporativas simulado no **Cisco Packet Tracer**:
topologia Matriz + Filial, VLANs, Router-on-a-Stick, WAN estática, DHCP e NAT.

## Topologia

```text
                    [Internet / Cloud]
                          |
                     RT-00 (Borda)
                    /            \
            10.0.0.0/30      10.100.0.0/30
                 |                  |
           RT-02 (Matriz)      RT-01 (Filial)
                 |                  |
           SW-02 (Matriz)      SW-01 (Filial)
                 |                  |
        VLANs 3/5/8/10       VLAN 1 (PCs)
        + Wi-Fi IoT          + VLAN 10 (IoT)
```

## Plano de endereçamento (resumo)

| Rede / VLAN | Sub-rede | Gateway | DHCP |
| --- | --- | --- | --- |
| WAN Matriz (RT-00↔RT-02) | 10.0.0.0/30 | — | — |
| WAN Filial (RT-00↔RT-01) | 10.100.0.0/30 | — | — |
| WAN Internet (RT-00↔Cloud) | 200.100.50.0/30 | — | — |
| VLAN 3 SERVIDORES | 192.168.3.0/24 | 192.168.3.1 | Não (statico) |
| VLAN 5 COLABORADORES | 192.168.5.0/24 | 192.168.5.1 | Sim (.21+) |
| VLAN 8 TI | 192.168.8.0/24 | 192.168.8.1 | Sim (.21+) |
| VLAN 10 IOT (Matriz) | 192.168.10.0/24 | 192.168.10.1 | Sim (.21+) |
| VLAN 1 LAN Filial | 192.168.55.0/24 | 192.168.55.1 | Sim (.21+) |
| VLAN 10 IOT (Filial) | 192.168.56.0/24 | 192.168.56.1 | Sim (.21+) |
| WLAN Wi-Fi Matriz | 192.168.15.0/24 | 192.168.15.1 | No roteador Wi-Fi |
| WLAN Wi-Fi Filial | 192.168.57.0/24 | 192.168.57.1 | No roteador Wi-Fi |

**DNS corporativo (todos os pools DHCP):** `192.168.3.10` (Servidor Matriz)

**Hosts estáticos importantes**

- Servidor DNS/Matriz: IP `192.168.3.10/24`, GW `192.168.3.1`
- Wi-Fi Matriz WAN: `192.168.10.2` (SSID `REDE_IOT_MATRIZ`)
- Wi-Fi Filial WAN: `192.168.56.2` (SSID `REDE_IOT_FILIAL`)

**Hosts via DHCP** (esperado)

- Matriz VLAN 5/8/10 e Filial VLAN 1/10: IP a partir de `.21`, GW da VLAN, DNS `192.168.3.10`

## Credenciais do lab

> **Somente ambiente acadêmico / Packet Tracer.** Não usar em produção.  
> Equipamentos: RT-00, RT-01, RT-02, SW-01, SW-02.

| Onde | Usuário / modo | Senha |
| --- | --- | --- |
| Enable (roteadores e switches) | modo privileged (`enable`) | `Senai@Enable2026` |
| Login SSH / console | usuário `admin` | `Senai@Admin2026` |
| Wi-Fi IoT Matriz — SSID `REDE_IOT_MATRIZ` | WPA2-Personal | `Senai@IoT2026` |
| Wi-Fi IoT Filial — SSID `REDE_IOT_FILIAL` | WPA2-Personal | `Senai@IoT2026` |

**Como logar (exemplo SSH):**

```text
ssh admin@<IP-do-equipamento>
# senha: Senai@Admin2026
enable
# senha: Senai@Enable2026
```

## Arquivos

| Arquivo | Descrição |
| --- | --- |
| `Projeto-final-test1.pkt` | Topologia Packet Tracer |
| `Documentacao Tecnica.txt` | Documentação técnica completa (IP plan + hosts) |
| `Comandos de Diagnosticos e Validacao.txt` | Comandos de diagnóstico/teste |
| `codigo RT-00.txt` | Roteador de borda (rotas + NAT + Internet) |
| `codigo RT-01.txt` | Roteador da Filial (on-a-stick + DHCP) |
| `codigo RT-02.txt` | Roteador da Matriz (on-a-stick + DHCP) |
| `codigo SW-01.txt` | Switch da Filial (VLAN 1 e 10, trunk) |
| `codigo SW-02.txt` | Switch da Matriz (VLANs 3/5/8/10, trunk) |
| `codigo WIFI-IOT.txt` | Config dos roteadores Wi-Fi (GUI) |
| `TESTES.md` | Matriz de testes (automáticos + Packet Tracer) |
| `scripts/validar_configs.py` | Valida configs .txt × IP plan |

## Como usar no Packet Tracer

1. Abra `Projeto-final-test1.pkt` no Cisco Packet Tracer.
2. Em cada equipamento, abra a **CLI** e cole o conteúdo do `codigo *.txt` correspondente.
3. Configure os roteadores Wi-Fi pela **GUI** conforme `codigo WIFI-IOT.txt`.
4. Configure os hosts:
   - Servidor: estático `192.168.3.10/24`, GW `192.168.3.1`
   - PCs Matriz/Filial: **DHCP** (ou IP estático conforme a doc técnica)
5. Cloud/Internet: se não existir no `.pkt`, crie o dispositivo e use gateway `200.100.50.2` em `RT-00 g0/0`.
6. Salve o `.pkt` e valide conforme `TESTES.md` e `Comandos de Diagnosticos e Validacao.txt`.

## Validação

### Automatizado (configs do repositório)

```bash
python scripts/validar_configs.py
```

O script confere se os `codigo *.txt`, a documentação e o README batem com o IP plan (DNS corporativo, gateways, trunks, rotas, NAT, SSIDs). Exit code `0` = OK.

### Manual (Packet Tracer)

Comandos mínimos no lab (detalhe completo em `TESTES.md`):

```text
SW-02# show vlan brief
SW-02# show interfaces trunk
RT-02# show ip interface brief
RT-02# show ip route
RT-00# show ip route
RT-00# show ip nat translations
RT-01# show ip dhcp pool
PC-01> ping 192.168.3.10
PC-04> ping 192.168.8.1
PC> ipconfig /all   (DNS deve ser 192.168.3.10)
```

### Fluxo recomendado

1. Editar configs/doc  
2. `python scripts/validar_configs.py`  
3. Validar o cenário afetado no Packet Tracer  
4. Commitar

## Segurança (ACLs + hardening)

| Recurso | Onde |
|---|---|
| `enable secret`, SSH, banner, `no ip http server` | RT-00/01/02, SW-01/02 |
| ACL IoT → nega TI e Colaboradores (permite DNS/servidor) | RT-02 `ACL_IOT_IN` |
| ACL Colaboradores → nega TI (permite DNS/servidor) | RT-02 `ACL_COLAB_IN` |
| ACL IoT Filial → nega TI da Matriz | RT-01 `ACL_FILIAL_IOT_IN` |
| Port security + DHCP snooping + portas ociosas down | SW-01, SW-02 |

Credenciais do lab (enable, SSH e Wi-Fi): ver seção **[Credenciais do lab](#credenciais-do-lab)**.

## O que foi corrigido / completado

- Documentação corrigida (arquivos de doc com o conteúdo certo)
- **DNS corporativo unico** `192.168.3.10` em todos os pools (filial não usa mais 8.8.8.8)
- DHCP nas VLANs da Matriz (5, 8, 10) e da Filial (1 e 10); faixa `.21+`
- VLAN 10 IoT da Filial implementada de fato (antes a porta Wi-Fi ficava na VLAN 1)
- Trunks com `switchport trunk allowed vlan` explícito
- NAT + rota padrão + interface de Internet no RT-00 (Cloud `200.100.50.2`)
- Configs de hosts (servidor e PCs) documentadas
- `spanning-tree portfast` + `bpduguard` nas portas de acesso
- **ACLs inter-VLAN** (IoT/Colab ≠ TI) e **hardening** (SSH, secrets, banners, port security, DHCP snooping)
- Comando de diagnóstico corrigido: `show ip interface` (singular)
- SSIDs `REDE_IOT_MATRIZ` e `REDE_IOT_FILIAL` na doc e nos testes
- `TESTES.md` + `scripts/validar_configs.py` (validação automática das configs)
- `README.md`, `codigo WIFI-IOT.txt` e `.gitignore`
