# Testes — Projeto SENAI (Matriz + Filial)

Este arquivo define **como validar** o projeto em três camadas:

1. **Automatizado** — `scripts/validar_configs.py` (configs .txt × IP plan)
2. **Manual no Packet Tracer** — cenários de lab com critério de aceite
3. **Checklist de entrega** — o que anexar no relatório

Antes de commitar ou entregar, rode:

```text
python scripts/validar_configs.py
```

Exit code `0` = configs consistentes. Exit code `1` = há falhas.

---

## 1. Testes automatizados (arquivos do repositório)

Script: `scripts/validar_configs.py`  
Não precisa abrir o Packet Tracer. Checa se os `codigo *.txt`, doc e README batem com o plano.

| ID | O que valida | Critério |
|---|---|---|
| A01 | Arquivos presentes | RT-00/01/02, SW-01/02, WIFI, DOC, DIAG, README |
| A02 | RT-00 | WANs, NAT, rotas de retorno, default Internet |
| A03 | RT-01 | Subifs VLAN 1 e 10, default WAN, **DNS 192.168.3.10**, sem 8.8.8.8 |
| A04 | RT-02 | 4 subifs, default WAN, excludes .1–.20, pools 5/8/10 |
| A05 | SW-01 | Trunk `1,10`, PCs na VLAN 1, Wi-Fi na VLAN **10** |
| A06 | SW-02 | Trunk `3,5,8,10`, servidor na VLAN 3, portas 5/8/10 |
| A07 | WIFI-IOT | IPs MAT/FIL, SSIDs, DNS corporativo |
| A08 | Doc/README | Gateways, DNS, SSIDs, Cloud 200.100.50.2 |
| A09 | Diagnóstico | `show ip interface` (singular) e cenário REDE_IOT_FILIAL |
| A10 | Hardening | enable secret, banner, SSH, no http server nos equipamentos |
| A11 | ACLs RT-02 | ACL_IOT_IN / ACL_COLAB_IN + `ip access-group` nas subifs |
| A12 | ACL RT-01 | ACL_FILIAL_IOT_IN na VLAN 10 |
| A13 | L2 | port security, DHCP snooping, portas ociosas nos switches |

**Como rodar**

```bash
# na raiz do projeto
python scripts/validar_configs.py

# ou com caminho explícito
python scripts/validar_configs.py --root "C:\Users\Admin\Desktop\projeto-final-Senai-teste01"

# só falhas
python scripts/validar_configs.py -q
```

> Requisito: Python 3.8+ (stdlib apenas — sem pip).

---

## 2. Validação manual no Packet Tracer

Abra `Projeto-final-test1.pkt`, cole as configs dos `codigo *.txt`, configure hosts/Wi-Fi e execute os testes abaixo.

### 2.1 Inventário e L2

| ID | Equipamento | Ação / comando | Critério de aceite |
|---|---|---|---|
| M01 | SW-02 | `show vlan brief` | VLANs 3,5,8,10 ativas com as portas do mapa |
| M02 | SW-02 | `show interfaces trunk` | Trunk em g0/1; allowed `3,5,8,10` |
| M03 | SW-01 | `show vlan brief` | VLAN 1 (PCs) e VLAN 10 (Wi-Fi) |
| M04 | SW-01 | `show interfaces trunk` | Trunk em g0/1; allowed `1,10` |
| M05 | SW-01 | `show interfaces f0/6 switchport` | Access na VLAN 10 |

### 2.2 Camada 3 e rotas

| ID | Equipamento | Ação / comando | Critério de aceite |
|---|---|---|---|
| M06 | RT-02 | `show ip interface brief` | g0/0.x e g0/1 up/up com IPs certos |
| M07 | RT-02 | `show ip route` | Default via `10.0.0.1` (RT-00) |
| M08 | RT-01 | `show ip interface brief` | g0/0.1 = .55.1, g0/0.10 = .56.1, g0/1 = 10.100.0.2 |
| M09 | RT-01 | `show ip route` | Default via `10.100.0.1` |
| M10 | RT-00 | `show ip route` | 192.168.3/5/8/10/15 via 10.0.0.2; 55/56/57 via 10.100.0.2 |
| M11 | RT-00 | `show ip route` | Default via `200.100.50.2` (se Cloud existir no .pkt) |

