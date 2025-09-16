# Source Measure Unit (SMU) Module Examples

The examples in this directory work with the [MP5103 Mainframe and Supported SMU Modules](https://www.tek.com/en/products/mp5000-series-modular-precision-test-system).

*Note: before running any example - verify slot and channel used.*

## Directory

### **[2 Channels In Parallel](./2_Channel_Parallel/)**
Combines channel sourcing in parallel to increase current capabilities.

### **[2 Channels in Series](./2_Channel_Series/)**
Combines channel sourcing in series to increase voltage capabilities.

### **[BJT Gummel Characterization](./BJT_Gummel/)**
Two channels are used to perform voltage sweeps for a Gummel characterization of a BJT. Measurements are recorded throughout the test.

### **[BJT Vce-Ic Characterization](./BJT_Vce-Ic/)**
Two channels are used to perform a voltage and current sweep for a Vce-Ic characterization of a BJT. Measurements are recorded

### **[DC/Pulse VCSEL LIV Characterization](./DC_Pulse_LIV_VCSEL_Char/)**
Two channels are used to perform a voltage and current sweep for an LIV characterization of a VCSEL. Measurements are recorded throughout the test.

### **[LED Characterization Config List Example](./LED_ConfigList_Example/)**
Create a large configuration list, iterate through the list and take measurements when the settings are applied.

### **[DC Linear Current Sweep](./Linear_Current_Sweep/)**
Configures and executes a linear current sweep while measuring voltage.

### **[DC Linear Voltage Sweep](./Linear_Voltage_Sweep/)**
Configures and executes a linear voltage sweep while measuring current.

### **[MOSFET Drain Family of Curves](./MOSFET_Drain_Family_Curves/)**
Two channels are used to perform voltage sweeps for a family of curves characterization of a MOSFET. Measurements are recorded throughout the test.

### **[MOSFET Transfer Curve](./MOSFET_Transfer_Curve/)**
Two channels are used to perform a voltage sweep for a transfer curve or Vg-Id. Measurements are recorded throughout the test.

### **[Current Pulse Waveform Capture](./Pulse_Current_Waveform_Capture/)**
Generate a pulsed current sweep while taking continuous measurements.

### **[Pulsed Linear Current Sweep](./Pulse_Linear_Current_Sweep/)**
Configures and executes a pulsed current sweep while measuring at the peaks of the pulse.

### **[Pulsed Linear Voltage Sweep](./Pulse_Linear_Voltage_Sweep/)**
Configures and executes a pulsed voltage sweep while measuring at the peaks of the pulse.

### **[Voltage Pulse Waveform Capture](./Pulse_Voltage_Waveform_Capture/)**
Generate a pulsed voltage sweep while taking continuous measurements.

### **[Sine Wave Generation and Waveform Capture](./Sine_Waveform_Capture/)**
Generates a sinewave using a list sweep and a trigger model.
