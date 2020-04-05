
import sys
sys.path.append('/home/panda')


from l3ns.ldc import DockerNode, DockerSubnet
from l3ns import defaults, net

defaults.subnet_class = DockerSubnet

nodes = [DockerNode(image='alpine', command='tail -f /dev/null', name='test_%d' % (i+1)) for i in range(4)]

for i in range(3):
    nodes[i].connect_to(nodes[i+1], size=8)

net.start(interactive=True)