### 2.3 DHCP e hosts

| ID | Host | Ação | Critério de aceite |
|---|---|---|---|
| M12 | Servidor | IP estático | `192.168.3.10/24`, GW `192.168.3.1`, DNS local |
| M13 | PC-04 (VLAN 5) | DHCP + `ipconfig /all` | IP `.21+`, GW `192.168.5.1`, DNS `192.168.3.10` |
| M14 | PC-05 (VLAN 8) | DHCP + `ipconfig /all` | IP `.21+`, GW `192.168.8.1`, DNS `192.168.3.10` |
| M15 | PC-01 (filial) | DHCP + `ipconfig /all` | IP `.21+`, GW `192.168.55.1`, DNS `192.168.3.10` |
| M16 | RT-01 | `show ip dhcp pool` / `binding` | Pools VLAN1 e VLAN10 presentes; clientes obtendo IP |

### 2.4 Conectividade

| ID | De | Para | Ação | Critério |
|---|---|---|---|---|
| M17 | PC-01 filial | GW filial | `ping 192.168.55.1` | Sucesso |
| M18 | PC-01 | Servidor | `ping 192.168.3.10` | Sucesso (via RT-01→RT-00→RT-02) |
| M19 | PC-04 | GW TI | `ping 192.168.8.1` | Sucesso inter-VLAN |
| M20 | PC-04 | PC-05 | `ping` host VLAN 8 | Sucesso |
| M21 | PC qualquer | Internet | `ping 8.8.8.8` | Sucesso **somente se** Cloud/ISP existir |
| M22 | PC | destino | `tracert` / `traceroute` | Caminho coerente com o mapa de rotas |

### 2.5 NAT

| ID | Equipamento | Ação | Critério |
|---|---|---|---|
| M23 | RT-00 | `show ip nat translations` | Entrada após ping Internet (fora: 200.100.50.1) |
| M24 | RT-00 | `show ip nat statistics` | inside/outside coerentes com g0/1,g0/2 vs g0/0 |

### 2.6 Wi-Fi IoT

| ID | Dispositivo | Ação | Critério |
|---|---|---|---|
| M25 | WIFI-MAT | Config GUI | WAN 192.168.10.2/24, GW 192.168.10.1, DNS 192.168.3.10, WLAN 192.168.15.1, SSID REDE_IOT_MATRIZ, WPA2 |
| M26 | WIFI-FIL | Config GUI | WAN 192.168.56.2/24, GW 192.168.56.1, DNS 192.168.3.10, WLAN 192.168.57.1, SSID REDE_IOT_FILIAL, WPA2 |
| M27 | Device Wi-Fi Matriz | DHCP + ping | IP 192.168.15.1xx; ping 192.168.15.1 e 192.168.3.10 |
| M28 | Device Wi-Fi Filial | DHCP + ping | IP 192.168.57.1xx; ping 192.168.57.1 e 192.168.3.10 |

### 2.7 Hardening e ACLs

| ID | Equipamento | Ação | Critério de aceite |
|---|---|---|---|
| M32 | Qualquer IOS | `show run | include enable secret` | `enable secret` presente (não `enable password`) |
| M33 | Qualquer IOS | `show run | include banner` | banner MOTD com texto SENAI |
| M34 | Qualquer IOS | `show ip ssh` / tentar SSH | SSH ativo; Telnet recusado (`transport input ssh`) |
| M35 | RT-02 | `show access-lists` | ACL_IOT_IN e ACL_COLAB_IN com contadores |
| M36 | RT-02 | `show ip interface g0/0.10` | `ip access-group ACL_IOT_IN in` |
| M37 | RT-02 | `show ip interface g0/0.5` | `ip access-group ACL_COLAB_IN in` |
| M38 | RT-01 | `show ip interface g0/0.10` | `ip access-group ACL_FILIAL_IOT_IN in` |
| M39 | IoT → TI | PC IoT ping 192.168.8.1 | **Falha** (negado pela ACL) |
| M40 | IoT → servidor | PC IoT ping 192.168.3.10 | **Sucesso** (permitido) |
| M41 | Colab → TI | PC-04 ping host TI (não o GW se preferir) | **Falha** em host TI; GW pode responder se for gateway |
| M42 | Colab → servidor | PC-04 ping 192.168.3.10 | **Sucesso** |
| M43 | SW-01/SW-02 | `show port-security` | Portas access com sticky / maximum 1 |
| M44 | SW-01/SW-02 | `show ip dhcp snooping` | Snooping ativo; trunk em trust |
| M45 | SW | `show ip dhcp snooping binding` | (opcional) bindings após DHCP |
| M46 | Portas ociosas | `show ip interface brief` | f0/7-24 administrativamente down |

