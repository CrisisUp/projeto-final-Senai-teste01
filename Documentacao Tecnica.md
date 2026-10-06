# Documentação Técnica — Projeto de Redes (SENAI)

**Matriz + Filial | VLANs | Router-on-a-Stick | WAN estática | NAT | ACLs | Hardening**

Arquivo de referência técnica do projeto. O guia rápido está no [`README.md`](README.md); a matriz de testes está em [`TESTES.md`](TESTES.md).

---

## 1. Visão geral

Topologia corporativa com duas sedes interligadas por WAN estática e borda com Internet via NAT overload.

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

---

## 2. Equipamentos

| Hostname | Dispositivo | Papel |
|----------|-------------|-------|
| RT-00 | Router Cisco (borda) | WAN Matriz/Filial + Internet |
| RT-01 | Router Cisco (filial) | Gateway filial (on-a-stick) |
| RT-02 | Router Cisco (matriz) | Gateway matriz (on-a-stick) |
| SW-01 | Switch Cisco 2960 | Access filial |
| SW-02 | Switch Cisco 2960 | Access matriz |
| WIFI-MAT | WRT300N | Wi-Fi IoT matriz |
| WIFI-FIL | WRT300N | Wi-Fi IoT filial |
| Server | PC-Server | DNS/Servidor matriz |

---

## 3. Plano de endereçamento

### 3.1 WANs (ponto a ponto `/30`)

| Link | Rede | Extremidades |
|------|------|--------------|
| RT-00 ↔ RT-02 | 10.0.0.0/30 | `.1` = RT-00 \| `.2` = RT-02 |
| RT-00 ↔ RT-01 | 10.100.0.0/30 | `.1` = RT-00 \| `.2` = RT-01 |
| RT-00 ↔ Cloud | 200.100.50.0/30 | `.1` = RT-00 \| `.2` = ISP/Cloud |

> **Atenção (Cloud/Internet):** a config do RT-00 pressupõe um dispositivo Cloud/ISP no `.pkt` com gateway `200.100.50.2`.  
> Se o `Projeto-final-test1.pkt` não tiver Cloud, crie o dispositivo, conecte em RT-00 `g0/0` e iguale o IP do ISP a `200.100.50.2` (ou ajuste a rota padrão e o IP de `g0/0` em `codigo RT-00.txt`).  
> Sem Cloud, o cenário Matriz↔Filial continua válido (rotas estáticas).

### 3.2 Rede Matriz (via RT-02 / SW-02)

| VLAN | Nome | Sub-rede | Gateway | DHCP |
|------|------|----------|---------|------|
| 3 | SERVIDORES | 192.168.3.0/24 | 192.168.3.1 | Não (estático) |
| 5 | COLABORADORES | 192.168.5.0/24 | 192.168.5.1 | Sim (`.21+`) |
| 8 | TI | 192.168.8.0/24 | 192.168.8.1 | Sim (`.21+`) |
| 10 | IOT | 192.168.10.0/24 | 192.168.10.1 | Sim (`.21+`) |

**Exceções DHCP (RT-02):** `.1` a `.20` em cada VLAN (gateway + hosts estáticos).

**Hosts estáticos Matriz**

| Host | IP | Observação |
|------|-----|------------|
| Servidor DNS/Matriz | 192.168.3.10 | DNS corporativo |
| WIFI-MAT WAN | 192.168.10.2 | GW 192.168.10.1, DNS 192.168.3.10 |
| WIFI-MAT LAN/WLAN | 192.168.15.1/24 | DHCP 192.168.15.100–149 |

### 3.3 Rede Filial (via RT-01 / SW-01)

| VLAN | Nome | Sub-rede | Gateway | DHCP |
|------|------|----------|---------|------|
| 1 | LAN_FILIAL | 192.168.55.0/24 | 192.168.55.1 | Sim (`.21+`) |
| 10 | IOT_WIRELESS | 192.168.56.0/24 | 192.168.56.1 | Sim (`.21+`) |

**Exceções DHCP (RT-01):** `.1` a `.20` em cada VLAN.

**Hosts estáticos Filial**

| Host | IP | Observação |
|------|-----|------------|
| WIFI-FIL WAN | 192.168.56.2 | GW 192.168.56.1, DNS 192.168.3.10 |
| WIFI-FIL LAN/WLAN | 192.168.57.1/24 | DHCP 192.168.57.100–149 |

**DNS corporativo (todos os pools DHCP):** `192.168.3.10` (Servidor Matriz) — padrão único da rede.

---

## 4. Configuração dos hosts (Packet Tracer)

### 4.1 Servidor Matriz (estático — fora de DHCP)

| Campo | Valor |
|-------|-------|
| IP | 192.168.3.10 |
| Subnet Mask | 255.255.255.0 |
| Gateway | 192.168.3.1 |
| DNS Server | 127.0.0.1 (ele próprio) ou 192.168.3.10 |
| Porta | SW-02 g0/2 (VLAN 3) |
| Serviços | DNS (e outros conforme o cenário do `.pkt`) |

