' TekVISASocketExample : 11/9/2016 (Updated 12/15/2016)
' 
' Code sample for communicating in VB.Net to an RSA instrument through TekVISA socket server on port 4000
' Sends PI commands to preset, sets CF to 1GHz, Span to 1MHz, and takes a peak reading
' Be sure to start to TekVISA socket server in the TekVISA LAN Server Control (can also set it to auto start).

Imports System.Net.Sockets
Imports System.IO

Module VbTekVISASocketExample
	Private Sub Message(s As String)
		Console.WriteLine("[{0}] {1}", DateTime.Now, s)
	End Sub

	Sub Main()
		Const  rsaIpAddress As String = "127.0.0.1"
		Dim rsaReader As StreamReader
		Dim rsaWriter As StreamWriter

		Try
			Dim rsaClient = New TcpClient(rsaIpAddress, 4000)
			Dim rsaStream = rsaClient.GetStream()
			rsaReader = New StreamReader(rsaStream)
			rsaWriter = New StreamWriter(rsaStream) With { .AutoFlush = True }
        Catch e As Exception
			Message(String.Format("Unable to connect to RSA at ipaddr {0}\n{1}", rsaIpAddress, e.Message))
			Return
		End Try

		' Confirm we are connected to the RSA.
		rsaWriter.WriteLine("*IDN?")
		Dim rsaInfo = rsaReader.ReadLine()
		Message(String.Format("Connected to: {0}", rsaIpAddress))
		Message("*IDN? returned " + rsaInfo)

		' Preset the system, set CF to 1 GHz, 1 MHz span, and turn off continous acquisitions
		rsaWriter.WriteLine(":SYSTEM:PRESET")
		rsaWriter.WriteLine("*OPC?")
		rsaReader.ReadLine()
		rsaWriter.WriteLine("*CLS")
		rsaWriter.WriteLine("INIT:CONT OFF")
		rsaWriter.WriteLine(":SENSE:SPEC:FREQ:CENTER 1e9")
		rsaWriter.WriteLine(":SENSE:SPEC:FREQ:SPAN 1e6")

		' Add a marker
		rsaWriter.WriteLine("CALCulate:MARKer:ADD")

		' Take one acquisition
		rsaWriter.WriteLine("INIT")
		rsaWriter.WriteLine("*OPC?")
		rsaReader.ReadLine()

        ' Use marker to find max peak
		rsaWriter.WriteLine("CALC:SPEC:MARKer0:MAX")
		rsaWriter.WriteLine("CALC:SPEC:MARK0:Y?")
		Dim peakLevel = Convert.ToDouble(rsaReader.ReadLine())
		Message(String.Format("Peak Amplitude is {0:0.00} dBm", peakLevel))

		Console.WriteLine("Hit enter to close...")
		Dim wait = Console.ReadLine()

		' Be a good .NET citizen and explicitly close resources.
		rsaReader.Close()
		rsaWriter.Close()
	End Sub

End Module

