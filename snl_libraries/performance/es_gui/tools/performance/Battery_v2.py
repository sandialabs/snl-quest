# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 11:24:37 2020

@author: wolis
"""

import scipy.optimize

class Battery:
    
    def __init__(self,eCap,pRat,n_s,n_p,q_rate = 2.5,v_rate = 3.6,r = 0.02,k = 0.005,tau = 0.25):
        
        self.eCap = eCap
        self.pRat = pRat
        
        self._p_c = 0
        self._p_d = 0
        self._heat_loss = 0
        self._pe_heat_loss = 0
        self._soc_begin = 0.5*eCap
        self._soc_end = 0
        self.n_s = n_s
        self.n_p = n_p
        self.q_rate = q_rate
        self.v_rate = v_rate
        self.r = r
        self.k = k
        self.tau = tau
        
        
    
    @property
    def p_c(self):
        """
            Charge Power. {MW}
        """
        return self._p_c
    
    @p_c.setter
    def p_c(self,value):
        
        if value > self.pRat:
            value = self.pRat
            
        self._p_c = value
    
    @property
    def p_d(self):
        """
            Discharge Power. {MW}
        """
        return self._p_d
    
    @p_d.setter
    def p_d(self,value):
        
        if value > self.pRat:
            value = self.pRat
            
        self._p_d = value
        
    @property
    def heat_loss(self):
        """
            Current heat loss of battery. {MW}
        """
        return self._heat_loss
    
    @heat_loss.setter
    def heat_loss(self,value):
        self._heat_loss = value
        
    @property
    def pe_heat_loss(self):
        """
            Current heat loss of power electronics. {MW}
        """
        return self._pe_heat_loss
    
    @pe_heat_loss.setter
    def pe_heat_loss(self,value):
        self._pe_heat_loss = value
        
    @property
    def soc_begin(self):
        """
            Current state of charge of battery. {MWh}
        """
        return self._soc_begin
    
    @soc_begin.setter
    def soc_begin(self,value):
        self._soc_begin = value
        
    @property
    def soc_end(self):
        """
            State of charge after simulation. {MWh}
        """
        return self._soc_end
    
    @soc_end.setter
    def soc_end(self,value):
        self._soc_end = value
        
    def find_pc(self,P_c):
        """
            For root finding algorithm to determine charge required to reach 95% charge.
        """
        
        soe = 0.95*self.eCap
        P_d = 0
        
        coef = self.q_rate/(self.v_rate*self.eCap)
        const_term = self.k*self.eCap*(self.eCap - self.soc_begin)/self.soc_begin
        heat_term_charge = (self.r + self.k*self.eCap/(self.eCap - self.soc_begin))*(self.n_p*P_c)**2
        heat_term_discharge = (self.r + self.k*self.eCap/self.soc_begin)*(self.p_d/self.n_p)**2
        P_lc = coef*(heat_term_charge + const_term*P_c*self.n_p)
        P_ld = coef*(heat_term_discharge + const_term*P_d/self.n_p)
        f_c = P_c*self.n_p - P_lc
        f_d = P_d/self.n_p + P_ld
        
        return self.n_s*self.soc_begin + f_c*self.tau - f_d*self.tau - soe

    def find_pd(self,P_d):
        """
            For root finding algorithm to determine discharge required to reach 5% charge.
        """
        
        soe = 0.05*self.eCap
        P_c = 0
        
        coef = self.q_rate/(self.v_rate*self.eCap)
        const_term = self.k*self.eCap*(self.eCap - self.soc_begin)/self.soc_begin
        heat_term_charge = (self.r + self.k*self.eCap/(self.eCap - self.soc_begin))*(self.n_p*P_c)**2
        heat_term_discharge = (self.r + self.k*self.eCap/self.soc_begin)*(self.p_d/self.n_p)**2
        P_lc = coef*(heat_term_charge + const_term*P_c*self.n_p)
        P_ld = coef*(heat_term_discharge + const_term*P_d/self.n_p)
        f_c = P_c*self.n_p - P_lc
        f_d = P_d/self.n_p + P_ld
    
        return self.n_s*self.soc_begin + f_c*self.tau - f_d*self.tau - soe
    
    def new_soe_Lion_Pbacid(self):
        """
            Determines next state of charge based upon charge/discharge profile.
        """
        

        coef = self.q_rate/(self.v_rate*self.eCap)
        const_term = self.k*self.eCap*(self.eCap - self.soc_begin)/self.soc_begin
        heat_term_charge = (self.r + self.k*self.eCap/(self.eCap - self.soc_begin))*(self.n_p*self.p_c)**2
        heat_term_discharge = (self.r + self.k*self.eCap/self.soc_begin)*(self.p_d/self.n_p)**2
        P_lc = coef*(heat_term_charge + const_term*self.p_c*self.n_p)
        P_ld = coef*(heat_term_discharge + const_term*self.p_d/self.n_p)
        f_c = self.p_c*self.n_p - P_lc
        f_d = self.p_d/self.n_p + P_ld
        
        soe = self.n_s*self.soc_begin + f_c*self.tau - f_d*self.tau
        
        self.soc_end = soe
        self.heat_loss = coef*heat_term_charge + coef*heat_term_discharge
        self.pe_heat_loss = (1-self.n_p)*(self.p_c + self.p_d)
    
    def sim_battery(self):
        """
            Controls the battery to charge/discharge within physical limits.
        """
            
        self.new_soe_Lion_Pbacid()
        
        if self.soc_end >= self.eCap*0.95:                
            try:
                sol = scipy.optimize.root_scalar(self.find_pc, bracket = [0,self.pRat], method = 'bisect')
                self.p_c = sol.root
            
                self.new_soe_Lion_Pbacid()
            except ValueError as e:
#                print(e)
#                print('Not charging')
                self.soc_end = self.soc_begin
                heat_loss = 0
            except BaseException as e:
                print('Charge root finding did not work')
                print(e)
                print(self.soc_begin,self.eCap,self.p_c)            
        elif self.soc_end <= self.eCap*0.05:
            try:
                sol = scipy.optimize.root_scalar(self.find_pd, bracket = [0,self.pRat], method = 'bisect')
                self.p_d = sol.root
                
                self.new_soe_Lion_Pbacid()
            except ValueError as e:
#                print(e)
#                print('Charging...')
                self.p_d = 0
                self.p_c = self.pRat
                self.new_soe_Lion_Pbacid()
            except BaseException as e:
                print('Discharge root finding did not work')
                print(e)
                print(self.soc_begin,self.eCap,self.p_c) 