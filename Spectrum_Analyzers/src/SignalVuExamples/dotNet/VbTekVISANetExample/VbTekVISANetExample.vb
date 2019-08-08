' TekVISASocketExample : 11/9/2016 (Updated 12/15/2016)
' 
' Code sample for communicating in VB.Net to an RSA instrument using TekVISANet.dll
' Sends PI commands to preset, sets CF to 1GHz, Span to 1MHz, and takes a peak reading
' The TekVISA socket server is not required for this example.

Imports TekVISANet

Module VbTekVISANetExample

		Private Sub Message(s As String)
			Console.WriteLine("[{0}] {1}", DateTime.Now, s)
		End Sub

		Sub Main()
			Const  rsaIpAddress As String = "127.0.0.1"
			Dim rsa = New VISA()
			Try
				'rsa.Open(String.Format("TCPIP::{0}::INSTR", rsaIpAddress))
                rsa.Open("GPIB8::1::INSTR")
				If rsa.Status <> TekVISADefs.Status.SUCCESS Then
					Message(String.Format("Unable to connect to RSA at ipaddr {0}", rsaIpAddress))
					Return
				End If

				' Confirm we are connected to the RSA.
				rsa.Write("*RST")
				Dim retString As String = String.Empty
				rsa.Query("*IDN?", retString)
				Message(Convert.ToString("Connected to: ") & rsaIpAddress)
				Message(Convert.ToString("*IDN? returned ") & retString)

				' Preset the system, set CF to 1 GHz, 1 MHz span, and turn off continous acquisitions
				rsa.Write(":SYSTEM:PRESET")
				Dim retVal As Integer
				rsa.Query("*OPC?", retVal)
				rsa.Write("*CLS")
				rsa.Write("INIT:CONT OFF")
				rsa.Write(":SENSE:SPEC:FREQ:CENTER 1e9")
				rsa.Write(":SENSE:SPEC:FREQ:SPAN 1e6")

				' Add a marker
				rsa.Write("CALCulate:MARKer:ADD")

				' Take one acquisition
				rsa.Write("INIT")
				rsa.Query("*OPC?", retVal)

				' Use marker to find max peak
				rsa.Write("CALC:SPEC:MARKer0:MAX")
				Dim peakLevel As Double
				rsa.Query("CALC:SPEC:MARK0:Y?", peakLevel)
				Message(String.Format("Peak Amplitude is {0:0.00} dBm", peakLevel))
			Finally
				' Be a good .NET citizen and explicitly close resources.
				rsa.Clear()
				rsa.Close()
			End Try

			Console.WriteLine("Hit enter to close...")
			Dim wait = Console.ReadLine()

		End Sub

End Module

