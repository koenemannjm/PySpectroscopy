from instruments.HighFinesseWLM import HighFinesseWLM
from instruments.TopticaDLCPro import TopticaDLCPro

class FrequencyPIDController:
    def __init__(
            self,
            voltParams=[],
            currParams=[],
            gratParams=[]
    ):
        self.voltageParams = voltParams
        self.gratingParams = gratParams
        self.currentParams = currParams
        self.converge = False

    def loopPID(self, target_frequency, tolerance):

        ei = 100000000.0
        integral = 0.0
        max_iterations = 50_000
        iterations = 0
        while abs(ei)<tolerance:

            if iterations > max_iterations:
                break

            iterations += 1

        if iterations < max_iterations:
            self.converge = True

        return self.converge
