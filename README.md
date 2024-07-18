# UVDOT (Node) Editor

This specific branch (`reformat`) is for @GirlInPurple to convert the entire project to the new UVDOT data format.\
This will be continuously worked on as I convert both the UVDOT router and this project over to the new format.\
An explaination of the uv-transit v2 migration [here](https://github.com/GirlInPurple/uv-transit/blob/node-port/technical.md#changes-in-2xx).\
No ETA, but within the next week.

The Editor for Methods, Nodes and Places for [uv-transit](https://github.com/GirlInPurple/uv-transit)
and [st-transports](https://github.com/Niklas20114552/st-transports).

## Installation

1. Clone the repository and navigate into the directory

   `git clone https://github.com/Niklas20114552/uvdot-editor && cd uvdot-editor`

2. **Optional but recommended:** (Only for linux) Make a venv

   `python3 -m venv uvdot-editor-venv && source uvdot-editor-venv/bin/activate`

3. Install the dependencies

   `pip3 install -r requirements.txt`

4. Run the application

   `python3 main.py`

## Feature list

- [ ] Method management
  - [ ] Get the checkbox for the `transfer?` option working
- [ ] Node management
- [ ] Places management
  - [ ] Get the data to display properly in the table again

- [ ] ST export mode
- [ ] ST export mode for UVDOT networks
- [ ] UVDOT export mode
  - [ ] Get this working, then ST and UVDOT -> ST exports

- [X] UVDOT import
- [X] ST import
  - These should continue working throughout the migration
