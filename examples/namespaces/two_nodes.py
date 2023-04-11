from l3ns.namespaces import NamespaceNode, NamespaceSubnet
from l3ns import defaults
from pyroute2.ndb.main import NDB

ndb = NDB()

n1 = NamespaceNode('t1', ['tail', '-f', '/dev/null'], ndb=ndb)
n2 = NamespaceNode('t2', ['tail', '-f', '/dev/null'], ndb=ndb)

n1.connect_to(n2, subnet_class=NamespaceSubnet, ndb=ndb)


defaults.network.start(interactive=True)
