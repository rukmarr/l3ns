from l3ns.ldc import DockerNode
from l3ns.base.network import Network
from l3ns import defaults

defaults.network = Network('11.0.0.0/8')

n1 = DockerNode('test1', image='alpine', command='tail -f /dev/null')
n2 = DockerNode('test2', image='alpine', command='tail -f /dev/null')

n1.connect_to(n2)
n1.connect_to_internet = True

defaults.network.start(interactive=False)

# for api details see
# https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.Container.exec_run

# for finite commands:  (-c 5 limit command to 5 pings)
ret = n1.exec_run('ping -c 5 8.8.8.8') # it still will take a while
print(ret.exit_code)
print(ret.output)


# for infinite commands:
ret = n1.exec_run('ping 1.1.1.1', stream=True)
print(ret.exit_code)  # None, command is still running
for i, line in enumerate(ret.output):
    print(line)
    if i >= 5:
        break

defaults.network.stop()
