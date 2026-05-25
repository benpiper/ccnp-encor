# Multicast Verification Commands

The following commands are the primary tools for verifying IP multicast operation and troubleshooting PIM adjacency, group membership, and forwarding problems.

### show ip pim neighbor

Lists all PIM neighbors discovered on each interface, along with their IP address, uptime, hold time, DR priority, and the interface's designated router (DR).

```
R2#show ip pim neighbor
PIM Neighbor Table
Mode: B - Bidir Capable, DR - Designated Router, N - Default DR Priority,
      P - Proxy Capable, S - State Refresh Capable, G - GenID Capable,
      L - DR Load-balancing Capable
Neighbor          Interface                Uptime/Expires    Ver   DR
Address                                                            Prio/Mode
10.0.12.1         GigabitEthernet0/0       00:23:11/00:01:28 v2    1 / S P G
10.0.27.7         GigabitEthernet0/1       00:22:58/00:01:41 v2    1 / DR S P G
```

A missing neighbor indicates a PIM Hello problem. Check that `ip pim sparse-mode` (or `sparse-dense-mode`) is configured on both sides of the link and that the interface is up. PIM Hellos are sent to 224.0.0.13 using IP protocol 103.

### show ip pim interface

Shows PIM configuration and state per interface: mode, neighbor count, DR address, and Hello/hold timers.

```
R2#show ip pim interface
Address          Interface                Ver/   Nbr    Query  DR         DR
                                         Mode   Count  Intvl  Prior
10.0.12.2        GigabitEthernet0/0       v2/S     1     30    1          10.0.12.1
10.0.27.2        GigabitEthernet0/1       v2/S     1     30    1          10.0.27.7
```

The DR column shows which router won the DR election on that segment. The DR is responsible for sending PIM Register messages to the RP when a directly connected source begins sending. Use `show ip pim interface detail` for Hello and hold timer values.

### show ip mroute

The primary multicast routing table command. Displays all (*,G) and (S,G) entries, the incoming interface (IIF), and the outgoing interface list (OIL).

```
R2#show ip mroute
IP Multicast Routing Table
Flags: D - Dense, S - Sparse, B - Bidir Group, s - SSM Group, C - Connected,
       L - Local, P - Pruned, R - RP-bit set, F - Register flag,
       T - SPT-bit set, J - Join SPT, M - MSDP created entry, E - Extranet,
       X - Proxy Join Timer Running, A - Candidate for MSDP Advertisement,
       U - URD, I - Received Source Specific Host Report,
       Z - Multicast Tunnel, z - MDT-data group sender,
       Y - Joined MDT-data group, y - Sending to MDT-data group,
       G - Received BGP C-Mroute, g - Sent BGP C-Mroute,
       N - Received BGP Shared-Tree Prune, n - BGP C-Mroute suppressed,
       q - BGP Quarterly transmission

(*,239.0.0.1), 00:14:22/stopped, RP 0.0.0.0, flags: DC
  Incoming interface: Null, RPF nbr 0.0.0.0
  Outgoing interface list:
    GigabitEthernet0/0, Forward/Dense, 00:14:22/00:00:00

(10.0.27.7,239.0.0.1), 00:03:47/00:02:52, flags: T
  Incoming interface: GigabitEthernet0/1, RPF nbr 10.0.27.7
  Outgoing interface list:
    GigabitEthernet0/0, Forward/Sparse-Dense, 00:03:47/00:00:00
```

Key fields:

- (*,G) entry: matches traffic to group G from any source; used for shared-tree forwarding in sparse mode
- (S,G) entry: matches traffic from a specific source S to group G; created after SPT switchover in sparse mode, or immediately in dense mode
- Incoming interface (IIF): the interface on which multicast traffic is expected to arrive, determined by the RPF check
- Outgoing interface list (OIL): interfaces out which traffic is forwarded; an empty OIL means the router has pruned itself from the tree
- Flags: T (SPT-bit) means the router is using the source tree; P (Pruned) means this interface has been pruned

To view a single group:

```
R2#show ip mroute 239.0.0.1
```

### show ip mroute summary

Condensed version of `show ip mroute`. Lists group addresses and per-group packet/byte counts without full interface detail. Useful for a quick count of active groups and to spot high-traffic sources.

