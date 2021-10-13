/*  * Source code written by Tektronix, Inc. or its affiliates (“Tektronix”) that
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
 
This code uses the Visa Wrapper, written by Tektronix to support the VISA32.dll
in the C# .NET environment.

This particular GUI program saves each each FastFrame frame as an individual csv.
It is designed to work on the 70000 series Windows 10 oscilloscopes.
Upon executing the program, it connects to the oscilloscope using the onboard TekVisa.  
You can then check which channels to save.

The program asssumes that the user has already captured FastFrame waveforms.

When you push "SAVE" The program use the save dialog box to allow you to chose where to save the 
files.  It will then save all of the frames individually.

 */
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Visa;
// Visa incorporates the visa wrapper.


namespace Save_Frames_Individually
{
    public partial class Save_Frames : Form
    {
        // Initiallize some of the variables that will be used throughout the program.
        private VisaWrapper instrument = null;
        private bool CH1 = false;
        private bool CH2 = false;
        private bool CH3 = false;
        private bool CH4 = false;
        public Save_Frames()
        {
            InitializeComponent();
        }

        private void Save_Frames_Load(object sender, EventArgs e)
        {
            try
            {
                /*This portion uses VISA to connect to the oscilloscope.  The TCPIP portion is used for remote debugging.
                 * normally it will connect to the GPIB8 address, which is the local oscilloscope address.
                */
                //instrument = VisaWrapper.OpenVisaSession("TCPIP::10.233.16.153::INSTR");
                instrument = VisaWrapper.OpenVisaSession("GPIB8::1::INSTR");
                instrument.Clear();// clear out the Visa buffer.
                // Inform the user that the program did connect to the oscilloscope.
                Visa_reply.Text = "Oscilloscope Connected";
            }
            catch (Exception ex)
            {
                // Show an error message if the connection fails. Also inform the customer that the
                // oscilloscope is not connected.
                MessageBox.Show("There was a connection error: " + ex.Message);
                Visa_reply.Text = "Oscilloscope did not connect";
                instrument = null;
                return;
            }
        }
        private void Save_Frames_Closing(object sender, CancelEventArgs e)
        {
            // When you close the program, close out the connections to clean it up.
            if (instrument != null) { instrument.Dispose(); }
        }

        private void Channel_Select_checkListBox_SelectedIndexChanged(object sender, EventArgs e)
        {
            /* This is where you can click the box to chose and unchose what channels to save.
             * Everytime you click in the box, the boolean check changes so that the save is corrrect.
               There are four check boxes for the 4 channels. */
            {
                if (Channel_Select_checkListBox.GetItemChecked(0) == true)
                { CH1 = true; }
            }
            {
                if (Channel_Select_checkListBox.GetItemChecked(0) == false)
                { CH1 = false; }
            }
            {
                if (Channel_Select_checkListBox.GetItemChecked(1) == true)
                { CH2 = true; }
            }
            {
                if (Channel_Select_checkListBox.GetItemChecked(1) == false)
                { CH2 = false; }
            }
            {
                if (Channel_Select_checkListBox.GetItemChecked(2) == true)
                { CH3 = true; }
            }
            {
                if (Channel_Select_checkListBox.GetItemChecked(2) == false)
                { CH3 = false; }
            }
            {
                if (Channel_Select_checkListBox.GetItemChecked(3) == true)
                { CH4 = true; }
            }
            {
                if (Channel_Select_checkListBox.GetItemChecked(3) == false)
                { CH4 = false; }
            }
        }

