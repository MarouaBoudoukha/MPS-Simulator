# solar_input_class.py
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

class SolarInput:
    def __init__(self, max_kw, peak_sun_hours):
        self.max_kw = max_kw
        self.peak_sun_hours = peak_sun_hours
        self.X = np.linspace(0, 24, 24) # 0 to 24 hours
        self.mean = 12  # Noon
        self.std_dev = 3  # Standard deviation
        self.Y = self.calculate_distribution()
        #self.plot_distribution()

    def calculate_distribution(self):
        Y = self.max_kw * self.peak_sun_hours * norm.pdf(self.X, self.mean, self.std_dev)
        area = np.trapz(Y, self.X)
        #print(f"kwh / day: {area:.2f}")
        return Y

    def plot_distribution(self):
        plt.plot(self.X, self.Y, label='Standard Normal Distribution')
        plt.xlabel('X')
        plt.ylabel('Probability Density')
        plt.title('Standard Normal Distribution Curve')
        plt.legend()
        plt.grid(True)
        plt.show()

    # Get the solar output for a given time
    def get_output(self, x):
        # x is the time in hours since the start of the simulation
        # need to get it in the form of 0-24 hours, to represent the time of day
        x = x % 24
        return self.Y[x]
