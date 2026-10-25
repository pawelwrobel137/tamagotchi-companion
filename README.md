# tamagotchi-companion
# Web Companion Application for Virtual Pet (Tamagotchi)

## 1. Project Concept (Brainstorming)
A web-based companion application designed to monitor, manage, and interact with a virtual pet. The application exposes a REST API to synchronize the pet's state (health, hunger, mood) and historical event logs between a web dashboard and an external hardware client.

## 2. Microcontroller & Sensors Research
* **Microcontroller Board:** ESP32 DevKit V1 – selected because it includes built-in Wi-Fi and Bluetooth, allowing it to send and receive HTTP JSON requests directly to our REST API without extra network shields.
