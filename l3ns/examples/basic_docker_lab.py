
import sys
sys.path.append('/home/panda')


from l3ns.ldc import DockerNode, DockerSubnet
from l3ns import defaults

defaults.subnet_class = DockerSubnet

n1 = DockerNode(image='alpine', command='tail -f /dev/null', name='test1')
n2 = DockerNode(image='alpine', command='tail -f /dev/null', name='test2')

n1.connect_to(n2)

defaults.network.start(interactive=True)
