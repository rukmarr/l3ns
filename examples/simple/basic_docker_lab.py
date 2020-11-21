from l3ns.ldc import DockerNode
from l3ns import defaults

n1 = DockerNode('test1', image='alpine', command='tail -f /dev/null')
n2 = DockerNode('test2', image='alpine', command='tail -f /dev/null')

n1.connect_to(n2)

print(n1.get_ip())
print(n2.get_ip())

defaults.network.start(interactive=True)
