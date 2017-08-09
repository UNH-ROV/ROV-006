import time
import numpy

class HLController:
    """ High Level Controller.
        Wrapper over all types of controllers (PID, LQR, etc)
        Stores state information and asks the underlying controller for updates.
    """
    def __init__(self, controller):
        self.goalPos = numpy.zeros(3)
        self.position = numpy.zeros(3)
        self.velocity = numpy.zeros(3)
        self.rotation = numpy.zeros(3)

        self.time = time.time()

        self.controller = controller
        self.output = numpy.zeros(3)

    def update(self, accel, gyro):
        """
        Given accelerometer and gyro data, update internal state
        Returns controller output.
        """
        accelx, accely, accelz = accel
        rotx, roty, rotz = gyro

        curr_time = time.time()
        delta_time = curr_time - self.time

        # update internal state
        self.position += self.velocity * delta_time
        self.velocity[0] += accelx * delta_time
        self.velocity[1] += accely * delta_time
        self.velocity[2] += accelz * delta_time
        self.rotation = [rotx, roty, rotz]

        # Ask the controller how to reach goal
        state = numpy.concatenate((self.position, self.rotation))
        output = self.controller.update(state, delta_time)

        self.time = curr_time
        return output


class LQR:
    def __init__(self):
        self.K = 3

    def solve(A,B,Q,R):
        """
        x[k+1] = A x[k] + B u[k]

        cost = sum x[k].T*Q*x[k] + u[k].T*R*u[k]
        """
        #ref Bertsekas, p.151

        #first, try to solve the ricatti equation
        X = np.matrix(scipy.linalg.solve_discrete_are(A, B, Q, R))

        #compute the LQR gain
        K = np.matrix(scipy.linalg.inv(B.T*X*B+R)*(B.T*X*A))

        eigVals, eigVecs = scipy.linalg.eig(A-B*K)

        return K, X, eigVals

class PID:
    """ PID controller over 6 values
    """
    def __init__(self, goal=numpy.zeros(6), p=2.0, i=0.0, d=0.0):
        self.kP = p
        self.kI = i
        self.kD = d
        self.integral = 0.0

        self.prev_error = numpy.zeros(6)
        self.goal = goal

    def update(self, current_value, delta_time):
        """ Calculate PID output value for given reference input and feedback
            Delta_time is expected as msec (but obviously kD can be modified to compensate)
        """
        error = self.goal - current_value

        p = self.kP * error

        self.integral += self.integral + error
        i = self.kI * self.integral

        # Help
        #d = self.kD * (error - self.prev_error)
        d = self.kD * (error - self.prev_error) / delta_time

        self.prev_error = error

        #print(error)
        #print("{} {} {}".format(p, i, d))

        return p + i + d

    def reset(self):
        self.integral = 0.0
        self.prev_error = numpy.zeros(6)

if __name__ == "__main__":
    controller = PID()
    state = numpy.array([300.0, 150.0, 100.0, 3.0, 60.0, 44.0])
    controller.goal = numpy.array([301.0, 150.0, 100.0, 3.0, 60.0, 44.0])
    prev_time = time.time()

    while True:
        curr_time = time.time()
        delta_time = curr_time - prev_time
        error = numpy.random.rand(6) * 0.05

        output = controller.update(state, delta_time * 1000)
        #print("State: {}".format(state))
        #print("Output: {}".format(output))
        state += output + error

        prev_time = curr_time
        time.sleep(0.2)
