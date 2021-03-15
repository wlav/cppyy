import cppyy

def ann_adapt(node: 'FPTA::Node&') -> cppyy.gbl.FPTA.EventId:
    return cppyy.gbl.FPTA.EventId(node.fData)

