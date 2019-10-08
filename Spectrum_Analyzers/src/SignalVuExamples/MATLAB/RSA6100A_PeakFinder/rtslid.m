function h = rtslid(fig,f,hh,varargin)

%RTSLID Slider widget that responds to dragging realtime
%
%       h2 = RTSLID(h,@Fcn,h3) places a slider on the figure
%       with handle h, and returns the handle to the slider
%       in h2.  The second argument is a pointer to a
%       function that takes a two input arguments, which
%       should be the function you wish to be responding to
%       changes in the slider position.  The first of these
%       input arguments will be a number between 0 and 1
%       (if using the default scale) that corresponds to the
%       slider vertical position, while the second is the
%       handle of the axes to that responds to the slider
%       movement (as a result of Fnc). This handle should be
%       passed to RTSLID as the third input argument h3.
%
%       Alternatively instead of passing a function handle
%       as the second argument, a set of commands can be
%       passed as a string.  In order to use the slider
%       output value in such a set of commands, the lower
%       case variable 'out' should be used which contains
%       this number (Look at bottom of DEMO1.m for example).
%
%       h2 = RTSLID(h,@fcn,h3,style) allows the user to
%       specify the style of the slider by including an
%       optional third input argument.
%       The different styles affect the slider's response
%       to mouse movement, and are:
%
%               0 - (Default) Jumps to the mouse pointer
%                   on click, and locks to the mouse on drag.
%               1 - Only moves with mouse drags.
%
%       Additional parameters are passed as parameter pairs,
%       ie. rtslid(h,@fcn,h3,'param1',v1,'param2',v2,'...).
%       Inclusion of the fourth argument 'style' is optional.
%       These parameter names are listed below (all parameter
%       names are case insensitive) and all are optional:
%
%               'POSITION'  -   Control the position and size
%                               of the slider by passing a
%                               four element vector in the
%                               range [0 to 1] as a multiple
%                               of current figure size.
%                               Use [x y width height].
%                               {Default: [0.03 0.1 0.03 0.8]}
%               'BACK'      -   Either a string of the name
%                               of a valid colormap, or a 3-
%                               element RGB vector in the
%                               range [0 to 1].
%                               {Default: 'jet'}
%               'SCALE'     -   A two element vector of the
%                               lower and upper output limits
%                               for the slider.
%                               {Default: [0 1]}
%               'LABEL'     -   A string for the slider label.
%                               {Default: ''}
%               'DEF'       -   A default initial value (with
%                               respect to the SCALE), although
%                               does not cause output.
%                               {Default: 0.5}
%               'BUTMOT'    -   Additional mouse callback for
%                               WindowButtonMotionFcn of the
%                               slider figure, to allow other
%                               processes to use this callback.
%                               {Default: ''}
%               'MOUSEDOWN' -   Additional mouse callback for
%                               WindowButtonDownFcn of the
%                               slider figure, to allow other
%                               processes to use this callback.
%                               {Default: ''}
%               'MOUSEUP'   -   Additional mouse callback for
%                               WindowButtonDownFcn of the
%                               slider figure, to allow other
%                               processes to use this callback.
%                               {Default: ''}
%
%   matthew jones (matt_jones@fastmail.fm), 2004

DEFstyle = 0;
DEFback = 'jet';
DEFscale = [0 1];
DEFlabel = '';
DEFdef = 0.5;

style = DEFstyle;
back = DEFback;
scale = DEFscale;
label = DEFlabel;
def = DEFdef;

butmot = '';
mousedown = '';
mouseup = '';

if nargin>3,    % Set the style and any other parameters
    [style,args] = parseparams(varargin);
    if (length(style)==0),
        style = 0;
    else
        style = style{1};
    end
    try
        for l=1:(length(args)/2),
            inparam = args((l*2)-1);
            switch upper(inparam{1}),
            case 'POSITION' % Adjust the size and position of slider
                inparam = args(l*2);
                pos = inparam{1};
            case 'BACK'     % Change the background colour
                inparam = args(l*2);
                back = inparam{1};
            case 'SCALE'    % Change the output scale limits
                inparam = args(l*2);
                scale = inparam{1};
            case 'LABEL'    % Give the slider a label
                inparam = args(l*2);
                label = inparam{1};
            case 'DEF'      % Set the initial position
                inparam = args(l*2);
                def = inparam{1};
            case 'BUTMOT'   % Add extra WindowButtonMotionFcn commands
                inparam = args(l*2);
                butmot = inparam{1};
            case 'MOUSEDOWN'   % Add extra WindowButtonDownFcn commands
                inparam = args(l*2);
                mousedown = inparam{1};
            case 'MOUSEUP'   % Add extra WindowButtonUpFcn commands
                inparam = args(l*2);
                mouseup = inparam{1};
            end
        end
    catch
        error('Incorrect input arguments!');
    end
end

def2 = (def-scale(1))*(1000/(scale(2)-scale(1)));   % The initial position now in range [0 1000]

figure(fig);
params.fig = fig;   % Set so that focus returns to slider figure ofter plotting
params.butmot = butmot;
params.mousedown = mousedown;
params.mouseup = mouseup;

params2 = get(fig,'UserData');
if (length(params2)==0),    % If there are no sliders already,
                            % initialise the first elements of 'params'.
                            
    if exist('pos'),        % Draw the slider on its own axes
        h = axes('Position',pos);
    else
        h = axes('Position',[0.03 0.1 0.03 0.8]);
    end

	if ischar(back),        % Any string wll cause the background to be 'jet'
        try
            eval(['colormap(''',back,''');']);
        catch
            error('If passing a string for background, string must be valid colormap!');
        end
        back = repmat(linspace(0,1,1000).',[1,10]);
        imagesc(back);
    else                    % Or construct an RGB matrix m for the background
        m = ones(1000,10,3);
        for l=1:3,
            m(:,:,l) = back(l)*m(:,:,l);
        end
        image(m);
    end
            
	title(label);
    
    % Make the slider look nice
    set(h,'XTick',[],'XTickLabel','','YTick',[],'YTickLabel','','YDir','normal','LineWidth',2);
	set(fig,'DoubleBuffer','on');   % Double buffering required for smooth display

    % Draw the small black box that indicates current position
    ind = patch([0 0 10 10],[def2-20 def2+20 def2+20 def2-20],[0.25 0.25 0.25]);axis tight;

	params.mdown = 0;   % Initialise mousedown state
	params.ind = ind;   % Save the handle to the position indicator
	params.funhand{1} = f;  % Save the function handle or string
	params.h = h;       % Save the handle to this slider
	params.h2 = hh;     % Save the handle to the plotting axes (for this slider)
    if exist('scale'),  % Set the output limits
        params.scale{1} = scale;
    else
        params.scale{1} = DEFscale;
    end
    params.noslids = 1; % Keep tab of how many sliders in this figure
else
    if (params2.noslids<8), % If there is one or more sliders on this figure (and less
                            % than an upper limit), concatenate fields of 'params'
        params.noslids = params2.noslids+1; % Keep tab of how many sliders in this figure
        if exist('pos'),    % Draw the slider on its own axes
            h = axes('Position',pos);
        else
            h = axes('Position',[(((params.noslids-1)*0.06)+0.03) 0.1 0.03 0.8]);
        end
        
        if ischar(back),    % Any string wll cause the background to be 'jet'
            back = repmat(linspace(0,1,1000).',[1,10]);
            imagesc(back);
        else                % Or construct an RGB matrix m for the background
            m = ones(1000,10,3);
            for l=1:3,
                m(:,:,l) = back(l)*m(:,:,l);
            end
            image(m);
        end
    
        title(label);
        
        % Make the slider look nice
        set(h,'XTick',[],'XTickLabel','','YTick',[],'YTickLabel','','YDir','normal','LineWidth',2);
		set(fig,'DoubleBuffer','on');
	
        % Draw the small black box that indicates current position
        ind = patch([0 0 10 10],[def2-20 def2+20 def2+20 def2-20],[0.25 0.25 0.25]);axis tight;
 
        % Copy old parameters and concatenate new values
        params.mdown = [params2.mdown 0];   % Initialise new mousedown state
		params.ind = [params2.ind ind];     % Save the handle to the position indicator
		params.funhand = params2.funhand;   % Save the function handle or string
        params.funhand{params.noslids} = f;
		params.h = [params2.h h];           % Save the handle to this slider
		params.h2 = [params2.h2 hh];        % Save the handle to the plotting axes (for this slider)
        for l=1:(params.noslids-1),
            params.scale{l} = params2.scale{l};
        end
        if exist('scale'),  % Set the output limits
            params.scale{params.noslids} = scale;
        else
            params.scale{params.noslids} = DEFscale;
        end
        params.style = params2.style;       % Copy list of slider styles
        params.motfcn = params2.motfcn;     % Copy the WindowButtonMotionFcn list
        params.current = params2.current;   % Copy the 'current' slider positions
    end

end

if (style==0),
    params.style(params.noslids) = 0;               % Set the slider style
    params.motfcn{params.noslids} = {@butmotfcn0};  % Set the corresponding WindowButtonMotionFcn
else
    params.style(params.noslids) = 1;               % Set the slider style
    params.current(params.noslids) = def2;          % Initialise slider position (only required for style 1)
    params.motfcn{params.noslids} = {@butmotfcn1};  % Set the corresponding WindowButtonMotionFcn
end

% Now save these params and set the figure's mouse callback functions
set(fig,'UserData',params,'WindowButtonDownFcn',{@butdownfcn},'WindowButtonUpFcn',{@butupfcn});


% Callback functions defined here to keep any variables created
% localto these functions.
%------------------------------------------------------------------------%
function butdownfcn(in,varargin)

params=get(gcf,'UserData');     % Get current parameters
for l=1:params.noslids,
    p=get(params.h(l),'CurrentPoint');
    if ((p(1)>0) & (p(1)<10.7) & (p(3)>0) & (p(3)<1000)),   % Find out if mouse is on slider l
        params.mdown(l)=1;                                  % Set slider MouseDown sate to 1
        if (params.style(l)==0),                            % If jump-to-click style, use new
            params.old=p(3);                                % mouse position as output
            params.current(l)=p(3);                         % Save current position
            set(params.ind(l),'YData',[p(3)-20 p(3)+20 p(3)+20 p(3)-20]);   % Update indicator
            scal=params.scale{l};
            out=(p(3)*(scal(2)-scal(1))/1000);              % Convert output to desired scale
            out=out+scal(1);
        else                                                % Else use old position for output
            scal=params.scale{l};
            out=(params.current(l)*(scal(2)-scal(1))/1000); % Convert output to desired scale
            out=out+scal(1);
            params.old=p(3);
        end
        axes(params.h2(l));
        if ischar(params.funhand{l}),                       % If passed string as function
            eval(params.funhand{l});                        % evaluate using eval()
        else                                                % Else if passed function handle
            feval(params.funhand{l},out,params.h2(l));      % evaluate using feval()
        end
        figure(params.fig);
        set(gcf,'UserData',params,'WindowButtonMotionFcn',params.motfcn{l});    % Save new params and
    end;                                                                        % activate slider's Motion Function
end
if (length(params.mousedown)>0),    % If additional MouseDown parameters passed,
    eval(params.mousedown);         % evaluate these too.
end


%------------------------------------------------------------------------%
function butupfcn(in,varargin)

params=get(gcf,'UserData'); % Get old parameters
for l=1:params.noslids,
     params.mdown(l) = 0;   % Set ALL slider MouseDown states to zero
end
set(gcf,'UserData',params); % Save these new states

if (length(params.butmot)==0),  % If no additional ButMot commands passed,
    set(gcf,'WindowButtonMotionFcn','');    % Clear figure WindowButtonMotionFcn
else                            % Otherwise set it to these extra commands
    set(gcf,'WindowButtonMotionFcn',params.butmot);
end
    
if (length(params.mouseup)>0),  % Evaluate any additional MouseUp commands passed
    eval(params.mouseup);
end


%------------------------------------------------------------------------%
function butmotfcn0(in,varargin)
% Mouse motion function for style 0 (only active during mouse press)

params = get(gcf,'UserData'); % Get the saved parameters
for l=1:params.noslids,
   if (params.mdown(l)),
       p = get(params.h(l),'CurrentPoint');   % Get mouse position relative to the slider axis
       p = p(3);                              % Jump to mouse position
       p = max([0 min([1000 p])]);            % Constrain position
       if (abs(params.old-p)>0),            % Only act if mouse has moved
           scal = params.scale{l};            % Get the lower and upper limits
           out = (p*(scal(2)-scal(1))/1000);  % Convert from [0 to 1000] to new scale
           out = out+scal(1);
           axes(params.h2(l));              % Avoid plotting on the slider axis
           if ischar(params.funhand{l}),    % If string passed as function
               eval(params.funhand{l});     % Evaluate the string
           else                             % Else if function handle passed
               feval(params.funhand{l},out,params.h2(l));   % Perform function
           end
           set(params.ind(l),'YData',[p-20 p+20 p+20 p-20]);% Update position indicator
           figure(params.fig);              % Make sure focus returns to slider after plotting
       end
   end
end
params.old = p;             % Save old mouse position (vertical only)
set(gcf,'UserData',params); % Save all parameters
if (length(params.butmot)>0),   % Evaluate any extra ButMot functions passed to rtslid
    eval(params.butmot);
end


%------------------------------------------------------------------------%
function butmotfcn1(in,varargin)
% Mouse motion function for style 1 (only active during mouse press)

params = get(gcf,'UserData'); % Get the saved parameters
for l=1:params.noslids,
	if (params.mdown(l)),                       % If mouse was clicked on slider l
		p = get(params.h(l),'CurrentPoint');    % Get mouse position relative to the slider axis
		dy = p(3)-params.old;                   % Calculate change in mouse position
		if (abs(dy)>0),                         % If mouse has moved
			p2 = params.current(l)+dy;          % Find new slider position
			params.old = p(3);                  % Save this new mouse position
			p2=max([0 min([1000 p2])]);         % Constrain position
			params.current(l) = p2;             % Save current slider position
			scal = params.scale{l};             % Get the lower and upper limits
			out = (p2*(scal(2)-scal(1))/1000);  % Convert from [0 to 1000] to new scale
			out = out+scal(1);
			axes(params.h2(l));                 % Avoid plotting on the slider axis
			if ischar(params.funhand{l}),       % If string passed as function
			    eval(params.funhand{l});        % Evaluate the string
			else                                % Else if function handle passed
			    feval(params.funhand{l},out,params.h2(l));  % Perform function
			end
			set(params.ind(l),'YData',[p2-20 p2+20 p2+20 p2-20]);% Update position indicator
			figure(params.fig);                 % Make sure focus returns to slider after plotting
		end
	end
	set(gcf,'UserData',params); % Save all parameters
end
if (length(params.butmot)>0),   % Evaluate any extra ButMot functions passed to rtslid
    eval(params.butmot);
end