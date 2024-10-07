# mps_class.py

import time
from solar_input_class import SolarInput
from load_output_class import LoadOutput

# MPS class is used to model the behavior of a mobile power system (MPS) in the simulation.

# Constants
POWER_IN_THRESHOLD = 40  # battery soc threshold for allowing power in
POWER_OUT_THRESHOLD = 100  # battery soc threshold for allowing power out
HUB_POWER_IN_THRESHOLD = 100  # battery soc threshold for allowing power in
HUB_POWER_OUT_THRESHOLD = 15  # battery soc threshold for allowing power out
CUTOFF_THRESHOLD = 15  # battery soc threshold for safe operation
INTERVAL_DURATION = 0.5  # half hour intervals
LOAD_START = 6  # load start time
TYPE_STD = 0
TYPE_HUB = 1
POWER_OUT_MIN_TIME = 6  # minimum time to allow power out
POWER_IN_MIN_TIME = 6  # minimum time to allow power in
GRAPH_SCALE = 10  # scale factor for graphing

class MPS:
    def __init__(self, max_power, max_battery, max_solar, peak_sun_hours, init_soc, load_power, load_hours, mps_type, name):
        self.max_power = max_power # max power in kw
        self.max_battery = max_battery # battery max of the MPS (kwh)
        self.soc = init_soc # battery state of charge (0-100)
        self.remaining_battery = max_battery*(init_soc / 100) # (kwh)
        self.bat_charge = 0 # battery charge (kw)
        self.bat_discharge = 0 # battery discharge (kw)
        self.local_load = 0     # local load (kw)
        self.power_in = 0       # external power in (kw)
        self.power_out = 0    # external power out (kw)
        self.power_out_allowed = 0  # flag to allow power out
        self.power_in_allowed = 0       # flag to allow power in
        self.solar_array = SolarInput(max_solar, peak_sun_hours)  # max kw, peak sun hours
        self.solar_input = 0
        self.load_power = LoadOutput(load_power, LOAD_START, LOAD_START + load_hours)  # kw, start time, end time
        self.load_hours = load_hours
        self.mps_type = mps_type #1 if hub, 0 if not hub
        self.name = name
        self.power_out_timer = 0 #initialize timer to 0
        self.power_in_timer = 0 #initialize timer to 0
        self.results = {}

        if self.mps_type == TYPE_HUB:
            self.power_in_threshold = HUB_POWER_IN_THRESHOLD
            self.power_out_threshold = HUB_POWER_OUT_THRESHOLD
        else:
            self.power_in_threshold = POWER_IN_THRESHOLD
            self.power_out_threshold = POWER_OUT_THRESHOLD

        for var in ["name", "soc", "remaining_battery", "bat_charge", "bat_discharge", "solar_input", "local_load", "power_in", "power_out", "power_in_allowed", "power_out_allowed"]:
            #create a results array for each variable
            self.results[var] = []

    def power_out(self, new_value=None):
        if new_value is not None:
            if self.mps_type == TYPE_HUB:
                #allow power out to be based onpower output based on demands of connected MPS's
                self.power_out = new_value
        else:
            return self.power_out

    def power_in(self, new_value=None):
        if new_value is not None:
            if self.mps_type == TYPE_HUB:
                #allow power in to be based on availability from connected MPS's
                self.power_in = new_value
        else:
            return self.power_in

    def update(self,iteration):

        self.updatePowerOutTimer()
        self.updatePowerInTimer()

        # new local load and solar power values
        self.local_load = self.load_power.get_output(iteration)

        #todo - fix this hack (remove the 4*) after fixing the solar to be higher
        self.solar_input = 4*self.solar_array.get_output(iteration)

        # update power out
        if self.soc > self.power_out_threshold:
            if (self.getPowerOutTimer() == 0):
                self.power_out_allowed = 1*GRAPH_SCALE
                self.power_out = self.max_power -  self.local_load  #todo - fix this: assumes the hub can handle as much as the mps can give it
                self.setPowerOutTimer(POWER_OUT_MIN_TIME)
        else:
            self.power_out_allowed = 0
            self.power_out = 0

        # update power in
        if self.soc < self.power_in_threshold:
            if (self.getPowerInTimer() == 0):
                self.power_in_allowed = 1*GRAPH_SCALE
                self.power_in = self.max_power #todo: fix this - assumes the hub can deliver as much as the mps can take
                self.setPowerInTimer(POWER_IN_MIN_TIME)
        else:
            self.power_in_allowed = 0
            self.power_in = 0

        # update battery charge and discharge
        self.bat_charge = self.solar_input
        if(self.power_in_allowed > 0 ):
            self.bat_charge = self.bat_charge + self.power_in

        self.bat_discharge = self.local_load
        if(self.power_out_allowed > 0):
            self.bat_discharge = self.bat_discharge + self.power_out

        # update remaining capacity and soc
        self.remaining_battery = self.remaining_battery + (self.bat_charge - self.bat_discharge) * INTERVAL_DURATION
        if(self.remaining_battery > self.max_battery):
            self.remaining_battery = self.max_battery
        self.soc = (self.remaining_battery / self.max_battery) * 100

        # Add to the results array
        for var in ["name", "soc", "remaining_battery", "bat_charge", "bat_discharge", "solar_input", "local_load", "power_in", "power_out", "power_in_allowed", "power_out_allowed"]:
            self.results[var].append(getattr(self, var))

    def get_results(self):
        return self.results
        #self.soc, self.remaining_battery, self.bat_charge, self.bat_discharge, self.local_load, self.solar_input, self.power_in, self.power_out, self.power_out_allowed, self.power_in_allowed

#    def get_status_strings(self):
#        return "{:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {}, {}".format(
#            self.soc, self.remaining_battery, self.bat_charge, self.bat_discharge, self.local_load, self.solar_input, self.power_in, self.power_out, self.power_out_allowed, self.power_in_allowed
#        )

    def setPowerOutTimer(self, value):
        self.power_out_timer = value

    def updatePowerOutTimer(self):
        if(self.power_out_timer > 0):
            self.power_out_timer = self.power_out_timer - 1

    def getPowerOutTimer(self):
        return self.power_out_timer

    def setPowerInTimer(self, value):
        self.power_in_timer = value

    def updatePowerInTimer(self):
        if(self.power_in_timer > 0):
            self.power_in_timer = self.power_in_timer - 1

    def getPowerInTimer(self):
        return self.power_in_timer
