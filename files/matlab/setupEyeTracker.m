function [el, exit_flag] = setupEyeTracker( tracker, window, constants )
% SET UP TRACKER CONFIGURATION


%%
exit_flag = 'OK';

switch tracker
    
    case 'T60'
        % Provide Eyelink with details about the graphics environment
        % and perform some initializations. The information is returned
        % in a structure that also contains useful defaults
        % and control codes (e.g. tracker state bit and Eyelink key values).
        el = EyelinkInitDefaults(window.pointer);
        
        % overrride default gray background of eyelink, otherwise runs end
        % up gray! also, probably best to calibrate with same colors of
        % background / stimuli as participant will encounter
        el.backgroundcolour = window.background;
        el.foregroundcolour = window.white;
        el.msgfontcolour = window.white;
        el.imgtitlecolour = window.white;
        el.calibrationtargetcolour=[window.white window.white window.white];
        EyelinkUpdateDefaults(el);
        
        if ~EyelinkInit(0, 1)
            fprintf('\n Eyelink Init aborted \n');
            exit_flag = 'ESC';
            return;
        end
        
        %Reduce FOV
        Eyelink('command','calibration_area_proportion = 0.5 0.5');
        Eyelink('command','validation_area_proportion = 0.48 0.48');
        
        % open file to record data to
        i = Eyelink('Openfile', constants.eyelink_data_fname);
        if i ~= 0
            fprintf('\n Cannot create EDF file \n');
            exit_flag = 'ESC';
            return;
        end
        
        Eyelink('command', 'add_file_preamble_text ''Recorded by VTF''');
        
        % Setting the proper recording resolution, proper calibration type,
        % as well as the data file content;
        Eyelink('command','screen_pixel_coords = %ld %ld %ld %ld', 0, 0, window.winRect(3)-1, window.winRect(4)-1);
        Eyelink('message', 'DISPLAY_COORDS %ld %ld %ld %ld', 0, 0, window.winRect(3)-1, window.winRect(4)-1);
        % set calibration type.
        Eyelink('command', 'calibration_type = HV5');
        
        % set EDF file contents using the file_sample_data and
        % file-event_filter commands
        % set link data thtough link_sample_data and link_event_filter
        Eyelink('command', 'file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT');
        Eyelink('command', 'link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT');
        
        % check the software version
        % add "HTARGET" to record possible target data for EyeLink Remote
        Eyelink('command', 'file_sample_data  = LEFT,RIGHT,GAZE,HREF,GAZERES,AREA,HTARGET,STATUS,INPUT');
        Eyelink('command', 'link_sample_data  = LEFT,RIGHT,GAZE,HREF,GAZERES,AREA,HTARGET,STATUS,INPUT');
        
        % make sure we're still connected.
        if Eyelink('IsConnected')~=1 && input.dummymode == 0
            exit_flag = 'ESC';
            return;
        end
        
        %% possible changes from EyelinkPictureCustomCalibration
        
        % set sample rate in camera setup screen
        Eyelink('command', 'sample_rate = %d', 1000);
        
        
        %%
        EyelinkDoTrackerSetup(el);
        
        
    case 'none'
        el = [];
end

end
