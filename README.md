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
| VLAN 5 COLABORADORES | 192.168.5.0/24 | 192.168.5.1 | Sim |
| VLAN 8 TI | 192.168.8.0/24 | 192.168.8.1 | Sim |
| VLAN 10 IOT (Matriz) | 192.168.10.0/24 | 192.168.10.1 | Sim |
| VLAN 1 LAN Filial | 192.168.55.0/24 | 192.168.55.1 | Sim |
| VLAN 10 IOT (Filial) | 192.168.56.0/24 | 192.168.56.1 | Sim |
| WLAN Wi-Fi Matriz | 192.168.15.0/24 | 192.168.15.1 | No roteador Wi-Fi |
| WLAN Wi-Fi Filial | 192.168.57.0/24 | 192.168.57.1 | No roteador Wi-Fi |

## Hosts estáticos importantes

- Servidor DNS/Matriz: `192.168.3.10`
- Wi-Fi Matriz WAN: `192.168.10.2` (SSID `REDE_IOT_MATRIZ`)
- Wi-Fi Filial WAN: `192.168.56.2` (SSID `REDE_IOT_FILIAL`)

## Arquivos

| Arquivo | Descrição |
| --- | --- |
| `Projeto-final-test1.pkt` | Topologia Packet Tracer |
| `Documentacao Tecnica.txt` | Documentação técnica completa |
| `Comandos de Diagnosticos e Validacao.txt` | Comandos de diagnóstico/teste |
| `codigo RT-00.txt` | Roteador de borda (rotas + NAT + Internet) |
| `codigo RT-01.txt` | Roteador da Filial (on-a-stick + DHCP) |
| `codigo RT-02.txt` | Roteador da Matriz (on-a-stick + DHCP) |
| `codigo SW-01.txt` | Switch da Filial (VLAN 1 e 10, trunk) |
| `codigo SW-02.txt` | Switch da Matriz (VLANs 3/5/8/10, trunk) |
| `codigo WIFI-IOT.txt` | Config dos roteadores Wi-Fi (GUI) |

## Como usar no Packet Tracer

1. Abra `Projeto-final-test1.pkt` no Cisco Packet Tracer.
2. Em cada equipamento, abra a **CLI** e cole o conteúdo do `codigo *.txt` correspondente.
3. Configure os roteadores Wi-Fi pela **GUI** conforme `codigo WIFI-IOT.txt`.
4. Ajuste no `.pkt`, se preciso:
   - Gateway do Cloud/ISP em `RT-00 g0/0` (padrão: `200.100.50.2`)
   - IPs dos PCs/servidor conforme o plano acima
5. Valide com os comandos de `Comandos de Diagnosticos e Validacao.txt`.

## Validação mínima

```text
SW-02# show vlan brief
SW-02# show interfaces trunk
RT-02# show ip interface brief
RT-02# show ip route
RT-00# show ip route
RT-00# show ip nat translations
PC-01> ping 192.168.3.10
PC-04> ping 192.168.8.1
```

## O que foi corrigido / completado

- Documentação corrigida (arquivos de doc com o conteúdo certo)
- DHCP nas VLANs da Matriz (5, 8, 10) e da Filial (1 e 10)
- VLAN 10 IoT da Filial implementada de fato (antes a porta Wi-Fi ficava na VLAN 1)
- Trunks com `switchport trunk allowed vlan` explícito
- NAT + rota padrão + interface de Internet no RT-00
- Configs limpas (um bloco por equipamento, sem `end`/`write memory` duplicados)
- `README.md` com topologia, IP plan e passo a passo
