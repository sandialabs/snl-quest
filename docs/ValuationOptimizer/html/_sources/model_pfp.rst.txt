.. _sec_pfp:

Pay-for-performance models
==========================

Regulation up (RegUp) and down (RegDown) are ancillary services designed to maintain frequency stability and are sometimes combined into a single regulation product. In order to maintain tight tolerances on the frequency, generation must be constantly dithered so that load and generation are balanced. Depending on the market, a balancing authority or vertically integrated utility will control generation on a second-by-second basis to track the load. The balancing authority must reserve enough regulation capacity to meet expected variations in load.

RegUp is the ability to provide additional generation on command while RegDown is the ability to reduce generation or store power on demand. Until recently, the practice was to reimburse regulation services providers based mainly on capacity reserved along with compensation for any electricity that is purchased or sold. This approach did not compensate fast-responding systems for more accurately following commanded regulation signals and the corresponding increased benefit compared to slower resources. FERC order 755 and FERC order 784 provide pay-for-performance requirements and direct utilities and independent system operators to consider speed and accuracy when purchasing frequency regulation [FERC1]_, [FERC2]_. Independent System Operators (ISOs) have differing implementations of pay-for-performance.

---
PJM
---

PJM is a regional transmission organization in the northeastern United States that serves 13 states and the District of Columbia [PJM1]_. PJM’s implementation employs a two part payment based on the Regulation Market Capability Clearing Price (RMCCP) and the Regulation Market Performance Clearing Price (RMPCP), compensating for both capability offered as well as the performance provided [PJM2]_. These payments are weighted by a performance score that may be calculated hourly based on a delay score, a correlation score, and a precision score [PJM3]_.

The capability credit is a function of the Regulation Market Capability Clearing Price (RMCCP) [PJM2]_:

.. math::
    \text{RMCCP credit} = REG_t \times \eta_t \times RMCCP_t

where :math:`REG_t` is the hourly integrated regulation signal, :math:`\eta_t` is the actual performance score, and :math:`RMCCP_t` is the RMCCP, all at time :math:`t`. For fast responding resources, the performance credit compensates for how much the resource changes to track the regulation signal [PJM2]_:

.. math::
    \text{RMPCP credit} = REG_t \times \eta_t \times \beta_t^M \times RMPCP_t

where :math:`\beta_t^M` is the mileage ratio at time :math:`t`.

PJM offers two different regulation signals: :math:`RegA` and :math:`RegD`. :math:`RegA` is a low pass filtered area control error (ACE) signal designed for traditional regulating resources. :math:`RegD` is a high pass filtered ACE signal for faster responding resources like energy storage. For :math:`RegD` systems, the PJM mileage ratio, :math:`\beta_t^M`, is defined as:

.. math::
    \beta_t^M = \frac{RegD \text{ Mileage}}{RegA \text{ Mileage}}

Mileage is simply defined as the movement requested by the regulation control signal. For example, the :math:`RegD` mileage is defined as:

.. math::
    RegD \text{ Mileage} = \sum_{i=1}^N \left| RegD_i - RegD_{i-1} \right|

over the one hour time period. The PJM mileage ratio increases the compensation for faster responding resources. The increased mileage results from following a signal with higher frequency content, e.g., :math:`RegD`. The total compensation for a plant providing regulation services is the sum of the RMCCP and RMPCP credits.

The model of the energy storage device follows similarly from the generic :ref:`arbreg_model_desc`. A device participating solely in arbitrage in the PJM market will have an identical optimization formulation as the pay-for-performance aspects are ignored.

For a device participating in both arbitrage and regulation in the PJM market, the formulation changes slightly. Bids into the regulation market are combined into the non-negative :math:`q_t^{reg}` decision variable rather than being separated into :math:`q_t^{RU}` and :math:`q_t^{RD}` variables. In regulation markets, there is no guarantee that the capacity reserved will actually be deployed but for this formulation it is assumed that the assigned quantity is equal to the bid quantity, e.g., :math:`q_t^{reg} = REG_t`.

