# EdgeKG-MicroBench: Live IoT-LAB Edge Reasoning Profiler

**Author:** Sriram Kumar Nallapati

**Context:** An empirical micro-benchmark designed for the PhD research project at the Stream Intelligence Lab, KU Leuven (ref. BAP-2026-601) under Prof. Pieter Bonte.

## Objective

To empirically quantify the computational and memory bottlenecks of deploying Semantic Knowledge Graphs on resource-constrained Edge devices processing continuous live data streams.

This project benchmarks the two primary Knowledge Graph reasoning paradigms—**Materialization** vs. **Virtualization**—by ingesting a live physical sensor stream from a microcontroller deployed in a French IoT testbed.

## Live Physical Architecture

Rather than using simulated Python queues or static CSV files, this benchmark executes on a live Edge-to-Hardware bridge:

1. **The Sensor Node (Hardware):** An M3 ARM Cortex-M3 microcontroller deployed at the FIT IoT-LAB site in Strasbourg, France. It runs a basic RTOS firmware broadcasting a continuous serial data stream.
2. **The Network Tunnel:** A secure SSH TCP Tunnel bridges port `20000` of the physical node in France directly to `localhost` on the Edge Gateway.
3. **The Edge Gateway (Stream Intelligence):** A local Python dashboard application that ingests the live TCP socket stream, buffers the unstructured data into time-windows (30 events per window), and applies semantic reasoning algorithms on the fly.

## The Paradigms Investigated

Once a 30-event window is buffered on the Edge Gateway, the stream is processed using two competing strategies:

1. **Materialization (Heavy Edge - RDFlib):**
Translates all unstructured live stream data into formal W3C RDF triples. It explicitly computes and stores inferred semantic facts (e.g., inferring `<node> a ex:Overheating` based on temperature thresholds).
* **Advantage:** Supports powerful, cascading, multi-hop reasoning.
* **Disadvantage:** Highly resource-intensive and relies on in-memory graph construction.


2. **Virtualization (Lightweight Edge - Native):**
Leaves the live stream in its native format. Semantic queries are translated on-the-fly into native logical operations without storing new relational facts or building a graph payload.
* **Advantage:** Highly efficient; near-zero memory footprint.
* **Disadvantage:** Limits the capacity for complex, schema-driven semantic reasoning.



## Empirical Results

Profiling conducted on a live continuous serial stream from the Strasbourg M3 node. Metrics represent the average processing cost per 30-event micro-window.

| Reasoning Strategy | Avg. Execution Time | Peak Memory Usage | Edge Viability (Constraint: 64KB RAM) |
| --- | --- | --- | --- |
| **Materialization (RDFlib)** | ~0.024 seconds | ~0.22 MB | **Critical Failure** (OOM Crash on Node) |
| **Virtualization (Native)** | < 0.0001 seconds | ~0.00 MB | **High** (Sustainable, but limits logic) |

### Research Conclusion

This live benchmark perfectly illustrates the core bottleneck of edge-based stream reasoning. Explicitly materializing a tiny 30-event time window consumes 0.22 MB of memory. If this logic were pushed entirely to the physical M3 sensor node (which only possesses 64 KB of RAM), the device would immediately suffer an Out-Of-Memory (OOM) crash. Conversely, pure virtualization easily survives edge deployment but sacrifices the rich expressiveness of the Knowledge Graph.

## Future Work (PhD Direction)

A binary choice between Materialization and Virtualization is insufficient for modern IoT ecosystems. My proposed research direction involves developing a **Hybrid Orchestration Paradigm**:

* Implementing **Machine Learning** to dynamically predict which specific inferences must be explicitly materialized based on historical query patterns.
* Designing a distributed reasoning topology that dynamically offloads heavy materialization tasks from the physical edge up to Fog/Cloud layers, while keeping lightweight virtualized stream-filtering on the constraint device itself.

---

## How to Reproduce the Experiment

### 1. Prerequisites

* A registered [FIT IoT-LAB](https://www.iot-lab.info/) account with an active SSH key.
* Python 3.8+
* `pip install rdflib`

### 2. Hardware Allocation

Launch a new experiment in the FIT IoT-LAB portal:

* **Architecture:** 1x M3 Node
* **Site:** Strasbourg (or Grenoble)
* **Firmware:** `tutorial_m3.elf` (Provided firmware)

### 3. Establish the Live TCP Tunnel

Open a terminal and establish the physical bridge to the assigned node (e.g., `m3-17`):

```bash
ssh -L 20000:<YOUR_NODE_ID>:20000 <username>@strasbourg.iot-lab.info

```

### 4. Run the Edge Gateway Profiler

Leave the SSH tunnel terminal open. In a new terminal, execute the stream processor:

```bash
python iot_lab_benchmark.py

```

*Note: Press `Enter` in the python terminal to send a carriage return through the socket if the node firmware requires a wake-up command.*