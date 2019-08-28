#    The ImpedanceFitter is a package that provides means to fit impedance spectra to theoretical models using open-source software.
#
#    Copyright (C) 2018, 2019 Leonard Thiele, leonard.thiele[AT]uni-rostock.de
#    Copyright (C) 2018, 2019 Julius Zimmermann, julius.zimmermann[AT]uni-rostock.de
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import matplotlib.pyplot as plt
import numpy as np
import yaml
from scipy.constants import epsilon_0 as e0
import logging

logger = logging.getLogger('impedancefitter-logger')


def Z_CPE(omega, k, alpha):
    return (1. / k) * (1j * omega) ** (-alpha)


def Z_sus(omega, es, kdc, c0, cf):  # only valid for cole_cole_fit and suspension_fit
    return 1. / (1j * es * omega * c0 + (kdc * c0) / e0 + 1j * omega * cf)


def e_sus(omega, eh, el, tau, a):  # this is only valid for the cole_cole_fit and suspension_fit
    return eh + (el - eh) / (1. + (1j * omega * tau) ** (a))


def compare_to_data(omega, Z, Z_fit, filename, subplot=None):
    '''
    plots the relative difference of the fitted function to the data
    '''
    if subplot is None:
        plt.figure()
    else:
        plt.subplot(subplot)
    plt.xscale('log')
    if subplot is None:
        plt.title(str(filename) + "relative difference to data")
    else:
        plt.title("relative difference to data")
    plt.ylabel('rel. difference [%] to data')
    plt.plot(omega, 100. * np.abs((Z.real - Z_fit.real) / Z.real), 'g', label='rel .difference real part')
    plt.plot(omega, 100. * np.abs((Z.imag - Z_fit.imag) / Z.imag), 'r', label='rel. difference imag part')
    plt.legend()


def return_diel_properties(omega, epsc):
    eps_r = epsc.real
    conductivity = -epsc.imag * e0 * omega
    return eps_r, conductivity


def plot_dielectric_properties(omega, cole_cole_output, suspension_output):
    '''
    eps is the complex valued permitivity from which we extract relative permitivity and conductivity
    compares the dielectric properties before and after the compensation
    '''
    eh = suspension_output.params.valuesdict()['eh']
    el = suspension_output.params.valuesdict()['epsi_l']
    tau = suspension_output.params.valuesdict()['tau']
    a = suspension_output.params.valuesdict()['a']
    eps_fit = e_sus(omega, eh, el, tau, a)
    eps_r_fit, cond_fit = return_diel_properties(omega, eps_fit)
    eh = cole_cole_output.params.valuesdict()['eh']
    el = cole_cole_output.params.valuesdict()['epsi_l']
    tau = cole_cole_output.params.valuesdict()['tau']
    a = cole_cole_output.params.valuesdict()['a']
    eps_fit_corrected = e_sus(omega, eh, el, tau, a)
    eps_r_fit_corr, cond_fit_corr = return_diel_properties(omega, eps_fit_corrected)
    plt.figure()
    plt.suptitle('dielectric properties compared', y=1.05)
    plt.subplot(211)
    plt.title("permittivity")
    plt.xscale('log')
    plt.yscale('log')
    plt.plot(omega, eps_r_fit, label="fit")
    plt.plot(omega, eps_r_fit_corr, label="fit_corr")
    plt.legend()

    plt.subplot(212)
    plt.title("conductivity")
    plt.xscale('log')
    plt.plot(omega, cond_fit, label="fit")
    plt.plot(omega, cond_fit_corr, label="corr")
    plt.legend()
    plt.tight_layout()
    plt.show()


def set_parameters_from_yaml(params, modelName):
    """
    for suspension model: if wanted one could create an own file
    """
    if(modelName == 'single_shell'):
        single_shell_input = open('single_shell_input.yaml', 'r')
        bufdict = yaml.safe_load(single_shell_input)
    if(modelName == 'double_shell'):
        double_shell_input = open('double_shell_input.yaml', 'r')
        bufdict = yaml.safe_load(double_shell_input)
    if(modelName == 'cole_cole' or modelName == 'suspension'):
        cole_cole_input = open('cole_cole_input.yaml', 'r')
        bufdict = yaml.safe_load(cole_cole_input)
    if(modelName == 'suspension'):
        try:
            suspension_input = open('suspension_input.yaml', 'r')
            bufdict = yaml.safe_load(suspension_input)
        except FileNotFoundError:
            # remove values from cole_cole model that are not needed
            del bufdict['alpha']
            del bufdict['k']
    for key in bufdict:
        params.add(key, value=float(bufdict[key]['value']), min=float(bufdict[key]['min']), max=float(bufdict[key]['max']), vary=bool(bufdict[key]['vary']))
    return params


def load_constants_from_yaml(model=None):
    constants_file = open('constants.yaml', 'r')
    constants = yaml.safe_load(constants_file)
    constants['Rn'] = eval(constants['Rn'])
    return process_constants(constants, model)


def process_constants(constants, model=None):
    for c in constants:
        if not isinstance(constants[c], float):
            constants[c] = float(constants[c])
    if model == 'SingleShell' or model == 'DoubleShell':
        constants['v1'] = (1. - constants['dm'] / constants['Rc'])**3
    if model == 'DoubleShell':
            constants['v2'] = (constants['Rn'] / (constants['Rc'] - constants['dm']))**3
            constants['v3'] = (1. - constants['dn'] / constants['Rn'])**3
    for c in constants:
        logger.info("Constant {} has value {}.".format(c, constants[c]))
    return constants
