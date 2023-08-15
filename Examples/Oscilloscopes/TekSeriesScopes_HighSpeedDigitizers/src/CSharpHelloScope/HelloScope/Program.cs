using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Ivi.Visa;

namespace HelloScope
{
    internal class Program
    {
        static void Main(string[] args)
        {
            // Edit this to match the VISA Resource Address of your instrument
            string visaRsrcAddr = "TCPIP::192.168.1.2::inst0::INSTR";
            
            // Open a connection to the instrument located at the visaRsrcAddr string
            // Cast the returned object as an IMessagedBasedSession. This is the interface of the
            // IVI VISA library used to send and receive commands and data.
            var scope = GlobalResourceManager.Open(visaRsrcAddr) as IMessageBasedSession;

            // using statement ensures that the connection will be closed even if an exception is thrown.
            using (scope)
            {
                // Query instrument ID and print response to console
                scope.FormattedIO.WriteLine("*IDN?");
                Console.WriteLine(scope.FormattedIO.ReadLine());

                // Reset the instrument to default state and wait for it to complete
                Console.Write("Resetting instrument...");
                scope.FormattedIO.WriteLine("*RST");
                scope.FormattedIO.WriteLine("*OPC?");
                scope.RawIO.ReadString();
                Console.WriteLine("Done!");

                // Perform an Autoset and wait for it to complete
                Console.Write("Autoset instrument...");
                scope.FormattedIO.WriteLine("AUTOSET EXECUTE");
                scope.FormattedIO.WriteLine("*OPC?");
                scope.RawIO.ReadString();
                Console.WriteLine("Done!");

                // Add an amplitude measurement and stop acquiring
                scope.FormattedIO.WriteLine("MEASU:ADDMEAS AMPLITUDE");
                scope.FormattedIO.WriteLine("ACQ:STATE STOP");
                scope.FormattedIO.WriteLine("*OPC?");
                scope.RawIO.ReadString();

                // Initiate a single acquisition and wait for it to complete
                Console.Write("Performing Single Sequence...");
                scope.FormattedIO.WriteLine("ACQ:STOPAFTER SEQUENCE");
                scope.FormattedIO.WriteLine("ACQ:STATE RUN");
                scope.FormattedIO.WriteLine("*OPC?");
                scope.RawIO.ReadString();
                Console.WriteLine("Done!\r\n");

                // Fetch the measurement result and print to console
                scope.FormattedIO.WriteLine("MEASU:MEAS1:RESULTS:CURRENTACQ:MEAN?");
                float ampl = float.Parse(scope.FormattedIO.ReadLine());
                Console.WriteLine($"Signal Amplitude: {ampl} Volts\r\n");

                Console.WriteLine("Press the Enter key to continue.");
                Console.ReadLine();
            }
        }
    }
}
