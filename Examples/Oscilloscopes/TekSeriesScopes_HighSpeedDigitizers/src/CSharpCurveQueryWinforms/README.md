<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://theme.tekcloud.com/prod/github/tek-logo-round-dark-mode.png" width="100px">
  <source media="(prefers-color-scheme: light)" srcset="https://theme.tekcloud.com/prod/github/tek-logo-round-light-mode.png" width="100px">
  <img alt="Tek Logo" src="https://theme.tekcloud.com/prod/github/tek-logo-round-light-mode.png" width="100px">
</picture>

# Curve Query (Fetch Waveform) Windows Forms C# Example

This example demonstrates how to use C# and Windows Forms to:
* Connect to a scope
* Query the horizontal and vertical scaling factors to scale the waveform data
* Fetch the raw waveform data from the oscilloscope
* Scale the data to create a series of XY data pairs
* Plot the data on screen


## About

**Title:** Curve Query (Fetch Waveform) Windows Forms C# Example

**Author:** David Wyban

**Language:** [![C Sharp](https://img.shields.io/badge/-C%20Sharp-&?labelColor=3E434A&colorB=73BF44&logo=Microsoft)](https://github.com/dotnet/roslyn)

**Development Environment Used:**
* Visual Studio 2022
* Windows 10
* NI-VISA 2023 Q2

**Libraries Used:**
* .NET Framework 4.7.2
* Windows Forms (included in .NET Framework 4.7.2)
* IVI VISA.NET (Installed with NI-VISA)
* OxyPlot (Installed by NuGet Package Manager)

## Supported Instruments:

This example works with the following Tektronix Oscilloscopes.
* 2 Series MSO
* 4 Series MSO
* 5 Series (B) MSO
* 5 Series LP MSO
* 6 Series (B) MSO
* LPD64 Digitizer
* DPO MSO 5000(B) Series
* DPO 7000(C) Series
* DPO DSA MSO 70000 (B)(C)(D)(DX)(SX) Series

It may work with the following additional models of Tektronix Oscilloscopes, but it has not been verified.
* TBS1000(B)(C) Series
* TBS1000B-EDU Series
* TBS2000(B) Series
* DPO MSO 2000(B) Series
* DPO MSO 3000 Series (Firmware Version 2.4 or Later)
* MDO3000 Series
* DPO MSO 4000(B) Series
* MDO4000(B)(C) Series
* 3 Series MDO


## Maintainer

* [David Wyban](https://github.com/dwyban)


## License

Licensed under the [Tektronix Sample License](https://www.tek.com/sample-license).