.. figure:: _static/regulation_signal_example_legend.png
   :width: 325px
   :align: center
   :figclass: align-center

.. _fig_regD_signal_PJM:

.. figure:: _static/regulation_signal_example.png
   :width: 750px
   :align: center
   :figclass: align-center

   Example PJM regulation signal from June 1, 2014.

In order to quantify the change in state of charge from participation in the regulation market, it is useful to define the regulation up efficiency :math:`\gamma_t^{RU}` as the fraction of the regulation up reserve capacity that is actually employed at time :math:`t`. Similarly, the regulation down efficiency :math:`\gamma_t^{RD}` is the fraction of the regulation down reserve capacity that is actually employed at time :math:`t`. In the actual operation of a storage system, :math:`\gamma_t^{RU}` and :math:`\gamma_t^{RD}` will vary over each time interval. To formulate the problem as a linear program, a known value must be employed. Fortunately, PJM provides historical regulation signals so it is possible to calculate these efficiencies at each time step (c.f. :ref:`fig_regD_signal_PJM` [PJM4]_). The state of charge is thus given by:

.. math::
    S_t = \gamma_s S_{t-1} + \gamma_c q_t^R - q_t^D + q_t^{reg} \left( \gamma_c \gamma_t^{RD} - \gamma_t^{ru} \right)

It is complemented by the following constraints:

.. math::
   S_{min} \leq S_t \leq S_{max}, \mbox{for all }t

   0 \leq q_t^R + q_t^{reg} \leq \bar{q}^R, \mbox{for all }t

   0 \leq q_t^D + q_t^{reg} \leq \bar{q}^D, \mbox{for all }t

The quantity allocated to regulation, :math:`q_t^{reg}`, reduces the maximum potential quantities allocated to arbitrage subject to the charge/discharge constraints of the device.

Given these constraints and the objective of maximizing revenue, the problem is naturally formulated as a linear program. The objective function using the pay-for-performance model is expressed as:

.. math::
    J = \sum_{t=1}^T \left[ (P_t-C_d) q_t^D - (P_t+C_r) q_t^R + q_t^{reg} \eta_t \left( \beta_t^M RMPCP_t + RMCCP_t \right) \right] e^{-rt}

The financial quantities of interest are:

================ ===========
Parameter        Description
================ ===========
:math:`P_t`      Price of electricity (LMP) at time :math:`t`
:math:`C_d`      Cost of discharging at time :math:`t`
:math:`C_r`      Cost of recharging at time :math:`t`
:math:`RMPCP_t`  Regulation Market Performance Clearing Price at time :math:`t`
:math:`RMCCP_t`  Regulation Market Capacity Clearing Price at time :math:`t`
:math:`r`        Interest rate for one period
================ ===========

Other regulation-related parameters include:

================= ===========
Parameter         Description
================= ===========
:math:`\eta_t`    Performance score at time :math:`t`
:math:`\beta_t^M` Mileage ratio at time :math:`t`
================= ===========

The decision variables are:

================= ===========
Decision variable Description
================= ===========
:math:`q_t^D`     quantity of energy sold (discharged) at time :math:`t` (MWh)
:math:`q_t^R`     quantity of energy purchased (charged) at time :math:`t` (MWh)
:math:`q_t^{reg}` quantity of energy offered into the regulation market at time :math:`t` (MWh)
================= ===========

The pay-for-performance model can be summarized as:

.. math::
    \max_{q_t^D, q_t^R, q_t^{reg}} \sum_{t=1}^T \left[ (P_t-C_d) q_t^D - (P_t+C_r) q_t^R + q_t^{reg} \eta_t \left( \beta_t^M RMPCP_t + RMCCP_t \right) \right] e^{-rt}

subject to:

.. math::
    S_{min} \leq S_t \leq S_{max}, \mbox{for all }t

    0 \leq q_t^R + q_t^{reg} \leq \bar{q}^R, \mbox{for all }t

    0 \leq q_t^D + q_t^{reg} \leq \bar{q}^D, \mbox{for all }t
