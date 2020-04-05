import docker
import sys
sys.path.append('/home/panda')


from l3ns.ldc import DockerNode, DockerSubnet
from l3ns.base.network import Network, NetworkConcurrent


N = 1000

net = NetworkConcurrent('10.0.0.0/16', max_workers=4)

s = DockerSubnet(name='polygon', size=N+10, network=net)

nodes = []


for i in range(N):
    n = DockerNode(image='alpine', command='tail -f /dev/null' if not len(nodes) else 'ping {}'.format(nodes[-1].get_ip()), name='l3ns_node_' + str(i+1))
    nodes.append(n)
    s.add_node(n)

if len(sys.argv) == 2 and sys.argv[1] == 'stop':
    net.stop()
else:
    net.start()


