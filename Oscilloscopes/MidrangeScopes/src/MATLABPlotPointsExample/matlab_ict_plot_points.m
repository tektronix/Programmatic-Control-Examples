visa_brand = 'ni';
visa_address = 'TCPIP0::134.62.36.74::inst0::INSTR';
buffer = 20 * 1024; %20 KiB
record = 10000;

DpoMsoMdo = instrfind('Type', 'visa-tcpip', 'RsrcName', visa_address , 'Tag', '');

if isempty(DpoMsoMdo)
    DpoMsoMdo = visa(visa_brand, visa_address, 'InputBuffer', buffer, ...
    'OutputBuffer', buffer);
else
    fclose(DpoMsoMdo);
    DpoMsoMdo = DpoMsoMdo(1);
end

% Connect to instrument object
fopen(DpoMsoMdo);

%% Write
fwrite(DpoMsoMdo, 'VERBose 0');
fwrite(DpoMsoMdo, 'acq:state 0');
fwrite(DpoMsoMdo, 'head 0');
fwrite(DpoMsoMdo, 'acq:mod sam');
fwrite(DpoMsoMdo, 'hor:mode man');
fprintf(DpoMsoMdo, 'hor:reco %i', record);
fwrite(DpoMsoMdo, 'acq:state 1');
fwrite(DpoMsoMdo, 'curve?');

%% Read
fread(DpoMsoMdo, 1);
a = char(fread(DpoMsoMdo, 1));
bytes = char(fread(DpoMsoMdo, str2double(a))');
samples = zeros(record, 'int8');
samples = fread(DpoMsoMdo, record, 'int8');
fread(DpoMsoMdo, 1);

%% Close connection
fclose(DpoMsoMdo); 
delete(DpoMsoMdo); 
clear DpoMsoMdo; 

% plot samples
plot(samples);


