function eyelinkFcn = makeEyelinkFcn(handlerName)
%{
TODO: add eyetracking event tags

%}


valid_types = {'none','T60'};
assert(ismember(handlerName, valid_types),...
    ['"handlerType" argument must be one of the following: ' strjoin(valid_types,', ')])

switch handlerName
    case 'T60'
        eyelinkFcn = @T60;
    case 'none'
        eyelinkFcn = @do_nothing;
end

    function status = T60(varargin)
        status = [];
        switch varargin{1}
            case 'EyelinkDoDriftCorrection'
                % Do a drift correction at the beginning of each trial
                % Performing drift correction (checking) is optional for
                % EyeLink 1000 eye trackers.
                EyelinkDoDriftCorrection(varargin{2},[],[],0);
                
            case 'Command'
                Eyelink('Command', varargin{2})
                
            case 'ImageTransfer'
                %transfer image to host
                transferimginfo = imfinfo(varargin{2});
                [width, height] = Screen('WindowSize', 0);
                
                % image file should be 24bit or 32bit b5itmap
                % parameters of ImageTransfer:
                % imagePath, xPosition, yPosition, width, height, trackerXPosition, trackerYPosition, xferoptions
                transferStatus =  Eyelink('ImageTransfer',transferimginfo.Filename,...
                    0, 0, transferimginfo.Width, transferimginfo.Height, ...
                    width/2-transferimginfo.Width/2 ,height/2-transferimginfo.Height/2, 1);
                if transferStatus ~= 0
                    fprintf('*****Image transfer Failed*****-------\n');
                end
                
            case 'StartRecording'
                Eyelink('StartRecording');
                
            case 'Message'
                if nargin == 2
                    Eyelink('Message', varargin{2});
                elseif nargin == 3
                    Eyelink('Message', varargin{2}, varargin{3});
                elseif nargin == 4
                    Eyelink('Message', varargin{2}, varargin{3}, varargin{4});
                end
            case 'StopRecording'
                Eyelink('StopRecording');
            case 'CloseFile'
                Eyelink('CloseFile');
            case 'ReceiveFile'
                Eyelink('ReceiveFile');
            case 'EyeAvailable'
                status = Eyelink('EyeAvailable');
        end
        
    end

    function do_nothing(varargin)
        % do nothing with arguments
    end


end