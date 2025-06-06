from functools import wraps

def handle_audio_errors(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.update_queue.put(('error', f"Error in {func.__name__}: {str(e)}"))
            return None
    return wrapper
