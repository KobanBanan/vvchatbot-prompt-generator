import json
import logging
from typing import List, Dict, Tuple


class PromptGenerator:
    def __init__(self):
        logging.info(f'[PROMPT]: Initializing {self.__class__}')
        with open('prompt.json', encoding='utf-8') as f:
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

    def generate(
            self, query: str, search_documents: List[Dict[str, str]], summaries_count: int = 6
    ) -> Tuple[str, Dict]:

        search_documents = [sd for sd in search_documents if sd]

        logging.info(f'[PROMPT]: Generating prompt for query {query}')
        sources = self._generate_sources(len(search_documents))
        urls_and_sources = {source: i.get("url") for source, i in zip(sources, search_documents)}

        if search_documents:
            title_key = 'title'
            context_key = 'context'
            summaries_count = summaries_count if summaries_count < len(search_documents) else len(search_documents)

            message = f'QUESTION: {query}\n' \
                      '=========\n' \
                      'SEARCH RESULT:\n'

            for i in range(summaries_count):
                source = sources[i]
                message += f'{i}.[\nContent: [{title_key}_{i}]{source} - {context_key}_{i}\n'

            message += '=========\n' \
                       'FINAL ANSWER: '

            for index, doc in enumerate(search_documents):
                title = doc[title_key]
                context = doc[context_key]

                message = message.replace(f'{title_key}_{index}', title).replace(f'{context_key}_{index}', context)

            final_prompt = self.search_prompt + '\n' + message
        else:
            message = f'QUESTION: {query}\n'
            message += '=========\n' \
                       'ANSWER:\n'
            final_prompt = self.dialog_prompt + '\n' + message

        return final_prompt, urls_and_sources

    def __call__(self, query: str, search_documents: List[Dict[str, str]], summaries_count: int = 5, *args,
                 **kwargs):
        return self.generate(query, search_documents, summaries_count)