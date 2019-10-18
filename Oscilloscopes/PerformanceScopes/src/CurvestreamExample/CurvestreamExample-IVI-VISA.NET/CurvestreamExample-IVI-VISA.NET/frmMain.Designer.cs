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

namespace CurvestreamExample
{
    partial class frmMain
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.cmdStartTest = new System.Windows.Forms.Button();
            this.cmdEndTest = new System.Windows.Forms.Button();
            this.lblCurvesread = new System.Windows.Forms.Label();
            this.lblCurveCount = new System.Windows.Forms.Label();
            this.txtVisaResourceName = new System.Windows.Forms.TextBox();
            this.lblVisaResourceName = new System.Windows.Forms.Label();
            this.lblSaveDirectory = new System.Windows.Forms.Label();
            this.txtSaveDirectory = new System.Windows.Forms.TextBox();
            this.lblWfmSec = new System.Windows.Forms.Label();
            this.lblWfmPerSec = new System.Windows.Forms.Label();
            this.cbxSaveToDisk = new System.Windows.Forms.CheckBox();
            this.SuspendLayout();
            // 
            // cmdStartTest
            // 
            this.cmdStartTest.Location = new System.Drawing.Point(279, 60);
            this.cmdStartTest.Name = "cmdStartTest";
            this.cmdStartTest.Size = new System.Drawing.Size(75, 23);
            this.cmdStartTest.TabIndex = 1;
            this.cmdStartTest.Text = "Start";
            this.cmdStartTest.UseVisualStyleBackColor = true;
            this.cmdStartTest.Click += new System.EventHandler(this.cmdStartTest_Click);
            // 
            // cmdEndTest
            // 
            this.cmdEndTest.Enabled = false;
            this.cmdEndTest.Location = new System.Drawing.Point(279, 90);
            this.cmdEndTest.Name = "cmdEndTest";
            this.cmdEndTest.Size = new System.Drawing.Size(75, 23);
            this.cmdEndTest.TabIndex = 2;
            this.cmdEndTest.Text = "End Test";
            this.cmdEndTest.UseVisualStyleBackColor = true;
            this.cmdEndTest.Click += new System.EventHandler(this.cmdEndTest_Click);
            // 
            // lblCurvesread
            // 
            this.lblCurvesread.AutoSize = true;
            this.lblCurvesread.Font = new System.Drawing.Font("Microsoft Sans Serif", 14.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblCurvesread.Location = new System.Drawing.Point(54, 18);
            this.lblCurvesread.Name = "lblCurvesread";
            this.lblCurvesread.Size = new System.Drawing.Size(124, 24);
            this.lblCurvesread.TabIndex = 3;
            this.lblCurvesread.Text = "Curves Read:";
            // 
            // lblCurveCount
            // 
            this.lblCurveCount.AutoSize = true;
            this.lblCurveCount.Font = new System.Drawing.Font("Microsoft Sans Serif", 14.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblCurveCount.Location = new System.Drawing.Point(184, 18);
            this.lblCurveCount.Name = "lblCurveCount";
            this.lblCurveCount.Size = new System.Drawing.Size(20, 24);
            this.lblCurveCount.TabIndex = 4;
            this.lblCurveCount.Text = "0";
            // 
            // txtVisaResourceName
            // 
            this.txtVisaResourceName.Location = new System.Drawing.Point(12, 81);
            this.txtVisaResourceName.Name = "txtVisaResourceName";
            this.txtVisaResourceName.Size = new System.Drawing.Size(242, 20);
            this.txtVisaResourceName.TabIndex = 5;
            this.txtVisaResourceName.Text = "TCPIP0::192.168.1.10::inst0::INSTR";
            // 
            // lblVisaResourceName
            // 
            this.lblVisaResourceName.AutoSize = true;
            this.lblVisaResourceName.Location = new System.Drawing.Point(9, 65);
            this.lblVisaResourceName.Name = "lblVisaResourceName";
            this.lblVisaResourceName.Size = new System.Drawing.Size(114, 13);
            this.lblVisaResourceName.TabIndex = 6;
            this.lblVisaResourceName.Text = "VISA Resource Name:";
            // 
            // lblSaveDirectory
            // 
            this.lblSaveDirectory.AutoSize = true;
            this.lblSaveDirectory.Location = new System.Drawing.Point(9, 116);
            this.lblSaveDirectory.Name = "lblSaveDirectory";
            this.lblSaveDirectory.Size = new System.Drawing.Size(80, 13);
            this.lblSaveDirectory.TabIndex = 7;
            this.lblSaveDirectory.Text = "Save Directory:";
            // 
            // txtSaveDirectory
            // 
            this.txtSaveDirectory.Location = new System.Drawing.Point(12, 132);
            this.txtSaveDirectory.Name = "txtSaveDirectory";
            this.txtSaveDirectory.Size = new System.Drawing.Size(242, 20);
            this.txtSaveDirectory.TabIndex = 8;
            this.txtSaveDirectory.Text = "C:\\Temp\\";
            // 
            // lblWfmSec
            // 
            this.lblWfmSec.AutoSize = true;
            this.lblWfmSec.Location = new System.Drawing.Point(310, 29);
            this.lblWfmSec.Name = "lblWfmSec";
            this.lblWfmSec.Size = new System.Drawing.Size(51, 13);
            this.lblWfmSec.TabIndex = 9;
            this.lblWfmSec.Text = "Wfm/sec";
            // 
            // lblWfmPerSec
            // 
            this.lblWfmPerSec.AutoSize = true;
            this.lblWfmPerSec.Location = new System.Drawing.Point(276, 29);
            this.lblWfmPerSec.Name = "lblWfmPerSec";
            this.lblWfmPerSec.Size = new System.Drawing.Size(13, 13);
            this.lblWfmPerSec.TabIndex = 10;
            this.lblWfmPerSec.Text = "0";
            this.lblWfmPerSec.TextAlign = System.Drawing.ContentAlignment.MiddleRight;
            // 
            // cbxSaveToDisk
            // 
            this.cbxSaveToDisk.AutoSize = true;
            this.cbxSaveToDisk.Location = new System.Drawing.Point(279, 134);
            this.cbxSaveToDisk.Name = "cbxSaveToDisk";
            this.cbxSaveToDisk.Size = new System.Drawing.Size(93, 17);
            this.cbxSaveToDisk.TabIndex = 11;
            this.cbxSaveToDisk.Text = "Save to Disk?";
            this.cbxSaveToDisk.UseVisualStyleBackColor = true;
            // 
            // frmMain
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(373, 168);
            this.Controls.Add(this.cbxSaveToDisk);
            this.Controls.Add(this.lblWfmPerSec);
            this.Controls.Add(this.lblWfmSec);
            this.Controls.Add(this.txtSaveDirectory);
            this.Controls.Add(this.lblSaveDirectory);
            this.Controls.Add(this.lblVisaResourceName);
            this.Controls.Add(this.txtVisaResourceName);
            this.Controls.Add(this.lblCurveCount);
            this.Controls.Add(this.lblCurvesread);
            this.Controls.Add(this.cmdEndTest);
            this.Controls.Add(this.cmdStartTest);
            this.Name = "frmMain";
            this.Text = "Curvestream Example";
            this.Load += new System.EventHandler(this.frmMain_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button cmdStartTest;
        private System.Windows.Forms.Button cmdEndTest;
        private System.Windows.Forms.Label lblCurvesread;
        private System.Windows.Forms.Label lblCurveCount;
        private System.Windows.Forms.TextBox txtVisaResourceName;
        private System.Windows.Forms.Label lblVisaResourceName;
        private System.Windows.Forms.Label lblSaveDirectory;
        private System.Windows.Forms.TextBox txtSaveDirectory;
        private System.Windows.Forms.Label lblWfmSec;
        private System.Windows.Forms.Label lblWfmPerSec;
        private System.Windows.Forms.CheckBox cbxSaveToDisk;
    }
}

