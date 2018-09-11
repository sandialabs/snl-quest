.. _op_model_desc:

Optimization models
===================

Here we will describe the expressions that comprise the objective functions and constraints for each model implemented.

The following are the decision variables:

================== ================================================================================================ =====
Decision variables Description                                                                                      Units
================== ================================================================================================ =====
:math:`q_d(t)`     energy sold (discharged) at time :math:`t`                                                       MWh
:math:`q_r(t)`     energy purchased (charged) at time :math:`t`                                                     MWh
:math:`q_{reg}(t)` energy bid for regulation up/down at time :math:`t` in a one product frequency regulation market MWh
:math:`q_{ru}(t)`  energy bid for regulation up at time :math:`t` in a two product frequency regulation market      MWh
:math:`q_{rd}(t)`  energy bid for regulation down at time :math:`t` in a two product frequency regulation market    MWh
:math:`s(t)`       device state of charge at time :math:`t` (defined as decision variable for formulation)          MWh                                            
================== ================================================================================================ =====

The following are the energy storage device parameters:

========================== ====================================================== =====
Storage parameters         Description                                            Units
========================== ====================================================== =====
:math:`\bar{S}`            energy capacity                                        MWh
:math:`\bar{Q}`            energy charge/discharge rating                         MWh
:math:`S_0`                initial state of charge                                MWh
:math:`\gamma_s^{min}`     fraction of energy capacity to reserve for discharging                                                     
:math:`\gamma_s^{max}`     fraction of energy capacity to reserve for charging                                                        
:math:`\gamma_{reg}^{min}` fraction of regulation bid to reserve for discharging                                                      
:math:`\gamma_{reg}^{max}` fraction of regulation bid to reserve for charging
:math:`\eta_s`             self-discharge efficiency                              %/h
:math:`\eta_c`             round trip efficiency                                  %
========================== ====================================================== =====

The following are market-related parameters, typically derived from market data:

========================== ========================================================================================================== =====
Market parameters          Description
========================== ========================================================================================================== =====
:math:`\gamma_{ru}(t)`     fraction of regulation up bid actually deployed at time :math:`t`                                          
:math:`\gamma_{rd}(t)`     fraction of regulation down bid actually deployed at time :math:`t`                                        
:math:`\lambda(t)`         price of electricity at time :math:`t`                                                                     $/MWh
:math:`\lambda_c(t)`       frequency regulation capacity price at time :math:`t` in a one product frequency regulation market         $/MWh
:math:`\lambda_c^{ru}(t)`  frequency regulation up capacity price at time :math:`t` in a two product frequency regulation market      $/MWh
:math:`\lambda_c^{rd}(t)`  frequency regulation down capacity price at time :math:`t` in a two product frequency regulation market    $/MWh
:math:`\lambda_p(t)`       frequency regulation performance price at time :math:`t` in a one product frequency regulation market      $/MWh
:math:`\lambda_p^{ru}(t)`  frequency regulation up performance price at time :math:`t` in a two product frequency regulation market   $/MWh
:math:`\lambda_p^{rd}(t)`  frequency regulation down performance price at time :math:`t` in a two product frequency regulation market $/MWh
:math:`\beta(t)`           mileage ratio at time :math:`t`                                                                             
:math:`\alpha`             make whole parameter for adjusting regulation credit
:math:`R`                  interest/discount rate          
:math:`\Gamma`             performance score
========================== ========================================================================================================== =====

The time-indexed variables are defined for all hours :math:`t \in \mathcal{T}` where :math:`\mathcal{T} = [0, 1, ..., N-1]` where :math:`N` equals the number of hours in the time horizon, which is assumed to be one month. The state of charge :math:`s(t)` is defined for :math:`[0, 1, ..., N]` (one additional time step) to ensure that the final state of charge meets the constraints as expected.

Furthermore, the final state of charge is constrained to be equal to the initial state of charge, :math:`S_0`, which is equal to :math:`\gamma_s^{min} \bar{S}`, the minimum state of charge (reserved for discharging), unless otherwise specified.

Arbitrage only
^^^^^^^^^^^^^^

Arbitrage, in this context, generally refers to managing state of charge by buying and selling energy. A storage device engaging in arbitrage is trying to maximize profit from buying energy at low prices and selling energy at higher prices, subject to the constraints of the storage facility. Valuation with this particular revenue stream only has the same formulation among all market areas.

For a storage device that participates in arbitrage only, the decision variables are :math:`q_d(t)`, :math:`q_r(t)`, and :math:`s(t)`.

The recursion relation describing the state of charge :math:`s(t)` for time :math:`t > 0` is given by:

.. math::
   s(t+1) = \eta_s s(t) + \eta_c q_r(t) - q_d(t)

with:

.. math::
  s(0) = S_0

The constraints on the state of charge :math:`s(t)`, the quantity purchased :math:`q_r(t)`, and the quantity sold :math:`q_d(t)` at each time step :math:`t` are given by:

.. math::
  \gamma_s^{min} \bar{S} \leq s(t) 
  
  s(t) \leq (1 - \gamma_s^{max})\bar{S}

  q_r(t) + q_d(t) \leq \bar{Q}

  S(N) = S_0

