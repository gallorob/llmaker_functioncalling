import logging
from typing import List, Optional

from level import Enemy, Level, Trap, Treasure


def create_room(level: Level,
                name: str,
                description: str,
                room_from: str) -> str:
	logging.getLogger().debug(f'\tCalled create_room: {name=} {description=} {room_from=}')
	success_msg = f'Added {name} to the level.'
	if room_from != '':
		success_msg += f' Also added corridor between {name} and {room_from}.'
	fail_msg = f'Could not add {name} to the level; it may be already in the level or could not be connected to other rooms.'
	return success_msg if level.try_add_room(name, description, room_from if room_from != '' else None) else fail_msg


def remove_room(level: Level,
                name: str) -> str:
	logging.getLogger().debug(f'\tCalled remove_room: {name=}')
	success_msg = f'{name} has been removed from the dungeon.'
	fail_msg = f'{name} is not in the level.'
	return success_msg if level.try_remove_room(room_name=name) else fail_msg


def update_room(level: Level,
                room_reference_name: str,
                name: str,
                description: str) -> str:
	logging.getLogger().debug(f'\tCalled update_room: {room_reference_name=} {name=} {description=}')
	success_msg = f'Updated {room_reference_name}.'
	fail_msg = f'{room_reference_name} is not in the level.'
	return success_msg if level.try_update_room(room_reference_name, name, description) else fail_msg


def add_corridor(level: Level,
                 room_from_name: str,
                 room_to_name: str,
                 corridor_length: int) -> str:
	logging.getLogger().debug(f'\tCalled add_corridor: {room_from_name=} {room_to_name=} {corridor_length=}')
	success_msg = f'Added corridor from {room_from_name} to {room_to_name}.'
	fail_msg = f'Could not add corridor: either it exists already or one (or both) of the rooms has 4 corridors already.'
	return success_msg if level.try_add_corridor(room_from_name, room_to_name, corridor_length) else fail_msg


def remove_corridor(level: Level,
                    room_from_name: str,
                    room_to_name: str) -> str:
	logging.getLogger().debug(f'\tCalled remove_corridor: {room_from_name=} {room_to_name=}')
	success_msg = f'Removed corridor between {room_from_name} and {room_to_name}.'
	fail_msg = f'Could not remove corridor: it is not in the level.'
	return success_msg if level.try_remove_corridor(room_from_name, room_to_name) else fail_msg


def update_corridor(level: Level,
                    room_from_name: str,
                    room_to_name: str,
                    corridor_length: int) -> str:
	logging.getLogger().debug(f'\tCalled update_corridor: {room_from_name=} {room_to_name=} {corridor_length=}')
	success_msg = f'Updated corridor between {room_from_name} and {room_to_name}.'
	fail_msg = f'Could not update corridor: either it does not exist or the new length of the corridor is invalid.'
	return success_msg if level.try_update_corridor(room_from_name, room_to_name, corridor_length) else fail_msg


def add_enemies(level: Level,
                room_name: str,
                names: List[str],
                descriptions: List[str],
                races: List[str],
                hps: List[int],
                dodges: List[float],
                prots: List[float],
                spds: List[float],
                other_room_name: Optional[str] = None,
                cell_index: Optional[int] = None) -> str:
	logging.getLogger().debug(
		f'\tCalled add_enemies: {room_name=} {other_room_name=} {cell_index=} {names=} {descriptions=} {races=} {hps=} {dodges=} {prots=} {spds=}')
	added, not_added = [], []
	if other_room_name is None and cell_index is None:
		# adding to a room
		if room_name in level.rooms.keys():
			level.current_room = room_name
			# try adding each enemy in the list
			for i in range(len(names)):
				enemy = Enemy(name=names[i], description=descriptions[i],
				              race=races[i], hp=hps[i], dodge=dodges[i], prot=prots[i], spd=spds[i])
				if level.rooms[room_name].encounter.try_add_entity(entity=enemy):
					added.append(f'{names[i]}')
				else:
					not_added.append(f'{names[i]}')
		else:
			return f'Could not add enemies: {room_name} is not in the level.'
	else:
		# adding to a corridor
		corridor = level.get_corridor(room_name, other_room_name, ordered=False)
		if corridor is not None:
			level.current_room = corridor.name
			if cell_index - 1 >= corridor.length: return f'Invalid cell index: the corridor is {corridor.length} cells long.'
			encounter = corridor.encounters[cell_index - 1]
			for i in range(len(names)):
				enemy = Enemy(name=names[i], description=descriptions[i],
				              race=races[i], hp=hps[i], dodge=dodges[i], prot=prots[i], spd=spds[i])
				if encounter.try_add_entity(entity=enemy):
					added.append(f'{names[i]}')
				else:
					not_added.append(f'{names[i]}')
		else:
			return f'Could not add enemies: corridor between {room_name} and {other_room_name} is not in the level.'
	msg = ''
	if len(added) > 0: msg += f'Added {"; ".join(added)}.'
	if len(not_added) > 0: msg += f'Could not add {"; ".join(not_added)}. There are too many entities of this type.'
	return msg


