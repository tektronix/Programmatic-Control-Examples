------------------------------------------------------------------------------------
--- Function: setup_smu()
--- Description: This function initializes each SMU with the settings appropriate
--- to complete this test. 
------------------------------------------------------------------------------------
function setup_smus()
    for slot_no=1, slot_count do
        for chan_no=1, 2 do
            local smu = slot[slot_no].smu[chan_no]
            -- Reset SMU
            smu.reset()
            smu.defbuffer1.clear()
            smu.defbuffer2.clear()
            -- Source settings
            smu.source.func         = smu.FUNC_DC_VOLTAGE
            smu.source.limiti       = ilimit
            smu.source.levelv       = vlevel
            smu.source.autorangev   = smu.OFF
            smu.source.rangev       = vlevel
            --Measure settings
            smu.measure.autorangei  = smu.OFF
            smu.measure.rangei      = ilimit
            smu.measure.aperture    = aperture
            smu.trigger.measure.i(smu.defbuffer1)
        end
    end
end

------------------------------------------------------------------------------------
--- Function: sync_measurements_trigger_timer()
--- Description: This function performs measurements across multiple SMU channels, 
--- up to six, in parallel. This is done with the use of a trigger timer which
--- allows for minimal drift in measurement timing.
------------------------------------------------------------------------------------
function sync_measurements_trigger_timer()

    --local loopCt = 100  -- Used for fixed count scan
    -- Trigger timer allows easy syncronization
    local triggerTimer          = trigger.timer[1]
    --triggerTimer.count          = loopCt  -- Used for fixed count scan
    triggerTimer.count          = 0 -- Infinite timer events
    triggerTimer.delay          = measure_interval
    triggerTimer.passthrough    = false
    triggerTimer.stimulus       = trigger.generator[1].EVENT_ID
    
    -- Create identical trigger models for all channels
    for slot_no=1, slot_count do
        local triggerModel = slot[slot_no].trigger.model
        for chan_no=1, 2 do
            local tm_name = string.format("trigModel%d", chan_no)
            -- Create trigger model
            triggerModel.create(tm_name)
            triggerModel.addblock.source.output(tm_name, "output-on", chan_no, 1)
            triggerModel.addblock.wait(tm_name, "wait", trigger.timer[1].EVENT_ID)  -- Wait for event from trigger timer
            triggerModel.addblock.measure(tm_name, "measure", chan_no, 1)           -- Take a single measurement (not ideal for fast measurements)
            triggerModel.addblock.branch.event(tm_name, "abort", "output-off", trigger.generator[2].EVENT_ID)   -- Check for abort event
            --triggerModel.addblock.branch.counter(tm_name, "branch", "wait", loopCt)  -- Used for fixed count scan
            triggerModel.addblock.branch.always(tm_name, "branch", "wait")          -- Loop back to wait
            triggerModel.addblock.source.output(tm_name, "output-off", chan_no, 0)  -- Output off and end
            triggerModel.initiate(tm_name)
        end
    end
    delay(100e-3)   -- Allow time for trigger models to build
    trigger.generator[1].assert()   -- Begin the trigger timer