```
R2#show ip mroute summary
IP Multicast Routing Table
(*,224.0.1.40), 00:24:11/00:02:59, RP 0.0.0.0, flags: DCL
(*,239.0.0.1), 00:14:22/stopped, RP 0.0.0.0, flags: DC
(10.0.27.7,239.0.0.1), 00:03:47/00:02:52, flags: T
```

### show ip igmp groups

Lists multicast groups that have active receivers on directly connected interfaces, along with the interface, last reporter, and uptime. Use it to confirm that a host's IGMP Membership Report was received.

```
R2#show ip igmp groups
IGMP Connected Group Membership
Group Address    Interface                Uptime    Expires   Last Reporter   Group Accounted
239.0.0.1        GigabitEthernet0/0       00:04:12  00:02:17  10.0.12.1
```

If a group is missing from this table, the router has not received an IGMP Membership Report for it. Check whether the host is sending reports using `debug ip igmp` on the directly connected router.

### show ip igmp interface

Shows IGMP configuration and state per interface: version, querier IP, query interval, and active group count.

```
R2#show ip igmp interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet address is 10.0.12.2/24
  IGMP is enabled on interface
  Current IGMP host version is 2
  Current IGMP router version is 2
  IGMP query interval is 60 seconds
  IGMP querier timeout is 120 seconds
  IGMP max query response time is 10 seconds
  Last member query count is 2
  Last member query response interval is 1000 ms
  Inbound IGMP access group is not set
  IGMP activity: 3 joins, 1 leaves
  Multicast routing is enabled on interface
  Multicast TTL threshold is 0
  Multicast designated router (DR) is 10.0.12.1
  IGMP querying router is 10.0.12.2 (this system)
  Multicast groups joined by this system (number of users):
      239.0.0.1(1)
```

The querier is the PIM router on the segment with the lowest IP address. It sends periodic IGMP General Queries to 224.0.0.1. All other routers suppress their own queries when they hear a querier.

### show ip rpf

Performs the RPF lookup for a given source address and shows which interface and next-hop the router would use to reach that source. The RPF interface is the interface on which multicast from that source must arrive; packets arriving on any other interface fail the RPF check and are dropped.

```
R2#show ip rpf 10.0.27.7
RPF information for ? (10.0.27.7)
  RPF interface: GigabitEthernet0/1
  RPF neighbor: 10.0.27.7 (directly connected)
  RPF route/mask: 10.0.27.0/24
  RPF type: unicast (connected)
  Doing distance-preferred lookups across tables
  RPF topology: ipv4 multicast base
```

Use this command when multicast traffic is being dropped or not forwarded. If the RPF interface does not match the interface on which the source is actually sending, the multicast traffic will fail the RPF check on every router. Correct the unicast routing table (which drives the RPF lookup) to fix the mismatch.

### debug ip pim

Generates real-time output for PIM events: Hello messages, Join/Prune processing, Register messages, and DR elections.

```
R2#debug ip pim
PIM debugging is on
*May 25 09:14:03.221: PIM(0): Received v2 Hello on GigabitEthernet0/1 from 10.0.27.7
*May 25 09:14:03.221: PIM(0): Update GigabitEthernet0/1/10.0.27.7 to neighbor
*May 25 09:14:12.008: PIM(0): Received v2 Join/Prune on GigabitEthernet0/0 from 10.0.12.1, to us
*May 25 09:14:12.008: PIM(0):  Join-list: (*, 239.0.0.1), RPT-bit set, WC-bit set, S-bit set
```

Use sparingly on production routers. The output volume is high on busy multicast networks. Disable with `no debug ip pim` or `undebug all`.

### debug ip igmp

Generates real-time output for IGMP events: Membership Reports, General Queries, Group-Specific Queries, and Leave messages. Use it on the router directly connected to the hosts to confirm that joins and leaves are being received.

```
R1#debug ip igmp
IGMP debugging is on
*May 25 09:15:01.442: IGMP(0): Received v2 Report on GigabitEthernet0/0 from 10.0.12.10 for 239.0.0.1
*May 25 09:15:01.443: IGMP(0): Updating IGMP router entry for 239.0.0.1 on GigabitEthernet0/0
*May 25 09:16:01.101: IGMP(0): Sending v2 Query on GigabitEthernet0/0 to 224.0.0.1
```

Disable with `no debug ip igmp` or `undebug all` when done.
