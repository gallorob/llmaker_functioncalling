from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from configs import configs


class Entity(BaseModel):
	class Config:
		arbitrary_types_allowed = True
	
	name: str = Field(..., description="The name of the entity.", required=True)
	description: str = Field(..., description="The description of the entity.", required=True)
	
	def __str__(self):
		return f'{self.name}: {self.description}'


class Enemy(Entity):
	race: str = Field(..., description="The enemy race.", required=True)
	hp: int = Field(..., description="The enemy HP.", required=True)
	dodge: float = Field(..., description="The enemy dodge stat.", required=True)
	prot: float = Field(..., description="The enemy prot stat.", required=True)
	spd: float = Field(..., description="The enemy spd stat.", required=True)
	
	def __str__(self):
		return f'Enemy {super().__str__()} HP={self.hp} DODGE={self.dodge} PROT={self.prot} SPD={self.spd}'


class Trap(Entity):
	effect: str = Field(..., description="The effect of the trap.", required=True)
	
	def __str__(self):
		return f'Trap {super().__str__()} Effect={self.effect}'


class Treasure(Entity):
	loot: str = Field(..., description="The loot in the treasure.", required=True)
	
	def __str__(self):
		return f'Treasure {super().__str__()} Loot={self.loot}'


class EntityClass(Enum):
	ENEMY = Enemy
	TRAP = Trap
	TREASURE = Treasure


entityclass_to_str = {
	Enemy:    'enemy',
	Trap:     'trap',
	Treasure: 'treasure'
}

entityclass_thresholds = {
	Enemy:    configs.max_enemies_per_encounter,
	Trap:     configs.max_traps_per_encounter,
	Treasure: configs.max_treasures_per_encounter
}


class Encounter(BaseModel):
	class Config:
		arbitrary_types_allowed = True
	
	entities: Dict[str, List[Union[Enemy, Trap, Treasure]]] = Field(
		default={k: [] for k in entityclass_to_str.values()},
		description="The entities for this encounter.", required=True)
	
	def __str__(self):
		s = ''
		for k in self.entities.keys():
			all_type_str = [str(x) for x in self.entities[k]]
			unique_with_count = [f'{all_type_str.count(x)}x {x}' for x in all_type_str]
			s += f'\n\t{str(k).lower()}: {", ".join(unique_with_count)}'
		return s
	
	def try_add_entity(self, entity: Entity) -> bool:
		klass = entityclass_to_str[entity.__class__]
		if klass not in self.entities.keys(): self.entities[klass] = []
		if len(self.entities[klass]) < entityclass_thresholds[entity.__class__]:
			# add the entity
			self.entities[klass].append(entity)
			return True
		return False
	
	def try_remove_entity(self, entity_name: str, entity_type: str) -> bool:
		n = None
		for i, entity in enumerate(self.entities[entity_type]):
			if entity.name == entity_name:
				n = i
			if n is not None:
				self.entities[entity_type].pop(n)
				return True
		return False
	
	def try_update_entity(self, entity_reference_name: str, entity_reference_type: str, updated_entity: Entity):
		for i, entity in enumerate(self.entities[entity_reference_type]):
			if entity.name == entity_reference_name:
				self.entities[entity_reference_type][i] = updated_entity
				return True
		return False


class Room(BaseModel):
	class Config:
		arbitrary_types_allowed = True
	
	name: str = Field(..., description="The name of the room.", required=True)
	description: str = Field(..., description="The description of the room", required=True)
	encounter: Encounter = Field(default=Encounter(), description='The encounter in the room.', required=True)
	
	def __str__(self):
		return f'{self.name}: {self.description};{self.encounter}'


class Corridor(BaseModel):
	class Config:
		arbitrary_types_allowed = True
	
	room_from: str = Field(..., description="The room the corridor is connected to.", required=True)
	room_to: str = Field(..., description="The room the corridor is connects to.", required=True)
	name: str = Field('', description="The name of the corridor.", required=True)
	length: int = Field(default=configs.corridor_length, description="The length of the corridor", required=True)
	encounters: List[Encounter] = Field(default=[Encounter() for _ in range(configs.corridor_length)],
	                                    description="The encounters in the corridor.", required=True)
	
	def __str__(self):
		return f'Corridor long {self.length} cells from {self.room_from} to {self.room_to};{"".join(str(e) for e in self.encounters)}'


