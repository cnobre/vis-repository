from dataclasses import asdict
from typing import Dict
from llmx import TextGenerator, TextGenerationConfig, TextGenerationResponse

from ..scaffold import ChartScaffold
from lida.datamodel import Task


system_prompt = ("You are a helpful assistant highly skilled in writing PERFECT code for visualizations." +
                 "Given some code template, you complete the template to generate a visualization given the dataset " +
                 "and the task described. The code you write MUST FOLLOW VISUALIZATION BEST PRACTICES i.e., meet the " +
                 "specified task, apply the right transformation, use the right visualization type, use the right " +
                 "data encoding, and use the right aesthetics (e.g., ensure axis are legible). You are able to apply " +
                 "well-known visualization best practices and design principles, such as the ones stated in the book " +
                 "\"Visualization Analysis and Design\" by Tamara Munzner. The transformations " +
                 "you apply MUST be correct and the fields you use MUST be correct. The visualization CODE MUST BE " +
                 "CORRECT and MUST NOT CONTAIN ANY SYNTAX OR LOGIC ERRORS (e.g., it must consider the field types " +
                 "and use them correctly). You MUST first generate a brief plan for how you would solve the task " +
                 "e.g. what transformations you would apply e.g. if you need to construct a new column, what fields " +
                 "you would use, what visualization type you would use, what aesthetics you would use, etc.")


