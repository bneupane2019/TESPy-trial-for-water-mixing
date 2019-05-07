import numpy as np
from tespy import cmp, con, nwk, hlp


# inputs


class Parameters:
    def __init__(self,tw, tc, td, ta, q, cp):
        self.Tw = tw
        self.Tc = tc
        self.Td = td
        self.Ta = ta
        self.Q = q
        self.Cp = cp


def select_parameters():
    tw = 45+273
    tc = 8+273
    td = 40+273
    ta = 15+273
    q = 100
    cp = 4.19
    p = Parameters(tw, tc, td, ta, q, cp)
    return p


parameters_data = select_parameters()


def mass_flow():
    mf = parameters_data.Q/(4.19*(parameters_data.Td-parameters_data.Tc))
    E_w = (hlp.h_pT(100000,318,'H2O'))
    E_c = (hlp.h_pT(100000,281,'H2O'))
    mfc = (100-(E_w*mf))/(E_c-E_w)
    mfw = mf-mfc
    return mfc, mfw


mass_flow_data = mass_flow()

nw = nwk.network(fluids=['H2O'], T_unit='K', p_unit='bar', h_unit='kJ / kg',
                 m_unit='kg / s')


hw_in = cmp.source('hot water')
ww_out = cmp.sink('warm water out')
cc_in = cmp.source('cold water in')
m = cmp.merge('merge',num_in=2)

# connections
lin1 = con.connection(hw_in, 'out1', m, 'in1')
lin2 = con.connection(cc_in, 'out1', m, 'in2')
lin3 = con.connection(m, 'out1', ww_out, 'in1')

nw.add_conns(lin1, lin2, lin3)

# connection parametrization
lin1.set_attr(fluid={'H2O': 1}, T=parameters_data.Tw, m=mass_flow_data[0])
lin2.set_attr(fluid={'H2O': 1}, T=parameters_data.Tc, m=mass_flow_data[1])
lin3.set_attr(T=parameters_data.Td)

# solve
nw.solve('design')
mass_flow = round(lin3.m.val_SI,2)
print('Demand mass_flow = ',mass_flow)

# demand exergy calculations
Tf = parameters_data.Td - parameters_data.Tc\
     - parameters_data.Ta * np.log(parameters_data.Td/parameters_data.Tc)
Supply_exergy = mass_flow*Tf*parameters_data.Cp
print('Supply_exergy =', Supply_exergy)

# input exergy calculations
CarnotExergy_inputm1 = parameters_data.Q*(
        1-(parameters_data.Ta/parameters_data.Tw))
CarnotExergy_inputm2=parameters_data.Q*(
        1-(parameters_data.Ta/parameters_data.Tc))
Input_exergy = CarnotExergy_inputm1+CarnotExergy_inputm2
print('Input_exergy =', Input_exergy)
Consumed_exergy=Input_exergy-Supply_exergy
print('Exergy_consumed =', Consumed_exergy)
