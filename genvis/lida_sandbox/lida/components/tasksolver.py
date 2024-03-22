import json
import logging
from lida.utils import clean_code_snippet
from llmx import TextGenerator, TextGenerationResponse
from lida.datamodel import Task, TextGenerationConfig, Persona


prompt = ("You are a skilled data analyst, highly skilled in writing PERFECT code for answering analysis tasks " +
                 "given a dataset." +
                 "Given some code template, you complete the template to generate the correct answer for the analysis " +
                 "question given the dataset. The transformations you apply in your code MUST be correct and the " +
                 "fields you use MUST be correct. The CODE MUST BE " +
                 "CORRECT and MUST NOT CONTAIN ANY SYNTAX OR LOGIC ERRORS (e.g., it must consider the field types " +
                 "and use them correctly). You MUST first generate a brief plan for how you would solve the task " +
                 "e.g. what transformations you would apply e.g. if you need to construct a new column, what fields " +
                 "you would use, etc.")




FORMAT_INSTRUCTIONS = """
THE OUTPUT MUST BE A CODE SNIPPET OF A VALID LIST OF JSON OBJECTS. IT MUST USE THE FOLLOWING FORMAT:

```[
    { "goal":"histogram of X",
      "visualization": { "chart type": "histogram",
                         "position": "A",
                         "color": "B",
                         "size": "C",
                         "shape": "D",
                         "text": "E",
                         "opacity": "F",
                         "title": "G",
                         "x_ax_label": "H",
                         "y_ax_label": "I",
                         "x_ax_ticks": "J",
                         "y_ax_ticks": "K",
                         "legend": "L",
                         "legend_title": "M",
                         "legend_labels": "N",                 
      },
      "rationale": "This tells about "} ..
    ]
```
THE OUTPUT SHOULD ONLY USE THE JSON FORMAT ABOVE.

"""

template = '```python\nimport pandas as pd\n\ndef solve(data: pd.DataFrame, summary: dict):\n    # Include comments inside this Python code explaining your entire thought process\n    <stub_0> # any logic to find the ONE correct answer\n    correct = <correct> #Please provide a full-sentence answer that includes relevant context\n    <stub_1> # any logic to find the FIRST incorrect but plausible answer related to the analysis task\n    incorrect1 = <incorrect1> # Please provide a full-sentence answer that includes relevant context\n    <stub_2> # any logic to find the SECOND incorrect but plausible answer related to the analysis task\n    incorrect2 = <incorrect2> # Please provide a full-sentence answer that includes relevant context\n    <stub_3> # any logic to find the THIRD incorrect but plausible answer related to the analysis task\n    incorrect3 = <incorrect3> # Please provide a full-sentence answer that includes relevant context\n    answers = {"correct": str(correct), "incorrect1": str(incorrect1), "incorrect2": str(incorrect2), "incorrect3": str(incorrect3)}\n    return answers\n\nanswers = solve(data, summary)  # data already contains the data to analyze.  Always include this line. No additional code beyond this line.\n```'

logger = logging.getLogger("lida")


class TaskSolver:
    """Generate tasks given a summary of data"""

    def __init__(self) -> None:
        pass

    @staticmethod
    def solve(summary: dict,
              task: Task,
              textgen_config: TextGenerationConfig,
              text_gen: TextGenerator,
              n=3) -> dict[str, list[Task]]:
        """Generate tasks given a summary of data"""

        user_prompt = f""" Solve the following [ANALYSIS TASK] taking into consideration the [DATA SUMMARY] AND THE [TEMPLATE OUTPUT]. Note that your answer shold only be based in the [TEMPLATE OUTPUT]: do not add anything before the initial "```" or after the last "```". The correct and incorrect answers you come up with must not explicitly mention if they are correct or incorrect.\n\n[ANALYSIS TASK]:\n{task.description}\n\n[DATA SUMMARY]:\n{summary}\n\n[TEMPLATE OUTPUT]:{template}"""

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user",
             "content":
             f"{user_prompt}\n"}]

        result: list[Task] = text_gen.generate(messages=messages, config=textgen_config)

        completions: TextGenerationResponse = text_gen.generate(
            messages=messages, config=textgen_config)
        response = [x['content'] for x in completions.text]

        return response
        """
        try:
            json_string = clean_code_snippet(result.text[0]["content"])
            json_result = json.loads(json_string)
            # cast each item in the list to a Goal object
            result_dict: dict[str, list[Task]] = {
                category: [Task(**x) for x in tasks] for (category, tasks) in json_result.items()}
        except json.decoder.JSONDecodeError:
            logger.info(f"Error decoding JSON: {result.text[0]['content']}")
            print(f"Error decoding JSON: {result.text[0]['content']}")
            raise ValueError(
                "The model did not return a valid JSON object while attempting generate goals. Consider using a " +
                "larger model or a model with higher max token length.")
        return result_dict
        """
