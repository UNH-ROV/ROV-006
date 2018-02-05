/*
 * goio.c
 *	data acquisition module for the Vernier GoIO-style interfaces
 *	assumes GoIO SDK is compiled and installed  in a place the linker can see
 *	Can be freely distributed and used under the terms of the GNU GPL
 *
 * Written by:	E.Sternin <edward.sternin@brocku.ca>
 * Completed:	2014.04.28 - basic version, no device/sensor selection (tested on a Go!Link)
 * Revisions:	
 *
 */

/*
 * Parts of this code are inspired by the GoIO_DeviceCheck.cpp from the Vernier 
 * GoIO SDK, and therefore are subject to the following restrictions:
 */

/*********************************************************************************
Copyright (c) 2010, Vernier Software & Technology
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of Vernier Software & Technology nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL VERNIER SOFTWARE & TECHNOLOGY BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
**********************************************************************************/

#ifndef TRUE
#define	TRUE	1
#define	FALSE	0
#endif

#ifndef VERSION			/* date-derived in Makefile */
#define	VERSION	"2014-04-28"	/* default, that's when we started */
#endif

#include <sys/io.h>
#include <asm/types.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>		/* adds the C++ style bool type to C */
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <GoIO/GoIO_DLL_interface.h>	/* assumed installed in /usr/include/GoIO */

/* Global variables */

#define	MAX_STR		80
#define	MIN_DWELL	40	/* 40ms = the fastest sampling time from a GoIO interface */

static char	whoami[MAX_STR] ;		/* argv[0] will end up here */
static int	verbosity;			/* Show detailed information */
static int	nsamples,completed_samples;
static char	options[] = "Vvhtd:n:o:" ;	/* command-line options, : means takes a valus */
static char	help_msg[] = "\
%s [<options>]\n\
\t-V\t\t report version information\n\
\t-v\t\t increase verbosity, may combine several\n\
\t-t\t\t test if a GoIO device is present\n\
\t-d #\t\t dwell time between measurements, in ms, defaults to 40 ms\n\
\t-n #\t\t number of samples, defaults to 1\n\
\t-o filename\t output file, defaults to stdout\n\
\t-h\t\t print out this help message" 
;
static char	*deviceDesc[8] = {"?", "?", "Go! Temp", "Go! Link", "Go! Motion", "?", "?", "Mini GC"};
static void	OSSleep(unsigned long msToSleep);

/*************************************************service routines************/

void __attribute__((noreturn))
die(char *msg, ...)
{
  va_list args;

  va_start(args, msg);
  vfprintf(stderr, msg, args);
  fputc('\n', stderr);
  exit(1);
}

void OSSleep(
  unsigned long msToSleep) { //milliseconds
  struct timeval tv;
  unsigned long usToSleep = msToSleep*1000;
  tv.tv_sec = usToSleep/1000000;
  tv.tv_usec = usToSleep % 1000000;
  select (0, NULL, NULL, NULL, &tv);
  }

