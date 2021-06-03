# controls.py
# Takes keyboard input and sends info to Communications
import sys
import time

import pygame


class Controls:
    def __init__(self,
                 comms: Communications,
                 exit_program: ExitProgram,
                 screen_color: (int, int, int) = (0, 0, 0),
                 screen_dimensions: (int, int) = (100, 100)):
        """ Initializes the Controls class to be used by the Main class
        
            Parameters:
                comms - Object responsible for converting and sending the packets to the microcontroller subsystem
                    Methods:
                        kill_elec_ops : void
                            Sends a packet immediately to terminate all microcontroller operations
                        read_send : void
                            Reads key string inputted and converts the string into a packet, then sends the packet to the MCU through mcu.py
                            
                exit_program - Object responsible for closing all operations safely in an emergency
                    Methods:
                        exit : void
                            Closes both software and mcu operations immediately
        """
        self.comms: Communications = comms
        self.exit_program: ExitProgram = exit_program
        
        self.running: bool = True
        self.SCREEN_COLOR: (int, int, int) = screen_color
        self.SCREEN_SIZE: (int, int) = screen_dimensions
        
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        self.screen.fill(self.SCREEN_COLOR)
    
    def on_trigger(self, key: str):
        self.comms.read_send(key)

    def check_keys(self, event, keys):
        for (key, trigger: str) in keys:
            if event.key == key:
                self.on_trigger(trigger)
    
    def run(self):
        while self.running:
            keys_down = [
                (pygame.K_w, "w"),
                (pygame.K_a, "a"),
                (pygame.K_s, "s"),
                (pygame.K_d, "d"),
                (pygame.K_e, "e"),
                (pygame.K_q, "q"),
                (pygame.K_SPACE, "spacebar")
            ]
            
            keys_up = [
                (pygame.K_w, "sw"),
                (pygame.K_a, "sa"),
                (pygame.K_s, "ss"),
                (pygame.K_d, "sd"),
                (pygame.K_e, "se"),
                (pygame.K_q, "sq")
            ]
            
            keys_sensitive = [
                (pygame.K_w, "lw"),
                (pygame.K_a, "la"),
                (pygame.K_s, "ls"),
                (pygame.K_d, "ld"),
                (pygame.K_e, "le"),
                (pygame.K_q, "lq")
            ]
            
            if pygame.event.peek():
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                    if not (pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]):
                        if event.type == pygame.KEYDOWN:
                            self.check_keys(event, keys_down)
                    else:
                        if event.type == pygame.KEYDOWN:
                            self.check_keys(event, keys_sensitive)

                    if event.type == pygame.KEYUP:
                        self.check_keys(event, keys_up)
                        
            time.sleep(0.004)

        exit_program.exit()
