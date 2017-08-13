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
   "#t" - Output sensors in TEXT format (Output has the form "#ACC=-142.28,-5.38,33.52#GYR=-142.28,-5.38,33.52"
   followed by carriage return and line feed [\r\n]).
   "#a" - Output angle

   Newline characters are not required. So you can send #b#a to get sensor and angle data.

   Byte order of binary output is little-endian: least significant byte comes first.
 */

#define OUTPUT__BAUD_RATE 57600

// Sensor data output interval in milliseconds
// This may not work, if faster than 20ms (=50Hz)
// Code is tuned for 20ms, so better leave it like that
#define READ_INTERVAL 20  // milliseconds
#define DELTA_TIME (READ_INTERVAL / 1000.0)

// Output format definitions (do not change)
#define OUTPUT__FORMAT_TEXT 0 // Outputs data as text
#define OUTPUT__FORMAT_BINARY 1 // Outputs data as binary float

// Values of gravity on the various axis, both + and -
#define ACCEL_X_MIN -265
#define ACCEL_X_MAX 256
#define ACCEL_Y_MIN -253
#define ACCEL_Y_MAX 264
#define ACCEL_Z_MIN -302
#define ACCEL_Z_MAX 214

// Moves accelerometer output so that 0 is 0
#define ACCEL_X_OFFSET ((ACCEL_X_MIN + ACCEL_X_MAX) / -2.0f)
#define ACCEL_Y_OFFSET ((ACCEL_Y_MIN + ACCEL_Y_MAX) / -2.0f)
#define ACCEL_Z_OFFSET ((ACCEL_Z_MIN + ACCEL_Z_MAX) / -2.0f)

// Scales accelerometer output so that ACCEL_X_MAX is GRAVITY
#define ACCEL_X_SCALE (GRAVITY / (ACCEL_X_MAX + ACCEL_X_OFFSET))
#define ACCEL_Y_SCALE (GRAVITY / (ACCEL_Y_MAX + ACCEL_Y_OFFSET))
#define ACCEL_Z_SCALE (GRAVITY / (ACCEL_Z_MAX + ACCEL_Z_OFFSET))

#define GYRO_X_OFFSET (-49.66)
#define GYRO_Y_OFFSET (18.375)
#define GYRO_Z_OFFSET (14.177)

// Obtained from docs(Sensitivity Scale Factor). Converts gyro output to deg/s
#define GYRO_SCALE (-14.375)

// Stuff
#define STATUS_LED_PIN 13  // Pin number of status LED
#define GRAVITY 256.0f // "1G reference". Direction not included.

struct Vector3 {
    float x;
    float y;
    float z;
};

struct Vector3 accel, gyro, angle;

int output_format = OUTPUT__FORMAT_TEXT;
int prev_time;

/**
 * modifies accel and gyro with all error_compensation.
 * Error compensation includes using basic calibration values
 * and any filters of interest.
 */
void sensors_fix() {
    // In the future one should compensate for ROV axis here
    // For now I'll just flip the z axis
    // Compensate accelerometer error
    accel.x =  (accel.x + ACCEL_X_OFFSET) * ACCEL_X_SCALE;
    accel.y =  (accel.y + ACCEL_Y_OFFSET) * ACCEL_Y_SCALE;
    accel.z =  -1.0 * (accel.z + ACCEL_Z_OFFSET) * ACCEL_Z_SCALE;

    // Compensate gyroscope error
    gyro.x = (gyro.x + GYRO_X_OFFSET) / GYRO_SCALE;
    gyro.y = (gyro.y + GYRO_Y_OFFSET) / GYRO_SCALE;
    gyro.z = (gyro.z + GYRO_Z_OFFSET) / GYRO_SCALE;
}

void sensors_read() {
    gyro = gyro_read();
    accel = accel_read();

    sensors_fix();
}


void angle_update()
{
    angle.x += gyro.x * DELTA_TIME;
    angle.y += gyro.y * DELTA_TIME;
    angle.z += gyro.z * DELTA_TIME;
    //complementary(accel, gyro, &(angle.x), &(angle.y));
}


// Prints the current values of the sensors
void sensors_output()
{
    struct Vector3 accel_out = accel;
    struct Vector3 gyro_out = gyro;

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

// Prints the current angle
// This will be relative to initial starting orientation.
void angle_output() {
    if (output_format == OUTPUT__FORMAT_TEXT) {
        Serial.print("#YPR");
        Serial.print(angle.x); Serial.print(",");
        Serial.print(angle.y); Serial.print(",");
        Serial.print(angle.z);

        Serial.print("\r\n");
    } else {
        Serial.write((byte *) &angle.x, 4);
        Serial.write((byte *) &angle.y, 4);
        Serial.write((byte *) &angle.z, 4);
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

    // Initialize state
    angle = { 0, 0, 0 };

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
            case 't':
                output_format = OUTPUT__FORMAT_TEXT;
                break;
            case 'b':
                output_format = OUTPUT__FORMAT_BINARY;
                break;
            case 's':
                sensors_output();
                break;
            case 'a':
                angle_output();
                break;
            default:
                break;
        }
    }

    // Time to read the sensors again?
    int curr_time = millis();
    if ((curr_time - prev_time) >= READ_INTERVAL) {
        prev_time = curr_time;
        sensors_read();
        angle_update();
    }
}
