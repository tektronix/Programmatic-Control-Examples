//-------------------------------------------------------------------------------
// Name:  Save Hardcopy with C++ using VISA for 2/3/4/5/6 Series Scopes
// Purpose : This example demonstrates how to save a hard copy screen image from
//   the scope to the PC.
//
// Created:  10/4/2023
//
// Compatible Instruments : 2/3/4/5/6 Series Riddick Based Oscilloscopes
//
// Compatible Interfaces : USB, Ethernet, GPIB
//
// Tektronix provides the following example "AS IS" with no support or warranty.
//
//-------------------------------------------------------------------------------
#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <visa.h>

int main() {

    ViStatus  status;
    ViSession defaultRM, instr;
    ViUInt32 retCount;
    ViChar buffer[80000];

    // Modify the following line to configure this script for your instrument
    char resourceString[] = "TCPIP::10.233.70.92::INSTR";
    ViBuf scpi;

    // Where to save (PC side)
    char target_path[] = "C:\\tempx\\";
    char target_name[] = "scope_screenshot.png";
    char full_path[256];

    // Initialize VISA session
    status = viOpenDefaultRM(&defaultRM);;
    if (status < VI_SUCCESS) {
        printf("Failed to initialize\n");
        return -1;
    }

    // Open instrument connection
    status = viOpen(defaultRM, resourceString, VI_NULL, VI_NULL, &instr);
    if (status < VI_SUCCESS) {
        printf("Error connecting to instrument\n");
        viStatusDesc(defaultRM, status, buffer);
        printf("%s\n", buffer);
        return 0;
    }

    // Set timeout
    status = viSetAttribute(instr, VI_ATTR_TMO_VALUE, 10000);

    // Configure scope for screenshot, see programmers manual for scope-specific syntax
    // Setting where to save screenshot on scope
    scpi = "SAVE:IMAGE \"C:\\screenshots\\tek.png\"\n";
    status = viWrite(instr, scpi, (ViUInt32)strlen(scpi), &retCount);
    if (status < VI_SUCCESS) {
        printf("Error writing to instrument\n");
        viStatusDesc(defaultRM, status, buffer);
        printf("%s\n", buffer);
        return 0;
    }

    // Transfer screenshot to PC
    status = viWrite(instr, "FILESystem:READFile \"C:\\screenshots\\tek.png\"\n", 45, &retCount);
    if (status < VI_SUCCESS) {
        printf("Error writing to instrument\n");
        viStatusDesc(defaultRM, status, buffer);
        printf("%s\n", buffer);
        return 0;
    }
    status = viRead(instr, buffer, sizeof(buffer), &retCount);
    if (status < VI_SUCCESS) {
        printf("Error reading from instrument\n");
        viStatusDesc(defaultRM, status, buffer);
        printf("%s\n", buffer);
        return 0;
    }

    snprintf(full_path, sizeof(full_path), "%s%s", target_path, target_name);
    FILE* file = fopen(full_path, "wb");
    if (file == NULL) {
        printf("Failed to open file for writing.\n");
        return -1;
    }

    size_t bytesWritten = fwrite(buffer, 1, retCount, file);

    // Check if the write operation was successful
    if (bytesWritten != buffer) {
        perror("Error writing to the file");
        fclose(file);
        return 1; // Exit with an error code
    }

    fclose(file);

    viClose(instr);
    viClose(defaultRM);
    return 0;
}