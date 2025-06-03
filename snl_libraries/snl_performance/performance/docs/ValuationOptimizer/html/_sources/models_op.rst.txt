.. _op_model_desc:

Optimization models
===================

The optimization models are discrete-time, energy-based linear programs. The discrete time steps are assumed to be one hour. Without loss of generality, the time horizon for optimization is assumed to be one month. The energy storage model is based on tracking the ESS state of charge based on the energy charged and/or discharged at each time step.

Here we will describe the expressions that comprise the objective functions and constraints for each model implemented.

The following are the decision variables:

======================= ====================================================================================================================== =====
Decision variables      Description                                                                                                            Units
======================= ====================================================================================================================== =====
:math:`q_i^\text{d}`    energy sold (discharged) from time period :math:`i` to :math:`i+1`                                                     MWh
:math:`q_i^\text{r}`    energy purchased (charged) from time period :math:`i` to :math:`i+1`                                                   MWh
:math:`q_i^\text{reg}`  energy bid for regulation up/down at time :math:`t` in a one product frequency regulation market                       MWh
:math:`q_i^\text{ru}`   energy bid for regulation up from time period :math:`i` to :math:`i+1`  in a two product frequency regulation market   MWh
:math:`q_i^\text{rd}`   energy bid for regulation down from time period :math:`i` to :math:`i+1`  in a two product frequency regulation market MWh
:math:`s_i`             device state of charge at time period :math:`i`                                                                        MWh                                            
======================= ====================================================================================================================== =====

While not explicitly appearing as a decision variable in the mathematical model, :math:`s_i` is defined as one for the Pyomo formulation. The following are the energy storage device parameters:

==================================== ====================================================== =====
Storage parameters                   Description                                            Units
==================================== ====================================================== =====
:math:`\bar{S}`                      energy capacity                                        MWh
:math:`\bar{Q}`                      energy charge/discharge rating                         MWh
:math:`S_0`                          initial state of charge                                MWh
:math:`\delta_\text{s}^\text{min}`   fraction of energy capacity to reserve for discharging                                                     
:math:`\delta_\text{s}^\text{max}`   fraction of energy capacity to reserve for charging                                                        
:math:`\delta_\text{reg}^\text{min}` fraction of regulation bid to reserve for discharging                                                      
:math:`\delta_\text{reg}^\text{max}` fraction of regulation bid to reserve for charging
:math:`\eta_\text{s}`                self-discharge efficiency                              %/h
:math:`\eta_\text{c}`                round trip efficiency                                  %
==================================== ====================================================== =====

The following are market-related parameters, typically derived from market data:

============================= ============================================================================================================= =====
Market parameters             Description
============================= ============================================================================================================= =====
:math:`\delta_i^\text{ru}`    fraction of regulation up bid actually deployed from time period :math:`i` to :math:`i+1`                                          
:math:`\delta_i^\text{rd}`    fraction of regulation down bid actually deployed from time period :math:`i` to :math:`i+1`                                      
:math:`\lambda_i`             price of electricity from time period :math:`i` to :math:`i+1`                                                $/MWh
:math:`\lambda_i^\text{c}`    frequency regulation capacity price from time period :math:`i` to :math:`i+1` in a one product market         $/MWh
:math:`\lambda_i^\text{c,ru}` frequency regulation up capacity price from time period :math:`i` to :math:`i+1` in a two product market      $/MWh
:math:`\lambda_i^\text{c,rd}` frequency regulation down capacity price from time period :math:`i` to :math:`i+1` in a two product market    $/MWh
:math:`\lambda_i^\text{p}`    frequency regulation performance price from time period :math:`i` to :math:`i+1` in a one product market      $/MWh
:math:`\lambda_i^\text{p,ru}` frequency regulation up performance price from time period :math:`i` to :math:`i+1` in a two product market   $/MWh
:math:`\lambda_i^\text{p,rd}` frequency regulation down performance price from time period :math:`i` to :math:`i+1` in a two product market $/MWh
:math:`\beta_i`               mileage ratio from time period :math:`i` to :math:`i+1`                                                                             
:math:`\alpha`                make whole parameter for adjusting regulation credit
:math:`R`                     interest/discount rate          
:math:`\gamma_i`              performance score from time period :math:`i` to :math:`i+1`
============================= ============================================================================================================= =====

