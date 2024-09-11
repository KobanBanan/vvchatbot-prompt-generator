import json
import logging
from typing import List, Dict, Tuple

from pkg_resources import resource_filename


class PromptGenerator:
    def __init__(self, add_system=False):
        logging.info(f'[PROMPT]: Initializing {self.__class__}')
        with open(resource_filename("prompt_generator", "prompt.json"), encoding='utf-8') as f:
            data = json.load(f)
            self.search_prompt = data['search']['system_prompt']
            self.dialog_prompt = data['dialogue']['system_prompt']

        self.add_system = add_system

    @staticmethod
    def _generate_sources(num_sources: int):
        template = '[^{}^]'
        res = []
        for i in range(1, num_sources + 1):
            res.append(template.format(i))

        return res

    @staticmethod
    def _generate_dialogue_prompt(query: str):
        return query, {}

    def _generate_search_prompt(
            self, query: str, search_documents: List[Dict[str, str]], summaries_count: int = 6
    ) -> Tuple[str, Dict]:

        search_documents = [sd for sd in search_documents if sd]

        logging.info(f'[PROMPT]: Generating prompt for query {query}')
        sources = self._generate_sources(len(search_documents))
        urls_and_sources = {source: i for source, i in zip(sources, search_documents)}

        title_key = 'title'
        context_key = 'description'
        summaries_count = summaries_count if summaries_count < len(search_documents) else len(search_documents)

        message = f'QUESTION: {query}\n' \
                  '=========\n' \
                  'SEARCH RESULT:'
        if sources:
            for i in range(summaries_count):
                source = sources[i]
                message += f'\n- {title_key}_{i}. {context_key}_{i} {source}'
        else:
            message += '[]'

        message += '\n=========\n' \
                   'FINAL ANSWER: '

        for index, doc in reversed(list(enumerate(search_documents))):
            title = doc[title_key]
            context = doc[context_key]

            message = message.replace(f'{title_key}_{index}', title).replace(f'{context_key}_{index}', context)

        final_prompt = message if not self.add_system else self.search_prompt + '\n' + message

        return final_prompt, urls_and_sources

    def generate(
            self,
            query: str,
            search_documents: List[Dict[str, str]],
            summaries_count: int = 6,
            force_search=False
    ):
        if search_documents or force_search:
            return self._generate_search_prompt(query, search_documents, summaries_count)
        else:
            return self._generate_dialogue_prompt(query)

    def __call__(
            self,
            query: str,
            search_documents: List[Dict[str, str]],
            summaries_count: int = 6,
            force_search: bool = False,
            *args,
            **kwargs
    ):
        return self.generate(
            query=query,
            search_documents=search_documents,
            summaries_count=summaries_count,
            force_search=force_search
        )
