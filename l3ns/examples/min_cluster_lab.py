import sys
sys.path.append('/home/panda')

from l3ns.ldc import DockerNode, DockerSubnet
from l3ns import defaults
from l3ns.cluster import RemoteNode, WgSubnet, ClusterHost

host1 = ClusterHost('t2')
host2 = ClusterHost('t3')

n1 = RemoteNode('test1', host1, image='alpine', command='tail -f /dev/null')
n2 = RemoteNode('test2', host2, image='alpine', command='tail -f /dev/null')

n1.connect_to(n2, subnet_class=WgSubnet)

defaults.network.start(interactive=True)
