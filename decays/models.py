from __future__ import unicode_literals

from django.db import models
import math, random

class Particle(models.Model):
    """
    A particular subatomic particle, with properties including
    its mass, charge and name.
    """
    POSITIVE = 1
    NEGATIVE = -1
    NEUTRAL = 0
    CHARGE_CHOICES = (
        (POSITIVE, '+'),
        (NEGATIVE, '-'),
        (NEUTRAL, '0')
        )

    verbose_name = models.CharField(max_length=40, help_text = "e.g., K-plus")
    name = models.CharField(max_length=40, help_text = "e.g., K^+")
    mass = models.FloatField(help_text = "mass in MeV/c^2")
    charge = models.IntegerField(choices = CHARGE_CHOICES)

    def __unicode__(self):
        return '{0}'.format(self.verbose_name)


class AliasName(models.Model):
    """
    Names of particle aliases, such as X^+, Y^0, etc.
    """
    name = models.CharField(max_length = 40, help_text = "e.g., X^+")

    def __unicode__(self):
        return self.name

class AnalyzedEvent(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    owner = models.ForeignKey('auth.User', related_name='analyzed_events')

    def __unicode__(self):
        return self.title


class DecayType(models.Model):
    """
    A particular subatomic decay mode.  Notes: (i) can accommodate 1 -> 2
    and 1 -> 3 types of decays; (ii) if a particle has an 'alias', then
    the particle's identity will be hidden from the user; (iii) if a daughter
    particle has a decay associated with it, then that particle can itself decay.

    Probably should have abstracted out DecayProduct, or something, and had a many-to-many
    relation to it...!  Ah well.
    """
    parent = models.ForeignKey(Particle, related_name = 'decay_types')
    # if parent_alias is blank, then there is no alias and the type of
    # parent particle is NOT hidden from the user
    parent_alias = models.ForeignKey(AliasName, blank = True, null = True)

    daughter_one = models.ForeignKey(Particle, related_name = 'decay_types_d1')
    daughter_one_alias = models.ForeignKey(AliasName,
                                           blank = True, null = True,
                                           related_name = 'decay_types_d1a')
    daughter_one_decay = models.ForeignKey('DecayType', blank = True, null = True,
                                           related_name = 'decay_types_d1d')

    daughter_two = models.ForeignKey(Particle, related_name = 'decay_types_d2')
    daughter_two_alias = models.ForeignKey(AliasName,
                                           blank = True, null = True,
                                           related_name = 'decay_types_d2a')
    daughter_two_decay = models.ForeignKey('DecayType', blank = True, null = True,
                                           related_name = 'decay_types_d2d')

    # the third decay particle is optional
    daughter_three = models.ForeignKey(Particle, related_name = 'decay_types_d3',
                                       blank = True, null = True)
    daughter_three_alias = models.ForeignKey(AliasName,
                                             blank = True, null = True,
                                           related_name = 'decay_types_d3a')
    daughter_three_decay = models.ForeignKey('DecayType', blank = True, null = True,
                                           related_name = 'decay_types_d3d')

    name = models.CharField(max_length=200,
                            help_text = "e.g., X-plus -> mu-plus + Y^0")

    def __unicode__(self):
        return '{0}'.format(self.name)

    def is_two_body_decay(self):
        if self.daughter_three == None:
            return True
        else:
            return False



    def rand_momentum_config_parent_cm(self, xi_lab, theta_lab):
        """
        For a given DecayType object, determines a random configuration of momenta
        and energies for the final state particles in the parent center of mass, then
        boosts by xi_lab and rotates by theta_lab.
        """
        if self.is_two_body_decay():
            costheta = -1+2*random.random()
            theta = math.acos(costheta)

            m_a = self.parent.mass
            m_b = self.daughter_one.mass
            m_c = self.daughter_two.mass

            p_b = momentum(m_a, m_b, m_c)
            energy_b = energy(m_b, p_b)
            p_c = p_b
            energy_c = energy(m_c, p_c)

            coords_a = [m_a, 0, 0]
            coords_b = [energy_b, 0, p_b]
            coords_c = [energy_c, 0, -p_b]

            # boost and rotate pa relative to the lab

            coords_a = boost_then_rotate(xi_lab, theta_lab, coords_a)

            # now rotate pb and pc (in the cm) and then boost and rotate relative to the lab

            coords_b = boost_then_rotate(xi_lab, theta_lab,
                                         boost_then_rotate(0, theta, coords_b))
            coords_c = boost_then_rotate(xi_lab, theta_lab,
                                         boost_then_rotate(0, theta, coords_c))

            print coords_a
            print coords_b
            print coords_c

            print [coords_b[0]+coords_c[0],coords_b[1]+coords_c[1],coords_b[2]+coords_c[2]]

            # Note: if one of the decay products itself decays, then 'decay_dict" will be replaced
            #       by its own complete data_dict(!)
            data_dict = {'is_two_body_decay': True,
                         'xi_lab': xi_lab,
                         'theta_lab': theta_lab,
                         'name': self.name,
                         'parent': {
                             'particle_id': self.parent.id,
                             'mass': m_a,
                             'charge': self.parent.charge,
                             'energy_momentum': coords_a
                         },
                         'decay_products': [
                             {
                                 'particle_id': self.daughter_one.id,
                                 'mass': m_b,
                                 'charge': self.daughter_one.charge,
                                 'energy_momentum': coords_b,
                                 'decay_dict': None
                             },
                             {
                                 'particle_id': self.daughter_two.id,
                                 'mass': m_c,
                                 'charge': self.daughter_two.charge,
                                 'energy_momentum': coords_c,
                                 'decay_dict': None
                             }
                         ]
            }
            return data_dict

        else:
            # in this case need to do an extra boost and rotation....
            costheta = -1+2*random.random()
            theta = math.acos(costheta)

            costheta2 = -1+2*random.random()
            theta2 = math.acos(costheta2)

            m_a = self.parent.mass
            m_b = self.daughter_one.mass
            m_c = self.daughter_two.mass
            m_d = self.daughter_three.mass

            # the kinematics are the following:
            # a -> b + (c + d)
            # ...where (c + d) have invariant mass M2; so we regard this first as
            # a -> b + M2, then we boost to the M2 rest frame, and have
            # M2 -> c + d

            m_min = m_c + m_d
            m_max = m_a - m_b

            # the following is the invariant mass of the (c + d) pseudoparticle
            M2 = m_min+(m_max-m_min)*random.random()

            # momentum of M2 and of b in the a rest frame:
            P3 = momentum(m_a, m_b, M2)
            # boost parameter to get to M2 cm from a cm:
            xi_M2 = math.atanh(P3/energy(M2, P3))

            # energy of b in the a rest frame:
            energy_b = energy(m_b, P3)

            # coords of a in its own rest frame
            coords_a = [m_a, 0, 0]

            # coords of b in the a rest frame (M2 goes in the +y direction, before being rotated; b in the -y direction):
            coords_b = [energy_b, 0, -P3]

            # momentum of c and d in the M2 rest frame:
            P2 = momentum(M2, m_c, m_d)
            # energy of c and d in the M2 rest frame:
            energy_c = energy(m_c, P2)
            energy_d = energy(m_d, P2)

            # coords of c and d in the M2 rest frame
            coords_c = [energy_c, 0, P2]
            coords_d = [energy_d, 0, -P2]

            # boost and rotate pa relative to the lab

            coords_a = boost_then_rotate(xi_lab, theta_lab, coords_a)

            # now rotate pb (in the cm) and then boost and rotate relative to the lab

            coords_b = boost_then_rotate(xi_lab, theta_lab,
                                         boost_then_rotate(0, theta, coords_b))

            # finally, rotate pc and pd (in the M2 cm), then boost and rotate, and do it again....

            coords_c = boost_then_rotate(xi_lab, theta_lab,
                                         boost_then_rotate(xi_M2, theta,
                                                           boost_then_rotate(0, theta2, coords_c)))
            coords_d = boost_then_rotate(xi_lab, theta_lab,
                                         boost_then_rotate(xi_M2, theta,
                                                           boost_then_rotate(0, theta2, coords_d)))

#            print coords_a
#            print [coords_b[0]+coords_c[0]+coords_d[0],coords_b[1]+coords_c[1]+coords_d[1],
#                   coords_b[2]+coords_c[2]+coords_d[2]]

            data_dict = {'is_two_body_decay': False,
                         'xi_lab': xi_lab,
                         'theta_lab': theta_lab,
                         'name': self.name,
                         'parent': {
                             'particle_id': self.parent.id,
                             'mass': m_a,
                             'charge': self.parent.charge,
                             'energy_momentum': coords_a
                             },
                         'decay_products': [
                             {
                                 'particle_id': self.daughter_one.id,
                                 'mass': m_b,
                                 'charge': self.daughter_one.charge,
                                 'energy_momentum': coords_b,
                                 'decay_dict': None
                             },
                             {
                                 'particle_id': self.daughter_two.id,
                                 'mass': m_c,
                                 'charge': self.daughter_two.charge,
                                 'energy_momentum': coords_c,
                                 'decay_dict': None
                             },
                             {
                                 'particle_id': self.daughter_three.id,
                                 'mass': m_d,
                                 'charge': self.daughter_three.charge,
                                 'energy_momentum': coords_d,
                                 'decay_dict': None
                             }
                         ]
            }

            return data_dict


def lambda_func(x, y, z):
    """
    Utility function used to find magnitude of the momenta of two particles
    in the rest frame of the parent particle.
    """
    return x**2+y**2+z**2-2*(x*y+x*z+y*z)

def momentum(m_a, m_b, m_c):
    """
    Calculates the momenta of b and c in the rest from of a, for a -> b + c.
    """
    return math.sqrt(lambda_func(m_a**2, m_b**2, m_c**2))/2/m_a

def energy(m, p):
    """
    Calculates the energy of a particle that has mass m and momentum p.
    """
    return math.sqrt(m**2+p**2)

def boost_then_rotate(xi, theta, coord_list):
    """
    Performs a boost (boost parameter xi) in the y direction,
    followed by a rotation by polar angle theta away from the
    y axis, in the x-y plane.  coord_list is of the form [energy, x, y].
    """
    boost_matrix = [[math.cosh(xi), 0, math.sinh(xi)],
                    [math.sinh(xi)*math.sin(theta), math.cos(theta), math.cosh(xi)*math.sin(theta)],
                    [math.sinh(xi)*math.cos(theta), -math.sin(theta), math.cosh(xi)*math.cos(theta)]]

    boosted_coord_list = [0, 0, 0]

    for j in range(len(coord_list)):
        for i in range(len(boost_matrix[j])):
            boosted_coord_list[i] += boost_matrix[i][j]*coord_list[j]

    return boosted_coord_list

