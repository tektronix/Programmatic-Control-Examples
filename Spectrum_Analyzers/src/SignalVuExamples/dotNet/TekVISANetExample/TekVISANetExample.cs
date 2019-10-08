// TekVISASocketExample : 11/9/2016 (Updated 12/15/2016)
// 
// Code sample for communicating in C# to an RSA instrument using TekVISANet.dll
// Sends PI commands to preset, sets CF to 1GHz, Span to 1MHz, and takes a peak reading
// The TekVISA socket server is not required for this example.

using System;
using TekVISANet;

namespace TekVISANetExample
{
    internal static class TekVISANetExample
    {
        private static void Message(string s)
        {
            Console.WriteLine("[" + DateTime.Now + "] " + s);
        }

        private static void Main(string[] args)
        {
            //const string rsaAddress = "127.0.0.1";
			const string rsaAddress = "GPIB8::1::INSTR";
            var rsa = new VISA();
            try
            {
				rsa.Open(rsaAddress);
                //rsa.Open(string.Format("TCPIP::{0}::INSTR", rsaAddress));
                if (rsa.Status != TekVISADefs.Status.SUCCESS)
                {
                    Message(string.Format("Unable to connect to RSA at address {0}", rsaAddress));
                    return;
                }

                // Confirm we are connected to the RSA.
                rsa.Write("*RST");
                string retString;
                rsa.Query("*IDN?", out retString);
                Message("Connected to: " + rsaAddress);
                Message("*IDN? returned " + retString);

                // Preset the system, set CF to 1 GHz, 1 MHz span, and turn off continous acquisitions
                rsa.Write(":SYSTEM:PRESET");
                int retVal;
                rsa.Query("*OPC?", out retVal);
                rsa.Write("*CLS");
                rsa.Write("INIT:CONT OFF");
                rsa.Write(":SENSE:SPEC:FREQ:CENTER 1e9");
                rsa.Write(":SENSE:SPEC:FREQ:SPAN 1e6");

                // Add a marker
                rsa.Write("CALCulate:MARKer:ADD");

                // Take one acquisition
                rsa.Write("INIT");
                rsa.Query("*OPC?", out retVal);

                // Use marker to find max peak
                rsa.Write("CALC:SPEC:MARKer0:MAX");
                double peakLevel;
                rsa.Query("CALC:SPEC:MARK0:Y?", out peakLevel);
                Message(string.Format("Peak Amplitude is {0:0.00} dBm", peakLevel));
            }
            finally
            {
                // Be a good .NET citizen and explicitly close resources.
                rsa.Clear();
                rsa.Close();
            }

            Console.WriteLine("Hit enter to close...");
            var wait = Console.ReadLine();

        }
    }
}

