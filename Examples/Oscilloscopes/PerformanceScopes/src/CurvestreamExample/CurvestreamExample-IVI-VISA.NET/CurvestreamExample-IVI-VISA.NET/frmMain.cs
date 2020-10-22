/* TEKTRONIX SAMPLE SOURCE CODE LICENSE AGREEMENT
 * 
 * Source code written by Tektronix, Inc. or its affiliates (“Tektronix”) that
 * is designated as a “sample,” “example,” “sample code,” or any similar
 * designation will be considered “Sample Source Code.” Tektronix grants you a
 * license to download, reproduce, display, distribute, modify, and create
 * derivative works of Tektronix Sample Source Code, only for use in or with
 * Tektronix products. You may not remove or alter any copyright notices or
 * trademarks.
 * 
 * SAMPLE SOURCE CODE IS PROVIDED “AS-IS,” WITHOUT ANY EXPRESS OR IMPLIED
 * WARRANTIES OF ANY KIND, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT
 * OF INTELLECTUAL PROPERTY. IN NO EVENT SHALL TEKTRONIX, ITS AFFILIATES,
 * OFFICERS, EMPLOYEES, DIRECTORS, AGENTS, SUPPLIERS, OR OTHER THIRD PARTIES BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, PUNITIVE, SPECIAL, EXEMPLARY,
 * OR CONSEQUENTIAL DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS SAMPLE
 * SOURCE CODE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/* Title: Curvestream Usage Example - IVI VISA.NET
 * 
 * Date: 2020-10-22
 * 
 * Description: This example demonstrates how to use the curve stream feature
 * of the Series 5K, 7K and 70K scopes.  It first configures the waveform
 * output for 8-bit binary format, reads back the scaling parameters for the
 * curve data and then starts the curve stream query.  The program then
 * continues to read the curve stream data, writing each curve to a
 * timestamped .csv file until the user clicks End Test.
 * 
 * Compatibility: MSO/DPO5000/B, DPO7000/C, DPO70000/B/C/D/DX/SX, 
 * DSA70000/B/C/D, and MSO70000/C/DX Series Digital Oscilloscopes
 * 
 * Tested & Developed:
 * Microsoft Visual Studio 2017
 * Microsoft Windows 10
 * .NET Framework 4.6.2
 * NI-VISA 18.5
 * IVI VISA.NET Shared Components 5.8.0 (64-Bit)
 * MSO73304DX FW 10.9.1
 * Ethernet VXI-11 Interface
 * 
*/

using System;
using System.Text;
using System.Windows.Forms;
using System.IO;
using Ivi.Visa; // Reference -> Ivi.Visa Assembly


namespace CurvestreamExample
{
    public partial class frmMain : Form
    {
        private static int BUFFER_SIZE = 1024 * 1024 * 2;
        private IMessageBasedSession TekScope = null;
        private bool GatherCurves = false;

        private enum SaveToDisk
        {
            None,
            Text,
            Binary
        }

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

            cmbxSaveToDisk.SelectedIndex = 0;
        }