The time-indexed variables are defined for all time periods (hours) :math:`i \in \mathcal{T}` where :math:`\mathcal{T} = \{0, 1, ..., N-1\}` and :math:`N` equals the number of time periods in the time horizon, which is assumed to be one month. The state of charge :math:`s_i` is defined for :math:`i = \{0, 1, ..., N\}` (one additional time step) to ensure that the final state of charge is still properly constrained.

Furthermore, the final state of charge is constrained to be equal to the initial state of charge, :math:`S_0`, which is by default equal to :math:`\delta_\text{s}^\text{min} \bar{S}`, the minimum state of charge (reserved for discharging).

Arbitrage only
^^^^^^^^^^^^^^

Arbitrage, in this context, refers to the managing state of charge by buying and selling energy. A storage device engaging in arbitrage is trying to maximize profit from buying energy at low prices and selling energy at higher prices, subject to the constraints of the storage facility. Valuation with this particular revenue stream only has the same formulation among all market areas.

For a storage device that participates in arbitrage only, the decision variables are :math:`q_i^\text{d}`, :math:`q_i^\text{r}`, and :math:`s_i`.

The recursion relation describing the state of charge :math:`s_i` for :math:`i > 0` is given by:

.. math::
   s_{i+1} = \eta_\text{s} s_i + \eta_\text{c} q_i^\text{r} - q_i^\text{d}

with:

.. math::
  s_0 = S_0

The constraints on the state of charge :math:`s_i`, the quantity purchased :math:`q_i^\text{r}`, and the quantity sold :math:`q_i^\text{d}` at each time step :math:`i` are given by:

.. math::
  \delta_\text{s}^\text{min} \bar{S} \leq s_i 
  
  s_i \leq (1 - \delta_\text{s}^\text{max}) \bar{S}

  q_i^\text{r} + q_i^\text{d} \leq \bar{Q}

  s_N = S_0

for all :math:`i \in \mathcal{T}`. The first two sets of constraints limits the state of charge between its minimum and maximum values as specified at each time step. The next set of constraints limits the total energy charged over the time step (both charging and discharging) to the energy charge limit (derived from the power limit) at each time step. This constraint permits charging and discharging during the same time step but restricts the throughput based on the power rating.

The objective is to maximize the total revenue over the time horizon. We do not include costs associated with, e.g., charging or discharging. If data is available, it may be included in the objective function, changing the objective to profit maximization. Otherwise, the objective function for the arbitrage only model is:

.. math::
   J = \sum_{i \in \mathcal{T}} \left [q_i^\text{d} - q_i^\text{r} \right ] \lambda_i e^{-Ri}

Revenue is solely generated by buying and selling energy. The arbitrage only model can therefore be summarized as:

.. math::
  \max_{q^\text{d}, q^\text{r}, s} J

subject to:

.. math::
  s_{i+1} = \eta_\text{s} s_i + \eta_\text{c} q_i^\text{r} - q_i^\text{d}

  \delta_\text{s}^\text{min} \bar{S} \leq s_i \leq (1 - \delta_\text{s}^\text{max}) \bar{S}

  q_i^\text{r} + q_i^\text{d} \leq \bar{Q}

  s_0 = S_0

  s_N = S_0

for all :math:`i \in \mathcal{T}`.

.. note:: In many areas, the net energy for regulation is settled at the real-time price. This provides an additional arbitrage opportunity between the day ahead price and the real-time price. These models are primarily concerned with arbitrage and regulation revenue from the day ahead market; therefore, the price :math:`\lambda_i` typically represents the day ahead LMP. While this does not reflect the actual settlement process, it keeps the optimization from incorporating any arbitrage between the day ahead and the real-time market.

Arbitrage and regulation (ERCOT)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ERCOT has a frequency regulation market that does not explicitly provide credits based on frequency regulation performance, only for capacity offered. It offers different prices for regulation up and regulation down is thus considered a *two product frequency regulation* market.

For a storage device that participates in both arbitrage and frequency regulation, the decision variables are :math:`q_i^\text{d}`, :math:`q_i^\text{r}`, :math:`q_i^\text{ru}`, :math:`q_i^\text{rd}`, and :math:`s_i`.

The recursion relation describing the state of charge :math:`s_i` for :math:`i > 0` is given by:

.. math::
  s_{i+1} = \eta_\text{s} s_i + \eta_\text{c} q_i^\text{r} - q_i^\text{d} + \eta_\text{c} \delta_i^\text{rd} q_i^\text{rd} - \delta_i^\text{ru} q_i^\text{ru}

with:

.. math::
  s_0 = S_0

The constraints on the decision variables are given by:

