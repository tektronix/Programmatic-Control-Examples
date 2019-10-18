// TekVISASocketExample : 11/9/2016 (Updated 12/15/2016)
// 
// Code sample for communicating in C# to an RSA instrument through TekVISA socket server on port 4000
// Sends PI commands to preset, sets CF to 1GHz, Span to 1MHz, and takes a peak reading
// Be sure to start to TekVISA socket server in the TekVISA LAN Server Control (can also set it to auto start).

using System;
using System.Net.Sockets;
using System.IO;

namespace TekVISASocketExample
{
    internal static class Program
    {
        private static void Message(string s)
        {
            Console.WriteLine("[" + DateTime.Now + "] " + s);
        }

        private static void Main(string[] args)
        {
            const string rsaIpAddress = "127.0.0.1";
            StreamReader rsaReader;
            StreamWriter rsaWriter;

            try
            {
                var rsaClient = new TcpClient(rsaIpAddress, 4000);
                var rsaStream = rsaClient.GetStream();
                rsaReader = new StreamReader(rsaStream);
                rsaWriter = new StreamWriter(rsaStream) { AutoFlush = true };
            }
            catch (Exception e)
            {
                Message("Unable to connect to RSA at ipaddr " + rsaIpAddress + "\n" + e.Message);
                return;
            }

            // Confirm we are connected to the RSA.
            rsaWriter.WriteLine("*IDN?");
            var rsaInfo = rsaReader.ReadLine();
            Message("Connected to: " + rsaIpAddress);
            Message("*IDN? returned " + rsaInfo);

            // Preset the system, set CF to 1 GHz, 1 MHz span, and turn off continous acquisitions
            rsaWriter.WriteLine(":SYSTEM:PRESET");
            rsaWriter.WriteLine("*OPC?");
            rsaReader.ReadLine();
            rsaWriter.WriteLine("*CLS");
            rsaWriter.WriteLine("INIT:CONT OFF");
            rsaWriter.WriteLine(":SENSE:SPEC:FREQ:CENTER 1e9");
            rsaWriter.WriteLine(":SENSE:SPEC:FREQ:SPAN 1e6");

            // Add a marker
            rsaWriter.WriteLine("CALCulate:MARKer:ADD");

            // Take one acquisition
            rsaWriter.WriteLine("INIT");
            rsaWriter.WriteLine("*OPC?");
            rsaReader.ReadLine();

            // Use marker to find max peak
            rsaWriter.WriteLine("CALC:SPEC:MARKer0:MAX");
            rsaWriter.WriteLine("CALC:SPEC:MARK0:Y?");
            var peakLevel = Convert.ToDouble(rsaReader.ReadLine());
            Message(string.Format("Peak Amplitude is {0:0.00} dBm", peakLevel));

            Console.WriteLine("Hit enter to close...");
            var wait = Console.ReadLine();

            // Be a good .NET citizen and explicitly close resources.
            rsaReader.Close();
            rsaWriter.Close();

        }
    }
}