        private void Save_Button_Click(object sender, EventArgs e)
        {
            bool saved = false;
            
            /* If one or more of the channel boxes is checked, the program will save the checked channels, otherwise the program
               will ask the customer to pick a chennel to save.*/

            if (CH1 | CH2 | CH3 | CH4)
            {
                string AcqLength = instrument.Query("horizontal:acqlength?"); // Find the number of samples in one frame
                string strNumFrames = instrument.Query("horizontal:fastframe:count?"); //fidn out how many frames there are to save
                instrument.Write("save:waveform:fileformat SPREADSHEETCsv");// Set the oscilloscope to save as a csv
                // The next two lines are for initializing the save.
                instrument.Write("save:waveform:data:start 1");// Set the first sample to save on each frame as the first sample of the frame
                instrument.Write("save:waveform:data:stop " + AcqLength); // set the last sample to save per each frame as the last sample of the frame 
                int intNumFrames = Int32.Parse(strNumFrames); // change the number of frames to be an integer so that it can be in the loop counter below
                string CH1Av = instrument.Query("SELECT:CH1?"); // See if CH1 is on, if not it can't be saved and we need to account for it in case it is chosen.
                int intCH1AV = Int32.Parse(CH1Av); // change to an integer to make it easier to use as a condition
                string CH2Av = instrument.Query("SELECT:CH2?");//See if CH2 is on
                int intCH2AV = Int32.Parse(CH2Av);
                string CH3Av = instrument.Query("SELECT:CH3?"); //See if CH3 is on
                int intCH3AV = Int32.Parse(CH3Av);
                string CH4Av = instrument.Query("SELECT:CH4?"); //See if CH4 is on
                int intCH4AV = Int32.Parse(CH4Av);


                if (CH1 & intCH1AV == 0)
                    /* This section handles if someone choses a channel that is not on.  If they push "Save" the program will tell
                     * them to chose an active channel*/
                {
                    MessageBox.Show("CH1 is not active. Cannot save waveform, chose an active Channel");
                }
                if (CH2 & intCH2AV == 0)
                {
                    MessageBox.Show("CH2 is not active. Cannot save waveform, chose an active Channel");
                }
                if (CH3 & intCH3AV == 0)
                {
                    MessageBox.Show("CH3 is not active. Cannot save waveform, chose an active Channel");
                }
                if (CH4 & intCH4AV == 0)
                {
                    MessageBox.Show("CH4 is not active. Cannot save waveform, chose an active Channel");
                }
                // This is the main part of the save, if there is a channel chosen and if that channel is on, it will be saved.
                if ((CH1 & intCH1AV == 1) | (CH2 & intCH2AV == 1) | (CH3 & intCH3AV == 1) | (CH4 & intCH4AV == 1))
                {
                    SaveFileDialog Save_Files = new SaveFileDialog(); //Use the save dialog so that the name and location can be set by the user
                    Save_Files.Filter = "CSV|*.csv"; // Save as a csv file
                    Save_Files.Title = "Save CSV's of Files"; // Make the title descriptive
                    Save_Files.ShowDialog();


                    if (Save_Files.FileName != "")// Ensure that a name has been chosen
                    {
                        // Loop through to save each frame as csv file in turn using the naming convention chosen in the Save Dialog
                        for (int i = 1; i <= intNumFrames; i++)
                        {
                            instrument.Write("data:framestart " + i); // pick the frame start and start the same to save the single frame
                            instrument.Write("data:framestop " + i);
                            if (CH1 & intCH1AV == 1)
                            {
                                //Save channel 1's waveform if chosen and it is on.  insert a CH1_frame identifier and the number of the frame being saved.
                                instrument.Write("SAVE:WAVEFORM CH1,'" + Save_Files.FileName.Replace(".csv", "") + "_CH1_Frame_" + i + ".csv'");
                                saved = true; //set the indicator that the file has been saved
                            }
                            // Save channel 2's waveform if chosen and it is on
                            if (CH2 & intCH2AV == 1)
                            { 
                                instrument.Write("SAVE:WAVEFORM CH2,'" + Save_Files.FileName.Replace(".csv", "") + "_CH2_Frame_" + i + ".csv'");
                                saved = true;
                            }
                            // Save channel 3's waveform if chosen and it is on
                            if (CH3 & intCH3AV == 1)
                            {
                                instrument.Write("SAVE:WAVEFORM CH3,'" + Save_Files.FileName.Replace(".csv", "") + "_CH3_Frame_" + i + ".csv'");
                                saved = true;
                            }
                            // Save channel 4's waveform if chosen and it is on
                            if (CH4 & intCH4AV == 1)
                            {
                                instrument.Write("SAVE:WAVEFORM CH4,'" + Save_Files.FileName.Replace(".csv", "") + "_CH4_Frame_" + i + ".csv'");
                                saved = true;
                            }

                        }
                    }
                    // inform the user that the files have been saved.
                    if (saved)
                    { MessageBox.Show("The files have been saved."); }
                }
                else
                { MessageBox.Show("Please chose an Active channel."); }
            }
            else
            { MessageBox.Show("Please chose a channel."); }
        }
    }
}