.. math::
  \delta_\text{reg}^\text{min} q_i^\text{ru} + \delta_\text{s}^\text{min} \bar{S} \leq s_{i+1} 
  
  s_{i+1} \leq (1 - \delta_\text{s}^\text{max}) \bar{S} - \eta_\text{c} \delta_\text{reg}^\text{max} q_i^\text{rd}

  q_i^\text{r} + q_i^\text{d} + q_i^\text{ru} + q_i^\text{rd} \leq \bar{Q}

  s_N = S_0

for all :math:`t \in \mathcal{T}`. The first two sets of constraints limits the state of charge between its minimum and maximum values as specified at each time step. The :math:`\delta_\text{reg}` factors are safety factors used to reserve energy capacity headroom and/or legroom to avoid penalties due to not meeting regulation obligations; they are defined as fractions of the capacity bid. The next set of constraints limits the total energy charged over the time step (both charging and discharging) to the energy charge limit (derived from the power limit) at each time step. This constraint permits charging and discharging during the same time step but restricts the throughput based on the power rating. Bids for regulation up/down are constrained together with arbitrage-related actions.

The objective function for the model is:

.. math::
  J = \sum_\mathcal{i \in T} \left [ \left(q_i^\text{d} - q_i^\text{r} \right) \lambda_i + \lambda_i^{c,ru} q_i^\text{ru} + \lambda_i^{c,rd} q_i^\text{rd} + \left( \delta_i^\text{ru} q_i^\text{ru} - \delta_i^\text{rd} q_i^\text{rd} \right) \lambda_i \right ] e^{-Ri}

In addition to the arbitrage revenue stream, electricity prices are accounted for depending on the actual amount of the regulation bid that is called upon. Additionally, the revenue from regulation up/down bids are included. The ERCOT arbitrage and regulation model can therefore be summarized as:

.. math::
  \max_{q^\text{d}, q^\text{r}, q^\text{ru}, q^\text{rd}, s} J

subject to:

.. math::
  s_{i+1} = \eta_\text{s} s_i + \eta_\text{c} q_i^\text{r} - q_i^\text{d} + \eta_\text{c} \delta_i^\text{rd} q_i^\text{rd} - \delta_i^\text{ru} q_i^\text{ru}

  \delta_\text{reg}^\text{min} q_i^\text{ru} + \delta_\text{s}^\text{min} \bar{S} \leq s_{i+1} \leq (1 - \delta_\text{s}^\text{max}) \bar{S} - \eta_\text{c} \delta_\text{reg}^\text{max} q_i^\text{rd}

  q_i^\text{r} + q_i^\text{d} + q_i^\text{ru} + q_i^\text{rd} \leq \bar{Q}

  s_0 = S_0

  s_N = S_0

for all :math:`i \in \mathcal{T}`.

.. note:: The :math:`\delta_i^\text{ru}` and :math:`\delta_i^\text{rd}` terms are assumed to be fixed for all time in the absence of additional information. 

Arbitrage and regulation (PJM)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PJM has a *single product* frequency regulation market that provides payment for performance.

For a storage device that participates in both arbitrage and frequency regulation, the decision variables are :math:`q_d(t)`, :math:`q_r(t)`, :math:`q_{reg}(t)`, and :math:`s(t)`.

The recursion relation describing the state of charge :math:`s(t)` for time :math:`t > 0` is given by:

.. math::
  s(t+1) = \eta_s s(t) + \eta_c q_r(t) - q_d(t) + \eta_c \gamma_{rd}(t) q_{reg}(t) - \gamma_{ru}(t) q_{reg}(t)

with:

.. math::
  s(0) = S_0

The constraints on the decision variables are given by:

.. math::
  \gamma_{reg}^{min} q_{reg}(t) + \gamma_{s}^{min} \bar{S} \leq s(t+1) 
  
  s(t+1) \leq (1 - \gamma_{s}^{max}) \bar{S} - \eta_c \gamma_{reg}^{max} q_{reg}(t)

  q_r(t) + q_d(t) + q_{reg}(t) \leq \bar{Q}

  S(N) = S_0

for all :math:`t \in \mathcal{T}`. The first two sets of constraints limits the state of charge between its minimum and maximum values as specified at each time step. The :math:`\gamma_{reg}` factors are safety factors used to reserve energy capacity headroom and/or legroom to avoid penalties due to not meeting regulation obligations; they are defined as fractions of the capacity bid. The next set of constraints limits the total energy charged over the time step (both charging and discharging) to the energy charge limit (derived from the power limit) at each time step. This constraint permits charging and discharging during the same time step but restricts the throughput based on the power rating. Bids for regulation capacity are constrained together with arbitrage-related actions.

