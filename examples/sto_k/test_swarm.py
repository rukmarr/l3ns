from hosts import hosts


for h in hosts:
    print(h.address, h.get_docker_client().containers.list())