bool GetAvailableDeviceName(char *deviceName, gtype_int32 nameLength, gtype_int32 *pVendorId, gtype_int32 *pProductId) {
	bool bFoundDevice = false;
	deviceName[0] = 0;
	int numSkips = GoIO_UpdateListOfAvailableDevices(VERNIER_DEFAULT_VENDOR_ID, SKIP_DEFAULT_PRODUCT_ID);
	int numJonahs = GoIO_UpdateListOfAvailableDevices(VERNIER_DEFAULT_VENDOR_ID, USB_DIRECT_TEMP_DEFAULT_PRODUCT_ID);
	int numCyclopses = GoIO_UpdateListOfAvailableDevices(VERNIER_DEFAULT_VENDOR_ID, CYCLOPS_DEFAULT_PRODUCT_ID);
	int numMiniGCs = GoIO_UpdateListOfAvailableDevices(VERNIER_DEFAULT_VENDOR_ID, MINI_GC_DEFAULT_PRODUCT_ID);

	if (numSkips > 0) {
		GoIO_GetNthAvailableDeviceName(deviceName, nameLength, VERNIER_DEFAULT_VENDOR_ID, SKIP_DEFAULT_PRODUCT_ID, 0);
		*pVendorId = VERNIER_DEFAULT_VENDOR_ID;
		*pProductId = SKIP_DEFAULT_PRODUCT_ID;
		bFoundDevice = true;
		}
	else if (numJonahs > 0) {
		GoIO_GetNthAvailableDeviceName(deviceName, nameLength, VERNIER_DEFAULT_VENDOR_ID, USB_DIRECT_TEMP_DEFAULT_PRODUCT_ID, 0);
		*pVendorId = VERNIER_DEFAULT_VENDOR_ID;
		*pProductId = USB_DIRECT_TEMP_DEFAULT_PRODUCT_ID;
		bFoundDevice = true;
		}
	else if (numCyclopses > 0) {
		GoIO_GetNthAvailableDeviceName(deviceName, nameLength, VERNIER_DEFAULT_VENDOR_ID, CYCLOPS_DEFAULT_PRODUCT_ID, 0);
		*pVendorId = VERNIER_DEFAULT_VENDOR_ID;
		*pProductId = CYCLOPS_DEFAULT_PRODUCT_ID;
		bFoundDevice = true;
		}
	else if (numMiniGCs > 0) {
		GoIO_GetNthAvailableDeviceName(deviceName, nameLength, VERNIER_DEFAULT_VENDOR_ID, MINI_GC_DEFAULT_PRODUCT_ID, 0);
		*pVendorId = VERNIER_DEFAULT_VENDOR_ID;
		*pProductId = MINI_GC_DEFAULT_PRODUCT_ID;
		bFoundDevice = true;
		}
	return bFoundDevice;
	}

