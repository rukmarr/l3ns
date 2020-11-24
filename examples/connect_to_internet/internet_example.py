from l3ns.ldc import DockerNode
from l3ns.base.network import Network
from l3ns import defaults

defaults.network = Network('11.0.0.0/8')

n1 = DockerNode('test1', image='alpine', command='ping 8.8.8.8')
n2 = DockerNode('test2', image='alpine', command='tail -f /dev/null')

n1.connect_to(n2)
n1.connect_to_internet = True

# check "docker logs test1" in second terminal after starting network
defaults.network.start(interactive=True)
