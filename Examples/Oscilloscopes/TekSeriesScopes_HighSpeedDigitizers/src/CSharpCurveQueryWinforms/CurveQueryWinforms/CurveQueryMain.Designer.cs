namespace CurveQuery
{
    partial class frmCurveQuery
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
            this.btnGetWaveform = new System.Windows.Forms.Button();
            this.plotView = new OxyPlot.WindowsForms.PlotView();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.dropDownCH = new System.Windows.Forms.ComboBox();
            this.lblChannel = new System.Windows.Forms.Label();
            this.txtVisaRsrcAddr = new System.Windows.Forms.TextBox();
            this.lblVisaAddr = new System.Windows.Forms.Label();
            this.lblInstrumentID = new System.Windows.Forms.Label();
            this.txtInstrumentID = new System.Windows.Forms.TextBox();
            this.groupBox1.SuspendLayout();
            this.SuspendLayout();
            // 
            // btnGetWaveform
            // 
            this.btnGetWaveform.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.btnGetWaveform.Location = new System.Drawing.Point(422, 346);
            this.btnGetWaveform.Name = "btnGetWaveform";
            this.btnGetWaveform.Size = new System.Drawing.Size(90, 23);
            this.btnGetWaveform.TabIndex = 0;
            this.btnGetWaveform.Text = "Get Waveform";
            this.btnGetWaveform.UseVisualStyleBackColor = true;
            this.btnGetWaveform.Click += new System.EventHandler(this.btnGetWaveform_Click);
            // 
            // plotView
            // 
            this.plotView.BackColor = System.Drawing.SystemColors.ControlLightLight;
            this.plotView.Dock = System.Windows.Forms.DockStyle.Fill;
            this.plotView.Location = new System.Drawing.Point(3, 16);
            this.plotView.Name = "plotView";
            this.plotView.PanCursor = System.Windows.Forms.Cursors.Hand;
            this.plotView.Size = new System.Drawing.Size(494, 277);
            this.plotView.TabIndex = 1;
            this.plotView.Text = "plotView1";
            this.plotView.ZoomHorizontalCursor = System.Windows.Forms.Cursors.SizeWE;
            this.plotView.ZoomRectangleCursor = System.Windows.Forms.Cursors.SizeNWSE;
            this.plotView.ZoomVerticalCursor = System.Windows.Forms.Cursors.SizeNS;
            // 
            // groupBox1
            // 
            this.groupBox1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.groupBox1.Controls.Add(this.plotView);
            this.groupBox1.Location = new System.Drawing.Point(12, 32);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(500, 296);
            this.groupBox1.TabIndex = 2;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Waveform";
            // 
            // dropDownCH
            // 
            this.dropDownCH.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.dropDownCH.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.dropDownCH.Items.AddRange(new object[] {
            "CH1",
            "CH2",
            "CH3",
            "CH4"});
            this.dropDownCH.Location = new System.Drawing.Point(371, 347);
            this.dropDownCH.Name = "dropDownCH";
            this.dropDownCH.Size = new System.Drawing.Size(45, 21);
            this.dropDownCH.TabIndex = 3;
            // 
            // lblChannel
            // 
            this.lblChannel.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.lblChannel.AutoSize = true;
            this.lblChannel.Location = new System.Drawing.Point(328, 351);
            this.lblChannel.Name = "lblChannel";
            this.lblChannel.Size = new System.Drawing.Size(37, 13);
            this.lblChannel.TabIndex = 4;
            this.lblChannel.Text = "Fetch:";
            // 
            // txtVisaRsrcAddr
            // 
            this.txtVisaRsrcAddr.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.txtVisaRsrcAddr.Location = new System.Drawing.Point(105, 348);
            this.txtVisaRsrcAddr.Name = "txtVisaRsrcAddr";
            this.txtVisaRsrcAddr.Size = new System.Drawing.Size(216, 20);
            this.txtVisaRsrcAddr.TabIndex = 5;
            this.txtVisaRsrcAddr.Text = "TCPIP::192.168.1.2::inst0::INSTR";
            // 
            // lblVisaAddr
            // 
            this.lblVisaAddr.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.lblVisaAddr.AutoSize = true;
            this.lblVisaAddr.Location = new System.Drawing.Point(24, 352);
            this.lblVisaAddr.Name = "lblVisaAddr";
            this.lblVisaAddr.Size = new System.Drawing.Size(75, 13);
            this.lblVisaAddr.TabIndex = 6;
            this.lblVisaAddr.Text = "VISA Address:";
            // 
            // lblInstrumentID
            // 
            this.lblInstrumentID.AutoSize = true;
            this.lblInstrumentID.Location = new System.Drawing.Point(9, 9);
            this.lblInstrumentID.Name = "lblInstrumentID";
            this.lblInstrumentID.Size = new System.Drawing.Size(73, 13);
            this.lblInstrumentID.TabIndex = 7;
            this.lblInstrumentID.Text = "Instrument ID:";
            // 
            // txtInstrumentID
            // 
            this.txtInstrumentID.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.txtInstrumentID.Location = new System.Drawing.Point(88, 6);
            this.txtInstrumentID.Name = "txtInstrumentID";
            this.txtInstrumentID.ReadOnly = true;
            this.txtInstrumentID.Size = new System.Drawing.Size(421, 20);
            this.txtInstrumentID.TabIndex = 8;
            // 
            // frmCurveQuery
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(524, 381);
            this.Controls.Add(this.txtInstrumentID);
            this.Controls.Add(this.lblInstrumentID);
            this.Controls.Add(this.lblVisaAddr);
            this.Controls.Add(this.txtVisaRsrcAddr);
            this.Controls.Add(this.lblChannel);
            this.Controls.Add(this.dropDownCH);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.btnGetWaveform);
            this.MinimumSize = new System.Drawing.Size(540, 420);
            this.Name = "frmCurveQuery";
            this.Text = "Curve Query Winforms Example";
            this.Load += new System.EventHandler(this.frmCurveQuery_Load);
            this.groupBox1.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button btnGetWaveform;
        private OxyPlot.WindowsForms.PlotView plotView;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.ComboBox dropDownCH;
        private System.Windows.Forms.Label lblChannel;
        private System.Windows.Forms.TextBox txtVisaRsrcAddr;
        private System.Windows.Forms.Label lblVisaAddr;
        private System.Windows.Forms.Label lblInstrumentID;
        private System.Windows.Forms.TextBox txtInstrumentID;
    }
}