> Nota ACL: negar **hosts** da TI, não apenas a gateway — o gateway da VLAN TI (`192.168.8.1`) pode continuar respondendo a ICMP dependendo da ordem/escopo da ACL. O teste crítico é host real da VLAN 8 (ou outro IP de host TI) vs host IoT/Colab.

### 2.8 Cloud / Internet (opcional no .pkt)

| ID | Ação | Critério |
|---|---|---|
| M47 | Conferir Cloud no .pkt | Existe ISP com gateway `200.100.50.2` em RT-00 g0/0 |
| M48 | Se não existir | Criar Cloud, igualar IP e repetir M11–M12, M21, M23–M24 |
| M49 | Sem Cloud | Cenários Matriz↔Filial (M17–M20) **continuam válidos** |

---

## 3. Checklist de entrega (prints / evidências)

Anexe ao relatório (mínimo):

- [ ] `RT-02#show running-config`
- [ ] `SW-02#show running-config`
- [ ] `SW-01#show vlan brief`
- [ ] `SW-02#show interfaces trunk`
- [ ] `RT-00#show ip route`
- [ ] `RT-00#show ip nat translations` (se houver Cloud)
- [ ] `RT-01#show ip dhcp pool`
- [ ] `RT-02#show access-lists`
- [ ] `RT-02#show ip interface g0/0.10` (ACL_IOT_IN)
- [ ] `SW-02#show port-security`
- [ ] `ipconfig /all` de um PC da Matriz (DNS `192.168.3.10`)
- [ ] `ipconfig /all` de um PC da Filial (DNS `192.168.3.10`)
- [ ] Ping Filial → Matriz (`192.168.3.10`)
- [ ] Ping inter-VLAN na Matriz (ex.: `192.168.8.1` para Colab→GW TI)
- [ ] Ping IoT → TI (**deve falhar**) e IoT → servidor (**deve funcionar**)
- [ ] (Opcional) Ping Internet + `show ip nat translations`
- [ ] (Opcional) Teste Wi-Fi SSID `REDE_IOT_MATRIZ` e `REDE_IOT_FILIAL`
- [ ] (Opcional) SSH para o equipamento (usuário `admin`)

---

## 4. Matriz rápida — o que cobre o quê

```text
Arquivo configs (.txt)  →  python scripts/validar_configs.py   [automático]
Topologia .pkt + CLI    →  testes M01–M28                      [manual PT]
Internet / NAT          →  M11, M21, M23–M24, M29–M31          [depende do Cloud]
Entrega acadêmica       →  seção 3 (prints)
```

---

## 5. Regressão (evitar reverter correções)

O script falha se alguém reintroduzir problemas já corrigidos, por exemplo:

- DNS da filial voltar a ser `8.8.8.8`
- Trunk sem `allowed vlan`
- VLAN 10 da filial com o Wi-Fi na VLAN 1
- Doc com faixa DHCP divergente dos excludes (avisos/falhas conforme o texto)
- `show ip interfaces` inválido no arquivo de diagnóstico

**Fluxo recomendado**

1. Editar configs/doc  
2. `python scripts/validar_configs.py`  
3. Se OK, validar no Packet Tracer o cenário afetado  
4. Commitar  

---

## 6. Limitações conhecidas

| Limitação | Impacto |
|---|---|
| Script lê só `.txt`/`.md`, não o `.pkt` | Topologia real do PT precisa de teste manual |
| Cloud/ISP pode não existir no `.pkt` | Testes de Internet podem falhar sem ser bug de config |
| Packet Tracer não roda CI nativo | Validação “de lab” é humana |
| Passphrase Wi-Fi em texto no repo | Aceitável em aula; não usar em produção real |