class VizGenerator(object):
    """Generate visualizations from prompt"""

    def __init__(
        self
    ) -> None:

        self.scaffold = ChartScaffold()

    def generate(self, summary: Dict,
                 task: Task,
                 textgen_config: TextGenerationConfig,
                 text_gen: TextGenerator,
                 n: int,
                 data_path,
                 library='vegalite'):
        """Generate visualization code given a summary and a task"""

        library_template, library_instructions = self.scaffold.get_template(task, library, data_path, n=n)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"The dataset summary is : {summary} \n\n"},
            library_instructions,
            {"role": "user", "content":
                f"Complete this [TEMPLATE] according to the instructions. It is crucial for the functionality of the entire script that the final line of code, vega_lite_spec = plot(data), remains active and is not commented out.\n\n [TEMPLATE]:\n{library_template} \n"}
             ]

        """
        f"The visualization code MUST only use data " +
                f"fields that exist in the dataset (field_names). " +
                f"Only use variables that have been defined in the code or are in the dataset summary. " +
                f"You MUST return a FULL PYTHON PROGRAM ENCLOSED IN BACKTICKS ``` that starts with an import statement. " +
                f"DO NOT add any explanation. \n\n Here is the template described before: \n\n {library_template} \n\n.The FINAL COMPLETED CODE BASED ON " +
                f"THE TEMPLATE above is ... \n\n"
                """

        """
        messages = [
            {"role": "system",
             "content": "Your task is to write Python code for generating a data visualization that answers a specific analytical question derived from a given dataset summary. You will be provided with a code template and must adhere to visualization best practices, including selecting the correct visualization type, applying the right data transformations, and using appropriate data encodings and aesthetics. Ensure your code is correct, follows best practices, and includes no syntax or logic errors."},
            {"role": "system",
             "content": "Handle NaN values with 'coerce', and ensure proper formatting for plotting. If the analysis task is related to a date field, convert it to pandas datetime objects. The 'plot' function must take a pandas DataFrame ('data') as input, perform any necessary data transformations, and return a matplotlib plot object. Do not include data loading code; assume the 'data' variable is already provided."},
            # {"role": "user",
            # "content": f"Complete the given template by filling in the '<imports>' and '<stub>' sections to generate the visualization. \"{task.description}\" is the analysis task that the visualization will help answer. This is the data summary containing important information: {summary}. Given the {task.description}, include in the <stub> an statement that gets the correct_answer from the data, and add it as a label/text in the plot. Also, fill out <correct_answer>, <wrong_answer1>, <wrong_answer2>, <wrong_answer3> in the multi-line string in the template so that I can use them as a multiple choice question. Ensure the plot function returns a matplotlib object without including plt.show(). Below is the template you need to modify (which includes the enclosing backticks):\n\n```python\nimport matplotlib.pyplot as plt\nimport pandas as pd\n<imports>\n\ndef plot(data: pd.DataFrame):\n    plt.title({task.description}, wrap=True)\n    <stub>  # Allowed modify this section\n    \"\"\" # Allowed modify this section\n    Correct answer: <correct_answer>\n    Wrong answer 1: <wrong_answer1>\n    Wrong answer 2: <wrong_answer2>\n    Wrong answer 3: <wrong_answer3>\n\"\"\"\n    return plt\n\n# Assume 'data' contains the dataset to be plotted\nchart = plot(data)\n```\n\n The program should strictly use dataset fields or their transformations (related to the analysis task aforementioned) and include a legend where appropriate. Do not add any explanation outside the code."}
            {"role": "user",
                "content": f"Create {n} well-designed visualizations within the provided template that independently help answer the analysis task: \"{task.description}\". Each visualization should enable answering the same multiple-choice question derived from the analysis task. Here are the details you need to incorporate:\n\n- **Title**: Each plot should have the same title, which is the analysis task to be answered.\n- **Answers**: Incorporate the correct answer and three wrong answers into each plot based on the dataset summary and column names (i.e., don't make up answers), either as labels or integrated within the visualization, ensuring they help in answering the analysis task. These should be traversal across visualizations.\n\nVary the visualizations along these channels: (1) chart type, (2) encoding channels (position, color, size, shape, text labels, opacity), (3) customizing axes (titles, labels, ticks, format), and (4) configuring legends (position, title, labels, layout). Ensure each plot function in the `<stub>` section generates a visualization that adheres to these guidelines, storing them in specific variables (e.g., fig1 = plt.figure()) and returns a list them (e.g., plots.append(fig1)) without including plt.show(). Below is the template you need to modify (enclosed in backticks):\n\n```python\nimport matplotlib.pyplot as plt\nimport pandas as pd\n<imports>\ndef plot(data: pd.DataFrame):\n    plots = []\n    # Setup for first plot\n    fig1 = plt.figure()\n    plt.title(\"{task.description}\", wrap=True)\n    <stub>  # Modify this section for each visualization\n    \"\"\" # This section should be true and the same for every visualization\n    Correct answer: <correct_answer>\n    Wrong answer 1: <wrong_answer1>\n    Wrong answer 2: <wrong_answer2>\n    Wrong answer 3: <wrong_answer3>\n    \"\"\"\n    plots.append(fig1)\n    # Repeat for additional plots as needed\n    return plots\n\n# 'data' contains the dataset to be plotted\ncharts = plot(data)\n```\n\nThe program must strictly use dataset fields or their transformations related to the aforementioned analysis task and include a legend where appropriate for each visualization. Each visualization should be crafted to allow a user to answer the multiple-choice question based on insights from any of the plots. Do not add any explanation outside the code."}
        ]"""

        #if library == "vegalite":
        #    return ['```python\nimport pandas as pd\n\ndef plot(data: pd.DataFrame):\n    vega_lite_spec = {"$schema": "https://vega.github.io/schema/vega-lite/v5.json","description": "A scatter plot of Horsepower vs. Miles per Gallon for various cars.", "data": {"url": "https://raw.githubusercontent.com/vega/vega-datasets/main/data/cars.json"},"mark": "point","encoding": {"x": {"field": "Horsepower", "type": "quantitative", "title": "Horsepower"},"y": {"field": "Miles_per_Gallon", "type": "quantitative", "title": "Miles per Gallon"},"color": {"field": "Origin", "type": "nominal", "title": "Origin"}}}\n    return vega_lite_spec\n\nvega_lite_spec = plot(data)\n```']

        completions: TextGenerationResponse = text_gen.generate(
            messages=messages, config=textgen_config)
        response = [x['content'] for x in completions.text]

        return response