class Slot:
    def __init__(self, o: float, L: float):
        """ TT Slot in GCL

		Args:
			o (float): start time
			L (float): window length

		"""
        self.o = o	
        self.L = L
    
    def __repr__(self):
        return f"Slot: o={self.o}, L={self.L}"
        