end
------------------------------------------------------------------------------------
--- Function: sync_measurements_delay_constant()
--- Description: This function performs measurements across multiple SMU channels, 
--- up to six, in parallel. Timing is achieved by making the first channel a master
--- which uses a delay constant and notifys the other channels when to measure.
--- This is less accurate than using a trigger timer and has a drift of roughly .5
--- to .33 us per iteration.
------------------------------------------------------------------------------------
function sync_measurements_delay_constant()
    --local loopCt = 2000  -- Used for fixed count scan
    -- Create trigger models for every channel
    for slot_no=slot_count, 1, -1 do
        local triggerModel = slot[slot_no].trigger.model
        for chan_no=2, 1, -1 do
            local tm_name = string.format("trigModel%d", chan_no)
            -- Channel 1 of Slot 1 serves as master, notifying others when to take measurements
            if slot_no == 1 and chan_no == 1 then
                triggerModel.create(tm_name)
                triggerModel.addblock.source.output(tm_name, "output-on", chan_no, 1)
                triggerModel.addblock.notify(tm_name, "notify-slots", triggerModel.EVENT_NOTIFY1)                   -- Notify others to take a measurements
                triggerModel.addblock.measure(tm_name, "measure", chan_no, 1)                                       -- Take single measurement (not ideal for fast measurements)
                triggerModel.addblock.branch.event(tm_name, "abort", "output-off", trigger.generator[2].EVENT_ID)   -- Check for abort event
                triggerModel.addblock.delay.constant(tm_name, "delay-constant", measure_interval, "notify-slots")   -- Delay for constant time (introduces error, not ideal)
                --triggerModel.addblock.branch.counter(tm_name, "branch", "notify-slots", loopCt)  -- Used for fixed count scan
                triggerModel.addblock.branch.always(tm_name, "branch", "notify-slots")                              -- Loop to notificataion
                triggerModel.addblock.source.output(tm_name, "output-off", chan_no, 0)                              -- Turn output off and end test
                delay(100e-3)
                triggerModel.initiate(tm_name)
            -- All other channels wait for notification from master to measure
            else
                triggerModel.create(tm_name)
                triggerModel.addblock.source.output(tm_name, "output-on", chan_no, 1)
                triggerModel.addblock.wait(tm_name, "wait-main", slot[1].trigger.model.EVENT_NOTIFY1)               -- Wait for notificaiton from master
                triggerModel.addblock.measure(tm_name, "measure", chan_no, 1)                                       -- Take single measurement (not ideal for fast measurements)
                triggerModel.addblock.branch.event(tm_name, "abort", "output-off", trigger.generator[2].EVENT_ID)   -- Check for abort event
                --triggerModel.addblock.branch.counter(tm_name, "branch", "wait-main", loopCt)  -- Used for fixed count scan
                triggerModel.addblock.branch.always(tm_name, "branch", "wait-main")                                 -- Loop to wait
                triggerModel.addblock.source.output(tm_name, "output-off", chan_no, 0)                              -- Turn output off and end test
                triggerModel.initiate(tm_name)
            end
        end
    end
end

-- This function deletes the trigger models off each module
function delete_trigger_models()
    for i=1, slot_count do
        slot[i].trigger.model.delete("trigModel1")
        slot[i].trigger.model.delete("trigModel2")
    end
end
-- This function aborts all trigger models
function abort_trigger_models()
    trigger.generator[2].assert() -- Send event to abort trigger models
    delay(500e-3) -- Wait for all models to abort
    for i=1, slot_count do
        -- Turn outputs off
        slot[i].smu[1].source.output = 0 
        slot[i].smu[2].source.output = 0
    end
end

-- This function prints contents of reading buffers in a table format 
function print_reading_buffers()
    if slot_count == 1 then
        print("Time\t\t Ch1\t\t Ch2")
        for i=1, slot[1].smu[1].defbuffer1.n do
            print(slot[1].smu[1].defbuffer1.timestamps[i],
                  vlevel/slot[1].smu[1].defbuffer1[i], vlevel/slot[1].smu[2].defbuffer1[i]
                 )
        end
    elseif slot_count == 2 then
        print("Time\t\t Ch1\t\t Ch2\t\t Ch3\t\t Ch4")
        for i=1, slot[1].smu[1].defbuffer1.n do
            print(slot[1].smu[1].defbuffer1.timestamps[i],
                  vlevel/slot[1].smu[1].defbuffer1[i], vlevel/slot[1].smu[2].defbuffer1[i],
                  vlevel/slot[2].smu[1].defbuffer1[i], vlevel/slot[2].smu[2].defbuffer1[i]
                 )
        end
    else
        print("Time\t\t Ch1\t\t Ch2\t\t Ch3\t\t Ch4\t\t Ch5\t\t Ch6")
        for i=1, slot[1].smu[1].defbuffer1.n do
            print(slot[1].smu[1].defbuffer1.timestamps[i],
                  vlevel/slot[1].smu[1].defbuffer1[i], vlevel/slot[1].smu[2].defbuffer1[i],
                  vlevel/slot[2].smu[1].defbuffer1[i], vlevel/slot[2].smu[2].defbuffer1[i],
                  vlevel/slot[3].smu[1].defbuffer1[i], vlevel/slot[3].smu[2].defbuffer1[i]
                 )
        end
    end
