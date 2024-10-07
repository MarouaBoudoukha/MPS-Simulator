# load_output_class.py

# This class is used to store the load output for a given time

class LoadOutput:
    def __init__(self, load_kw, load_start, load_end):
        self.load_kw = load_kw
        self.load_start = load_start
        self.load_end = load_end

    # Get the load output for a given time
    def get_output(self, x):
        # x is the time in hours since the start of the simulation
        # need to get it in the form of 0-24 hours, to represent the time of day
        x = x % 24

        if x >= self.load_start and x < self.load_end:
            return self.load_kw
        else:
            return 0

