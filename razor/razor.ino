/**
 * Razor IMU Firmware
 * Very minimal accelerometer and gyro reader. Only supports SEN-10736, which was used on the ROV.
 * Adapted from https://github.com/ptrbrtz/razor-9dof-ahrs
 * Use the codebase from that repo to find calibration values.
 */

/*
   "9DOF Razor IMU" hardware versions: SEN-10125 and SEN-10736

   ATMega328@3.3V, 8MHz

ADXL345  : Accelerometer
HMC5843  : Magnetometer on SEN-10125
HMC5883L : Magnetometer on SEN-10736
ITG-3200 : Gyro

Arduino IDE : Select board "Arduino Pro or Pro Mini (3.3v, 8Mhz) w/ATmega328"
 */

/*
   Axis definition (differs from definition printed on the board!):
   X axis pointing forward (towards the short edge with the connector holes)
   Y axis pointing to the right
   Z axis pointing down.

   Positive yaw   : clockwise
   Positive roll  : right wing down
   Positive pitch : nose up

   Transformation order: first yaw then pitch then roll.
 */

/*
   Serial commands that the firmware understands:
   "#b" - Output sensors in BINARY format - acc, gyro (3 floats for each sensor so output frame is 24 bytes)
   "#t" - Output angles in TEXT format (Output frames have form like "#ACC=-142.28,-5.38,33.52#GYR=-142.28,-5.38,33.52#GYR
   followed by carriage return and line feed [\r\n]).

   "#f" - Request one output frame - Sensors only update internally every 20ms(50Hz)

   Newline characters are not required. So you could send "#b#f", which
   would set binary output mode, and fetch

   Byte order of binary output is little-endian: least significant byte comes first.
 */

#define OUTPUT__BAUD_RATE 57600

// Sensor data output interval in milliseconds
// This may not work, if faster than 20ms (=50Hz)
// Code is tuned for 20ms, so better leave it like that
#define READ_INTERVAL 20  // milliseconds

// Output format definitions (do not change)
#define OUTPUT__FORMAT_TEXT 0 // Outputs data as text
#define OUTPUT__FORMAT_BINARY 1 // Outputs data as binary float

// Accelerometer
// "accel x,y,z (min/max) = X_MIN/X_MAX  Y_MIN/Y_MAX  Z_MIN/Z_MAX"
#define ACCEL_X_MIN ((float) -265)
#define ACCEL_X_MAX ((float) 256)
#define ACCEL_Y_MIN ((float) -253)
#define ACCEL_Y_MAX ((float) 264)
#define ACCEL_Z_MIN ((float) -302)
#define ACCEL_Z_MAX ((float) 214)

// Sensor calibration scale and offset values
#define ACCEL_X_OFFSET ((ACCEL_X_MIN + ACCEL_X_MAX) / 2.0f)
#define ACCEL_Y_OFFSET ((ACCEL_Y_MIN + ACCEL_Y_MAX) / 2.0f)
#define ACCEL_Z_OFFSET ((ACCEL_Z_MIN + ACCEL_Z_MAX) / 2.0f)
#define ACCEL_X_SCALE (GRAVITY / (ACCEL_X_MAX - ACCEL_X_OFFSET))
#define ACCEL_Y_SCALE (GRAVITY / (ACCEL_Y_MAX - ACCEL_Y_OFFSET))
#define ACCEL_Z_SCALE (GRAVITY / (ACCEL_Z_MAX - ACCEL_Z_OFFSET))

// Gyroscope
// "gyro x,y,z (current/average) = .../OFFSET_X  .../OFFSET_Y  .../OFFSET_Z
#define GYRO_AVERAGE_OFFSET_X ((float) -48.1)
#define GYRO_AVERAGE_OFFSET_Y ((float) 24.89)
#define GYRO_AVERAGE_OFFSET_Z ((float) 1.21)

// Gain for gyroscope (ITG-3200)
#define GYRO_GAIN 0.06957 // Same gain on all axes
#define GYRO_SCALED_RAD(x) (x * TO_RAD(GYRO_GAIN)) // Calculate the scaled gyro readings in radians per second

