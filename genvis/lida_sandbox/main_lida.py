from lida import Manager, llm, TextGenerationConfig
from datetime import datetime
import os
import json


def pretty_print_dict(d):
    # take empty string
    pretty_dict = ''

    # get items for dict
    for k, v in d.items():
        pretty_dict += f'{k}: \n'
        for value in v:
            pretty_dict += f'    {value}: {v[value]}\n'
    # return result
    return pretty_dict

base_url= 'https://raw.githubusercontent.com/vega/vega-datasets/main/data/'
dataset_names = ['cars.json',
             #'countries.json',
             #'income.json'
            ]

categories_to_question_type = {
    'Identification Tasks': {'type': 'MC',
                             'subtype': 'SingleAnswer'},
    'Comparison Tasks': {'type': 'TextEntry',
                         'subtype': 'Essay'},
    'Trend Analysis Tasks': {'type': 'MC',
                             'subtype': 'SingleAnswer'},
    'Relationship and Correlation Tasks': {'type': 'MC',
                                           'subtype': 'SingleAnswer'},
    'Data Exploration Tasks': {'type': 'TextEntry',
                               'subtype': 'Essay'},
}

n_task = 2
n_vis = 2

for dataset_name in dataset_names:
    if not os.path.exists(f'output/{dataset_name}'):
        os.makedirs(f'output/{dataset_name}')

    lida = Manager(text_gen=llm("openai", api_key='' , model='gpt-4-turbo-preview'))
    summary = lida.summarize(base_url + dataset_name)
    print(summary)

    textgen_config_task = TextGenerationConfig(temperature=0.1,
                                          top_p=1.0,
                                          top_k=50,
                                          use_cache=False)

    tasks = lida.tasks(summary, n=n_task, textgen_config=textgen_config_task)
    # print(len(tasks))

    textgen_config_vis = TextGenerationConfig(temperature=1.5,
                                          top_p=0.5,
                                          top_k=50,
                                          use_cache=False)

    merged = {}
    id = 1

    for category in tasks:
        print(f'\n\n\n\ncategory: {category}')
        for i, task in enumerate(tasks[category]):
            print(f'\n\n\nTask {i+1}: {task.description}')
            # print("\n\n\nNew task:")
            # print(f'{task.description}')
            # print(f'{task.rationale}')

            charts = lida.visualize(summary=summary,
                                    task=task,
                                    n=n_vis,
                                    data_path=base_url + dataset_name,
                                    textgen_config=textgen_config_vis,
                                    library="vegalite")
            if not charts:
                print("Error generating charts. Moving to next task.")
                continue

            answers = None
            if categories_to_question_type[category]['type'] == 'MC':
                answers = lida.solve(summary=summary,
                                     task=task,
                                     textgen_config=textgen_config_task)
            elif categories_to_question_type[category]['type'] == 'TextEntry':
                answers = {}

            if answers:
                print("answers")
                # print(pretty_print_dict(answers))
                print(answers)
            else:
                answers = {
                    'correct': 'python code broken',
                    'incorrect1': 'python code broken',
                    'incorrect2': 'python code broken',
                    'incorrect3': 'python code broken',
                    }


            # print("len(charts)")
            # print(len(charts))
            for j, chart in enumerate(charts):
                print(f'Chart {j+1}')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                img_format = '.png'
                path = f'output/{dataset_name}/{timestamp}_{task.analysis_type}_task{i+1}_vis{j+1}'
                if chart.savefig(path + img_format):
                    out = {
                    'url': f'https://raw.githubusercontent.com/cnobre/vis-repository/vis_generation/genvis/lida_sandbox/{path}{img_format}',
                    'Task Type': category,
                    'Analysis Task': task.description,
                    'Question type': categories_to_question_type[category]['type'],
                    'Question sub-type': categories_to_question_type[category]['subtype'],
                    'Chart': chart.spec['mark'],
                    'Complexity': 'ToDo', # TODO
                    'spec': chart.spec,
                    }
                    if 'correct' in answers:
                        out['correct'] = answers['correct']
                        out['incorrect1'] = answers['incorrect1']
                        out['incorrect2'] = answers['incorrect2']
                        out['incorrect3'] = answers['incorrect3']

                    merged[id] = out
                    id += 1

                    print('--------------id--------------')
                    print(id)

                    with open(path + '.json', 'w') as file:
                        json.dump(out, file, indent=2)

    print('merged')
    print(merged)
    with open(f'output/{dataset_name}/merged_output' + '.json', 'w') as file2:
        json.dump(merged, file2, indent=2)


"""
textgen_config = TextGenerationConfig(n=1, temperature=0.5, use_cache=True)
for task in tasks:
    charts = lida.visualize(summary=summary, tasks=task, textgen_config=textgen_config)
    for chart in charts:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart.savefig(f'test_{timestamp}.png')

# if "box plot" in goals['visualization']['description'].lower():
#     print(f"Box plot in chart {0}\n\n\n")
chart = lida.visualize(summary=summary, goal=goals[0], textgen_config=textgen_config)[0]
print(chart.code)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
chart.savefig(f'output/test_{timestamp}.png')

# for i in range(1):
#     try:
#
#     except:
#         print(f"Chart {i} wasn't saved\n\n\n")
"""
