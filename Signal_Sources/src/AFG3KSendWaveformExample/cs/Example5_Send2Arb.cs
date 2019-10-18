using System;
using System.IO;
using System.Linq;
using System.Text;
using NationalInstruments.VisaNS;
using System.Windows.Forms;

namespace Example5_Send2Arb
{
    public partial class Form1 : Form
    {
        private MessageBasedSession mbSession;
        // Instrument VISA address
        string resourceString = "USB0::0x0699::0x0348::CU010018::INSTR";

        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            // example waveform: sine wave using 12 sample points, integers between 0 to
            // 16382 (range of AFG).  hex notation is easier to verify later
            // (note: max value of afg3000 is '3FFE' not '3FFF')

            int[] hexArray = { 0x2000, 0x2FFF, 0x3BB6, 0x3FFE, 0x3BB6, 0x2FFF, 0x2000, 0x1000, 0x0449, 0x0000, 0x0449, 0x1000 };
            string[] hexStr1 = new string[hexArray.Length];
            string[] hexStr2 = new string[hexArray.Length * 2];


            // pre-processing
            // encode variable 'wave' into binary waveform data for AFG.  This is
            // the same as AWG5000B but marker bits are ignored.  see AWG5000B series
            // programmer manual for bit definitions.
            for (int i = 0; i < hexArray.Length; i++)
            {
                hexStr1[i] = hexArray[i].ToString("X4");
                hexStr2[2 * i] = hexStr1[i].Substring(0, 2);
                hexStr2[(2 * i) + 1] = hexStr1[i].Substring(2, 2);
            }
            byte[] Str2Byt = hexStr2.Select(s => Convert.ToByte(s, 16)).ToArray();
            string EnCdStr = System.Text.Encoding.ASCII.GetString(Str2Byt);


            // build binary block header
            int bytes = Str2Byt.Length;
            string header = "#" + Convert.ToString(Convert.ToString(bytes).Length) + Convert.ToString(bytes);


            //Open connection to instrument
            mbSession = (MessageBasedSession)ResourceManager.GetLocalManager().Open(resourceString);
            mbSession.Write("*RST");
            mbSession.Write("*CLS");
            mbSession.Write("DATA:DEFine EMEMory, " + hexArray.Length.ToString());
            mbSession.Write("DATA EMEMory," + header + EnCdStr);
            mbSession.Write("SOURce1:FUNCtion EMEMory");
            mbSession.Write("OUTPut1 ON");


            //Close instrument connection
            mbSession.Dispose();
        }
    }
}

