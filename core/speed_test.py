# core/speed_test.py
import speedtest
from core.speech import speak
from core.utils import handle_error

def run_speed_test():
    try:
        speak("Initiating speed test. This may take a few seconds.")
        st = speedtest.Speedtest()
        st.get_servers([])

        download_speed = st.download(threads=1) / 1_000_000  # bits to Mbps
        upload_speed = st.upload(threads=1) / 1_000_000
        ping = st.results.ping

        download_speed = round(download_speed, 2)
        upload_speed = round(upload_speed, 2)

        speak(f"Your Download speed is {download_speed} megabits per second.")
        speak(f"Your Upload speed is {upload_speed} megabits per second.")
        speak(f"Your Ping is {ping} milliseconds.")

    except Exception as e:
        handle_error("run_speed_test", e)
        speak("Sorry, I was unable to complete the speed test.")
