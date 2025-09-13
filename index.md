---
title: Welcome to NSW Mesh
---

This is the community-maintained knowledge base for everything Meshtastic in Sydney and throughout New South Wales.

We're experimenters, bushwalkers, emergency‑comms nerds and tinkerers. Jump into [our Discord](https://discord.gg/Du437Usj3K) and say hi, or explore the live tools and articles below.


[//]: # (This is auto generated based on the contents of the docs folder!)
{% assign docs_pages = site.pages | where_exp: "item", "item.dir contains '/docs/'" %}
{% assign docs_pages = docs_pages | where_exp: "item", "item.title" %}
{% assign grouped_pages = docs_pages | group_by: "dir" %}

{% for group in grouped_pages %}
  {% assign folder_name = group.name | remove: "/docs/" | remove: "/" | replace: "-", " " | capitalize %}
  {% if folder_name == "" %}
    {% assign folder_name = "General" %}
  {% endif %}
- {{ folder_name }}
{% for page in group.items %}
    - [{{ page.title | escape }}]({{ page.url | relative_url }})
{% endfor %}
{% endfor %}
- Meshtastic Tools
    - [Live Map](https://map.nswmesh.au/map)
    - [Node List](https://map.nswmesh.au/nodelist)
    - [Conversations / Weekly Net](https://map.nswmesh.au/net)
    - [Mesh Statistics](https://map.nswmesh.au/stats)
    - [Top Traffic](https://map.nswmesh.au/top)
    - [Sydney Mesh Statistics Dashboard](https://map.nswmesh.au/stats) (Login: guest/guest)
