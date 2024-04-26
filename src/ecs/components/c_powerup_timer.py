
class CPowerupTimer:
    def __init__(self, max_time:float) -> None:
        self.current_time:float = max_time #start with ability ready
        self.max_time = max_time
    
    def reset(self) -> bool:
        if self.current_time >= self.max_time:
            self.current_time = 0.0
            return True
        else:
            return False