The objective function for the model is:

.. math::
  J = \sum_\mathcal{T} \left [ \left(q_d(t) - q_r(t) \right) \lambda(t) + \left( \beta(t) \lambda_p(t) + \lambda_c(t) \right) \Gamma q_{reg}(t) \right ] e^{-Rt}

In addition to the arbitrage revenue stream, terms for revenue based on the regulation bid are included. A performance score term, :math:`\Gamma \in [0, 1]`, scales the total credit based on historical demonstrated ability for the device to follow regulation signals; in general, it is computed hourly based on delay, correlation, and precision scores. The total regulation credit consists of two different prices. The performance price, :math:`\lambda_p(t)`, is scaled by the mileage ratio, :math:`\beta`, defined as:

.. math::
  \beta(t) := \frac{\text{RegD mileage}}{\text{RegA mileage}}

where RegD is a high pass filtered ACE signal designed for faster responding resources and RegA is the low pass filtered equivalent designed for traditional regulating resources. Mileage is the amount of movement requested by the regulation control signal. By design, a larger ratio of RegD mileage to RegA mileage will increase :math:`\beta(t)` and lead to larger credits from :math:`\lambda_p(t)`.

The PJM arbitrage and regulation model can be summarized as:

.. math::
  \max_{q_d(t), q_r(t), q_{reg}(t), s(t)} J

subject to:

.. math::
  \gamma_{reg}^{min} q_{ru}(t) + \gamma_{s}^{min} \bar{S} \leq s(t+1) 
  
  s(t+1) \leq (1 - \gamma_{s}^{max}) \bar{S} - \eta_c \gamma_{reg}^{max} q_{rd}(t)

  q_r(t) + q_d(t) + q_{reg}(t) \leq \bar{Q}

  S(N) = S_0

for all :math:`t \in \mathcal{T}`.

Arbitrage and regulation (MISO)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MISO has a *single product* frequency regulation market that provides payment for performance.

For a storage device that participates in both arbitrage and frequency regulation, the decision variables are :math:`q_d(t)`, :math:`q_r(t)`, :math:`q_{reg}(t)`, and :math:`s(t)`.

The recursion relation describing the state of charge :math:`s(t)` for time :math:`t > 0` is given by:

.. math::
  s(t+1) = \eta_s s(t) + \eta_c q_r(t) - q_d(t) + \eta_c \gamma_{rd}(t) q_{reg}(t) - \gamma_{ru}(t) q_{reg}(t)

with:

.. math::
  s(0) = S_0

The constraints on the decision variables are given by:

.. math::
  \gamma_{reg}^{min} q_{reg}(t) + \gamma_{s}^{min} \bar{S} \leq s(t+1) 
  
  s(t+1) \leq (1 - \gamma_{s}^{max}) \bar{S} - \eta_c \gamma_{reg}^{max} q_{reg}(t)

  q_r(t) + q_d(t) + q_{reg}(t) \leq \bar{Q}

  S(N) = S_0

for all :math:`t \in \mathcal{T}`. These equations are the same as in the PJM model.

The objective function for the model is:

.. math::
  J = \sum_\mathcal{T} \left [ \left(q_d(t) - q_r(t) \right) \lambda(t) + \left( 1 + \alpha \right) \Gamma \lambda_c(t) q_{reg}(t) \right ] e^{-Rt}

In this model, only one price for regulation services is used: RegMCP and is associated with the :math:`\lambda_c(t)` interface. Like in the PJM model, the credit is scaled by a performance score parameter. The "make whole" parameter, :math:`\alpha`, is a system-wide parameter used to adjust the regulation service credit such that the market payout is "balanced" in an ensemble and temporal sense.

The MISO arbitrage and regulation model can be summarized as:

.. math::
  \max_{q_d(t), q_r(t), q_{reg}(t), s(t)} J

subject to:

.. math::
  \gamma_{reg}^{min} q_{ru}(t) + \gamma_{s}^{min} \bar{S} \leq s(t+1) 
  
  s(t+1) \leq (1 - \gamma_{s}^{max}) \bar{S} - \eta_c \gamma_{reg}^{max} q_{rd}(t)

  q_r(t) + q_d(t) + q_{reg}(t) \leq \bar{Q}

  S(N) = S_0

for all :math:`t \in \mathcal{T}`.
