import keyboard
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
        print("Sent")

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if not (pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]):
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w:
                            self.on_trigger("w")
                        if event.key == pygame.K_a:
                            self.on_trigger("a")
                        if event.key == pygame.K_s:
                            self.on_trigger("s")
                        if event.key == pygame.K_d:
                            self.on_trigger("d")
                        if event.key == pygame.K_e:
                            self.on_trigger("e")
                        if event.key == pygame.K_q:
                            self.on_trigger("q")
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w:
                            self.on_trigger("lw")
                        if event.key == pygame.K_a:
                            self.on_trigger("la")
                        if event.key == pygame.K_s:
                            self.on_trigger("ls")
                        if event.key == pygame.K_d:
                            self.on_trigger("ld")
                        if event.key == pygame.K_e:
                            self.on_trigger("le")
                        if event.key == pygame.K_q:
                            self.on_trigger("lq")

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w:
                        self.on_trigger("sw")
                    if event.key == pygame.K_a:
                        self.on_trigger("sa")
                    if event.key == pygame.K_s:
                        self.on_trigger("ss")
                    if event.key == pygame.K_d:
                        self.on_trigger("sd")
                    if event.key == pygame.K_e:
                        self.on_trigger("se")
                    if event.key == pygame.K_q:
                        self.on_trigger("sq")
                    #if event.type == pygame.K_c:
                        # Take a screenshot
                    if event.key == pygame.K_SPACE:
                        self.on_trigger("spacebar")

        exit_program.Exit()

#ctrls = Controls(None, None)
#ctrls.run()
