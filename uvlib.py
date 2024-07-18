import json
import re

from chompjs import parse_js_object

class NetworkFiles:
    def __init__(self):
        self.network_files: dict = {}
        self.st_mode: bool = False

    def get_traveltimes(self, stations: list[str], st_string: dict) -> int:
        stations.sort()
        for time in st_string['traveltimes']:
            if time['start'] == stations[0] and time['end'] == stations[1]:
                return time['time']
        return 0

    def get_nextstation(self, line: str, cstation: str, st_string: dict) -> str:
        for lines in st_string['lines']:
            if lines['name'] == line:
                if not lines['stations'].index(cstation) + 1 == len(lines['stations']):
                    return lines['stations'][lines['stations'].index(cstation) + 1]

    def replace_ust(self, string: str):
        return string.replace('UltraStar express', 'USTe').replace('UltraStar', 'UST')

    def replace_ultrastar(self, string: str):
        return string.replace('USTe', 'UltraStar express').replace('UST', 'UltraStar')

    def convert_st_uvdot(self, st_string: dict) -> tuple:
        print('[D> Converting ST Network...')
        lines = {}
        routes = {}

        for station in st_string['stations']:
            routes[station['name']] = [['CHANGE-ME', 'CHANGE-ME'], {'railways': {}}]
            for line in station['lines']:
                next_station = self.get_nextstation(line['name'], station['name'], st_string)
                if next_station:
                    stations = [station['name'], next_station]
                    routes[station['name']][1]['railways'][next_station] = [
                        [self.replace_ultrastar(line['name'])],
                        self.get_traveltimes(stations, st_string) * 8,
                        {'currency': 'Emerald', 'price': 4, 'pass': 'SeaCard', 'passPrice': 2}]

        for line in st_string['lines']:
            if line['name'].startswith('USTe'):
                lines[line['name']] = {'color': ['#066b5f', 'white']}
            else:
                lines[line['name']] = {'color': ['#6b006b', 'white']}
            lines[line['name']]['operator'] = 'Seacrestica Transports Outpost'

        return lines, routes

    def process_file(self, inputstr: str):
        self.network_files: dict = {}
        pattern = re.compile(
            r'(?:const|let|var) (network|places|lines|routes|transfers) = ([{\[](?:[^;]|\n)*[}\]]);$',
            re.MULTILINE)

        matches = re.finditer(pattern, inputstr)
        for match in matches:
            self.network_files[match.groups()[0]] = parse_js_object(match.groups()[1])
            if match.groups()[0] == 'network':
                print('[D> ST Network detected')
                self.network_files['lines'], self.network_files['routes'] = self.convert_st_uvdot(parse_js_object(match.groups()[1]))
                self.st_mode = True
            else:
                print(f'[D> UVDOT Network detected ({match.groups()[0]})')
                self.st_mode = False

    def replace_dict_entry_at_index(self, d: dict, index: int, new_key: str, new_value: str) -> dict:
        items = list(d.items())
        items[index] = (new_key, new_value)
        return dict(items)

    def rename_place(self, old_name: str, new_name: str, index: int):
        self.network_files['routes'] = self.replace_dict_entry_at_index(self.network_files['routes'], index, new_name,
                                                                        self.network_files['routes'][old_name])

    def remove_place(self, index: int):
        self.network_files['routes'].pop(tuple(self.network_files['routes'].keys())[index])

    def rename_method(self, old_name: str, new_name: str, index: int):
        self.network_files['lines'] = self.replace_dict_entry_at_index(self.network_files['lines'],
                                                                                index, new_name,
                                                                                self.network_files['lines'][
                                                                                    old_name])

    def remove_method(self, index: int):
        self.network_files['lines'].pop(tuple(self.network_files['lines'].keys())[index])

    def add_place(self, name: str, loc: str):
        self.network_files['routes'][name] = loc

    def add_method(self, name: str, bg: str, fg: str, op: str):
        self.network_files['lines'][name] = {'color': [bg, fg], 'operator': op}

    def get_method_by_index(self, index: int) -> str:
        return tuple(self.network_files['lines'].keys())[index]

    def get_place_by_index(self, index: int) -> str:
        return tuple(self.network_files['routes'].keys())[index]

    def set_index_place(self, index: str, val: str):
        self.network_files['routes'][index] = val

    def get_index_place(self, index: str) -> str:
        return self.network_files['routes'][index]

    def get_place_len(self) -> int:
        return len(self.network_files['routes'])

    def get_methods_len(self) -> int:
        return len(self.network_files['lines'])

    def get_places(self) -> dict:
        return self.network_files['routes']

    def get_methods(self) -> dict:
        return self.network_files['lines']

    def is_valid_network(self) -> bool:
        return ('routes' and 'lines') or 'network' in self.network_files

    def get_location_place(self, name: str) -> str:
        return self.network_files['routes'][name]
    
    def reset_network(self):
        self.network_files['lines'] = {}
        self.network_files['routes'] = {}

    def set_method_bg_color(self, name: str, value: str):
        self.network_files['lines'][name]['color'][0] = value

    def get_method_bg_color(self, name: str) -> str:
        return self.network_files['lines'][name]['color'][0]

    def set_method_fg_color(self, name: str, value: str):
        self.network_files['lines'][name]['color'][1] = value

    def get_method_fg_color(self, name: str) -> str:
        return self.network_files['lines'][name]['color'][1]

    def get_method_op(self, name: str) -> str:
        return self.network_files['lines'][name]['operator']

    def set_method_op(self, name: str, value: str):
        self.network_files['lines'][name]['operator'] = value

    def get_method_alt_name(self, name: str) -> str:
        try:
            return self.network_files['lines'][name]['altName']
        except Exception as _:
            return ""
    
    def set_method_alt_name(self, name: str, value: str):
        self.network_files['lines'][name]['altName'] = value
    
    def is_method_transfer(self, name: str) -> bool:
        try:
            return self.network_files['lines'][name]['transfer']
        except Exception as _:
            return False
    
    def set_method_transfer(self, name: str, value: bool) -> None:
        self.network_files['lines'][name]['transfer'] = value
    
    def create_export(self) -> str:
        export = ''

        for file in self.network_files:
            export += f'export const {file} = {json.dumps(self.network_files[file])};\n\n'
        export.removesuffix('\n')
        return export

    def convert_uvdot_st(self, uvdot_str: dict) -> dict:
        network = {'lines': [], 'stations': [], 'doublelines': [], 'traveltimes': []}
        lines = {}
        stations = []
        
        for route in uvdot_str['routes']:
            if 'railways' in uvdot_str['routes'][route][1]:
                stations.append(route)
                for next_stop in uvdot_str['routes'][route][1]['railways']:
                    line_connection = uvdot_str['routes'][route][1]['railways'][next_stop]
                    if line_connection[0][0] not in lines:
                        lines[line_connection[0][0]] = {'start-stations': [], 'stop-stations': []}
                    lines[line_connection[0][0]]['start-stations'].append(route)
                    lines[line_connection[0][0]]['stop-stations'].append(next_stop)

                    t_stations = [route, next_stop]
                    t_stations.sort()
                    t_time = {'start': t_stations[0], 'end': t_stations[1], 'time': round(line_connection[1] / 8)}
                    if t_time not in network['traveltimes']:
                        network['traveltimes'].append(t_time)

        for line in lines:
            for start in lines[line]['start-stations']:
                if start not in lines[line]['stop-stations']:
                    lines[line]['start'] = start
            for stop in lines[line]['stop-stations']:
                if stop not in lines[line]['start-stations']:
                    lines[line]['stop'] = stop

            network['lines'].append({'name': line, 'stations': [lines[line]['start']]})
            current_station = lines[line]['start']
            while current_station != lines[line]['stop']:
                for name in uvdot_str['routes'][current_station][1]['railways']:
                    if uvdot_str['routes'][current_station][1]['railways'][name][0][0] == line:
                        network['lines'][-1]['stations'].append(name)
                        current_station = name
                        break

            if self.st_mode:
                network['prices'] = self.network_files['network']['prices']

            line_number = int(re.findall(r'\d+', line)[0])
            if line_number % 2:
                network['doublelines'].append([line, line.replace(str(line_number), str(line_number + 1))])

        for station in stations:
            content = {'name': station, 'lines': []}
            for line in network['lines']:
                if station in line['stations']:
                    platform = 0
                    if self.st_mode:
                        for rstation in self.network_files['network']['stations']:
                            if rstation['name'] == station:
                                for rline in rstation['lines']:
                                    if rline['name'] == self.replace_ust(line['name']):
                                        platform = rline['platform']
                    content['lines'].append({'name': line['name'], 'platform': platform})
            network['stations'].append(content)
            
        return network

    def create_st_export(self) -> str:
        return f'const network = {self.replace_ust(json.dumps(self.convert_uvdot_st(self.network_files)))};\n\n'