        private void cmdStartTest_Click(object sender, EventArgs e)
        {
            DateTime curveTime;
            float wfmPerSec = 0;
            System.Diagnostics.Stopwatch stopWatch = new System.Diagnostics.Stopwatch();
            string temp;
            SaveToDisk saveToDisk = (SaveToDisk)cmbxSaveToDisk.SelectedIndex;
            StreamWriter textFile = null;
            FileStream binaryFile = null;
            BinaryWriter binWriter = null;

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

            if (saveToDisk != SaveToDisk.None)
            { 
                // Check that the save directory is valid
                if (!Directory.Exists(SaveDirectory))
                {
                    MessageBox.Show("Invalid save directory.  Please enter a valid directory then try again.", "Error: Invalid Directory", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    cmdStartTest.Enabled = true;
                    return;
                }
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
                //TekScope = new MessageBasedSession(txtVisaResourceName.Text.Trim());
                TekScope = GlobalResourceManager.Open(txtVisaResourceName.Text.Trim()) as IMessageBasedSession;
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
            TekScope.FormattedIO.WriteLine("*CLS");
            TekScope.FormattedIO.WriteLine("*CLE");
            TekScope.FormattedIO.WriteLine("DATa:SOUrce CH1");
            TekScope.FormattedIO.WriteLine("DATa:ENCdg RIBinary");
            TekScope.FormattedIO.WriteLine("DATa:STARt 0");
            TekScope.FormattedIO.WriteLine("HORizontal:ACQLENGTH?");
            temp = TekScope.RawIO.ReadString().Trim();
            AcqLength = Int32.Parse(temp);
            TekScope.FormattedIO.WriteLine(String.Format("DATa:STOP {0}", AcqLength));
            TekScope.FormattedIO.WriteLine("WFMOutpre:ENCdg BINary");
            TekScope.FormattedIO.WriteLine("WFMOutpre:BYT_Nr 1");

            // Get the needed values from the scope to scale the data
            TekScope.FormattedIO.WriteLine("WFMOutpre:PT_Off?");
            temp = TekScope.RawIO.ReadString().Trim();
            pt_off = Int32.Parse(temp);
            TekScope.FormattedIO.WriteLine("WFMOutpre:XINcr?");
            temp = TekScope.RawIO.ReadString().Trim();
            xinc = Single.Parse(temp);
            TekScope.FormattedIO.WriteLine("WFMOutpre:XZEro?");
            temp = TekScope.RawIO.ReadString().Trim();
            xzero = Single.Parse(temp);
            TekScope.FormattedIO.WriteLine("WFMOutpre:YMUlt?");
            temp = TekScope.RawIO.ReadString().Trim();
            ymult = Single.Parse(temp);
            TekScope.FormattedIO.WriteLine("WFMOutpre:YOFf?");
            temp = TekScope.RawIO.ReadString().Trim().TrimEnd('0').TrimEnd('.');
            yoff = Single.Parse(temp);
            TekScope.FormattedIO.WriteLine("WFMOutpre:YZEro?");
            temp = TekScope.RawIO.ReadString().Trim();
            yzero = Single.Parse(temp);

            // Turn on curve streaming
            TekScope.FormattedIO.WriteLine("CURVEStream?");
            stopWatch.Reset();
            stopWatch.Start();

            // While still collecting curves.  Ends when the user clicks End Test
            while (GatherCurves) 
            {
                int NumBytesCharCount = 0;
                string BlockHeader = "";

                TekScope.TimeoutMilliseconds = 200;

                // Loop until the block header is found
                while (BlockHeader.Length == 0)
                {
                    try
                    {
                        // Read the length of the string that contains the length of the data
                        // Note: If this times out it just means that no curve has been sent out yet so need to wait again
                        BlockHeader = TekScope.RawIO.ReadString(2); 

                        if (BlockHeader == ";\n") // Then it's the terminator from the previous curve so throw it out and try again.
                            BlockHeader = "";
                    }
                    catch (IOTimeoutException)
                    {

                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show(ex.Message, "Error Occured", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        break;
                    }
                   
                    wfmPerSec = (float)CurveCount / ((float)stopWatch.ElapsedMilliseconds / (float)1000);
                    lblWfmPerSec.Text = wfmPerSec.ToString("f");
                    Application.DoEvents();
                    if (!GatherCurves) break;
                }
                if (!GatherCurves) break;

                // Block header has been found.  Prepare to receive waveform data
                if (saveToDisk != SaveToDisk.None)
                {
                    // Create a file with the current date and time as the name
                    curveTime = DateTime.Now;
                    string FileName = String.Format("{0}{1}-{2:D2}-{3:D2}_{4:D2}{5:D2}{6:D2}.{7:D3}.{8}",
                        txtSaveDirectory.Text,
                        curveTime.Year,
                        curveTime.Month,
                        curveTime.Day,
                        curveTime.Hour,
                        curveTime.Minute,
                        curveTime.Second,
                        curveTime.Millisecond,
                        saveToDisk == SaveToDisk.Text ? "csv" : "dat");

                    if (saveToDisk == SaveToDisk.Text)
                    {
                        textFile = new StreamWriter(FileName, false, Encoding.ASCII, BUFFER_SIZE * 10);
                    }
                    else // binary
                    {
                        binaryFile = new FileStream(FileName, FileMode.Create, FileAccess.Write, FileShare.None, BUFFER_SIZE * 8, FileOptions.SequentialScan);
                        binWriter = new BinaryWriter(binaryFile);
                    }
                }

                // Calculate the xvalue for the first point in the record
                xvalue = (((float)(-pt_off)) * xinc) + xzero;

                // Get the number of bytes that make up the data length string
                NumBytesCharCount = Int32.Parse(BlockHeader.TrimStart('#'), System.Globalization.NumberStyles.HexNumber);

                // Read the data length string
                temp = TekScope.RawIO.ReadString(NumBytesCharCount);
                DataLength = int.Parse(temp);
                BytesRemaining = DataLength;

                // Read the back the data, process it and save it to the file
                TekScope.TimeoutMilliseconds = 5000;
                while (BytesRemaining > 0)
                {
                    // Read bytes from scope
                    if (BytesRemaining >= BUFFER_SIZE)
                    {
                        //DataBuffer = TekScope.ReadByteArray(BUFFER_SIZE);
                        DataBuffer = TekScope.RawIO.Read(BUFFER_SIZE);
                        BytesRemaining -= BUFFER_SIZE;
                    }
                    else
                    {
                        DataBuffer = TekScope.RawIO.Read(BytesRemaining);
                        BytesRemaining = 0;
                    }

                    // Convert byte values to floating point values then write them to the file
                    foreach (byte DataPoint in DataBuffer)
                    {
                        yvalue = ((Convert.ToSingle((sbyte)DataPoint) - yoff) * ymult) + yzero;

                        switch (saveToDisk)
                        {
                            case SaveToDisk.Binary:
                                // Store the data in binary file as 32-bit floating point XY pairs
                                binWriter.Write(xvalue);
                                binWriter.Write(yvalue);
                                break;
                            case SaveToDisk.Text:
                                textFile.WriteLine(xvalue.ToString() + "," + yvalue.ToString());
                                // Note: Converting to .CSV is very time consuming operation.
                                // Saving in a binary format is much faster and highly recommended for waveforms >= 1 Million points.
                                break;
                        }
                        xvalue += xinc;
                    }
                }

                if (saveToDisk == SaveToDisk.Binary)
                {
                    binWriter.Close();
                    binWriter.Dispose();
                    binaryFile.Dispose();
                }
                else if (saveToDisk == SaveToDisk.Text)
                {
                    textFile.Close();
                    textFile.Dispose();
                }
                
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
