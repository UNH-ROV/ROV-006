// Vector3 is generally small enough to pass by value.

// ---------------------- LOW PASS AVERAGE -------------------------
// This uses ROLLING_AVG_COUNT datapoints to reduce signal strength. 
// We have two similar functions which act on accel and gyro state variables.
// This is better as an odd number
#define ROLLING_AVG_COUNT 15

// These data structures assume we start at 0 acceleration
struct Vector3 prev_data[ROLLING_AVG_COUNT] = {{ }};
struct Vector3 prev_sum = {};
int prev_accel_idx = 0;

/**
 * Updates prev_accel_data with new_data and returns new average.
 * Treats prev_accel_data like a ring buffer.
 * Stateful.
 */
struct Vector3 rolling_average(struct Vector3 new_data)
{
    struct Vector3 popped_data = prev_accel_data[prev_accel_idx];
    prev_accel_data[prev_accel_idx++] = new_data;
    prev_accel_idx %= ROLLING_AVG_COUNT;

    prev_accel_sum.x += new_data.x - popped_data.x;
    prev_accel_sum.y += new_data.y - popped_data.y;
    prev_accel_sum.z += new_data.z - popped_data.z;

    struct Vector3 out = prev_accel_sum;
    out.x /= ROLLING_AVG_COUNT;
    out.y /= ROLLING_AVG_COUNT;
    out.z /= ROLLING_AVG_COUNT;
    return out;
}

// ---------------------- COMPLEMENTARY  -------------------------
#define ACCELEROMETER_SENSITIVITY 8192.0
#define GYROSCOPE_SENSITIVITY 65.536

#define M_PI 3.14159265359

#define dt 0.01							// 10 ms sample rate!

void ComplementaryFilter(short accData[3], short gyrData[3], float *pitch, float *roll)

    float pitchAcc, rollAcc;

    // Integrate the gyroscope data -> int(angularSpeed) = angle
    *pitch += ((float)gyrData[0] / GYROSCOPE_SENSITIVITY) * dt; // Angle around the X-axis
    *roll -= ((float)gyrData[1] / GYROSCOPE_SENSITIVITY) * dt;    // Angle around the Y-axis

    // Compensate for drift with accelerometer data if !bullshit
    // Sensitivity = -2 to 2 G at 16Bit -> 2G = 32768 && 0.5G = 8192
    int forceMagnitudeApprox = abs(accData[0]) + abs(accData[1]) + abs(accData[2]);
    if (forceMagnitudeApprox > 8192 && forceMagnitudeApprox < 32768)
    {
	// Turning around the X axis results in a vector on the Y-axis
        pitchAcc = atan2f((float)accData[1], (float)accData[2]) * 180 / M_PI;
        *pitch = *pitch * 0.98 + pitchAcc * 0.02;

	// Turning around the Y axis results in a vector on the X-axis
        rollAcc = atan2f((float)accData[0], (float)accData[2]) * 180 / M_PI;
        *roll = *roll * 0.98 + rollAcc * 0.02;
    }
} 
