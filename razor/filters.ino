// Vector3 is generally small enough to pass by value.

// Use ROLLING_AVG_COUNT previous values to determine the average
#define ROLLING_AVG_COUNT 8

// These data structures assume we start at 0 acceleration
struct Vector3 prev_accel_data[ROLLING_AVG_COUNT - 1] = {{ }};
int prev_accel_idx = 0;

struct Vector3 prev_gyro_data[ROLLING_AVG_COUNT - 1] = {{ }};
int prev_gyro_idx = 0;


/**
 * Updates prev_accel_data with new_data and returns new average.
 * Treats prev_accel_data like a ring buffer.
 * Stateful.
 */
struct Vector3 rolling_accel(struct Vector3 new_data)
{
    prev_accel_data[prev_accel_idx++] = new_data;
    prev_accel_idx = prev_accel_idx % ROLLING_AVG_COUNT;

    return average(prev_accel_data, ROLLING_AVG_COUNT);
}

/**
 * Same as above, but with prev_gyro_data
 */
struct Vector3 rolling_gyro(struct Vector3 new_data)
{
    prev_gyro_data[prev_gyro_idx++] = new_data;
    prev_gyro_idx = prev_gyro_idx % ROLLING_AVG_COUNT;

    return average(prev_gyro_data, ROLLING_AVG_COUNT);
}

// Calculates average of a set of data
struct Vector3 average(struct Vector3 *data, int size)
{
    struct Vector3 sum = { 0, 0, 0 };
    for (int i = 0; i < size; i++) {
        sum.x += data[i].x;
        sum.y += data[i].y;
        sum.z += data[i].z;
    }

    sum.x /= size;
    sum.y /= size;
    sum.z /= size;
    return sum;
}
