import random


from configuration import *




class Wind:

    def __init__(self, values, steps_per_transition=STEPS_PER_TRANSISION, delay_update_wind=DELAY_UPDATE_WIND):
        self.values = values
        self.steps_per_transition = steps_per_transition
        self.delay_update_wind = delay_update_wind

        self.start_value = random.choice(values)
        self.end_value = random.choice(values)
        self.current_force = self.start_value

        self.current_step = 0
        self.pause_timer = 0
        self.in_pause = False

    def update(self):
        if self.in_pause:
            # on reste sur la valeur finale
            self.pause_timer += 1
            if self.pause_timer >= self.delay_update_wind:
                # on choisit une nouvelle cible
                self.start_value = self.end_value
                self.end_value = random.choice(self.values)
                self.current_step = 0
                self.pause_timer = 0
                self.in_pause = False
        else:
            # interpolation vers end_value
            t = self.current_step / self.steps_per_transition
            self.current_force = self.start_value + (self.end_value - self.start_value) * t
            self.current_step += 1
            if self.current_step >= self.steps_per_transition:
                # on atteint la valeur cible, on lance le pause
                self.current_force = self.end_value
                self.in_pause = True
                self.pause_timer = 0

        return self.current_force
