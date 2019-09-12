/* Title: 2015-08-17
 *
 * Description: This example demonstrates how to use the curve stream feature
 * of the Series 5K, 7K and 70K scopes.  It first configures the waveform
 * output for 8-bit binary format, reads back the scaling parameters for the
 * curve data and then starts the curve stream query.  The program then
 * continues to read the curve stream data, writing each curve to a
 * timestamped .csv file until the user clicks End Test.
 *
 * Compatibility: MSO/DPO5000/B, DPO7000/C, DPO70000/B/C/D/DX,
 * DSA70000/B/C/D, and MSO70000/C/DX Series Digital Oscilloscopes
 *
 * Tested & Developed:
 * Microsoft Visual Studio 2010
 * Microsoft Windows 8.1
 * NI-VISA 15.0
 * MSO5204B FW 7.5.0
 * Ethernet VXI-11 Interface
 *
 * Tektronix provides the following example "AS IS" without any guarantees
 * or support.  This example is for instructional guidance only.
*/

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.IO;
using NationalInstruments.VisaNS;// Add Reference->NationalInstruments.VisaNS & NationalInstruments.common by installing NI-VISA .NET4 files from its Development Support
// Change Project Example Properties Applicaiton Target fromwork to ".Net Framework 4"

namespace Curve_Streaming_Example
{
    public partial class frmMain : Form
    {
        private static int BUFFER_SIZE = 1024 * 1024 * 2;
        private MessageBasedSession TekScope = null;
        private bool GatherCurves = false;

        public frmMain()
        {
            InitializeComponent();
        }

        private void frmMain_Load(object sender, EventArgs e)
        {
            if (TekScope != null)
            {
                TekScope.Dispose();
                TekScope = null;
            }
        }

