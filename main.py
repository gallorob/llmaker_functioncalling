import os.path
from enum import Enum
from time import perf_counter_ns
from typing import List, Tuple

import pandas as pd
import yaml
from pydantic import ValidationError
from tqdm.auto import tqdm

from configs import configs
from level import Level
from level_validation import validate_level_domain
from designer_validation import validate_level_design
from llm import run_prompt


class LLMLevel(Enum):
	ZeroShot = 'zero-shot'
	FewShot = 'few-shot'
	ChainOfThought = 'cot'
	FunctionCalling = 'func-calls'


def load_use_case(use_case_number) -> List[str]:
	with open(f'use_cases/use_case_{use_case_number}', 'r') as f:
		return [l for l in f.readlines() if not l.startswith('#')]


class Results:
	def __init__(self):
		self.successes = 0
		self.elapsed_time = 0
		self.n_responses = 0
		self.n_requests = 0
		
		self.hard_fail = 0
		self.domain_soft_fail = 0
		self.design_soft_fail = 0
		self.success = 0
		
		self.level = None
		
	@property
	def n_rooms(self) -> int:
		return len(self.level.rooms)
	
	def __get_amount(self, entity_type):
		n = 0
		for room in self.level.rooms.values():
			n += len(room.encounter.entities[entity_type])
		for corridor in self.level.corridors:
			for encounter in corridor.encounters:
				n += len(encounter.entities[entity_type])
		return n
	
	@property
	def n_enemies(self) -> int:
		return self.__get_amount(entity_type='enemy')
	
	@property
	def n_traps(self) -> int:
		return self.__get_amount(entity_type='trap')
	
	@property
	def n_treasures(self) -> int:
		return self.__get_amount(entity_type='treasure')


def run_use_case(use_case_number: int, llm_level: LLMLevel, run_n: int) -> Results:
	results = Results()

	level = Level()
	results.level = level
	
	instructions = load_use_case(use_case_number)
	results.n_requests = len(instructions)
	
	with open('prompts/base_system_prompt', 'r') as f:
		system_prompt = f.read()
	
	if llm_level == LLMLevel.FunctionCalling:
		with open('openai_functions.yml', 'r') as f:
			tools = yaml.safe_load(f)
	else:
		tools = None
	
	with open(f'prompts/{llm_level.value}_prompt', 'r') as f:
		additional_prompt = f.read()
	system_prompt += additional_prompt
	
	conversation_history = open(f'results/{llm_level.value}/{use_case_number}/{run_n}/conversation.txt', 'w')
	
	with tqdm(total=len(instructions)) as pbar:
		for step, instruction in enumerate(instructions):
			pbar.update(1)
			pbar.set_postfix(
				{'llm': llm_level.value, 'use_case': use_case_number, 'run_n': run_n, 'prompt': instruction})
			messages = [
				{"role": "system", "content": system_prompt},
				{"role": "system", "content": f'<Current Level>\n{level.model_dump_json()}'},
				{"role": "user", "content": f'User: {instruction}'}
			]
			conversation_history.write(f'User: {instruction}')
			
			old_level = level.model_copy(deep=True)
			
			try:
				start_time = perf_counter_ns()
				
				response, extra_info = run_prompt(messages=messages, level=level, tools=tools)
				
				results.n_responses += 1
				end_time = perf_counter_ns()
				results.elapsed_time += end_time - start_time
				
				conversation_history.write(f'AI: {extra_info}{response}\n')
				
				if llm_level != LLMLevel.FunctionCalling:
					bounds = response.index('{'), response.rindex('}') + 1
					level = Level.model_validate_json(response[bounds[0]:bounds[1]], strict=True)
					if not validate_level_domain(use_case=use_case_number, step=step, old_level=old_level, new_level=level):
						conversation_history.write(f'\n\nError:\nLevel validation error\n')
						results.domain_soft_fail = step + 1
						break
					
				with open(f'results/{llm_level.value}/{use_case_number}/{run_n}/level_{step}.json', 'w') as f:
					f.write(level.model_dump_json(indent=2))
				
				if validate_level_design(use_case=use_case_number, step=step, old_level=old_level, new_level=level):
					results.level = level
					results.successes += 1
				else:
					conversation_history.write(f'\n\nError:\nDesign validation error\n')
					if results.design_soft_fail == 0:
						results.design_soft_fail = step + 1
						
			except (ValidationError, ValueError, TypeError, KeyError) as e:
				conversation_history.write(f'\n\nError:\n{e}\n')
				results.hard_fail = step + 1
				break
	
	conversation_history.close()
	
	results.success = 1 if results.successes == results.n_responses else 0
	
	results.elapsed_time /= 1000000000
	
	return results


if __name__ == '__main__':
	tabular_results = pd.DataFrame(
		columns=['Prompting', 'Use Case', 'Requests', 'Run',
		         'Successes', 'Elapsed time (ns)',
		         'Number of rooms', 'Number of enemies', 'Number of traps', 'Number of treasures',
		         'Hard Fail', 'Domain Soft Fail','Design Soft Fail','Success',
		         'Number of Responses'])
	
	llm_levels = [LLMLevel.ZeroShot, LLMLevel.FewShot, LLMLevel.ChainOfThought, LLMLevel.FunctionCalling]
	
	if not os.path.exists('results/'):
		os.mkdir('results/')
	for llm in llm_levels:
		if not os.path.exists(f'results/{llm.value}'):
			os.mkdir(f'results/{llm.value}')
		for use_case_num in range(1, configs.n_use_cases + 1):
			if not os.path.exists(f'results/{llm.value}/{use_case_num}'):
				os.mkdir(f'results/{llm.value}/{use_case_num}')
			for run_n in range(configs.n_runs):
				if not os.path.exists(f'results/{llm.value}/{use_case_num}/{run_n}'):
					os.mkdir(f'results/{llm.value}/{use_case_num}/{run_n}')
	
	for llm_level in llm_levels:
		for use_case_num in range(1, configs.n_use_cases + 1):
			for run_n in range(configs.n_runs):
				results = run_use_case(use_case_number=use_case_num, llm_level=llm_level, run_n=run_n)
				tabular_results.loc[len(tabular_results)] = [llm_level.value, use_case_num, results.n_requests, run_n,
				                                             results.successes / results.n_requests, results.elapsed_time,
				                                             results.n_rooms, results.n_enemies, results.n_traps, results.n_treasures,
				                                             results.hard_fail, results.domain_soft_fail, results.design_soft_fail, results.success,
				                                             results.n_responses]
		
			tabular_results.to_csv('results/tabular_results.csv')
