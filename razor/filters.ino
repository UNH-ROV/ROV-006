// Vector3 is generally small enough to pass by value.

// ---------------------- LOW PASS AVERAGE -------------------------
// This uses ROLLING_AVG_COUNT datapoints to reduce signal strength. 
// We have two similar functions which act on accel and gyro state variables.
// This is better as an odd number
#define ROLLING_AVG_COUNT 15

// These data structures assume we start at 0 acceleration
struct Vector3 prev_data[ROLLING_AVG_COUNT] = {{ }};
struct Vector3 prev_sum = {};
int prev_idx = 0;

/**
 * Updates prev_data with new_data and returns new average.
 * Treats prev_data like a ring buffer.
 * Stateful.
 */
struct Vector3 rolling_average(struct Vector3 new_data)
{
    struct Vector3 popped_data = prev_data[prev_idx];
    prev_data[prev_idx++] = new_data;
    prev_idx %= ROLLING_AVG_COUNT;

    prev_sum.x += new_data.x - popped_data.x;
    prev_sum.y += new_data.y - popped_data.y;
    prev_sum.z += new_data.z - popped_data.z;

    struct Vector3 out = prev_sum;
    out.x /= ROLLING_AVG_COUNT;
    out.y /= ROLLING_AVG_COUNT;
    out.z /= ROLLING_AVG_COUNT;
    return out;
}

// ---------------------- COMPLEMENTARY  -------------------------
// Uses gyro and accel data to determine angle deltas.
// 256 = 1G
#define ACCEL_THRESHOLD 128.0
#define GYRO_SCALE 1.0

#define ACCEL_WEIGHT 0.02
#define GYRO_WEIGHT (1.0 - ACCEL_WEIGHT)

#define M_PI 3.14159265359
#define dt (READ_INTERVAL / 1000.0)

void complementary(const struct Vector3 accel,
                   const struct Vector3 gyro,
                   float *pitch, float *roll) {
    float pitch_acc, roll_acc;

    // Integrate the gyroscope data -> int(angularSpeed) = angle
    *pitch += (gyro.x / GYRO_SCALE) * dt; // Angle around the X-axis
    *roll += (gyro.y / GYRO_SCALE) * dt;  // Angle around the Y-axis

    // Compensate for drift with accelerometer data
    float accel_magnitude_approx = abs(accel.x) + abs(accel.y) + abs(accel.z);
    if (accel_magnitude_approx > ACCEL_THRESHOLD) {
	// Turning around the X axis results in a vector on the Y-axis
        pitch_acc = atan2f(accel.y, accel.z);
        *pitch = *pitch * GYRO_WEIGHT + pitch_acc * ACCEL_WEIGHT;

	// Turning around the Y axis results in a vector on the X-axis
        roll_acc = atan2f(accel.x, accel.z);
        *roll = *roll * GYRO_WEIGHT + roll_acc * ACCEL_WEIGHT;
    }
}
