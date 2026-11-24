Implementation Status and Outstanding Issues

The Sprint 4 network topology and initial router/server configurations have been implemented in Cisco Modeling Labs.

During connectivity verification, an unexpected interface-level connectivity issue arose between Router R1 (GigabitEthernet0/3) and the Alpine game server (eth0).

Despite repeated troubleshooting attempts, including interface reconfiguration, node restarts, and deletion and recreation of the virtual connection, the router interface continues to report a down/down status.

Consequently, end-to-end connectivity and the required DNS packet capture could not be completed at the time of submission.

The existing topology, configuration work, and troubleshooting evidence are included in this repository to document implementation progress. Further investigation is ongoing.

Controlled Carrier Test — November 24, 2026

A simultaneous diagnostic test was conducted on the
Alpine server (eth0) and Router R1 (GigabitEthernet0/3).

Alpine reported:
- Carrier: 1
- Interface state: UP, LOWER_UP

IOSv reported:
- Network link: DOWN (NO CARRIER)
- Physical status: DOWN

CML's Connectivity panel confirmed that Alpine eth0
was mapped to Router R1 GigabitEthernet0/3.

The contradictory link-state reports suggest a
possible issue involving CML's virtual connection
or IOSv's virtual network adapter.

Further investigation is required.