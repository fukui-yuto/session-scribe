# Proxmox VEクラスタでCorosyncの通信が確立できない問題の解決

## 環境

- OS: Proxmox VE 8.3
- ハードウェア: Intel NUC × 2, ミニPC × 1
- ネットワーク: VLAN構成（管理用VLAN 10, ストレージ用VLAN 20）

## 発生した問題

3ノードのProxmox VEクラスタを構築中、`pvecm status`で2番目のノードが`OFFLINE`と表示される。
Corosyncのログに以下のエラーが出力されていた:

```
corosync: [TOTEM ] Retransmit List: 0a0a0a02:5405 FAILED reason(No route to host)
```

## 試したこと

### 1. ファイアウォールルールの確認

Corosyncが使用するポート5405/udpの開放を確認。

```bash
iptables -L -n | grep 5405
```

→ ルールは正しく設定されていたが、問題は解消せず。

### 2. VLANインターフェースの確認

ノード間のVLAN 10上での疎通を確認。

```bash
ping -I vmbr0.10 10.10.10.2
```

→ ping応答あり。L3レベルでは問題なし。

### 3. Corosyncの設定ファイルを確認（成功）

`/etc/corosync/corosync.conf`を確認したところ、`bindnetaddr`が間違ったサブネットを指していた。

```diff
- bindnetaddr: 10.10.20.0
+ bindnetaddr: 10.10.10.0
```

## 解決方法

Corosyncの`bindnetaddr`を正しい管理用VLANのサブネット（10.10.10.0）に修正し、Corosyncを再起動した。

```bash
systemctl restart corosync
pvecm status
```

修正後、全3ノードが`ONLINE`になることを確認。

## 学び

- Corosyncの`bindnetaddr`はノードが通信に使うネットワークアドレスを指定するもの。VLANを分けている場合、管理用VLANのサブネットを正しく指定する必要がある
- ストレージ用VLAN（10.10.20.0）と管理用VLAN（10.10.10.0）を混同しやすい
- `pvecm status`だけでなく`corosync-cfgtool -s`でリング状態も確認するとよい

---

*この記事は [session-scribe](https://github.com/yuto/session-scribe) で生成されました。*

---

<!-- session-scribe metadata
session_id: example-session-001
project: proxmox-lab
generated: 2026-04-20T00:00:00
tool: session-scribe
-->
