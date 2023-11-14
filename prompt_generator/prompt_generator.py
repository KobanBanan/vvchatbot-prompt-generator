import json
import logging
from typing import List, Dict, Tuple

from pkg_resources import resource_filename


class PromptGenerator:
    def __init__(self):
        logging.info(f'[PROMPT]: Initializing {self.__class__}')
        with open(resource_filename("prompt_generator", "prompt.json"), encoding='utf-8') as f:
            data = json.load(f)
            self.search_prompt = data['search']['system_prompt']
            self.dialog_prompt = data['dialogue']['system_prompt']

    @staticmethod
    def _generate_sources(num_sources: int):
        template = '[^{}^]'
        res = []
        for i in range(1, num_sources + 1):
            res.append(template.format(i))

        return res

    @staticmethod
    def _generate_dialogue_prompt(query: str):
        return query, None

    def _generate_search_prompt(
            self, query: str, search_documents: List[Dict[str, str]], summaries_count: int = 6
    ) -> Tuple[str, Dict]:

        search_documents = [sd for sd in search_documents if sd]

        logging.info(f'[PROMPT]: Generating prompt for query {query}')
        sources = self._generate_sources(len(search_documents))
        urls_and_sources = {source: i.get("url") for source, i in zip(sources, search_documents)}

        title_key = 'title'
        context_key = 'context'
        summaries_count = summaries_count if summaries_count < len(search_documents) else len(search_documents)

        message = '\n' + f'QUESTION: {query}\n' \
                         '=========\n' \
                         'SEARCH RESULT:'

        for i in range(summaries_count):
            source = sources[i]
            message += f'\n- {title_key}_{i}. {context_key}_{i} {source}'

        message += '\n=========\n' \
                   'FINAL ANSWER: '

        for index, doc in enumerate(search_documents):
            title = doc[title_key]
            context = doc[context_key]

            message = message.replace(f'{title_key}_{index}', title).replace(f'{context_key}_{index}', context)

        final_prompt = message

        return final_prompt, urls_and_sources

    def generate(self, query: str, search_documents: List[Dict[str, str]], summaries_count: int = 6):
        return self._generate_dialogue_prompt(query) if not search_documents else self._generate_search_prompt(
            query, search_documents, summaries_count
        )

    def __call__(self, query: str, search_documents: List[Dict[str, str]], summaries_count: int = 6, *args,
                 **kwargs):
        return self.generate(query, search_documents, summaries_count)