end

-- This function exports all buffer data to a UBS drive
function export_to_usb()
    local filename = "/usb1/exported_data.csv"  -- Set file to be created, will overwrite if file exists
    local fptr, err = io.open(filename, "w")    -- Define a file pointer
    if err == nil then                          -- Check for USB error
        -- Write buffer data to USB in csv for easy analysis
        if slot_count == 1 then
            fptr:write("Time, Ch1, Ch2\n")
            for i=1, slot[1].smu[1].defbuffer1.n do
                local writeString = string.format("%f, %f, %f",
                    slot[1].smu[1].defbuffer1.timestamps[i],
                    vlevel/slot[1].smu[1].defbuffer1[i], vlevel/slot[1].smu[2].defbuffer1[i]
                )
                fptr:write(writeString)
            end
        elseif slot_count == 2 then
            fptr:write("Time, Ch1, Ch2, Ch3, Ch4\n")
            for i=1, slot[1].smu[1].defbuffer1.n do
                local writeString = string.format("%f, %f, %f, %f, %f\n",
                    slot[1].smu[1].defbuffer1.timestamps[i],
                    vlevel/slot[1].smu[1].defbuffer1[i], vlevel/slot[1].smu[2].defbuffer1[i],
                    vlevel/slot[2].smu[1].defbuffer1[i], vlevel/slot[2].smu[2].defbuffer1[i]
                )
                fptr:write(writeString)
            end
        else
            fptr:write("Time, Ch1, Ch2, Ch3, Ch4, Ch5, Ch6\n")
            for i=1, slot[1].smu[1].defbuffer1.n do
                local writeString = string.format("%f, %f, %f, %f, %f, %f, %f\n",
                    slot[1].smu[1].defbuffer1.timestamps[i],
                    vlevel/slot[1].smu[1].defbuffer1[i], vlevel/slot[1].smu[2].defbuffer1[i],
                    vlevel/slot[2].smu[1].defbuffer1[i], vlevel/slot[2].smu[2].defbuffer1[i],
                    vlevel/slot[3].smu[1].defbuffer1[i], vlevel/slot[3].smu[2].defbuffer1[i]
                )
                fptr:write(writeString)
            end
        end
        fptr:flush()
        fptr:close()
    else
        print("Error in Opening USB File")
    end
end

------------------------------------------------------------------------------------
--- THESE FUNCTIONS ARE INTENDED TO BE UTILIZED BY THE USER
------------------------------------------------------------------------------------
-- Start the test
function start_scan()
    delete_trigger_models()
    setup_smus()
    sync_measurements_trigger_timer()
    --sync_measurements_delay_constant()
end
-- Pause to export data to USB
function pause_export_resume()
    abort_trigger_models()
    delete_trigger_models()
    export_to_usb()
    setup_smus()
    sync_measurements_trigger_timer()
    --sync_measurements_delay_constant()
end
-- End the test
function end_scan()
    abort_trigger_models()
end

------------------------------------------------------------------------------------
--- CHANGE SCAN PARAMETERS
------------------------------------------------------------------------------------

slot_count = 1
vlevel = 5
ilimit = 100e-3
measure_interval = 20e-3
aperture = 10e-3

start_scan()
--pause_export_resume()
--end_scan()