import uhashring

# Define a list of servers (nodes)
servers = [f'server{i}' for i in range(1, 11)]

# Create a consistent hash ring using the servers
ring = uhashring.HashRing(servers)

keys = ["key1", "key2", "key3", "key4", "key5"]

key_server_map = {key: ring.get_node(key) for key in keys}

print("Key to server mapping:")
for k, v in key_server_map.items():
    print(f"{k}: {v}")
