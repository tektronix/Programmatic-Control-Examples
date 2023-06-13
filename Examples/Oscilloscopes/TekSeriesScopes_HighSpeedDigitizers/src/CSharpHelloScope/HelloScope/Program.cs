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
            string visaRsrcAddr = "TCPIP::192.168.1.2::inst0::INSTR";
            var scope = GlobalResourceManager.Open(visaRsrcAddr) as IMessageBasedSession;
            using (scope)
            {
                scope.FormattedIO.WriteLine("*IDN?");
                Console.WriteLine(scope.FormattedIO.ReadLine());

                Console.Write("Resetting instrument...");
                scope.FormattedIO.WriteLine("*RST");
                scope.FormattedIO.WriteLine("*OPC?");
                scope.RawIO.ReadString();
                Console.WriteLine("Done!");

                Console.Write("Autoset instrument...");
                scope.FormattedIO.WriteLine("AUTOSET EXECUTE");
                scope.FormattedIO.WriteLine("*OPC?");
                scope.RawIO.ReadString();
                Console.WriteLine("Done!");

                scope.FormattedIO.WriteLine("MEASU:ADDMEAS AMPLITUDE");
                scope.FormattedIO.WriteLine("ACQ:STATE STOP");
                scope.FormattedIO.WriteLine("*OPC?");
                scope.RawIO.ReadString();

                Console.Write("Performing Single Sequence...");
                scope.FormattedIO.WriteLine("ACQ:STOPAFTER SEQUENCE");
                scope.FormattedIO.WriteLine("ACQ:STATE RUN");
                scope.FormattedIO.WriteLine("*OPC?");
                scope.RawIO.ReadString();
                Console.WriteLine("Done!\r\n");

                scope.FormattedIO.WriteLine("MEASU:MEAS1:RESULTS:CURRENTACQ:MEAN?");
                float ampl = float.Parse(scope.FormattedIO.ReadLine());

                Console.WriteLine($"Signal Amplitude: {ampl} Volts\r\n");

                Console.WriteLine("Press the Enter key to continue.");
                Console.ReadLine();
            }
        }
    }
}