for all :math:`t \in \mathcal{T}`. The first two sets of constraints limits the state of charge between its minimum and maximum values as specified at each time step. The next set of constraints limits the total energy charged over the time step (both charging and discharging) to the energy charge limit (derived from the power limit) at each time step. This constraint permits charging and discharging during the same time step but restricts the throughput based on the power rating.

In the energy storage valuation problem, the objective is to maximize the total revenue over the time horizon. We do not include costs associated with, e.g., charging or discharging. If data is available, it may be included in the objective function, changing the objective to profit maximization. Otherwise, the objective function for the arbitrage only model is:

.. math::
   J = \sum_\mathcal{T} \left [q_d(t) - q_r(t) \right ] \lambda(t) e^{-Rt}

Revenue is solely generated by buying and selling energy. The arbitrage only model can therefore be summarized as:

.. math::
  \max_{q_d(t), q_r(t), s(t)} J

subject to:

.. math::
  \gamma_s^{min} \bar{S} \leq S(t) \leq (1 - \gamma_s^{max})\bar{S}

  q_r(t) + q_d(t) \leq \bar{Q}

  S(N) = S_0

for all :math:`t \in \mathcal{T}`.

.. note:: In many areas, the net energy for regulation is settled at the real-time price. This provides an additional arbitrage opportunity between the day ahead price and the real-time price. These models are primarily concerned with arbitrage and regulation revenue from the day ahead market; therefore, the price :math:`\lambda(t)` typically represents the day ahead LMP. While this does not reflect the actual settlement process, it keeps the optimization from incorporating any arbitrage between the day ahead and the real-time market.

Arbitrage and regulation (ERCOT)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ERCOT has a frequency regulation market that does not explicitly provide credits based on frequency regulation performance, only for capacity offered. It offers different prices for regulation up and regulation down is thus considered a *two product frequency regulation* market.

For a storage device that participates in both arbitrage and frequency regulation, the decision variables are :math:`q_d(t)`, :math:`q_r(t)`, :math:`q_{ru}(t)`, :math:`q_{rd}(t)`, and :math:`s(t)`.

The recursion relation describing the state of charge :math:`s(t)` for time :math:`t > 0` is given by:

.. math::
  s(t+1) = \eta_s s(t) + \eta_c q_r(t) - q_d(t) + \eta_c \gamma_{rd}(t) q_{rd}(t) - \gamma_{ru}(t) q_{ru}(t)

with:

.. math::
  s(0) = S_0

The constraints on the decision variables are given by:

.. math::
  \gamma_{reg}^{min} q_{ru}(t) + \gamma_{s}^{min} \bar{S} \leq s(t+1) 
  
  s(t+1) \leq (1 - \gamma_{s}^{max}) \bar{S} - \eta_c \gamma_{reg}^{max} q_{rd}(t)

  q_r(t) + q_d(t) + q_{ru}(t) + q_{rd}(t) \leq \bar{Q}

  S(N) = S_0

for all :math:`t \in \mathcal{T}`. The first two sets of constraints limits the state of charge between its minimum and maximum values as specified at each time step. The :math:`\gamma_{reg}` factors are safety factors used to reserve energy capacity headroom and/or legroom to avoid penalties due to not meeting regulation obligations; they are defined as fractions of the capacity bid. The next set of constraints limits the total energy charged over the time step (both charging and discharging) to the energy charge limit (derived from the power limit) at each time step. This constraint permits charging and discharging during the same time step but restricts the throughput based on the power rating. Bids for regulation up/down are constrained together with arbitrage-related actions.

The objective function for the model is:

.. math::
  J = \sum_\mathcal{T} \left [ \left(q_d(t) - q_r(t) \right) \lambda(t) + \lambda_c^{ru}(t) q_{ru}(t) + \lambda_c^{rd}(t) q_{rd}(t) + \left( \gamma_{ru}(t) q_{ru}(t) - \gamma_{rd}(t) q_{rd}(t) \right) \lambda(t) \right ] e^{-Rt}

In addition to the arbitrage revenue stream, electricity prices are accounted for depending on the actual amount of the regulation bid that is called upon. Additionally, the revenue from regulation up/down bids are included. The ERCOT arbitrage and regulation model can therefore be summarized as:

.. math::
  \max_{q_d(t), q_r(t), q_{ru}(t), q_{rd}(t), s(t)} J

subject to:

.. math::
  \gamma_{reg}^{min} q_{ru}(t) + \gamma_{s}^{min} \bar{S} \leq s(t+1) 
  
  s(t+1) \leq (1 - \gamma_{s}^{max}) \bar{S} - \eta_c \gamma_{reg}^{max} q_{rd}(t)

  q_r(t) + q_d(t) + q_{ru}(t) + q_{rd}(t) \leq \bar{Q}

  S(N) = S_0

for all :math:`t \in \mathcal{T}`.

.. note:: The :math:`\gamma_{ru}` and :math:`\gamma_{rd}` terms are assumed to be fixed for all time in the absence of additional information. 

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
