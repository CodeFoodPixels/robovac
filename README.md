[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
<a href="https://www.buymeacoffee.com/bmccluskey" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
# Eufy RobovVac control for Home Assistant

A brand new version Eufy RoboVac integration for Home Assistant that includes a Config Flow to add your RoboVac(s) and the local key and ID required.  All you need to do is enter your Eufy app credentials and the Config Flow will look up the details for you. After the initial config use the configuration button on the Integration to enter the RoboVac IP address when prompted.

This work has evovled from the original work by Richard Mitchell https://github.com/mitchellrj and the countless others who have contributed over the last couple of years. It also builds on the work done by Andre Borie https://gitlab.com/Rjevski/eufy-device-id-and-local-key-grabber to get the required local ID and key.

This project has been forked many times since the  I am building upon the original work done by Richard and attempting to simplfy the operation and number of files involved.  

## Installation ##
Couple of Pre-reqs 
1. Make sure your Home Assistant Core is up to date
2. Remove any previous Eufy or RoboVac installation including entries in the configuration.yaml


If you want you can clone this repo manually, oterwise use HACS (Recommended).

### Using HACS
1. In HACS add this repo as an integration additional repository.
2. Then install it. 
3. Restart Home Assistant
4. Go to the Integrations Page and Click +Add Integration button
5. Search for Eufy Robovac and select it
6. Enter your Eufy username and password (The ones you use to login to the add with) and submit
7. If youve done it correctly you should get a success dialoge and option to enter an Area for each RoboVac you have
8. Click Finish
9. On the Integrations Screen Locate your Eufy Robovac card and click the configure button
10. Select the Radio button beside the Vacuum name and type its IP addess in the box and press Submit
(You need to repeat steps 9 and 10 for each RoboVac you have)
11. Enjoy

Please note: You may have to get a new version of the access key for your vacuum from time to time if Eufy change it. Worst case you have to Delete the integration and re add it to get the new key.

### Optional 1: Scripts

The integration is designed to work with the standard Home Assistant Lovelace card but that doesnt support all the options of your Robovac. I have created some scripts to send the relevant commands to the Robovac. 

Add the below text to your scripts.yaml file for a xxC RoboVAC. It should be in the same folder as your configuration.yaml
```
15c_smallroomclean:
  alias: 15C_smallRoomClean
  sequence:
  - service: vacuum.send_command
    data:
      command: smallRoomClean
    target:
      entity_id: vacuum.15c
  mode: single
15c_edgeclean:
  alias: 15C_edgeClean
  sequence:
  - service: vacuum.send_command
    data:
      command: edgeClean
    target:
      entity_id: vacuum.15c
  mode: single
15c_dock:
  alias: 15C_dock
  sequence:
  - service: vacuum.return_to_base
    target:
      entity_id: vacuum.15c
  mode: single
```
If you have a Gxx add this to your scripts.yaml
```
g30_autoclean:
  alias: G30_autoClean
  sequence:
  - service: vacuum.send_command
    data:
      command: autoClean
    target:
      entity_id: vacuum.g30
  mode: single
g30_autoreturn:
  alias: G30_autoReturn
  sequence:
  - service: vacuum.send_command
    data:
      command: autoReturn
    target:
      entity_id: vacuum.g30
  mode: single
g30_donotdisturb:
  alias: G30_do_Not_Disturb
  sequence:
  - service: vacuum.send_command
    data:
      command: doNotDisturb
    target:
      entity_id: vacuum.g30
  mode: single
g30_dock:
  alias: G30_dock
  sequence:
  - service: vacuum.return_to_base
    target:
      entity_id: vacuum.g30
  mode: single
```
If you have an X8 add this to your scripts.yaml
```
x8_boostiq:
  alias: x8_boostIQ
  sequence:
  - service: vacuum.send_command
    data:
      command: boostIQ
    target:
      entity_id: vacuum.x8
  mode: single
x8_autoclean:
  alias: x8_autoClean
  sequence:
  - service: vacuum.send_command
    data:
      command: autoClean
    target:
      entity_id: vacuum.x8
  mode: single
x8_autoreturn:
  alias: X8_autoReturn
  sequence:
  - service: vacuum.send_command
    data:
      command: autoReturn
    target:
      entity_id: vacuum.x8
  mode: single
x8_donotdisturb:
  alias: X8_do_Not_Disturb
  sequence:
  - service: vacuum.send_command
    data:
      command: doNotDisturb
    target:
      entity_id: vacuum.x8
  mode: single
x8_dock:
  alias: X8_dock
  sequence:
  - service: vacuum.return_to_base
    target:
      entity_id: vacuum.x8
  mode: single
```
The facilities in the script options above only work on the those model series. i.e. You cant do edge cleaning on the G30 and you cant do the autoreturn on the 15C.

### Optional 2 : Lovelace Card

Search in HACS for the Vacuum Card by Denys Dovhan and install it and configure it in lovelace to use you vacuum.  Note there is a minor "feature" in the vacuum card where it doesnt show the correct values in toolbar when they update and there is a template adjusting what is being displayed. A screen refresh shows the correct vaules.  Hopefully this will be fixed soon.

Edit the lovelace vaccum card and add the following to the cards yaml if you have a xxC.
```
type: custom:vacuum-card
entity: vacuum.15c
image: default
show_name: true
show_status: true
show_toolbar: true
shortcuts:
  - name: Dock
    service: script.15c_dock
    icon: mdi:home-map-marker
  - name: Edge Cleaning
    service: script.15c_edgeclean
    icon: mdi:square-outline
  - name: Small Room
    service: script.15c_smallroomclean
    icon: mdi:timer-cog-outline
```
Again if you have the Gxx you will add these lines to the cards yaml.
```
type: custom:vacuum-card
entity: vacuum.g30
image: default
shortcuts:
  - name: Dock
    service: script.g30_dock
    icon: mdi:home-map-marker
  - name: Auto Clean
    service: script.g30_autoclean
    icon: mdi:caps-lock
  - name: Auto Return
    service: script.g30_autoreturn
    icon: mdi:arrow-u-down-left-bold
  - name: Do Not Disturb
    service: script.g30_donotdisturb
    icon: mdi:volume-off
stats:
  default:
    - attribute: cleaning_area
      unit: sq meters
      subtitle: Cleaning Area
    - attribute: cleaning_time
      value_template: '{{ (value | float(0) / 60) | round(1) }}'
      unit: minutes
      subtitle: Cleaning time
    - attribute: auto_return
      subtitle: Auto Ret
      value_template: '{% if (value == true) %}On{% else %}Off{% endif %}'
    - attribute: do_not_disturb
      subtitle: Dnd
      value_template: '{% if (value == true) %}On{% else %}Off{% endif %}'
```
Again if you have the X8 you will add these lines to the cards yaml.
```
type: custom:vacuum-card
entity: vacuum.x8
image: default
stats:
  default:
    - attribute: cleaning_area
      unit: sq meters
      subtitle: Cleaning Area
    - attribute: cleaning_time
      value_template: '{{ (value | float(0) / 60) | round(1) }}'
      unit: minutes
      subtitle: Cleaning time
    - attribute: boost_iq
      subtitle: Boost IQ
      value_template: '{% if (value == true) %}On{% else %}Off{% endif %}'
    - attribute: auto_return
      subtitle: Auto Ret
      value_template: '{% if (value == true) %}On{% else %}Off{% endif %}'
    - attribute: do_not_disturb
      subtitle: Dnd
      value_template: '{% if (value == true) %}On{% else %}Off{% endif %}'
shortcuts:
  - name: Dock
    service: script.x8_dock
    icon: mdi:home-map-marker
  - name: Auto Clean
    service: script.x8_autoclean
    icon: mdi:caps-lock
  - name: Boost IQ
    service: script.x8_boostiq
    icon: mdi:bootstrap
  - name: Auto Return
    service: script.x8_autoreturn
    icon: mdi:arrow-u-down-left-bold
  - name: Do Not Disturb
    service: script.x8_donotdisturb
    icon: mdi:volume-off
```

## Debugging ##
I have left quite a few debug statements in the code and they may be useful to see whats happening by looking in the System Log files. The Log Viewer Addon available in the Home Assistance store can be very useful to watch the logs being updated in real time.  To get the debugging to add to the logs you need to add the below text to your configuration.yaml 
```
logger:
  default: warning
  logs:
    custom_components.robovac.vacuum: debug
    custom_components.robovac.tuya: debug
```
---


