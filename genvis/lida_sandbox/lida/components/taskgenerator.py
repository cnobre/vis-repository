import json
import logging
from lida.utils import clean_code_snippet
from llmx import TextGenerator
from lida.datamodel import Task, TextGenerationConfig, Persona


prompt = (
    """Given a detailed summary of a dataset, you are able to create a structured list of visualization tasks that users can solve to gain insights into the dataset. Based on the information provided as the data summary, you generate visualization tasks per predefined categories. Each task is to be presented as a question with only one possible answer, that prompts the user to explore a relevant data visualization. When suggesting an analysis task, consider the complexity of visualizing large numbers of categorie; in such a case, specify the subset of interest of the data. Aim for simplicity and clarity in the resulting visualization.

Input Summary:
{}

Task Categories:
- Identification Tasks (identification): Users identify specific elements within a visualization.
- Comparison Tasks (comparison): Users compare different data points or groups within a visualization.
- Trend Analysis Tasks (trend): Users analyze trends over time or across categories.
- Relationship and Correlation Tasks (correlation): Users explore relationships or correlations between variables.
- Data Exploration Tasks (exploration): Users freely explore the data to discover insights.

Expected Output Format with Example:
{
  "Identification Tasks": [
                            {
                              "description": "Which X has the highest Y?",
                              "data_feature": ["X","Y"],
                              "analysis_type": "identification",
                              "rationale": "Z",
                            },
                            ...
                          ],
  "Comparison Tasks": [
                        ...
                      ],
  ...
}

For each task, include:
- 'description': A clear question based on the dataset's specific fields and their properties.
- 'data_feature': The dataset field(s) involved in the task.
- 'analysis_type': The type of analysis (Identification, Comparison, Trend Analysis, etc.).
- 'rationale': The rationale behind coming up with such a question (i.e., analysis task), including how it will lead to generate a user-friendly visualization.

Each task leverages the unique features and insights of the dataset as described in the summary, enabling users to engage deeply with the visualization tasks."""
)

"""
SYSTEM_INSTRUCTIONS = ("You are an experienced data analyst who can generate a given number of insightful GOALS " +
                       "about data, when given a summary of the data, and a specified persona.) The VISUALIZATIONS " +
                       "YOU RECOMMEND MUST FOLLOW VISUALIZATION BEST PRACTICES (e.g., must use bar charts instead of " +
                       "pie charts for comparing quantities) AND BE MEANINGFUL (e.g., plot longitude and latitude on " +
                       "maps where appropriate). They must also be relevant to the specified persona. Each goal must " +
                       "include a goal description, a " +
                       "visualization (THE VISUALIZATION MUST REFERENCE THE EXACT COLUMN " +
                       "FIELDS FROM THE SUMMARY, AND SPECIFY THE FOLLOWING: CHART TYPE " +
                       ", ENCODING CHANNELS [POSITION, COLOR, SIZE, SHAPE, TEXT, OPACITY], AXES, AND LEGENDS)" +
                       ", and a rationale (JUSTIFICATION FOR WHICH dataset FIELDS ARE USED and what we will learn " +
                       "from the visualization). Each goal MUST mention the exact fields from the dataset summary above"
                       )


FORMAT_INSTRUCTIONS = 
THE OUTPUT MUST BE A CODE SNIPPET OF A VALID LIST OF JSON OBJECTS. IT MUST USE THE FOLLOWING FORMAT:

```[
    { "index": 0,
      "goal":"histogram of X",
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


logger = logging.getLogger("lida")


class TaskGenerator:
    """Generate tasks given a summary of data"""

    def __init__(self) -> None:
        pass

    @staticmethod
    def generate(summary: dict,
                 textgen_config: TextGenerationConfig,
                 text_gen: TextGenerator,
                 n=5,
                 persona: Persona = None) -> dict[str, list[Task]]:
        """Generate tasks given a summary of data"""

        user_prompt = f""" Generate {n} TASKS per category. The tasks should be based on the data summary below, \n\n .
        {summary} \n\n"""

        # if not persona:
        #     persona = Persona(
        #         persona="A random participant in a user study about data visualization. We cannot assume any " +
        #                 "type of expertise with the subject domain, nor high visualization literacy",
        #         rationale="")

        # user_prompt += f"\n The generated goals SHOULD BE FOCUSED ON THE INTERESTS AND PERSPECTIVE of " + \
        #     f"a '{persona.persona} persona. \n"

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user",
             "content":
             f"{user_prompt}\n"}]

        result: list[Task] = text_gen.generate(messages=messages, config=textgen_config)

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
