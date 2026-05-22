# EIGRP Verification Commands

The following commands are the primary tools for verifying EIGRP operation and troubleshooting adjacency or routing problems.

### show ip eigrp neighbors

Lists all established EIGRP adjacencies along with the hold time remaining, smooth round-trip time (SRTT), retransmission timeout (RTO), and outstanding queue count (Q Cnt).

```
R5#show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
1   10.0.45.4               Gi0/3                    12 00:05:43   23   138  0  47
0   10.0.56.6               Gi0/0                    12 00:05:43   13   100  0  100
```

A persistently non-zero Q Cnt may indicate packet loss or an SIA condition. SRTT helps identify slow or congested links.

### show ip eigrp topology

Displays the EIGRP topology table, including successors and feasible successors for every known prefix. Use it to verify expected paths and confirm that feasible successors exist for critical prefixes.

```
R5#show ip eigrp topology
EIGRP-IPv4 Topology Table for AS(100)/ID(5.5.5.5)
Codes: P - Passive, A - Active, U - Update, Q - Query, R - Reply,
       r - reply Status, s - sia Status

P 10.0.23.0/29, 2 successors, FD is 3328
        via 10.0.45.4 (3328/3072), GigabitEthernet0/3
        via 10.0.56.6 (3328/3072), GigabitEthernet0/0
P 10.0.34.0/28, 1 successors, FD is 3072
        via 10.0.45.4 (3072/2816), GigabitEthernet0/3
```

A route in the A (Active) state is undergoing DUAL recomputation. Any route that remains active for more than 3 minutes will go SIA and trigger an adjacency reset. You can scope the output to a single prefix:

```
R5#show ip eigrp topology 10.0.34.0/28
```

### show ip route eigrp

Filters the IP routing table to EIGRP-learned routes. Internal routes are flagged **D** (for DUAL); redistributed external routes are flagged **D EX**.

```
R5#show ip route eigrp
      10.0.0.0/8 is variably subnetted, 7 subnets, 3 masks
D        10.0.23.0/29 [90/3328] via 10.0.56.6, 00:02:22, GigabitEthernet0/0
                      [90/3328] via 10.0.45.4, 00:02:22, GigabitEthernet0/3
D        10.0.34.0/28 [90/3072] via 10.0.45.4, 00:05:39, GigabitEthernet0/3
D        10.0.36.0/29 [90/3072] via 10.0.56.6, 00:05:37, GigabitEthernet0/0
```

The values in brackets are [administrative distance/metric].

### show ip eigrp interfaces

Lists all interfaces on which EIGRP is active and the number of peers on each. Use it to confirm EIGRP is running on the intended interfaces and not on any unintended ones.

```
R5#show ip eigrp interfaces
EIGRP-IPv4 Interfaces for AS(100)
                              Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface              Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Gi0/0                    1        0/0       0/0          13       0/0           50           0
Gi0/3                    1        0/0       0/0          23       0/0           50           0
```

Adding the `detail` keyword shows per-interface Hello and hold timers and whether authentication is configured.

### show ip eigrp traffic

Displays cumulative packet counters for each EIGRP packet type. Useful for confirming that Hellos, Updates, and ACKs are flowing normally and for detecting an elevated query count that may signal a recurring SIA problem. (On some platforms this command appears as `show ip eigrp statistics`.)

```
R5#show ip eigrp traffic
EIGRP-IPv4 Traffic Statistics for AS(100)
  Hellos sent/received: 523/519
  Updates sent/received: 14/12
  Queries sent/received: 2/1
  Replies sent/received: 1/2
  Acks sent/received: 13/11
  SIA-Queries sent/received: 0/0
  SIA-Replies sent/received: 0/0
  Hello Process ID: 166
  PDM Process ID: 138
  Socket Queue: 0/10000/2/0 (current/max/highest/drops)
  Input Queue: 0/10000/2/0 (current/max/highest/drops)
```

A non-zero SIA-Queries count is a red flag: it means routes have gone stuck-in-active on this router.
