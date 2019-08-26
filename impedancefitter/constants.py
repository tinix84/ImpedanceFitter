c0 = 2.41974648880026e-13    # air capacitance
cf = 2.42532194241202e-13    # stray capacitance

Rc = 9.05e-6  # unit(m). cell radius in buffer, this should be changed according to the chosed cell line
dm = 7e-9    # thickness of cell membrane m
ecp = 60     # permittivity for cytoplasm
p = 0.15     # volume fraction

Rn = (0.6)**(1. / 3.) * Rc  # Radius of nucleus, see Feldman 1999
dn = 40e-9   # thickness of nulear membrane
enp = 120    # Permittivity for nucleoplasm