### 4.2 PCs da Matriz

| Host | VLAN | Config | Esperado |
|------|------|--------|----------|
| PC-04 | 5 Colaboradores | DHCP | IP 192.168.5.21+, GW 192.168.5.1, DNS 192.168.3.10 |
| PC-05 | 8 TI | DHCP | IP 192.168.8.21+, GW 192.168.8.1, DNS 192.168.3.10 |

Portas: SW-02 `f0/4` e `f0/5`.

### 4.3 PCs da Filial

| Host | VLAN | Config | Esperado |
|------|------|--------|----------|
| PC-01, PC-02, PC-03 | 1 LAN | DHCP | IP 192.168.55.21+, GW 192.168.55.1, DNS 192.168.3.10 |

Portas: SW-01 `f0/4`, `f0/2`, `f0/3`.

### 4.4 Roteadores Wi-Fi (GUI — ver `codigo WIFI-IOT.txt`)

| Device | WAN | WLAN | SSID |
|--------|-----|------|------|
| WIFI-MAT | 192.168.10.2/24 | 192.168.15.1/24 | REDE_IOT_MATRIZ |
| WIFI-FIL | 192.168.56.2/24 | 192.168.57.1/24 | REDE_IOT_FILIAL |

Ambos: DNS `192.168.3.10`, WPA2-Personal, passphrase `Senai@IoT2026`.

> Se o `.pkt` já tiver IPs estáticos antigos nos hosts: prefira DHCP ou ajuste para os valores das tabelas acima.

---

## 5. Mapa de portas

### SW-02 (Matriz)

| Porta | Modo | VLAN | Destino |
|-------|------|------|---------|
| g0/1 | trunk | 3,5,8,10 | RT-02 g0/0 |
| g0/2 | access | 3 | Servidor Matriz (192.168.3.10) |
| f0/4 | access | 5 | PC-04 (DHCP) |
| f0/5 | access | 8 | PC-05 (DHCP) |
| f0/6 | access | 10 | WIFI-MAT (porta WAN) |
| f0/7–24 | shutdown | — | Portas ociosas |

### SW-01 (Filial)

| Porta | Modo | VLAN | Destino |
|-------|------|------|---------|
| g0/1 | trunk | 1,10 | RT-01 g0/0 |
| f0/2 | access | 1 | PC-02 (DHCP) |
| f0/3 | access | 1 | PC-03 (DHCP) |
| f0/4 | access | 1 | PC-01 (DHCP) |
| f0/6 | access | 10 | WIFI-FIL (porta WAN) |
| f0/7–24 | shutdown | — | Portas ociosas |

---

## 6. Roteamento

### RT-02 (Matriz)

- Default route: `0.0.0.0/0` → `10.0.0.1` (RT-00)

### RT-01 (Filial)

- Default route: `0.0.0.0/0` → `10.100.0.1` (RT-00)

### RT-00 (Borda)

| Destino | Via |
|---------|-----|
| 192.168.3.0/24, 5.0/24, 8.0/24, 10.0/24, 15.0/24 | 10.0.0.2 (RT-02) |
| 192.168.55.0/24, 56.0/24, 57.0/24 | 10.100.0.2 (RT-01) |
| 0.0.0.0/0 (Internet) | 200.100.50.2 (Cloud/ISP) |

- NAT overload: ACL 1 (redes internas) → `g0/0`

---

## 7. Segurança / hardening aplicado

### 7.1 Hardening IOS (RT-00, RT-01, RT-02, SW-01, SW-02)

- `enable secret` (lab: `Senai@Enable2026`) + `username admin` (`Senai@Admin2026`)
- `service password-encryption`
- SSH habilitado (`crypto key rsa` + `line vty transport input ssh`)
- `no ip http server` / `no ip http secure-server`
- `banner motd` de advertência
- console/vty: `login local`, `exec-timeout`, `logging synchronous`

### 7.2 ACLs inter-VLAN

| ACL | Onde | Política |
|-----|------|----------|
| `ACL_IOT_IN` | RT-02 g0/0.10 in | IoT: DHCP + DNS/servidor; **não** acessa TI nem Colab |
| `ACL_COLAB_IN` | RT-02 g0/0.5 in | Colab: DHCP + DNS/servidor; **não** acessa TI |
| `ACL_FILIAL_IOT_IN` | RT-01 g0/0.10 in | IoT filial: DHCP + DNS; **não** acessa TI da Matriz |

VLAN 8 (TI) e VLAN 1 (PCs filial) sem ACL restritiva de saída (admins/uso geral).

### 7.3 Hardening L2 (SW-01 / SW-02)

- Trunks com `switchport trunk allowed vlan` explícito
- Portas de acesso: `portfast` + `bpduguard`
- Port security: `maximum 1`, `violation shutdown`, `mac-address sticky`
- DHCP snooping (uplink em `trust`)
- Portas ociosas `f0/7-24` em `shutdown`