        private void cmdStartTest_Click(object sender, EventArgs e)
        {
            System.DateTime CurveTime;
            float wfmPerSec = 0;
            System.Diagnostics.Stopwatch stopWatch = new System.Diagnostics.Stopwatch();
            string temp;

            string SaveDirectory = txtSaveDirectory.Text;
            byte[] DataBuffer;
            int AcqLength = 0;
            int CurveCount = 0;
            int DataLength;
            int BytesRemaining;

            // Curve data conversion parameters
            int pt_off;
            float xinc;
            float xzero;
            float ymult;
            float yoff;
            float yzero;

            float xvalue;
            float yvalue;

            cmdStartTest.Enabled = false;
            lblCurveCount.Text = CurveCount.ToString();
            lblWfmPerSec.Text = wfmPerSec.ToString("f");
            Application.DoEvents();  // Allow the front panel to redraw

            // Check that the save directory is valid
            if (!System.IO.Directory.Exists(SaveDirectory))
            {
                MessageBox.Show("Invalid save directory.  Please enter a valid directory then try again.", "Error: Invalid Directory", MessageBoxButtons.OK, MessageBoxIcon.Error);
                cmdStartTest.Enabled = true;
                return;
            }

            // Prompt the user to prep the scope
            if (MessageBox.Show("Please setup the scope then press OK to start Curve Streaming.  Once Curve Streaming has started you will not be able to control the scope until Curve Streaming is ended.",
                "Setup Scope",
                MessageBoxButtons.OKCancel,
                MessageBoxIcon.Information) == DialogResult.Cancel)
            {
                cmdStartTest.Enabled = true;
                return;
            }

            // Open a connection to the instrument
            try
            {
                TekScope = new MessageBasedSession(txtVisaResourceName.Text.Trim());
                TekScope.Clear();
            }
            catch (Exception ex)
            {
                // Show and error message then exit if the connection fails
                MessageBox.Show(ex.Message, "Error Opening Connection to Instrument", MessageBoxButtons.OK, MessageBoxIcon.Error);
                TekScope = null;
                cmdStartTest.Enabled = true;
                return;
            }

            GatherCurves = true;
            cmdEndTest.Enabled = true;

            // Setup the waveform transfer
            TekScope.Write("*CLS");
            TekScope.Write("*CLE");
            TekScope.Write("DATa:SOUrce CH1");
            TekScope.Write("DATa:ENCdg RIBinary");
            TekScope.Write("DATa:STARt 0");
            TekScope.Write("HORizontal:ACQLENGTH?");
            temp = TekScope.ReadString().Trim();
            AcqLength = Int32.Parse(temp);
            TekScope.Write(String.Format("DATa:STOP {0}", AcqLength));
            TekScope.Write("WFMOutpre:ENCdg BINary");
            TekScope.Write("WFMOutpre:BYT_Nr 1");

            // Get the needed values from the scope to scale the data
            TekScope.Write("WFMOutpre:PT_Off?");
            temp = TekScope.ReadString().Trim();
            pt_off = Int32.Parse(temp);
            TekScope.Write("WFMOutpre:XINcr?");
            temp = TekScope.ReadString().Trim();
            xinc = Single.Parse(temp);
            TekScope.Write("WFMOutpre:XZEro?");
            temp = TekScope.ReadString().Trim();
            xzero = Single.Parse(temp);
            TekScope.Write("WFMOutpre:YMUlt?");
            temp = TekScope.ReadString().Trim();
            ymult = Single.Parse(temp);
            TekScope.Write("WFMOutpre:YOFf?");
            temp = TekScope.ReadString().Trim().TrimEnd('0').TrimEnd('.');
            yoff = Single.Parse(temp);
            TekScope.Write("WFMOutpre:YZEro?");
            temp = TekScope.ReadString().Trim();
            yzero = Single.Parse(temp);

            // Turn on curve streaming
            TekScope.Write("CURVEStream?");
            stopWatch.Reset();
            stopWatch.Start();

            // While still collecting curves.  Ends when the user clicks End Test
            while (GatherCurves) 
            {
                int NumBytesCharCount = 0;
                string BlockHeader = "";

                TekScope.Timeout = 200;

                // Loop until the block header is found
                while (BlockHeader.Length == 0)
                {
                    try
                    {
                        // Read the length of the string that contains the length of the data
                        // Note: If this times out it just means that no curve has been sent out yet so need to wait again
                        BlockHeader = TekScope.ReadString(2); 

                        if (BlockHeader == ";\n") // Then it's the terminator from the previous curve so throw it out and try again.
                            BlockHeader = "";
                    }
                    catch (VisaException ex)
                    {
                        if (ex.ErrorCode != VisaStatusCode.ErrorTimeout) // Then still waiting on another curve to come in
                        {
                            MessageBox.Show(ex.Message, "Error Occured", MessageBoxButtons.OK, MessageBoxIcon.Error);
                            break;
                        }
                    }

                    wfmPerSec = (float)CurveCount / ((float)stopWatch.ElapsedMilliseconds / (float)1000);
                    lblWfmPerSec.Text = wfmPerSec.ToString("f");
                    Application.DoEvents();
                    if (!GatherCurves) break;
                }
                if (!GatherCurves) break;

                // Create a file with the current date and time as the name
                CurveTime = System.DateTime.Now;
                string FileName = String.Format("{0}{1}-{2:D2}-{3:D2}_{4:D2}{5:D2}{6:D2}.{7:D3}.csv",
                    txtSaveDirectory.Text,
                    CurveTime.Year,
                    CurveTime.Month,
                    CurveTime.Day,
                    CurveTime.Hour,
                    CurveTime.Minute,
                    CurveTime.Second,
                    CurveTime.Millisecond);
                StreamWriter SaveFile = new StreamWriter(FileName, false, Encoding.ASCII, BUFFER_SIZE * 10);

                // Calculate the xvalue for the first point in the record
                xvalue = (float)(-pt_off * (xinc + xzero));

                // Get the number of bytes that make up the data length string
                NumBytesCharCount = Int32.Parse(BlockHeader.TrimStart('#'), System.Globalization.NumberStyles.HexNumber);

                // Read the data length string
                temp = TekScope.ReadString(NumBytesCharCount);
                DataLength = int.Parse(temp);
                BytesRemaining = DataLength;

                // Read the back the data, process it and save it to the file
                TekScope.Timeout = 5000;
                while (BytesRemaining > 0)
                {
                    // Read bytes from scope
                    if (BytesRemaining >= BUFFER_SIZE)
                    {
                        DataBuffer = TekScope.ReadByteArray(BUFFER_SIZE);
                        BytesRemaining -= BUFFER_SIZE;
                    }
                    else
                    {
                        DataBuffer = TekScope.ReadByteArray(BytesRemaining);
                        BytesRemaining = 0;
                    }

                    // Convert byte values to floating point values then write to .csv file
                    foreach (byte DataPoint in DataBuffer)
                    {
                        yvalue = (float)((Convert.ToSingle((sbyte)DataPoint) - yoff) * (ymult + yzero));
                        SaveFile.WriteLine(xvalue.ToString() + "," + yvalue.ToString());
                        // Note: Converting to .CSV is very time consuming operation.
                        // Save in a binary format to maximize speed.  Highly recommended for waveforms >= 1 Million points.
                        xvalue += xinc;
                    }
                }

                SaveFile.Close();

                CurveCount++;
                wfmPerSec = (float)CurveCount / ((float)stopWatch.ElapsedMilliseconds / (float)1000);
                lblWfmPerSec.Text = wfmPerSec.ToString("f");
                lblCurveCount.Text = CurveCount.ToString();
                Application.DoEvents();
            }

            // Send Device Clear to stop the curve streaming
            TekScope.Clear();

            TekScope.Dispose();
            TekScope = null;
            cmdStartTest.Enabled = true;
            cmdEndTest.Enabled = false;
        }

        private void cmdEndTest_Click(object sender, EventArgs e)
        {
            GatherCurves = false;
        }
    }
}

