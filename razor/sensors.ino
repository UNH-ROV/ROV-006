// I2C code to read the sensors

// Sensor I2C addresses
#define ACCEL_ADDRESS ((int16_t) 0x53) // 0x53 = 0xA6 / 2
#define GYRO_ADDRESS  ((int16_t) 0x68) // 0x68 = 0xD0 / 2

// Arduino backward compatibility macros
#if ARDUINO >= 100
  #define WIRE_SEND(b) Wire.write((byte) b)
  #define WIRE_RECEIVE() Wire.read()
#else
  #define WIRE_SEND(b) Wire.send(b)
  #define WIRE_RECEIVE() Wire.receive()
#endif

#include <Wire.h>

void i2c_init()
{
    Wire.begin();
}

void accel_init()
{
    Wire.beginTransmission(ACCEL_ADDRESS);
    WIRE_SEND(0x2D);  // Power register
    WIRE_SEND(0x08);  // Measurement mode
    Wire.endTransmission();
    delay(5);
    Wire.beginTransmission(ACCEL_ADDRESS);
    WIRE_SEND(0x31);  // Data format register
    WIRE_SEND(0x08);  // Set to full resolution
    Wire.endTransmission();
    delay(5);

    // Because our main loop runs at 50Hz we adjust the output data rate to 50Hz (25Hz bandwidth)
    Wire.beginTransmission(ACCEL_ADDRESS);
    WIRE_SEND(0x2C);  // Rate
    WIRE_SEND(0x09);  // Set to 50Hz, normal operation
    Wire.endTransmission();
    delay(5);
}

// Reads x, y and z accelerometer registers
struct Vector3 accel_read()
{
    struct Vector3 reading = {};
    int i = 0;
    uint8_t buff[6];

    Wire.beginTransmission(ACCEL_ADDRESS);
    WIRE_SEND(0x32);  // Send address to read from
    Wire.endTransmission();

    Wire.requestFrom(ACCEL_ADDRESS, 6);  // Request 6 bytes
    while (Wire.available()) {
        buff[i++] = WIRE_RECEIVE();
    }

    if (i == 6) { // All bytes received?
        // No multiply by -1 for coordinate system transformation here, because of double negation:
        // We want the gravity vector, which is negated acceleration vector.
        reading.x = (int16_t)((((uint16_t) buff[3]) << 8) | buff[2]);  // X axis (internal sensor y axis)
        reading.y = (int16_t)((((uint16_t) buff[1]) << 8) | buff[0]);  // Y axis (internal sensor x axis)
        reading.z = (int16_t)((((uint16_t) buff[5]) << 8) | buff[4]);  // Z axis (internal sensor z axis)
    } else {
        // Error reading accelerometer
    }

    return reading;
}

void gyro_init()
{
    // Power up reset defaults
    Wire.beginTransmission(GYRO_ADDRESS);
    WIRE_SEND(0x3E);
    WIRE_SEND(0x80);
    Wire.endTransmission();
    delay(5);

    // Select full-scale range of the gyro sensors
    // Set LP filter bandwidth to 42Hz
    Wire.beginTransmission(GYRO_ADDRESS);
    WIRE_SEND(0x16);
    WIRE_SEND(0x1B);  // DLPF_CFG = 3, FS_SEL = 3
    Wire.endTransmission();
    delay(5);

    // Set sample rato to 50Hz
    Wire.beginTransmission(GYRO_ADDRESS);
    WIRE_SEND(0x15);
    WIRE_SEND(0x0A);  //  SMPLRT_DIV = 10 (50Hz)
    Wire.endTransmission();
    delay(5);

    // Set clock to PLL with z gyro reference
    Wire.beginTransmission(GYRO_ADDRESS);
    WIRE_SEND(0x3E);
    WIRE_SEND(0x00);
    Wire.endTransmission();
    delay(5);
}

// Reads x, y and z gyroscope registers
struct Vector3 gyro_read()
{
    struct Vector3 reading = {};
    int i = 0;
    uint8_t buff[6];

    Wire.beginTransmission(GYRO_ADDRESS);
    WIRE_SEND(0x1D);  // Sends address to read from
    Wire.endTransmission();

    Wire.requestFrom(GYRO_ADDRESS, 6);  // Request 6 bytes
    while (Wire.available()) {
        buff[i++] = WIRE_RECEIVE();
    }

    if (i == 6) { // All bytes received?
        reading.x = -1 * (int16_t)(((((uint16_t) buff[2]) << 8) | buff[3]));    // X axis (internal sensor -y axis)
        reading.y = -1 * (int16_t)(((((uint16_t) buff[0]) << 8) | buff[1]));    // Y axis (internal sensor -x axis)
        reading.z = -1 * (int16_t)(((((uint16_t) buff[4]) << 8) | buff[5]));    // Z axis (internal sensor -z axis)
    } else {
        // Gyro error!
    }

    return reading;
}