def add_treasures(level: Level,
                  room_name: str,
                  names: List[str],
                  descriptions: List[str],
                  loots: List[str],
                  other_room_name: Optional[str] = None,
                  cell_index: Optional[int] = None) -> str:
	logging.getLogger().debug(
		f'\tCalled add_treasures: {room_name=} {other_room_name=} {cell_index=} {names=} {descriptions=} {loots=}')
	added, not_added = [], []
	if other_room_name is None and cell_index is None:
		# adding to a room
		if room_name in level.rooms.keys():
			for i in range(len(names)):
				treasure = Treasure(name=names[i], description=descriptions[i],
				                    loot=loots[i])
				if level.rooms[room_name].encounter.try_add_entity(entity=treasure):
					added.append(f'{names[i]}')
				else:
					not_added.append(f'{names[i]}')
		else:
			return f'Could not add treasures: {room_name} is not in the level.'
	else:
		# adding to a corridor
		corridor = level.get_corridor(room_name, other_room_name, ordered=False)
		if corridor is not None:
			if cell_index - 1 >= corridor.length: return f'Invalid cell index: the corridor is {corridor.length} cells long.'
			encounter = corridor.encounters[cell_index - 1]
			for i in range(len(names)):
				treasure = Treasure(name=names[i], description=descriptions[i],
				                    loot=loots[i])
				if encounter.try_add_entity(entity=treasure):
					added.append(f'{names[i]}')
				else:
					not_added.append(f'{names[i]}')
		else:
			return f'Could not add treasures: corridor between {room_name} and {other_room_name} is not in the level.'
	msg = ''
	if len(added) > 0: msg += f'Added {"; ".join(added)}. '
	if len(not_added) > 0: msg += f'Could not add {"; ".join(not_added)}. There are too many entities of this type.'
	return msg


def add_traps(level: Level,
              room_name: str,
              other_room_name: str,
              names: List[str],
              descriptions: List[str],
              effects: List[str],
              cell_index: int) -> str:
	logging.getLogger().debug(
		f'\tCalled add_traps: {room_name=} {other_room_name=} {cell_index=} {names=} {descriptions=} {effects=}')
	added, not_added = [], []
	# get the corridor
	corridor = level.get_corridor(room_name, other_room_name, ordered=True)
	if corridor is not None:
		# make sure we are adding to a valid encounter
		if cell_index - 1 >= corridor.length: return f'Invalid cell index: the corridor is {corridor.length} cells long.'
		encounter = corridor.encounters[cell_index - 1]
		for i in range(len(names)):
			# add the traps
			trap = Trap(name=names[i], description=descriptions[i],
			            effect=effects[i])
			if encounter.try_add_entity(entity=trap):
				added.append(f'{names[i]}')
			else:
				not_added.append(f'{names[i]}')
	else:
		return f'Corridor between {room_name} and {other_room_name} is not in the level.'
	msg = ''
	if len(added) > 0: msg += f'Added {"; ".join(added)}.'
	if len(
		not_added) > 0: msg += f'Could not add {"; ".join(not_added)}. There are too many traps in this corridor cell.'
	return msg


def update_enemies_properties(level: Level,
                              room_name: str,
                              reference_names: List[str],
                              names: List[str],
                              descriptions: List[str],
                              races: List[str],
                              hps: List[int],
                              dodges: List[float],
                              prots: List[float],
                              spds: List[float],
                              other_room_name: Optional[str] = None,
                              cell_index: Optional[int] = None) -> str:
	logging.getLogger().debug(
		f'\tCalled update_enemies_properties: {room_name=} {reference_names=} {names=} {descriptions=} {races=} {hps=} {dodges=} {prots=} {spds=}')
	updated, not_updated = [], []
	if other_room_name is None and cell_index is None:
		# add to a room
		if room_name in level.rooms.keys():
			for i in range(len(reference_names)):
				enemy = Enemy(name=names[i], description=descriptions[i],
				              race=races[i], hp=hps[i], dodge=dodges[i], prot=prots[i], spd=spds[i])
				if level.rooms[room_name].encounter.try_update_entity(entity_reference_name=reference_names[i],
				                                                      entity_reference_type='enemy',
				                                                      updated_entity=enemy):
					updated.append(f'{reference_names[i]} is now {str(enemy)}')
				else:
					not_updated.append(reference_names[i])
		else:
			return f'{room_name} is not in the level.'
	else:
		corridor = level.get_corridor(room_name, other_room_name, ordered=False)
		if corridor is not None:
			if cell_index - 1 >= corridor.length: return f'Invalid cell index: the corridor is {corridor.length} cells long.'
			for i in range(len(reference_names)):
				enemy = Enemy(name=names[i], description=descriptions[i],
				              race=races[i], hp=hps[i], dodge=dodges[i], prot=prots[i], spd=spds[i])
				if corridor.encounters[cell_index - 1].try_update_entity(entity_reference_name=reference_names[i],
				                                                         entity_reference_type='enemy',
				                                                         updated_entity=enemy):
					updated.append(f'{reference_names[i]} was updated: {str(enemy)}')
				else:
					not_updated.append(reference_names[i])
		else:
			return f'Corridor between {room_name} and {other_room_name} is not in the level.'
	msg = ''
	if len(updated) > 0: msg += f'Updated {", ".join(updated)}.'
	if len(not_updated) > 0: msg += f'Could not update {", ".join(not_updated)}.'
	return msg


