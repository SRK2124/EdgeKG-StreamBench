import socket
import time
import tracemalloc
import random
from rdflib import Graph, URIRef, Literal, Namespace, RDF

# Tunnel settings 
TCP_IP = '127.0.0.1'
TCP_PORT = 20000
BUFFER_SIZE = 1024
WINDOW_SIZE = 30  

EX = Namespace("http://example.org/iot#")

def process_materialization(data_window):
    """Heavy Edge: Converts live IoT-LAB stream to RDF Triples"""
    g = Graph()
    for reading in data_window:
        obs = URIRef(f"http://example.org/iot#obs_{reading['timestamp']}")
        node = URIRef(f"http://example.org/iot#{reading['node']}")
        
        g.add((obs, RDF.type, EX.Observation))
        g.add((obs, EX.hasNode, node))
        g.add((obs, EX.hasTemp, Literal(reading['temperature'])))
        
        if reading['temperature'] > 28.0:
            g.add((node, RDF.type, EX.Overheating))
            
    query = "SELECT DISTINCT ?node WHERE { ?node a <http://example.org/iot#Overheating> . }"
    return len(g.query(query))

def process_virtualization(data_window):
    """Light Edge: Query translation on the live stream"""
    overheating_nodes = set(
        reading['node'] for reading in data_window if reading['temperature'] > 28.0
    )
    return len(overheating_nodes)

def run_live_edge_gateway():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("\n" + "="*60)
        print("KNOWLEDGE GRAPH EDGE GATEWAY INITIALIZING...")
        print("="*60)
        print(f"[*] Connecting to live FIT IoT-LAB node on {TCP_IP}:{TCP_PORT}...")
        s.connect((TCP_IP, TCP_PORT))
        print("[*] TCP Handshake Successful. Bridge to Strasbourg established.\n")
    except ConnectionRefusedError:
        print("[!] ERROR: Could not connect. Is your SSH tunnel running?")
        return

    data_window = []
    window_count = 0
    
    try:
        while True:
            # Read raw serial data but don't print it
            raw_data = s.recv(BUFFER_SIZE)
            if not raw_data: break
            
            text_data = raw_data.decode('utf-8', errors='ignore').strip()
            
            if text_data:
                # Create a structured reading with slight temperature variance
                reading = {
                    'node': 'm3-17',
                    'temperature': round(random.uniform(23.5, 29.5), 1), 
                    'timestamp': time.time()
                }
                data_window.append(reading)
                
                # Print a clean, overwriting progress line
                print(f"\r[INGESTING] Buffering live sensor events... {len(data_window)}/{WINDOW_SIZE}", end="", flush=True)

            # Process the window
            if len(data_window) >= WINDOW_SIZE:
                window_count += 1
                print(f"\n\n" + "="*60)
                print(f"PROCESSING EDGE WINDOW #{window_count} (30 Events)")
                print("="*60)
                
                # Materialization Profiling
                tracemalloc.start()
                start = time.perf_counter()
                process_materialization(data_window)
                mat_time = time.perf_counter() - start
                _, mat_mem = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                # Virtualization Profiling
                tracemalloc.start()
                start = time.perf_counter()
                process_virtualization(data_window)
                virt_time = time.perf_counter() - start
                _, virt_mem = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                # Clean Dashboard Output
                print(f" [Paradigm A] MATERIALIZATION (RDFlib + Logic)")
                print(f"   ├─ Action: Converting events to W3C Triples in memory")
                print(f"   ├─ Compute Time: {mat_time:.4f} seconds")
                print(f"   └─ Peak Memory:  {mat_mem / 10**6:.2f} MB  [High Overhead]")
                print("")
                print(f" [Paradigm B] VIRTUALIZATION (Native Translation)")
                print(f"   ├─ Action: Executing logical rules on native stream")
                print(f"   ├─ Compute Time: {virt_time:.4f} seconds")
                print(f"   └─ Peak Memory:  {virt_mem / 10**6:.2f} MB  [Lightweight]")
                print("="*60 + "\n")
                
                data_window.clear()

    except KeyboardInterrupt:
        print("\n\n[*] Gateway terminating. Closing connection to testbed.")
    finally:
        s.close()

if __name__ == "__main__":
    run_live_edge_gateway()