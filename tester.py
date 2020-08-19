import RPi.GPIO as G

G.setmode(G.BCM)
G.setup(20, G.OUT)
G.setup(21, G.OUT)
G.setup(22, G.OUT)

G.output(20, 0)
G.output(21, 0)
G.output(22, 1)
