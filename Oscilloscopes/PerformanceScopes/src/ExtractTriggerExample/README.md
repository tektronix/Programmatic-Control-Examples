# Extract Trigger Timestamp from .wfm file
Original Attribution: Dave W - Tektronix Applications

OK, technically this isn't a Remote Programming example, but it's a useful example none the less.

The .wfm waveform files saved from Tektronix DPO/DSA/MSO 5K 7K 70K and 5 Series MSO oscilloscopes contains a time stamp that indicates the time that the scope was triggered. This example program shows how you can extract this time stamp from the file.

The example works by scanning the current working directory for .wfm files and then opening each file and extracting the time stamp and then printing the name of the file and the time stamp to the console in a tabular format. After you compile the example, place the executable in the same directory as the .wfm files you want to extract the time stamp from and then run it.

```
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
```
Resources
---------
Original Discussion: https://forum.tek.com/viewtopic.php?f=580&t=140463

