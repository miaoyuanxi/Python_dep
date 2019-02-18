import SimBase





if __name__ == '__main__':
    SimBase.callFunctionWithHQParms(SimBase.startSimulation)

    SimBase.callFunctionWithHQParms(SimBase.simulateSlice)

    SimBase.callFunctionWithHQParms(SimBase.stitchTiles)

    SimBase.callFunctionWithHQParms(SimBase.simulateCluster)

    SimBase.callFunctionWithHQParms(SimBase.startClusterSimulation)
    
