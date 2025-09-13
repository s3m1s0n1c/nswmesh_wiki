---
title: Sydney Meshtastic Network
---

## LoRa Settings

| Option         | Value            |
|----------------|------------------|
| Modem Preset   | Long Fast        |
| Frequency Slot | 20 (919.875 MHz) |

| Region      | Hop Limit |
|-------------|-----------|
| CBD         | 4-5       |
| Outer Metro | 6         |
| Regional    | 7         |

## Encryption Keys

| Channel Name | PSK                                            |
|--------------|------------------------------------------------|
| Long Fast    | Unchanged from default                         |
| Sydney       | `Clw2H9SaqRTipbNiAWUg5jBVxWu9XctUiKSsVfHbxIc=` |
| Nepean       | `ydRS2lA0cBxpGulfCoGEUdrrnyFzQjXP3qeVaeeuIKc=` |

## MQTT Gateway

| Option       | Value             |
|--------------|-------------------|
| Address      | `mqtt.nswmesh.au` |
| Port         | 1883              |
| Username     | nswmesh           |
| Password     | nswmesh           |
| Topic Format | msh/ANZ/NSW       |

Under modules please enable neigbour info - but only for MQTT as there is no need to flood the lora mesh for NI data.

The MQTT server mirrors over‑the‑air traffic so you can log messages or build dashboards without a radio. Treat the credentials as public‑read—nothing sensitive should be sent unencrypted.

Additional topics can be added by contacting the admins via the Contacts page

## Prefered Mestastic Node Settings

**Long Name**: keep it friendly and mark “(MQTT)” if you bridge via MQTT.

**GPS location**: choose a point near your real QTH and set a realistic ±error (≤ 1500 m).

**Device Role**: start as CLIENT_MUTE (indoor) or CLIENT (field).

> PLEASE Only go REPEATER / ROUTER / ROUTER_LATE if your node is mains‑powered with a decent antenna and you really need the extra coverage. Also jump on the Sydney Mesh Users Group Discord and discuss your proposed Repearer / Router / Router_Late location with the existing users in your area.

**Hop limit** – see table above. Seven is the absolute max—more hops can harm, not help.

Tip: Unsure about roles? The [official docs explain them well](https://meshtastic.org/docs/configuration/radio/device).
