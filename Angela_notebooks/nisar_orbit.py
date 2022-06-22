from astropy import units as u

from poliastro.bodies import Earth, Mars, Sun
from poliastro.twobody import Orbit

a = 7125.48662 * u.km
ecc = 0.0011650 * u.one
inc = 98.40508 * u.deg
raan = -19.61601 * u.deg
argp = 89.99764 * u.deg
nu = -89.99818 * u.deg

orb = Orbit.from_classical(Earth, a, ecc, inc, raan, argp, nu)
orb.plot()