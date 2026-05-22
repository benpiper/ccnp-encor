# BGP Verification Commands

The following commands are the primary tools for verifying BGP operation and troubleshooting session and routing problems.

### show ip bgp summary

Displays a one-line summary for each BGP neighbor: the neighbor's IP, AS number, number of messages sent and received, session uptime, and the number of prefixes received. A neighbor showing a state other than a number in the State/PfxRcd column has not reached the Established state.

```
R4#show ip bgp summary
BGP router identifier 198.51.100.1, local AS number 65004
BGP table version is 5, main routing table version 5
Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.0.14.1       4        65001      16      17        5    0    0 00:10:49        0
198.51.100.2    4        65550      52      55        5    0    0 00:44:38        0
```

### show ip bgp neighbors

Displays detailed information about a BGP session, including the session state, hold time, keepalive interval, capabilities negotiated, and prefix counts. This is the definitive command for confirming whether a session has reached the Established state.

```
R1#show ip bgp neighbors 203.0.113.2
BGP neighbor is 203.0.113.2,  remote AS 65550, external link
  BGP version 4, remote router ID 203.0.113.2
  BGP state = Established, up for 00:44:38
  Last read 00:00:23, last write 00:00:51, hold time is 180, keepalive interval is 60 seconds
  ...
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Address family IPv4 Unicast: advertised and received
  ...
  Prefixes received: 2
```

Append a neighbor IP to scope the output to a single peer.

### show ip bgp

Displays the full BGP RIB. Each entry shows the prefix, next hop, metric, local preference, weight, and AS path. The `>` symbol marks the best path for each prefix. The `r` flag indicates a RIB failure -- BGP was unable to install the route because a lower-AD route already exists in the IP routing table.

```
R1#show ip bgp
BGP table version is 14, local router ID is 203.0.113.1
Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
              r RIB-failure, S Stale, m multipath, b backup-path
Origin codes: i - IGP, e - EGP, ? - incomplete

     Network          Next Hop            Metric LocPrf Weight Path
 *   10.0.23.0/29     203.0.113.2                            0 65550 65004 i
 *>                   10.0.14.4             3072             0 65004 i
 *>  198.51.100.0/30  203.0.113.2              0             0 65550 i
```

Append a prefix to view all paths for a specific route:

```
R1#show ip bgp 10.0.23.0/29
```

### show ip route bgp

Filters the IP routing table to BGP-learned routes. eBGP routes are flagged `B` with an administrative distance of 20; iBGP routes show an AD of 200.

```
R4#show ip route bgp
      10.0.0.0/8 is variably subnetted, 8 subnets, 3 masks
B        10.0.12.0/30 [20/0] via 203.0.113.1, 02:49:53
B        10.0.23.0/29 [20/3072] via 198.51.100.1, 20:41:50
B        10.0.27.0/28 [20/2] via 203.0.113.1, 02:49:53
```

### show ip prefix-list

Displays configured prefix lists and their entries. Useful for verifying that prefix lists used in route filtering match the intended prefixes before applying them to a neighbor.

```
ISP#show ip prefix-list
ip prefix-list R4-summary: 3 entries
   seq 5 permit 10.0.32.0/19
   seq 10 permit 10.0.23.0/29
   seq 15 deny 0.0.0.0/0 le 32
```

### show route-map

Displays configured route maps, their match and set clauses, and a hit counter showing how many packets or routes have matched each sequence. Use the hit counters to confirm that filtering or attribute modification is working as expected after a soft reconfiguration.

```
ISP#show route-map R4
route-map R4, deny, sequence 10
  Match clauses:
    ip address prefix-lists: R4-summary
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
route-map R4, permit, sequence 20
  Match clauses:
  Set clauses:
    weight 101
  Policy routing matches: 14 packets, 1456 bytes
```

### clear ip bgp * soft

Triggers a soft reconfiguration, causing BGP to re-evaluate all received and advertised routes without tearing down sessions. Use this after making any change to BGP configuration -- adding a neighbor, modifying a route map, changing an attribute -- to force immediate reconvergence without waiting for BGP's slow natural propagation.

```
ISP#clear ip bgp * soft
```

To soft-reset only a single neighbor:

```
ISP#clear ip bgp 203.0.113.1 soft
```