### 7.4 Wi-Fi

- WPA2-Personal (AES)
  - SSID `REDE_IOT_MATRIZ` (Matriz)
  - SSID `REDE_IOT_FILIAL` (Filial)

### 7.5 Outros

- DHCP com faixas excluídas (`.1`–`.20`) para gateways e hosts estáticos
- NAT na borda para saída à Internet
- DNS corporativo único (`192.168.3.10`) em todos os pools

> **Atenção:** senhas em texto são apenas para o **LAB SENAI**.  
> Não usar em produção; rotacionar e guardar em cofre.  
> Credenciais completas: [`README.md`](README.md) → *Credenciais do lab*.

---

## 8. Decisões de design

| Decisão | Justificativa curta |
|---------|---------------------|
| Router-on-a-Stick (RT-01/RT-02) | Subifs 802.1Q centralizam VLANs; lab enxuto |
| Rotas estáticas (sem OSPF) | Topologia pequena; previsível e auditável |
| WAN `/30` | Ponto a ponto sem desperdício de IPs |
| VLAN 10 IoT separada | Segmenta dispositivos de baixa confiança |
| ACL IoT/Colab negam TI | Reduz movimento lateral; só DNS/servidor |
| DHCP a partir de `.21` | Reserva `.1`–`.20` p/ gateways e estáticos |
| DNS único `192.168.3.10` | Padroniza resolução Matriz e Filial |
| NAT overload só no RT-00 | Saída única à Internet; IP privado interno |
| Wi-Fi WAN estático | Teste determinístico, sem DHCP corporativo |
| Hardening básico (SSH/secret/L2) | Boas práticas de lab defensáveis |
| Script valida os `.txt` | `.pkt` é binário; protege IP plan no git |

---

## 9. Limites do cenário

Este é um **projeto acadêmico em Packet Tracer**, não produção.

**Não implementado (consciente):**

- OSPF/EIGRP, HSRP/VRRP, link de backup
- Firewall stateful / zone-based (só ACL extended)
- AAA (TACACS/RADIUS) — só usuário local `admin`
- IPv6, QoS, SNMP/syslog server
- Backup automático de configs
- Cloud/ISP real (depende do `.pkt` com `200.100.50.2`)
- ACL de saída em todas as VLANs (TI e VLAN 1 filial livres)
- Teste automatizado do arquivo `.pkt` (só configs `.txt`)

**Como ler o projeto:** topologia coerente + IP plan + segmentação IoT + hardening + testes.  
Escalar (GNS3/EVE-NG, OSPF, HA) seria outro nível de entrega.

---

## 10. Arquivos do projeto

| Arquivo | Conteúdo |
|---------|----------|
| `Projeto-final-test1.pkt` | Topologia Packet Tracer |
| `Documentacao Tecnica.md` | Este documento |
| `Comandos de Diagnosticos e Validacao.txt` | Comandos de teste/debug |
| `codigo RT-00.txt` | Config completa RT-00 |
| `codigo RT-01.txt` | Config completa RT-01 |
| `codigo RT-02.txt` | Config completa RT-02 |
| `codigo SW-01.txt` | Config completa SW-01 |
| `codigo SW-02.txt` | Config completa SW-02 |
| `codigo WIFI-IOT.txt` | Config dos roteadores Wi-Fi |
| `TESTES.md` | Matriz de testes (auto + PT) |
| `scripts/validar_configs.py` | Validação automática das configs |
| `.github/workflows/validar-configs.yml` | CI (GitHub Actions) no push/PR |
| `README.md` | Guia rápido do repositório |

---

## 11. Como aplicar as configs no Packet Tracer

1. Abra `Projeto-final-test1.pkt` no Cisco Packet Tracer.
2. Clique em cada equipamento → **CLI**.
3. Cole o conteúdo do arquivo `.txt` correspondente.
4. Configure os hosts conforme a **seção 4** (DHCP ou estático).
5. Configure os WRT300N pela GUI (`codigo WIFI-IOT.txt`).
6. Se preciso, ajuste no `.pkt`:
   - Cloud/ISP: gateway `200.100.50.2` em RT-00 `g0/0`
   - IPs dos hosts conforme o plano acima
7. Salve o `.pkt` e valide com os comandos de diagnóstico (`TESTES.md` / `Comandos de Diagnosticos e Validacao.txt`).

---

## 12. Validação rápida do projeto

```bash
python scripts/validar_configs.py
```

**CI:** o workflow `.github/workflows/validar-configs.yml` roda o script a cada push e pull request no GitHub.

Comandos mínimos no lab:

```text
SW-02# show vlan brief
SW-02# show interfaces trunk
RT-02# show ip interface brief
RT-02# show ip route
RT-00# show ip route
RT-00# show ip nat translations
RT-02# show access-lists
PC-01> ping 192.168.3.10
PC> ipconfig /all   (DNS deve ser 192.168.3.10)
```
