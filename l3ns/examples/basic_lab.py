from l3ns.debug import DebugNode, DebugSubnet
from l3ns import defaults

defaults.subnet_class = DebugSubnet

n1 = DebugNode(name='test1')
n2 = DebugNode(name='test2')

n1.connect_to(n2)

defaults.network.start()
