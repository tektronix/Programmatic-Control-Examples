#include <stdio.h>
#include <Windows.h>
#include "visa.h"

#define _CRT_SECURE_NO_WARNINGS
#define BUFFER 255

static ViSession defaultRM, vi;
static ViStatus status;
static unsigned char strCmd[256], strReply[256];
static ViUInt32 retCnt;

int main()
{
	//VISA Session Setup
	status = viOpenDefaultRM(&defaultRM);
	if (status < VI_SUCCESS) goto Error;

	status = viOpen(defaultRM, "GPIB8::1::INSTR", VI_NULL, 100000, &vi);
	if (status < VI_SUCCESS) goto Error;

	//Sending Reset and Identification Commands
	sprintf_s((char*)strCmd, 6, "*RST\n");
	status = viWrite(vi, strCmd, strlen((char*)strCmd), &retCnt);
	if (status < VI_SUCCESS) goto Error;

	sprintf_s((char*)strCmd, 7, "*IDN?\n");
	status = viWrite(vi, strCmd, strlen((char*)strCmd), &retCnt);
	if (status < VI_SUCCESS) goto Error;
	status = viRead(vi, strReply, 255, &retCnt);
	if (status < VI_SUCCESS) goto Error;

	// viRead() writes into the string only the data read from the instrument
	// therefore you need to NULL terminate the strings manually.
	strReply[retCnt] = 0;
	puts((char*)strReply);

	//General Setup
	sprintf_s((char*)strCmd, BUFFER, "display:general:measview:new toverview\n");
	status = viWrite(vi, strCmd, strlen((char*)strCmd), &retCnt);
	if (status < VI_SUCCESS) goto Error;

	sprintf_s((char*)strCmd, BUFFER, "display:general:measview:new avtime\n");
	status = viWrite(vi, strCmd, strlen((char*)strCmd), &retCnt);
	if (status < VI_SUCCESS) goto Error;
	
	double cf = 2.4453e9;
	sprintf_s((char*)strCmd, BUFFER, "spectrum:frequency:center %f\n", cf);
	status = viWrite(vi, strCmd, strlen((char*)strCmd), &retCnt);
	if (status < VI_SUCCESS) goto Error;

	double refLevel = 0;
	sprintf_s((char*)strCmd, BUFFER, "input:rlevel %f\n", refLevel);
	status = viWrite(vi, strCmd, strlen((char*)strCmd), &retCnt);
	if (status < VI_SUCCESS) goto Error;

	double aLength = 100e-6;
	sprintf_s((char*)strCmd, BUFFER, "sense:analysis:length %f\n", aLength);
	status = viWrite(vi, strCmd, strlen((char*)strCmd), &retCnt);
	if (status < VI_SUCCESS) goto Error;
	
	//Start Acquisition
	sprintf_s((char*)strCmd, BUFFER, "initiate:continuous off\n");
	status = viWrite(vi, strCmd, strlen((char*)strCmd), &retCnt);
	if (status < VI_SUCCESS) goto Error;

	sprintf_s((char*)strCmd, BUFFER, "initiate:immediate\n");
	status = viWrite(vi, strCmd, strlen((char*)strCmd), &retCnt);
	if (status < VI_SUCCESS) goto Error;


Error:
	if (status < VI_SUCCESS)
	{
		viStatusDesc(vi, status, (char*)strReply);
		printf("VISA Error Occured:\r\n%s", strReply);
	}
	if (vi != VI_NULL) viClose(vi);
	if (defaultRM != VI_NULL) viClose(defaultRM);

	printf("\r\nPress any key to continue ...");
	getchar();
	return 0;
}