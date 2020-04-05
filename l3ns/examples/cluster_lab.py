import sys
sys.path.append('/home/panda')

from l3ns.ldc import DockerNode, DockerSubnet
from l3ns import defaults
from l3ns.cluster import RemoteNode, WgSubnet, ClusterHost

host1 = ClusterHost('t2')
host2 = ClusterHost('t3')

'''
print(list(host1.get_docker_client().images.list()))
print(list(host2.get_docker_client().images.list()))

'''
n1 = RemoteNode('test1', host1, image='alpine', command='tail -f /dev/null')
n2 = RemoteNode('test2', host1, image='alpine', command='tail -f /dev/null')

r = RemoteNode('test3', host2, image='alpine', command='tail -f /dev/null')

r.connect_to(n1, subnet_class=WgSubnet)
r.connect_to(n2, subnet_class=WgSubnet)

try:
    defaults.network.start()
except Exception as e:
    print('\n_________________\n\n', e, '\n_________________\n', sep='')

input('Stop? ')

defaults.network.stop()

