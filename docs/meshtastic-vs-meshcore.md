---
title: Meshtastic vs Meshcore
---

# Why should I switch?

## Efficiency in Density: Meshcore vs. Meshtastic in LoRa Mesh Networks

LoRa (Long Range) technology enables low-power, long-distance wireless communication, making it ideal for off-grid mesh networks used in scenarios like emergency response, hiking, or community alerts. Two prominent open-source protocols built on LoRa are Meshtastic and Meshcore. While both facilitate peer-to-peer messaging without centralised infrastructure, they differ fundamentally in how they manage traffic, especially as the number of users—or nodes—grows.

Meshtastic relies on a flooding-based mesh algorithm where messages are broadcast and rebroadcast by all nodes to ensure delivery, which works well in sparse environments but becomes inefficient in dense ones. In contrast, Meshcore employs a hierarchical routing system that prioritises disciplined transmission, allowing it to scale more effectively with larger user bases by minimising airtime waste and collisions.

## How Meshtastic Works

Meshtastic's protocol operates on a "true" mesh principle, where every node acts as a router. When a message is sent, it floods the network: each receiving node rebroadcasts it until it reaches its destination or a hop limit. This ensures reliability in low-density setups, such as a few hikers in a remote area, but in high-density scenarios, it leads to excessive redundancy.

Nodes also constantly 'talk' to each other sending telemetry data such as position, signal and battery voltage as well, which also hampers the noise levels. Nodes compete for the shared LoRa channel, resulting in packet collisions, increased latency, and drained batteries from constant re-transmissions. The protocol's decentralised nature, while resilient, amplifies "noise" as more nodes join, overwhelming the limited bandwidth of LoRa's sub-GHz frequencies such as 915MHz.

Meshtastic developers recommend dropping to faster and short transmission modes once a mesh goes over 40 or so nodes, and this is fine if the nodes are confined into a smaller dense area. The downfall with this is changing to the faster shorter mode causes major reductions in range and in larger metropolitan areas this means isolation of users from other users they had contact with previously before the mesh got crowded. Meshtastic has proven to work well in crowded meshes in smaller confined areas such as Defcon and Burning Man events in the USA.

## How Meshcore Works

Meshcore, on the other hand, adopts a more structured approach inspired by routing efficiency. It designates specific nodes as repeaters (or routers) that handle forwarding, while edge nodes—such as user companion devices as they are known—transmit only their own messages without rebroadcasting others. This hierarchical model, often using role-specific firmware, reduces unnecessary traffic by confining routing to a backbone of dedicated repeaters.

In dense networks, this discipline prevents the channel from becoming saturated, enabling faster message propagation and lower power consumption. By saving airtime for essential routing rather than blanket flooding, Meshcore maintains performance even as node count rises, making it particularly suited for urban or crowded deployments.

## The Meshtastic Auditorium

To illustrate, imagine a large auditorium packed with 100 people, each representing a LoRa node trying to communicate—perhaps coordinating an event or sharing updates. In a Meshtastic network, it's like everyone shouting at once to pass messages across the room: voices overlap in a cacophony of noise, drowning out conversations as they all try to send messages, send trace routes and send telemetry data.

Let's add individuals whose job it is to take a message and pass it on to someone else by shouting it to pass on across the auditorium—these people represent routers or repeaters in Meshtastic. These individuals strain to hear amid the chaos, they shout over the nodes sitting down and messages get lost in collisions (like garbled shouts), and the overall noise mess makes coherent dialogue nearly impossible. The flooding mechanism, while ensuring some messages get through, creates too much interference, leading to frustration and inefficiency as the "crowd" grows denser. Eventually as more nodes come into the auditorium, passing messages will become impossible totally making the mesh unusable.

## The Meshcore Auditorium

Now picture the same auditorium under Meshcore: here, only a few designated "ushers" (repeaters) relay information, while attendees (edge nodes) speak only when they have something specific to say. The room stays orderly—conversations flow clearly because transmissions are targeted and infrequent, with ushers efficiently directing messages without everyone chiming in.

Nodes remain "disciplined," transmitting just enough to connect without overwhelming the space, allowing even in a full house of 100, people can communicate reliably and without the exhaustion of constant noise. If a user needs to know the voltage of his repeater, he can request that information be sent to them, instead of it constantly being transmitted all the time for no real reason.

With no real hop restrictions messages can travel long distances between nodes via this repeater network. Distances of hundreds of kilometres have been reported with well designed repeater chains to carry messages. This doesn't happen with Meshtastic's 7 hop limit which is due to coding limits. To add to this efficiency, users can set a path to make sure a message gets to the intended user node by selecting only repeaters on a path set on a map. This not only stops flooding of this data over all repeaters but makes sure the most efficient path is taken to get a successful message through.

## In Summary

While Meshtastic excels in flexible, small-scale meshes, its flooding approach falters under the load of many users, much like an undisciplined crowd. Meshcore's hierarchical discipline shines in such density, conserving resources and enabling scalable, effective communication. As LoRa networks expand to support larger communities, protocols like Meshcore represent a smarter path forward for robust, user-dense environments.

As mesh networking becomes more popular, users are gumming up well-established Meshtastic networks and these are failing their users in cities all over the world currently. Meshcore was designed to be the answer to this issue, and while Meshcore is still in early development, its usage is growing around the world to solve the issues Meshtastic networks have failed at.
Happy Meshing! David VK2FRT