class Level(BaseModel):
	class Config:
		arbitrary_types_allowed = True
	
	rooms: Dict[str, Room] = Field(default={}, description="The rooms in the level.", required=True)
	corridors: List[Corridor] = Field(default=[], description="The corridors in the level.", required=True)
	
	current_room: str = Field(default='', description="The currently selected room or corridor.", required=True)
	
	def __str__(self):
		level_description = '\n'.join([str(self.rooms[k]) for k in self.rooms.keys()]) + '\n'
		level_description += '\n'.join([str(c) for c in self.corridors])
		return level_description
	
	def get_corridor(self, room_from_name, room_to_name, ordered=False):
		for c in self.corridors:
			if (c.room_from == room_from_name and c.room_to == room_to_name) or (
				not ordered and (c.room_from == room_to_name and c.room_to == room_from_name)):
				return c
		return None
	
	def try_add_room(self, room_name: str, room_description: str, room_from: Optional[str] = None) -> bool:
		if room_name not in self.rooms.keys():
			# try add corridor to connecting room
			if room_from is not None and room_from in self.rooms.keys():
				n = 0
				for corridor in self.corridors:
					if corridor.room_from == room_from or corridor.room_to == room_from:
						n += 1
				# can only add corridor if the connecting room has at most 3 corridors already
				if n < 4:
					# add the new room to the level
					self.rooms[room_name] = Room(name=room_name, description=room_description)
					self.current_room = room_name
					self.corridors.append(
						Corridor(room_from=room_from, room_to=room_name, name=f'{room_from}_{room_name}'))
					return True
				else:
					return False
			# add the new room to the level
			self.rooms[room_name] = Room(name=room_name, description=room_description)
			self.current_room = room_name
			return True
		return False
	
	def try_remove_room(self, room_name: str) -> bool:
		if room_name in self.rooms.keys():
			# remove room
			del self.rooms[room_name]
			# remove connections from-to deleted room
			to_remove = []
			for i, corridor in enumerate(self.corridors):
				if corridor.room_from == room_name or corridor.room_to == room_name:
					to_remove.append(i)
			for i in reversed(to_remove):
				self.corridors.pop(i)
			self.current_room = list(self.rooms.keys())[0] if len(self.rooms) > 0 else None
			return True
		return False
	
	def try_update_room(self, room_reference_name: str, name: str, description: str) -> bool:
		if room_reference_name in self.rooms.keys():
			# get the current room
			room = self.rooms[room_reference_name]
			# remove it from the list of rooms (since room name can change)
			del self.rooms[room_reference_name]
			# update the room
			room.name = name
			room.description = description
			# add room back
			self.rooms[name] = room
			# reset the corridor(s) as well
			for corridor in self.corridors:
				if corridor.room_from == room_reference_name:
					corridor.room_from = room.name
				if corridor.room_to == room_reference_name:
					corridor.room_to = room.name
			if self.current_room == room_reference_name:
				self.current_room = name
			return True
		return False
	
	def try_add_corridor(self, room_from_name: str, room_to_name: str, corridor_length: int) -> bool:
		n = [0, 0]  # number of corridors for each room
		for corridor in self.corridors:
			# check if the corridor already exists
			if (corridor.room_from == room_from_name and corridor.room_to == room_to_name) or (
				corridor.room_to == room_from_name and corridor.room_from == room_to_name):
				return False
			# count corridors from each room
			if corridor.room_from == room_from_name or corridor.room_to == room_from_name:
				n[0] += 1
			if corridor.room_from == room_to_name or corridor.room_to == room_to_name:
				n[1] += 1
		# only add corridor if each room has at most 3 corridors
		if n[0] < 4 and n[1] < 4:
			self.corridors.append(Corridor(room_from=room_from_name, room_to=room_to_name,
			                               name=f'{room_from_name}_{room_to_name}',
			                               length=corridor_length,
			                               encounters=[Encounter() for _ in range(corridor_length)]))
			self.current_room = self.corridors[-1].name
			return True
		return False
	
	def try_remove_corridor(self, room_from_name: str, room_to_name: str) -> bool:
		to_remove = None
		# get the index of the corridor to remove
		for i, corridor in enumerate(self.corridors):
			if (corridor.room_from == room_from_name and corridor.room_to == room_to_name) or (
				corridor.room_to == room_from_name and corridor.room_from == room_to_name):
				to_remove = i
				break
		# remove the corridor if it exists
		if to_remove is not None:
			if self.current_room == f'{room_from_name}_{room_to_name}':
				self.current_room = room_from_name
			self.corridors.pop(to_remove)
			return True
		return False
	
	def try_update_corridor(self, room_from_name: str, room_to_name: str, corridor_length: int) -> bool:
		# make sure the length of the corridor is valid
		if corridor_length < configs.corridor_min_length or corridor_length > configs.corridor_max_length: return False
		# update the corridor
		corridor = self.get_corridor(room_from_name, room_to_name, ordered=False)
		if corridor is not None:
			corridor.length = corridor_length
			# drop encounters if the corridor has shrunk
			if len(corridor.encounters) > corridor.length:
				corridor.encounters = corridor.encounters[:corridor.length]
			self.current_room = f'{room_from_name}_{room_to_name}'
			return True
		return False