def update_treasures_properties(level: Level,
                                room_name: str,
                                reference_names: List[str],
                                names: List[str],
                                descriptions: List[str],
                                loots: List[str],
                                other_room_name: Optional[str] = None,
                                cell_index: Optional[int] = None) -> str:
	logging.getLogger().debug(
		f'\tCalled update_treasures_properties: {room_name=} {reference_names=} {names=} {descriptions=} {loots=}')
	updated, not_updated = [], []
	if other_room_name is None and cell_index is None:
		if room_name in level.rooms.keys():
			for i in range(len(reference_names)):
				treasure = Treasure(name=names[i], description=descriptions[i],
				                    loot=loots[i])
				if level.rooms[room_name].encounter.try_update_entity(entity_reference_name=reference_names[i],
				                                                      entity_reference_type='treasure',
				                                                      updated_entity=treasure):
					updated.append(f'{reference_names[i]} is now {str(treasure)}')
				else:
					not_updated.append(reference_names[i])
		else:
			return f'{room_name} is not in the level.'
	else:
		corridor = level.get_corridor(room_name, other_room_name)
		if corridor is not None:
			if cell_index - 1 >= corridor.length: return f'Invalid cell index: the corridor is {corridor.length} cells long.'
			for i in range(len(reference_names)):
				treasure = Treasure(name=names[i], description=descriptions[i],
				                    loot=loots[i])
				if corridor.encounters[cell_index - 1].try_update_entity(entity_reference_name=reference_names[i],
				                                                         entity_reference_type='treasure',
				                                                         updated_entity=treasure):
					updated.append(f'{reference_names[i]} was updated: {str(treasure)}')
				else:
					not_updated.append(reference_names[i])
		else:
			return f'Corridor between {room_name} and {other_room_name} is not in the level.'
	msg = ''
	if len(updated) > 0: msg += f'Updated {", ".join(updated)}.'
	if len(not_updated) > 0: msg += f'Could not update {", ".join(not_updated)}.'
	return msg


def update_traps_properties(level: Level,
                            room_name: str,
                            reference_names: List[str],
                            names: List[str],
                            descriptions: List[str],
                            effects: List[str],
                            other_room_name: str = None,
                            cell_index: int = None) -> str:
	logging.getLogger().debug(
		f'\tCalled update_traps_properties: {room_name=} {reference_names=} {names=} {descriptions=} {effects=}')
	updated, not_updated = [], []
	corridor = level.get_corridor(room_name, other_room_name)
	if corridor is not None:
		if cell_index - 1 >= corridor.length: return f'Invalid cell index: the corridor is {corridor.length} cells long.'
		for i in range(len(reference_names)):
			trap = Trap(name=names[i], description=descriptions[i],
			            effect=effects[i])
			if corridor.encounters[cell_index - 1].try_update_entity(entity_reference_name=reference_names[i],
			                                                         entity_reference_type='trap',
			                                                         updated_entity=trap):
				updated.append(f'{reference_names[i]} was updated: {str(trap)}')
			else:
				not_updated.append(reference_names[i])
	else:
		return f'Corridor between {room_name} and {other_room_name} is not in the level.'
	msg = ''
	if len(updated) > 0: msg += f'Updated {", ".join(updated)}.'
	if len(not_updated) > 0: msg += f'Could not update {", ".join(not_updated)}.'
	return msg


def remove_entities(level: Level,
                    room_name: str,
                    entities_name: List[str],
                    entities_type: List[str],
                    other_room_name: Optional[str] = None,
                    cell_index: Optional[int] = None) -> str:
	logging.getLogger().debug(f'\tCalled remove_entities_from_room: {room_name=} {entities_name=} {entities_type=}')
	removed, not_removed = [], []
	if other_room_name is None and cell_index is None:
		# removing from room
		if room_name in level.rooms.keys():
			for entity_name, entity_type in zip(entities_name, entities_type):
				if level.rooms[room_name].encounter.try_remove_entity(entity_name, entity_type):
					removed.append(entity_name)
				else:
					not_removed.append(entity_name)
		return f'{room_name} is not in the level.'
	else:
		# removing from corridor
		corridor = level.get_corridor(room_name, other_room_name)
		if corridor is not None:
			if cell_index - 1 >= corridor.length: return f'Invalid cell index: the corridor is {corridor.length} cells long.'
			for entity_name, entity_type in zip(entities_name, entities_type):
				if corridor.encounters[cell_index - 1].try_remove_entity(entity_name, entity_type):
					removed.append(entity_name)
				else:
					not_removed.append(entity_name)
		else:
			return f'Corridor between {room_name} and {other_room_name} is not in the level.'
	msg = ''
	if len(removed) > 0: msg += f'Removed {", ".join(removed)}.'
	if len(not_removed) > 0: msg += f'Could not remove {", ".join(not_removed)}.'
	return msg
