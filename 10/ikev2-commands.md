# IKEv2 and IPsec Commands

The following commands configure and verify IKEv2-based IPsec tunnels on Cisco IOS/IOS XE. IKEv2 replaces the legacy `crypto isakmp` (IKEv1) commands with a structured set of objects: proposal, policy, keyring, and profile.

---

## Configuration Commands

### crypto ikev2 proposal

Defines the cryptographic algorithms for IKE SA negotiation. Peers must agree on at least one common proposal.

```
R1(config)#crypto ikev2 proposal myproposal
R1(config-ikev2-proposal)#encryption aes-cbc-256
R1(config-ikev2-proposal)#integrity sha256
R1(config-ikev2-proposal)#group 14
```

Key parameters:

- `encryption` — Symmetric cipher for IKE messages. Use `aes-cbc-128`, `aes-cbc-192`, or `aes-cbc-256`. AES-256 is recommended.
- `integrity` — Hash algorithm for IKE message authentication. Options include `sha256`, `sha384`, `sha512`.
- `group` — Diffie-Hellman group for key exchange. Cisco recommends group 14 (2048-bit) or higher. Groups 19 and 20 use elliptic-curve DH.

### crypto ikev2 policy

Associates one or more proposals with a policy. IOS evaluates policies in order and uses the first one that matches the peer's offer.

```
R1(config)#crypto ikev2 policy mypolicy
R1(config-ikev2-policy)#proposal myproposal
```

### crypto ikev2 keyring

Stores preshared keys for one or more peers. Each `peer` block maps a remote address to a secret.

```
R1(config)#crypto ikev2 keyring mykeyring
R1(config-ikev2-keyring)#peer R2
R1(config-ikev2-keyring-peer)#address 10.10.30.2
R1(config-ikev2-keyring-peer)#pre-shared-key mysecret
```

Use a wildcard address (`0.0.0.0 0.0.0.0`) to apply the same key to all peers — useful in hub-and-spoke topologies.

### crypto ikev2 profile

Ties together the identity matching, authentication method, and keyring. This is the object you reference from an IPsec profile.

```
R1(config)#crypto ikev2 profile myikev2profile
R1(config-ikev2-profile)#match identity remote address 10.10.30.2
R1(config-ikev2-profile)#authentication remote pre-share
R1(config-ikev2-profile)#authentication local pre-share
R1(config-ikev2-profile)#keyring local mykeyring
```

Key parameters:

- `match identity remote address` — Selects which peers this profile applies to. Can match by IP address, subnet, FQDN, or email.
- `authentication remote / local` — Authentication method. `pre-share` uses preshared keys; `rsa-sig` uses certificates.
- `keyring local` — References the keyring that holds the preshared key for matched peers.

### crypto ipsec transform-set

Specifies the ESP encryption and authentication algorithms for the IPsec SA. The mode (`transport` or `tunnel`) determines how much of the original packet is encrypted.

```
R1(config)#crypto ipsec transform-set mytransformset esp-aes 256 esp-sha256-hmac
R1(cfg-crypto-trans)#mode transport
```

Use `mode transport` when encrypting GRE tunnel traffic (only the GRE payload is encrypted). Use `mode tunnel` (default) for native IPsec tunnels where ESP encapsulates the entire inner IP packet.

### crypto ipsec profile (with IKEv2)

Binds the transform set and IKEv2 profile together. This profile is then applied to a tunnel interface.

```
R1(config)#crypto ipsec profile myprofile
R1(ipsec-profile)#set transform-set mytransformset
R1(ipsec-profile)#set ikev2-profile myikev2profile
```

### tunnel protection ipsec profile

Applies an IPsec profile to a tunnel interface. IOS automatically encrypts outbound tunnel traffic and decrypts inbound traffic.

```
R1(config)#interface tunnel12
R1(config-if)#tunnel protection ipsec profile myprofile
```

---

## Verification Commands

### show crypto ikev2 sa

Displays active IKEv2 security associations. The `READY` status confirms that IKE negotiation completed and the peers have exchanged keys.

```
R1#show crypto ikev2 sa
 IPv4 Crypto IKEv2  SA

Tunnel-id Local                 Remote                fvrf/ivrf            Status
1         10.10.10.1/500        10.10.30.2/500        none/none            READY
      Encr: AES-CBC, keysize: 256, PRF: HMAC-SHA256, Hash: SHA256, DH Grp:14, Auth sign: PSK, Auth verify: PSK
      Life/Active Time: 86400/142 sec
```

The output shows the negotiated algorithms, the DH group, and the SA lifetime. If this command returns no output, IKEv2 negotiation has not completed — check the keyring, identity matching, and proposal compatibility between peers.

### show crypto ikev2 session

Provides a more concise per-session summary including the local and remote identities and the number of child SAs (IPsec SAs) spawned by this IKEv2 session.

```
R1#show crypto ikev2 session
 IPv4 Crypto IKEv2 Session

Session-id:1, Status:UP-ACTIVE, IKE count:1, CHILD count:1

Tunnel-id Local                 Remote                Status         
1         10.10.10.1/500        10.10.30.2/500        READY    
      Encr: AES-CBC, keysize: 256, PRF: HMAC-SHA256, Hash: SHA256, DH Grp:14, Auth sign: PSK, Auth verify: PSK
Child sa: local selector  10.10.10.1/0 - 10.10.10.1/65535
          remote selector 10.10.30.2/0 - 10.10.30.2/65535
          ESP SPI in/out: 0x5A34FC1E/0x3B2A9E7D
```

### show crypto ipsec sa

Displays detailed statistics for the IPsec SA, including packet counts and the current operating mode (Transport or Tunnel). Use this to confirm that traffic is actually being encrypted and decrypted.

```
R1#show crypto ipsec sa | i interface|10.10.|Transport|Tunnel,|bound esp|caps
interface: Tunnel12
   local crypto endpt.: 10.10.10.1, remote crypto endpt.: 10.10.30.2
     inbound esp sas:
        in use settings ={Transport, }
     outbound esp sas:
        in use settings ={Transport, }
    #pkts encaps: 47, #pkts encrypt: 47, #pkts digest: 47
    #pkts decaps: 52, #pkts decrypt: 52, #pkts verify: 52
```

If packet counters are not incrementing after sending traffic, check that `tunnel protection ipsec profile` is applied on both ends and that the IKEv2 SA is in `READY` state.

### show crypto ipsec profile

Lists configured IPsec profiles and their associated transform sets and IKEv2 profiles.

```
R1#show crypto ipsec profile
IPSEC profile myprofile
   IKEv2 Profile: myikev2profile
   Security association lifetime: 4608000 kilobytes/3600 seconds
   Responder-Only (Y/N): N
   PFS (Y/N): N
   Mixed-mode : Disabled
   Transform sets={
          mytransformset:  { esp-aes 256 esp-sha256-hmac  },
   }
```

---

## IKEv1 vs. IKEv2 Quick Reference

| | IKEv1 | IKEv2 |
|---|---|---|
| Config object | `crypto isakmp policy` | `crypto ikev2 proposal` + `policy` + `keyring` + `profile` |
| Verify SA | `show crypto isakmp sa` | `show crypto ikev2 sa` |
| Messages to establish | 6 (main mode) | 4 |
| NAT traversal | Extension | Built-in (UDP/4500) |
| EAP support | No | Yes |
| Interoperable | No — peers must use same version |  |
