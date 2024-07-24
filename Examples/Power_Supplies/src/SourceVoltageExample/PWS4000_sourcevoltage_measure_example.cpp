#include <ansi_c.h>
#include <stdio.h>
#include "visa.h"

static ViSession defaultRM, vi;
static ViStatus status;
static unsigned char strCmd[256], strReply[256];
static ViUInt32 retCnt;

int main()
{
    status = viOpenDefaultRM(&defaultRM);
    if (status < VI_SUCCESS) goto Error;

    status = viOpen(defaultRM, "PWS4000", VI_NULL, VI_NULL, &vi);
    if (status < VI_SUCCESS) goto Error;
    
    sprintf((char*)strCmd, "*RST\n");
    status = viWrite (vi, strCmd, strlen((char*)strCmd), &retCnt);
    if (status < VI_SUCCESS) goto Error;
    
    sprintf((char*)strCmd, "*IDN?\n");
    status = viWrite (vi, strCmd, strlen((char*)strCmd), &retCnt);
    if (status < VI_SUCCESS) goto Error;
    status = viRead(vi, strReply, 255, &retCnt);
    if (status < VI_SUCCESS) goto Error;
        
    // viRead() writes into the string only the data read from the instrument
    // therefore you need to NULL terminate the strings manually.
    strReply[retCnt] = 0;
    puts((char*)strReply);

    sprintf((char*)strCmd, "VOLT 5.0\n");
    status = viWrite (vi, strCmd, strlen((char*)strCmd), &retCnt);
    if (status < VI_SUCCESS) goto Error;

    sprintf((char*)strCmd, "CURR 0.5\n");
    status = viWrite (vi, strCmd, strlen((char*)strCmd), &retCnt);
    if (status < VI_SUCCESS) goto Error;
    
    sprintf((char*)strCmd, "OUTP ON\n");
    status = viWrite (vi, strCmd, strlen((char*)strCmd), &retCnt);
    if (status < VI_SUCCESS) goto Error;
    
    sprintf((char*)strCmd, "MEAS:VOLT?\n");
    status = viWrite (vi, strCmd, strlen((char*)strCmd), &retCnt);
    if (status < VI_SUCCESS) goto Error;
    status = viRead(vi, strReply, 255, &retCnt);
    if (status < VI_SUCCESS) goto Error;
    strReply[retCnt] = 0;
    printf("Voltage: %s", strReply);

    sprintf((char*)strCmd, "MEAS:CURR?\n");
    status = viWrite (vi, strCmd, strlen((char*)strCmd), &retCnt);
    if (status < VI_SUCCESS) goto Error;
    status = viRead(vi, strReply, 255, &retCnt);
    if (status < VI_SUCCESS) goto Error;
    strReply[retCnt] = 0;
    printf("Current: %s", strReply);

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
