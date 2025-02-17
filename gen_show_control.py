import os

f = open("midi_fader_sc_lists.csv", "w")

start_string = "START_SHOWCONTROL\nTARGET_TYPE,TARGET_TYPE_AS_TEXT,TARGET_LIST_NUMBER,TARGET_ID,PART_NUMBER,LABEL,TIME_ADDRESS,DATE,TRIGGER,ACTION\n28,Event,1,0,5,,,,Source 1 External,Network\n28,Event,1,1,5,Sub 9 Remote,,,sACN:  409,Sub  9 \n"
end_string = "END_SHOWCONTROL\n"

f.write(start_string)

def format_02x(val):
    return format(val, '02x').upper()

def setup_korg_nktrl2(event_lists, subs, channel):

    controllers = list(range(8)) + list(range(0x10, 0x18))

    button_names = [
        "S Button HIGH",
        "S Button LOW",
        "M Button HIGH",
        "M Button LOW",
        "R Button HIGH",
        "R Button LOW" 
    ]   
    button_controllers = [0x20, 0x20, 0x30, 0x30, 0x40, 0x40]
    button_data = [0x7F, 0x00, 0x7F, 0x00, 0x7F, 0x00]

    for idx in range(len(event_lists)):
        event_list = event_lists[idx]
        sub = subs[idx]
        target = f"Sub  {sub}"
        controller = controllers[idx]
        controller_hex = format_02x(controller % 128)
        f.write(f"28,Event,{event_list},0,5,,,,Source 1 External,Network\n")
        for data in range(1, 129):
            data_hex = format_02x(data % 128)
            event = data
            f.write(f"28,Event,{event_list},{event},5,Fader Level 0x{data_hex},,,MIDI: B{channel} {controller_hex} {data_hex},{target}\n")
        buttons = [4, 5] if idx < 8 else [0, 1]
        for button in buttons:
            button_controller = button_controllers[button] + controller%8
            button_controller_hex = format_02x(button_controller)
            data_hex = format_02x(button_data[button])
            button_name = button_names[button]
            f.write(f"28,Event,{event_list},{129+button%2},5,{button_name},,,MIDI: B{channel} {button_controller_hex} {data_hex},{target}\n")

event_lists_0 = list(range(41,49)) + list(range(51,59))
subs_0 = event_lists_0

setup_korg_nktrl2(event_lists_0, subs_0, 0)

event_lists_1 = list(range(61,69)) + list(range(71,79))
subs_1 = event_lists_1

setup_korg_nktrl2(event_lists_1, subs_1, 1)


# SETUP MATRIX

def square_to_grid(index):
    return index//8+1, index%8+1

def square_to_event_list(square):
    rank, file = square_to_grid(square)
    return 800+10*rank+file

def square_to_target(square):
    rank, file = square_to_grid(square)
    return f"Macro {8000+10*rank+file}"

def square_to_controller(square):
    rank, file = square_to_grid(square)
    return 0x24 + 0x20*((file-1)//4) + (rank-1)*4 + (file-1)%4

# for square in range(64):
#     if square % 8 == 0:
#         print("\n")
#     print(f"{format(square_to_controller(square),'02x')}", end = " ")

for square in range(64):
    event_list = square_to_event_list(square)
    f.write(f"28,Event,{event_list},0,5,,,,Source 1 External,Network\n")
    controller = square_to_controller(square)
    controller_hex = format_02x(controller)
    target = square_to_target(square)
    for data in range(1, 129):
        data_hex = format_02x(data % 128)
        event = data
        f.write(f"28,Event,{event_list},{event},5,Velocity 0x{data_hex},,,MIDI: 90 {controller_hex} {data_hex},{target} \n")
    f.write(f"28,Event,{event_list},129,5,Release,,,MIDI: 80 {controller_hex} 00, \n")

f.write(end_string)