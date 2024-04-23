from level import Level


def validate_level_domain(use_case: int, step: int, old_level: Level, new_level: Level) -> bool:
	if use_case == 1:
		if step == 0:  # Make a room in a swamp
			return len(new_level.rooms) == 1 and new_level.current_room != old_level.current_room
		elif step == 1:  # Add a couple of enemies
			return len(new_level.rooms[new_level.current_room].encounter.entities['enemy']) > 0
		elif step == 2:  # Add a new room set in the middle ages
			return len(new_level.rooms) == 2 and len(new_level.corridors) == 1 and new_level.current_room != old_level.current_room
		elif step == 3:  # Add an enemy and a treasure
			return len(new_level.rooms[new_level.current_room].encounter.entities['enemy']) == 1 and len(new_level.rooms[new_level.current_room].encounter.entities['treasure']) == 1
		elif step == 4:  # Add traps in the corridor
			corridor = new_level.corridors[-1]
			n_traps = 0
			for encounter in corridor.encounters:
				n_traps += len(encounter.entities['trap'])
			return n_traps > 0
		elif step == 5:  # Change the first enemy in the swamp to half its health and give it a sword
			return True
		elif step == 6:  # Add a trap in the first room
			# should not work, so level remains unchanged
			return len(new_level.rooms[new_level.current_room].encounter.entities['trap']) == 0
		else:
			raise ValueError("Invalid step")
	elif use_case == 2:
		if step == 0:  # Create a starting room with a torch-lit atmosphere
			return len(new_level.rooms) == 1 and new_level.current_room != old_level.current_room
		elif step == 1:  # Introduce an enemy in the starting room, described as a menacing shadow with 50 health points
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) == 1
		elif step == 2:  # Make a new room filled with ancient runes on the floor
			return len(new_level.rooms) == 2 and len(new_level.corridors) == 1 and new_level.current_room != old_level.current_room
		elif step == 3:  # Place a treasure chest at the end of the corridor
			return len(new_level.corridors[-1].encounters[-1].entities['treasure']) == 1
		elif step == 4:  # Add a hidden trap in the corridor
			for encounter in new_level.corridors[-1].encounters:
				if len(encounter.entities['trap']) > 0:
					return True
		elif step == 5:  # Insert a small chamber with a mystical pool
			return len(new_level.rooms) == 3 and len(new_level.corridors) == 2
		elif step == 6:  # Add a humanoid cat guarding a chest filled with wool
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) == 1 and len(room.encounter.entities['treasure']) == 1
		elif step == 7:  # Connect the mystical pool chamber to a larger cavernous room filled with glowing mushrooms
			return len(new_level.rooms) == 4 and len(new_level.corridors) == 3
		elif step == 8:  # Add a giant spider with 80 health points in the cavernous room
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0
		else:
			raise ValueError("Invalid step")
	elif use_case == 3:
		if step == 0:  # Create a starting room with dim lighting and a stone entrance
			return len(new_level.rooms) == 1
		if step == 1:  # Create a room with a collapsed bridge spanning a dark chasm
			return len(new_level.rooms) == 2 and len(new_level.corridors) == 1 and new_level.current_room != old_level.current_room
		if step == 2:  # Place a treasure chest
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['treasure']) > 0
		if step == 3:  # Introduce an enemy in the collapsed bridge room: a ghostly apparition with 60 health points
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0
		elif step == 4:  # Add an underground chamber with phosphorescent crystals connected to the starting room
			return len(new_level.rooms) == 3 and len(new_level.corridors) == 2  and new_level.current_room != old_level.current_room
		elif step == 5:  # Place a swarm of bats in the underground chamber with 40 health points collectively
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0
		elif step == 6:  # Create a room with a magical mirror that reflects the future actions of anyone who gazes into it
			return len(new_level.rooms) == 4 and len(new_level.corridors) == 3 and new_level.current_room != old_level.current_room
		elif step == 7:  # Introduce an enemy in the magical mirror room: a spectral guardian with 70 health points
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0
		elif step == 8:  # Connect the magical mirror room to a circular arena with a locked gate
			return len(new_level.rooms) == 5 and len(new_level.corridors) == 4 and new_level.current_room != old_level.current_room
		elif step == 9:  # Add a ferocious minotaur with 100 health points in the circular arena
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0
		else:
			raise ValueError('Invalid step')
	elif use_case == 4:
		if step == 0:  # Create a room with a gravity-defying effect where everything floats
			return len(new_level.rooms) == 1 and new_level.current_room != old_level.current_room
		elif step == 1:  # Place a treasure chest in the starting room
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['treasure']) > 0
		elif step == 2:  # Create a room where nothing exists, yet everything does
			return len(new_level.rooms) == 2 and len(new_level.corridors) == 1 and new_level.current_room != old_level.current_room
		elif step == 3:  # Add a treasure chest that is also an enemy
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0 or len(room.encounter.entities['treasure']) > 0
		elif step == 4:  # Place a trap in the room
			# should not work, so level remains unchanged
			return old_level.model_dump_json() == new_level.model_dump_json()
		elif step == 5:  # Place five unique enemies
			# should not work, so only add up to 4 enemies
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0
		elif step == 6:  # Add a room next to the current one
			return len(new_level.rooms) == 3 and len(new_level.corridors) == 2 and new_level.current_room != old_level.current_room
		elif step == 7:  # Add a room next to the current one
			return len(new_level.rooms) == 4 and len(new_level.corridors) == 3 and new_level.current_room != old_level.current_room
		elif step == 8:  # Add a room next to the current one
			return len(new_level.rooms) == 5 and len(new_level.corridors) == 4 and new_level.current_room != old_level.current_room
		elif step == 9:  # Add a room next to the current one
			return len(new_level.rooms) == 6 and len(new_level.corridors) == 5 and new_level.current_room != old_level.current_room
		elif step == 10:  # Add a room next to the current one
			return len(new_level.rooms) == 7 and len(new_level.corridors) == 6 and new_level.current_room != old_level.current_room
		else:
			raise ValueError('Invalid step')
	elif use_case == 5:
		if step == 0:  # Create 3 rooms, each connected to the next one, all set in a different European city
			return len(new_level.rooms) == 3 and len(new_level.corridors) == 2 and new_level.current_room != old_level.current_room
		elif step == 1:  # Add a goblin archer in the first room
			room = new_level.rooms[list(new_level.rooms.keys())[0]]
			return len(room.encounter.entities['enemy']) > 0
		elif step == 2:  # Also add two zombies
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0
		elif step == 3:  # Now generate a room connected to the first one, set in underground Atlantis
			return len(new_level.rooms) == 4 and len(new_level.corridors) == 3 and new_level.current_room != old_level.current_room
		elif step == 4:  # Put a couple of evil mermaids in Atlantis
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0
		elif step == 5:  # Place multiple ocean-themed traps in the corridor to Atlantis
			at_least_two = False
			for corridor in new_level.corridors:
				for encounter in corridor.encounters:
					at_least_two |= len(encounter.entities['trap']) > 0
			return at_least_two
		elif step == 6:  # Place a single treasure chest in all rooms, each containing a piece of a treasure map
			has_treasure = True
			for room in new_level.rooms.values():
				has_treasure &= len(room.encounter.entities['treasure']) > 0
			return has_treasure
		elif step == 7:  # Remove the chest containing the second piece of the treasure map
			has_treasure = True
			for room in new_level.rooms.values():
				has_treasure &= len(room.encounter.entities['treasure']) > 0
			return has_treasure
		elif step == 8:  # Add another room connected to Atlantis, set in Hell
			return len(new_level.rooms) == 5 and len(new_level.corridors) == 4 and new_level.current_room != old_level.current_room
		elif step == 9:  # Place two fallen angels armed with flaming swords
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0
		elif step == 10:  # Change one of the angels to a capybara monster
			room = new_level.rooms[new_level.current_room]
			return len(room.encounter.entities['enemy']) > 0
		elif step == 11:  # Set the health of the capybara to 1000
			return True
		elif step == 12:  # Make the capybara a punker, with pink spiky hair
			return True
		else:
			raise ValueError('Invalid step')
	else:
		raise ValueError("Invalid use case")
