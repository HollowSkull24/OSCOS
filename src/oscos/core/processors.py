class StreamProcessor:
    def __init__(self, out_buffer):
        self.out_buffer = out_buffer

    def push(self, timestamp, value):
        raise NotImplementedError

    def reset(self):
        pass

class SpeedProcessor(StreamProcessor):
    def __init__(self, tooth_length_mm, out_buffer):
        super().__init__(out_buffer)
        self.tooth_length = tooth_length_mm * 1e-3
        self.prev_ts = None

    def reset(self):
        self.prev_ts = None

    def push(self, timestamp):
        if self.prev_ts is None:
            self.prev_ts = timestamp
            return

        dt = (timestamp - self.prev_ts)
        if dt <= 0:
            self.prev_ts = timestamp
            return

        v = self.tooth_length / dt
        t_mid = (timestamp + self.prev_ts) / 2

        self.out_buffer.add(v, t_mid)
        self.prev_ts = timestamp

class AccelerationProcessor(StreamProcessor):
    def __init__(self, out_buffer):
        super().__init__(out_buffer)
        self.prev_v = None
        self.prev_t = None

    def __call__(self, timestamp, value):
        if self.prev_v is None:
            self.prev_v = value
            self.prev_t = timestamp
            return

        dt = timestamp - self.prev_t
        if dt <= 0:
            return

        a = (value - self.prev_v) / dt
        t_mid = (timestamp + self.prev_t) / 2

        self.out_buffer.add(a, t_mid)

        self.prev_v = value
        self.prev_t = timestamp

    def reset(self):
        self.prev_v = None
        self.prev_t = None

class SpeedCorrectedProcessor:
    def __init__(self, out_buffer):
        self.out_buffer = out_buffer

        self.prev_t = None
        self.prev_v = None

        self.state = None          # "ascending" | "descending"
        self.current_sign = 1

        # Tunables
        self.SLOPE_EPS = 0.02       # Slope deadband, which makes small slope values to be treated as zero
        self.CONFIRM_SAMPLES = 3    # Number of consecutive ascending slopes required to confirm a minimum
        self.MIN_FLIP_DT = 0.2     # Minimum time between sign flips (seconds)

        # Smoothing (exponential moving average)
        # Set `smoothing_alpha` to 0.0 to disable smoothing. Typical values: 0.1-0.4
        self.smoothing_alpha = 0.2
        self._smoothed_v = None

        self._asc_count = 0
        self._last_flip_t = None

        self.reset()

    def reset(self):
        self.prev_t = None
        self.prev_v = None
        self._smoothed_v = None
        self.state = None
        self.current_sign = 1
        self._asc_count = 0
        self._last_flip_t = None

    def __call__(self, t, v):
        # Update smoothed value (exponential moving average)
        if self._smoothed_v is None or self.smoothing_alpha <= 0.0:
            sm_v = v
            self._smoothed_v = sm_v
        else:
            sm_v = (self.smoothing_alpha * v) + (1.0 - self.smoothing_alpha) * self._smoothed_v
            self._smoothed_v = sm_v

        if self.prev_v is None:
            # prev_v now holds previous smoothed value
            self.prev_t = t
            self.prev_v = sm_v
            return

        dt = t - self.prev_t
        if dt <= 0:
            return

        # Compute slope using smoothed values
        slope = (sm_v - self.prev_v) / dt

        # Apply deadband
        if abs(slope) < self.SLOPE_EPS:
            slope = 0.0

        # Initialize state
        if self.state is None:
            self.state = "ascending" if slope > 0 else "descending"

        # State transitions
        if self.state == "descending":
            if slope > 0:
                self._asc_count += 1
                if self._asc_count >= self.CONFIRM_SAMPLES:
                    # Time gating
                    if (
                        self._last_flip_t is None or
                        (t - self._last_flip_t) >= self.MIN_FLIP_DT
                    ):
                        self.current_sign *= -1
                        self._last_flip_t = t

                    self.state = "ascending"
                    self._asc_count = 0
            else:
                self._asc_count = 0

        elif self.state == "ascending":
            if slope < 0:
                self.state = "descending"
                self._asc_count = 0

        # Apply correction to the smoothed value
        v_corrected = self.current_sign * sm_v
        self.out_buffer.add(v_corrected, t)

        # Update previous smoothed value and time
        self.prev_v = sm_v
        self.prev_t = t

class SpeedPeakDetection:
    def __init__(self, out_buffer, window_seconds=0.5, threshold=0.4):
        """Detecta máximos asegurando que no haya dos picos en `window_seconds`.

        La ventana no comienza hasta que se confirma un máximo: se mantiene un
        candidato a máximo que se actualiza si llegan valores mayores. Si desde
        el tiempo del candidato no llega ningún valor mayor durante
        `window_seconds`, el candidato se emite como pico. Tras emitir, se
        bloquean nuevos picos durante `window_seconds` desde el tiempo del
        pico emitido.
        """
        self.out_buffer = out_buffer
        self.window_seconds = float(window_seconds)
        self.threshold = float(threshold)

        # Candidate maximum waiting to be confirmed (value and time)
        self._candidate_v = None
        self._candidate_t = None

        # Block until this time after emitting a peak
        self._blocked_until = None

    def __call__(self, t, v):
        # First, if we have a candidate and enough time has passed without a
        # larger value, confirm and emit it (unless it's inside a blocked period).
        if self._candidate_v is not None:
            if t >= (self._candidate_t + self.window_seconds):
                if self._blocked_until is None or self._candidate_t >= self._blocked_until:
                    if self._candidate_v > self.threshold:
                        self.out_buffer.add(self._candidate_v, self._candidate_t)
                        # Block subsequent peaks for window_seconds
                        self._blocked_until = self._candidate_t + self.window_seconds
                # Clear candidate after handling
                self._candidate_v = None
                self._candidate_t = None

        # If we're still in the blocked period after emitting a peak, ignore
        # starting new candidates until the block expires.
        if self._blocked_until is not None and t < self._blocked_until:
            return

        # Consider this sample as a candidate if it exceeds the threshold.
        if v > self.threshold:
            if self._candidate_v is None:
                # Start a new candidate maximum
                self._candidate_v = v
                self._candidate_t = t
            else:
                # If this sample is larger, move the candidate forward
                if v > self._candidate_v:
                    self._candidate_v = v
                    self._candidate_t = t

    def reset(self):
        self._candidate_v = None
        self._candidate_t = None
        self._blocked_until = None