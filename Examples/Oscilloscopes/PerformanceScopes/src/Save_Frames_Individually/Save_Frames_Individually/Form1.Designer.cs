
namespace Save_Frames_Individually
{
    partial class Save_Frames
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
            this.Visa_reply = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.Save_Button = new System.Windows.Forms.Button();
            this.Channel_Select_checkListBox = new System.Windows.Forms.CheckedListBox();
            this.SuspendLayout();
            // 
            // Visa_reply
            // 
            this.Visa_reply.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Visa_reply.ForeColor = System.Drawing.Color.DarkOliveGreen;
            this.Visa_reply.Location = new System.Drawing.Point(37, 34);
            this.Visa_reply.Margin = new System.Windows.Forms.Padding(3, 2, 3, 2);
            this.Visa_reply.Name = "Visa_reply";
            this.Visa_reply.Size = new System.Drawing.Size(421, 30);
            this.Visa_reply.TabIndex = 0;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label1.Location = new System.Drawing.Point(32, 6);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(229, 25);
            this.label1.TabIndex = 1;
            this.label1.Text = "Oscilloscope Connection";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label2.Location = new System.Drawing.Point(132, 89);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(240, 25);
            this.label2.TabIndex = 3;
            this.label2.Text = "Which Channels to Save?";
            // 
            // Save_Button
            // 
            this.Save_Button.BackColor = System.Drawing.SystemColors.ControlDark;
            this.Save_Button.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Save_Button.Location = new System.Drawing.Point(162, 227);
            this.Save_Button.Margin = new System.Windows.Forms.Padding(3, 2, 3, 2);
            this.Save_Button.Name = "Save_Button";
            this.Save_Button.Size = new System.Drawing.Size(193, 49);
            this.Save_Button.TabIndex = 4;
            this.Save_Button.Text = "Save";
            this.Save_Button.UseVisualStyleBackColor = false;
            this.Save_Button.Click += new System.EventHandler(this.Save_Button_Click);
            // 
            // Channel_Select_checkListBox
            // 
            this.Channel_Select_checkListBox.CheckOnClick = true;
            this.Channel_Select_checkListBox.FormattingEnabled = true;
            this.Channel_Select_checkListBox.Items.AddRange(new object[] {
            "CH1",
            "CH2",
            "CH3",
            "CH4"});
            this.Channel_Select_checkListBox.Location = new System.Drawing.Point(208, 117);
            this.Channel_Select_checkListBox.Name = "Channel_Select_checkListBox";
            this.Channel_Select_checkListBox.Size = new System.Drawing.Size(92, 89);
            this.Channel_Select_checkListBox.TabIndex = 5;
            this.Channel_Select_checkListBox.SelectedIndexChanged += new System.EventHandler(this.Channel_Select_checkListBox_SelectedIndexChanged);
            // 
            // Save_Frames
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(504, 287);
            this.Controls.Add(this.Channel_Select_checkListBox);
            this.Controls.Add(this.Save_Button);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.Visa_reply);
            this.Margin = new System.Windows.Forms.Padding(3, 2, 3, 2);
            this.Name = "Save_Frames";
            this.ShowIcon = false;
            this.Text = "Save Frames Individually";
            this.Load += new System.EventHandler(this.Save_Frames_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TextBox Visa_reply;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Button Save_Button;
        private System.Windows.Forms.CheckedListBox Channel_Select_checkListBox;
    }
}