/***************************************************************** main *********/
int
main(int argc, char **argv)
{
  int 	i,j,dwell=MIN_DWELL,DryRun=FALSE;
  FILE	*fp;
  char 	*output_file;
  char	tmpstring[MAX_STR];
  gtype_int32 vendorId;			//USB vendor id
  gtype_int32 productId;		//USB product id
  char	deviceName[GOIO_MAX_SIZE_DEVICE_NAME];
  bool	GetAvailableDeviceName(char *deviceName, gtype_int32 nameLength, gtype_int32 *pVendorId, gtype_int32 *pProductId);

/*
 *  default values, may get changed by the command-line options
 */

  verbosity = 0;			/* 0 = quiet by default, 1 = info, 2 = debug */	
  fp = stdout;
  nsamples = 1;
  completed_samples = 0;
  output_file = NULL;

  strncpy(whoami, argv[0], MAX_STR);

  while ((i = getopt(argc, argv, options)) != -1)
    switch (i)
      {
      case 'V':
	fprintf(stderr," %s: version %s\n",whoami,VERSION);
	DryRun = TRUE;
	break;
      case 'v':
	verbosity++;
	if (verbosity > 1) fprintf(stderr," %s: verbosity level set to %d\n",whoami,verbosity);
	break;
      case 't':
	if (verbosity > 1) fprintf(stderr," %s: testing if a GoIO device is available\n",whoami);
	if (verbosity < 1) verbosity = 1;
  	DryRun = TRUE;
	break;
      case 'd':
	if ( ((dwell = atoi(optarg)) < 40) || dwell > 10000 )
	  die(" %s: -d %d (ms) is not a valid dwell time, 40ms .. 10s\n",whoami,dwell);
	break;
      case 'h':
	die(help_msg,whoami);
	break;
      case 'n':
	if ( ((nsamples = atoi(optarg)) < 0) || nsamples > 1000000 )
	  die(" %s: -n %d is not a valid number of samples\n",whoami,nsamples);
	if (verbosity > 1) fprintf(stderr," %s: N_samples = %d\n",whoami,nsamples);
	break;
      case 'o':
	if ( (fp = fopen(optarg,"w")) == NULL )
	  die(" %s: unable to create file %s (%s)\n",whoami,optarg,strerror(errno));
	fclose(fp);
	if (verbosity > 1) fprintf(stderr," %s: file %s created/emptied\n",whoami,optarg);
	if ( (output_file = malloc(i=strlen(optarg)+2)) == NULL )
	  die(" %s: unable to allocate memory for filename (%s)\n",whoami,optarg);
        strncpy(output_file,optarg,i);
	break;
      default:
	if (verbosity > 0) die(" try %s -?\n",whoami);	/* otherwise, die quietly */
	return 0;
      }

  /* 
   * the data acquisition loop
   */

  if (fp != stdout) fp = fopen(output_file,"w"); 	/* at this point we already know we can open fp */

  GoIO_Init();

  bool bFoundDevice = GetAvailableDeviceName(deviceName, GOIO_MAX_SIZE_DEVICE_NAME, &vendorId, &productId);
  if (!bFoundDevice) {
	if (verbosity > 1) fprintf(stderr," %s: no GoIO devices found\n",whoami);
	}
  else {
	GOIO_SENSOR_HANDLE hDevice = GoIO_Sensor_Open(deviceName, vendorId, productId, 0);
	if (hDevice != NULL) {
		unsigned char charId;
		GoIO_Sensor_DDSMem_GetSensorNumber(hDevice, &charId, 0, 0);
		GoIO_Sensor_DDSMem_GetLongName(hDevice, tmpstring, sizeof(tmpstring));
		if (verbosity > 0) fprintf(stderr," %s: found %s device = %s, sensor = %d (%s)\n", 
				whoami, deviceDesc[productId], deviceName, charId, tmpstring);
		if (!DryRun) {
			if (verbosity > 1) fprintf(stderr," %s: getting %d samples, one every %d ms\n",whoami,nsamples,dwell);
			char units[20];
			char equationType = 0;

			gtype_int32 raw_value;
			gtype_real64 volts,calibrated_value;

			GoIO_Sensor_SetMeasurementPeriod(hDevice, 0.001*dwell, SKIP_TIMEOUT_MS_DEFAULT); /* here dwell is in seconds */
			dwell = 1000*GoIO_Sensor_GetMeasurementPeriod(hDevice,SKIP_TIMEOUT_MS_DEFAULT); /* the actual dwell time may be different, get it in ms */
			GoIO_Sensor_SendCmdAndGetResponse(hDevice, SKIP_CMD_ID_START_MEASUREMENTS, NULL, 0, NULL, NULL, SKIP_TIMEOUT_MS_DEFAULT);
			for (j=0; j < nsamples; j++ ) {
			    OSSleep(dwell);
			    raw_value = GoIO_Sensor_GetLatestRawMeasurement(hDevice);
			    volts = GoIO_Sensor_ConvertToVoltage(hDevice, raw_value);
			    calibrated_value = GoIO_Sensor_CalibrateData(hDevice, volts);

			    GoIO_Sensor_DDSMem_GetCalibrationEquation(hDevice, &equationType);	/* keep these in the loop, as it may change ? */
			    gtype_real32 a, b, c;
			    unsigned char activeCalPage = 0;
			    GoIO_Sensor_DDSMem_GetActiveCalPage(hDevice, &activeCalPage);
			    GoIO_Sensor_DDSMem_GetCalPage(hDevice, activeCalPage, &a, &b, &c, units, sizeof(units));
			    fprintf(fp,"\t%8.3f\t%8.3f %s\n",((double)(j)*0.001*dwell),calibrated_value,units);
			    }
			}
		GoIO_Sensor_Close(hDevice);
		}
	}
  GoIO_Uninit();

  if (fp != stdout) fclose(fp);

  exit(0);
}