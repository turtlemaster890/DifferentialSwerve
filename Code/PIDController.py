class PIDController:
    def __init__(self, kp: float, ki: float = 0, kd: float = 0, integral_limit: float = 10.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.prev_error = 0
        self.integral = 0
        self.integral_limit = integral_limit

    def reset(self) -> None:
        self.prev_error = 0
        self.integral = 0

    def calculate(self, measurement: float, setpoint: float) -> float:
        error = setpoint - measurement
        self.integral += error
        self.integral = max(-self.integral_limit, min(self.integral_limit, self.integral))
        derivative = error - self.prev_error
        self.prev_error = error
        return (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)