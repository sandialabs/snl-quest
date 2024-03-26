.. _storage_model_desc:

Energy storage model
====================

The key parameters that characterize an energy storage device are:

**power rating** (MW)
  The maximum power of the storage device (charge and discharge). This model uses a single power rating for both charging and discharging. Because of the hourly timestep in the discrete time model, this can be represented as an energy charge rating (MWh).

**energy capacity** (MWh)
  The amount of energy that can be stored.

**round trip efficiency** (%)
  Describes the losses encountered when input power is stored in the system.

**storage efficiency** (%/h)
  Describes the amount of charge retained per timestep

Additional parameters can be used to describe the device to account for reserves in order to meet obligations not simulated in this analysis:

**minimum reserve charge** (MWh)
  The amount of energy to reserve for discharging for, e.g., resilience applications. Usually specified as a percentage of energy capacity, effectively increasing the minimum state of charge available for market participation.

**maximum reserve charge** (MWh)
  The amount of energy to reserve for charging for, e.g., primary frequency response applications. Usually specified as a percentage of energy capacity, effectively decreasing the maximum state of charge available for market participation.

**minimum regulation reserve charge** (MWh)
  The amount of energy to reserve to ensure that enough energy is available to discharge to meet the actual regulation capacity called upon. Usually specified as a percentage of the regulation bid, effectively increasing the minimum state of charge available for market participation.

**maximum regulation reserve charge** (MWh)
  The amount of energy capacity to reserve to ensure that enough energy is available to charge to meet the actual regulation capacity called upon. Usually specified as a percentage of the regulation bid, effectively decreasing the maximum state of charge available for market participation.

For this optimization model, we are concerned with the quantity of energy charged or discharged during each time period for each potential activity (e.g. arbitrage or regulation). For arbitrage, the device will maintain a constant output power over each time period. For regulation, it is assumed that the device is capable of tracking the regulation signal. Since the ramping time is negligible compared to the time period (e.g. one hour), it is safe to ignore the effects of ramp rate. If the ramp rate is slow compared to the time period this approximation does not hold and a model that incorporates ramp rate must be employed.