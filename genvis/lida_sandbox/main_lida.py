from lida import Manager, llm, TextGenerationConfig
from datetime import datetime
import os

data_urls = ['https://raw.githubusercontent.com/vega/vega-datasets/main/data/cars.json',
             #'https://raw.githubusercontent.com/vega/vega-datasets/main/data/countries.json',
             #'https://raw.githubusercontent.com/vega/vega-datasets/main/data/income.json'
            ]

n_task = 2
n_vis = 3

for data_url in data_urls:
    data_set_name = data_url.split('/')[-1]
    if not os.path.exists(f'output/{data_set_name}'):
        os.makedirs(f'output/{data_set_name}')

    lida = Manager(text_gen=llm("openai", api_key=''))
    summary = lida.summarize(data_url)
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

    for category in tasks:
        print(f'category: {category}')
        for i, task in enumerate(tasks[category]):
            print(f'Task {i+1}: {task.description}')
            # print("\n\n\nNew task:")
            # print(f'{task.description}')
            # print(f'{task.rationale}')

            charts = lida.visualize(summary=summary,
                                    task=task,
                                    n=n_vis,
                                    data_path=data_url,
                                    textgen_config=textgen_config_vis,
                                    library="vegalite")
            answers = lida.solve(summary=summary,
                                    task=task,
                                    textgen_config=textgen_config_task)
            print("answers")
            print(answers)

            # print("len(charts)")
            # print(len(charts))
            for j, chart in enumerate(charts):
                print(f'Chart {j+1}')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                chart.savefig(f'output/{data_set_name}/{timestamp}_{task.analysis_type}_task{i+1}_vis{j+1}', '.png')

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
