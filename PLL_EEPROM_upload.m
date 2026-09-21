%PLL arduino
% Uploads a binary file to program the eeprom and checks for the correct
% upload
%November 13, 2025

%% Read a binary file 

file = dir("\path\to\your\bin\file"); 

%%
d = 0:1279; %creates array 
f1 = fullfile(file.folder,file.name); %assign file data to variable
f2 = fopen(f1); %opens file
d = fread(f2,size(d),'uint8=>uint8'); %reads data from file into array
checksum_before = sum(d);  %checksum of the file
fprintf("Checksum before: %d\n", checksum_before)

fclose(f2); %closes file

%% Program the EEPROM
%open the arduino com port
device = serialport('COMX',9600); %identify port

pause(1);

% clear any text sent by the device
% read(device, device.NumBytesAvailable, 'char');
fprintf('\n');
fprintf("Writing data to device...\r\n")

%TODO:  send a command to indicate programming mode!!!!
writeline(device, "program") %wite data to eeprom

%write our bin file
write(device, d,"uint8"); %write data to eeprom

%% Read the uploaded data
d2 = read(device,100000,"char"); %reads all data in bus
d3 = split(d2,'kHz'); %finds where last printed from set up
d3 = d3{end}; %pulls last cell from cell array
d3 = split(d3,' '); %finds spaces inbetween wanted data and separates it
d3 = str2double(d3(1:length(d))); %converts string to numbers

%% Check for the correct upload 
checksum_after = sum(d3); %computes checksum
fprintf("Checksum after: %d\n",checksum_after)

fprintf('\n');
fprintf("Comparing checksum...")

if checksum_before == checksum_after
    fprintf('\nChecksum of file matches uploaded data.\n')
else
    fprintf('\nCHECKSUM ERROR\n')
end

device = 0; %closes port