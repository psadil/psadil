function [ flut, stim, el ] = ...
    runExpt( input, constants, window, eyetrackerFcn )

%{
Main experiment
 
    %}
    
    % show initial prompt. Timing not super critical (may be source of missed flip)
    showPrompt(window, 'Initializing...', false);
    
    keys = setupKeys(input.fMRI);
    responseHandler = makeInputHandlerFcn(input.responder, constants, keys);
    stim = setupStim( window, input);
    flut = setupFLUT( constants, input );
    
    % Draw a stim once, just to make sure the gfx-hardware is ready for the
    % benchmark run below and doesn't do one time setup work during the
    % main experiment. (still often misses very first flip)
    stim.drawStim(0, 1, 0, 'on');
    Screen('Flip', window.pointer);
    
    
    [el, exitflag] = setupEyeTracker( input.tracker, window, constants );
    if strcmp(exitflag, 'ESC')
        return;
    end
    %%
    
    [triggerSent, exitflag] = startup(window, eyetrackerFcn, responseHandler);
    
    switch exitflag{1}
        case 'ESCAPE'
            cleanup(eyetrackerFcn);
            return;
        otherwise
            % mark zero-plot time in data file
            eyetrackerFcn('message', 'SYNCTIME');
    end
    
    %% start flipping stims (most events happen here)
    for flip = 1:length(flut.flip_grand)
        
        % see setupStim for def
        stim.drawStim(flut.contrast_scale(flip), flut.stim(flip,:), flut.orientation(flip,:), flut.block_type(flip,:));
        
        switch input.task
            case 'unattended'
             %determine whether to draw letter or fixation from flut
                if ~ismissing(flut.letter_seq(flip))
                    stim.drawLetter(flut.letter_seq(flip));
                else
                    stim.drawFixation(1);
                end
            case 'attended'
                %always draw fixation
                    stim.drawFixation(1);
        end
        
        % signal that no more drawing will occur on this flip and let gpu
        % get to work. meanwhile, handle other business before flipping
        Screen('DrawingFinished', window.pointer);
        
            % calculate when next flip should occur, adjusted for monitor refresh rate
        if flip == 1
            % after trigger is sent, try to flip on next refresh cycle. All
            % subsequent flips will be based on this event
            flip_when = triggerSent + (1 - window.slack) * window.ifi;
        else
            % how many refresh cycles could the last event have occured
            % for?
            cycles_in_event = flut.duration(flip-1) / window.ifi;
            
            % adjust time based on small slack (stored since start of
            % experiment)
            flip_schedule_offset = (cycles_in_event - window.slack) * window.ifi;
            
            % next flip should happen the adjusted amount of time after
            % last flip (stored in computer time)
            flip_when = flut.vbl(flip - 1) + flip_schedule_offset;
        end
        
        % when there is going to be a long time before next flip, set
        % duration going to check for escapes. The - 1.4 accomplishes
        % allowance of a bit of time right before flip should happen,
        % should be enough for drawing to occur prior to flip. Note that
        % this does mean escape key will only be registered in longish (>1.4s)
        % periods without a flip. E.g., won't capture esc between each of
        % the stims, only during iti
        duration = max([0, flut.duration(flip) - 1.4]);
        
        [flut.vbl(flip), flut.stimulus_onset_time(flip), ...
            flut.flip_timestamp(flip), flut.missed(flip), flut.beampos(flip)] = ...
            Screen('Flip', window.pointer, flip_when);
        
        % wait for iti (or whatever is time before next flip)
        esc = responseHandler.checkEsc(duration, responseHandler.main);
        if esc
            break;
        end
        
    end
    
    cleanup(eyetrackerFcn);
    
    % ensure that very final flip stays on the screen for the expected
    % duration
    WaitSecs(GetSecs - flut.vbl(flip) + flut.duration(flip));
end


function[triggerSent, exitflag] = startup(window, eyetrackerFcn, responseHandler)

% Must be offline to draw to EyeLink screen
eyetrackerFcn('Command', 'set_idle_mode');

% clear tracker display and draw background img to host pc
eyetrackerFcn('Command', 'clear_screen 0');

% image file should be 24bit or 32bit bitmap
% parameters of ImageTransfer:
% imagePath, xPosition, yPosition, width, height, trackerXPosition, trackerYPosition, xferoptions
% VERY SLOW. Should only be done when not recording
% eyetrackerFcn('ImageTransfer', stim.background_img_filename);

eyetrackerFcn('StartRecording');

% always wait a moment for recording to definitely start
WaitSecs(0.1);


% show initial prompt. Timing not super critical with this one
showPrompt(window, 'Attend to the + in the center', 1);

% trigger sent isn't used until way later, when we're trying to show
% stimuli
[triggerSent, exitflag] = responseHandler.waitForStart(responseHandler.main);

end

function cleanup(eyetrackerFcn)

eyetrackerFcn('Command', 'set_idle_mode');

end