// Stuff
#define STATUS_LED_PIN 13  // Pin number of status LED
#define GRAVITY 256.0f // "1G reference" used for DCM filter and accelerometer calibration
#define TO_RAD(x) (x * 0.01745329252)  // *pi/180
#define TO_DEG(x) (x * 57.2957795131)  // *180/pi

struct Vector3 {
    float x;
    float y;
    float z;
};

struct Vector3 accel, gyro;

int output_format = OUTPUT__FORMAT_TEXT;
int prev_time;

void sensors_read() {
    // These modify accel and gyro
    gyro_read();
    accel_read();
}

/**
 * modifies accel_fixed and gyro_fixed with all error_compensation.
 * Error compensation includes using basic calibration values
 * and any filters of interest.
 */
void sensors_fix(struct Vector3 *accel_fixed, struct Vector3 *gyro_fixed) {
    // Compensate accelerometer error
    accel_fixed->x =  (accel.x - ACCEL_X_OFFSET) * ACCEL_X_SCALE;
    accel_fixed->y =  (accel.y - ACCEL_Y_OFFSET) * ACCEL_Y_SCALE;
    accel_fixed->z =  (accel.z - ACCEL_Z_OFFSET) * ACCEL_Z_SCALE;

    // Compensate gyroscope error
    gyro_fixed->x = gyro.x - GYRO_AVERAGE_OFFSET_X;
    gyro_fixed->y = gyro.y - GYRO_AVERAGE_OFFSET_Y;
    gyro_fixed->z = gyro.z - GYRO_AVERAGE_OFFSET_Z;
}

// Prints the current values of the sensors
void sensors_output()
{
    struct Vector3 accel_out = accel;
    struct Vector3 gyro_out = gyro;
    sensors_fix(&accel_out, &gyro_out);

    //accel_out = rolling_accel(accel_out);
    //gyro_out = rolling_gyro(gyro_out);

    if (output_format == OUTPUT__FORMAT_TEXT) {
        Serial.print("#A");
        Serial.print(accel_out.x); Serial.print(",");
        Serial.print(accel_out.y); Serial.print(",");
        Serial.print(accel_out.z);

        Serial.print("#G");
        Serial.print(gyro_out.x); Serial.print(",");
        Serial.print(gyro_out.y); Serial.print(",");
        Serial.print(gyro_out.z);

        Serial.print("\r\n");
    } else {
        // Structs are not densely packed.
        Serial.write((byte *) &accel_out.x, 4);
        Serial.write((byte *) &accel_out.y, 4);
        Serial.write((byte *) &accel_out.z, 4);
        Serial.write((byte *) &gyro_out.x, 4);
        Serial.write((byte *) &gyro_out.y, 4);
        Serial.write((byte *) &gyro_out.z, 4);
    }
}

void setup()
{
    // Init serial output
    Serial.begin(OUTPUT__BAUD_RATE);

    // Init status LED
    pinMode (STATUS_LED_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, LOW);

    // Init sensors
    delay(50);  // Give sensors enough time to start
    i2c_init();
    accel_init();
    gyro_init();

    // Read sensors to initialize state
    delay(20);  // Give sensors enough time to collect data
    prev_time = millis();
    sensors_read();
}

// Main loop
void loop()
{
    // Read incoming control messages
    if (Serial.available() >= 2 && Serial.read() == '#') {
        int command = Serial.read(); // Commands
        switch(command) {
            case 'f':
                sensors_output();
                break;
            case 't':
                output_format = OUTPUT__FORMAT_TEXT;
                break;
            case 'b':
                output_format = OUTPUT__FORMAT_BINARY;
                break;
            default:
                break;
        }
    }

    // Time to read the sensors again?
    int curr_time = millis();
    if ((curr_time - prev_time) >= READ_INTERVAL)
        prev_time = curr_time;
        sensors_read(); // Update sensor reading.

}
