import pygame
import sys


class Controls:
    def __init__(self, comms, exit_program):
        self.comms = comms
        self.exit_program = exit_program
        
        self.running = True
        self.SCREEN_COLOR = (0, 0, 0)
        self.SCREEN_SIZE = (100, 100)
        
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        self.screen.fill(self.SCREEN_COLOR)
    
    def on_trigger(self, key):
        self.comms.read_send(key)

    def key_down(self, event):
        keys = [
            (pygame.K_w, "w"),
            (pygame.K_a, "a"),
            (pygame.K_s, "s"),
            (pygame.K_d, "d"),
            (pygame.K_e, "e"),
            (pygame.K_q, "q"),
            (pygame.K_SPACE, "spacebar")
        ]
        
        for (key, trigger) in keys:
            if event.key == key:
                self.on_trigger(trigger)
            
    def key_up(self, event):
        keys = [
            (pygame.K_w, "sw"),
            (pygame.K_a, "sa"),
            (pygame.K_s, "ss"),
            (pygame.K_d, "sd"),
            (pygame.K_e, "se"),
            (pygame.K_q, "sq")
        ]
        
        for (key, trigger) in keys:
            if event.key == key:
                self.on_trigger(trigger)
            
    def sensitive_key_down(self, event):
        keys = [
            (pygame.K_w, "lw"),
            (pygame.K_a, "la"),
            (pygame.K_s, "ls"),
            (pygame.K_d, "ld"),
            (pygame.K_e, "le"),
            (pygame.K_q, "lq")
        ]
        
        for (key, trigger) in keys:
            if event.key == key:
                self.on_trigger(trigger)
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if not (pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]):
                    if event.type == pygame.KEYDOWN:
                        self.key_down(event)
                else:
                    if event.type == pygame.KEYDOWN:
                        self.sensitive_key_down(event)

                if event.type == pygame.KEYUP:
                    self.key_up(event)

        exit_program.Exit()
