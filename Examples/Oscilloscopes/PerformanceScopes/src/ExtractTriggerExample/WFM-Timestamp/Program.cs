using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

namespace WFM_Timestamp
{
    class Program
    {
        static void Main(string[] args)
        {
            string strCWD = Directory.GetCurrentDirectory();
            IEnumerable<string> files = Directory.EnumerateFiles(strCWD);

            List<string> wfmFiles = new List<string>();

            foreach (string file in files)
            {
                FileInfo fi = new FileInfo(file);
                if (fi.Extension == ".wfm" || fi.Extension == ".WFM")
                {
                    wfmFiles.Add(fi.Name);
                }
            }

            if (wfmFiles.Count == 0)
                Console.WriteLine("No .wfm files found in the current directory.");
            else
            {
                foreach (string wfmFile in wfmFiles)
                {
                    FileStream f = File.OpenRead(wfmFile);

                    byte[] hdr = new byte[838];
                    int bytesRead = 0;
                    bytesRead = f.Read(hdr, 0, 838);

                    if(bytesRead != 838)
                    {
                        Console.WriteLine(String.Format("File {0} is invalid.  Skipping File", wfmFile));
                    }

                    if (hdr[0] == 0xf && hdr[1] == 0xf && Encoding.ASCII.GetString(hdr, 2, 8) == ":WFM#003")
                    {
                        double fract = BitConverter.ToDouble(hdr, 796);
                        int tstamp = BitConverter.ToInt32(hdr, 804);

                        DateTime dt = new DateTime(1970, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc);
                        dt = dt.AddSeconds(Convert.ToDouble(tstamp));

                        Console.WriteLine(String.Format("{0}\t{1}\t{2}", wfmFile, dt.ToLocalTime(), fract));
                    }
                    else
                    {
                        Console.WriteLine(String.Format("File {0} is not ver 3 WFM file.  Skipping.", wfmFile));
                    }
                }
            }
            Console.Write("Press Enter to Close...");
            Console.ReadLine();
        }
    }
}
