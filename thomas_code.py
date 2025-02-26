while not stop_event.is_set():
        try:
            dataMyLaps = qMyLaps.get(block=True)       
            if dataMyLaps:
                # Get 'code' (transponder id)
                code = dataMyLaps["tag"]
                if code != '9992': # Start block, ignore
                    last_tcp_msg_time = time.time() # To monitor TCP connection
                laptimes[code] = dataMyLaps
                deviceId = dataMyLaps["location"]
                laptime = laptimes[code][deviceId]["lapTime"]
                passingTimeUtc = dataMyLaps[deviceId]["rtcTime"]/1000 # is actually UTC, and is sent in ms
                numPassings = dataMyLaps[deviceId]["numLaps"]
                if "console" in config["outputs"] and config["outputs"]["console"]:
                    # utcTime = datetime.fromtimestamp(passingTimeUtc).strftime("%Y-%m-%d %H:%M:%S.%f")
                    # print("Current " + code + ": " + str(numPassings) + " - " + str(passingTimeUtc) + " - " + deviceId)
                    pass
                # Fill log entry
                fields["transponder_id"] = code
                fields["loop"] = deviceId
                fields["utcTimestamp"] = passingTimeUtc
                fields["utcTime"] = datetime.fromtimestamp(passingTimeUtc, tz=tz_utc).strftime('%Y-%m-%d %H:%M:%S.%f')
                fields["localTime"] = datetime.fromtimestamp(passingTimeUtc).strftime('%Y-%m-%d %H:%M:%S.%f')
                fields["lapTime"] = laptime
                fields["cameraPreset"] = cam_coordinator.get_active_camera_preset() # Make sure this is updated in the main thread
                fields["eventName"], _, _, _ = auto_recorder.get_current_event()       
                fields["trackedRider"] = cam_coordinator.get_tracked_rider()