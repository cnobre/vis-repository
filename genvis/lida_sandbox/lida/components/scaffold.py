from dataclasses import asdict

from lida.datamodel import Task


# if len(plt.xticks()[0])) > 20 assuming plot is made with plt or
# len(ax.get_xticks()) > 20 assuming plot is made with ax, set a max of 20
# ticks on x axis, ticker.MaxNLocator(20)

class ChartScaffold(object):
    """Return code scaffold for charts in multiple visualization libraries"""

    def __init__(
        self,
    ) -> None:

        pass

    def get_template(self, task: Task, library: str, data_path: str, n: int = 1):

        instructions = ("Your task "
                        "is to fill in specific sections of the template: `<imports>`, `<stub>`, `<question>`, "
                        "and `<answer>`. Here's how to approach each section:\n"
                        "1. **<imports>:** In this section, list all the necessary Python libraries that must "
                        "be imported for the code to execute as expected. Focus on libraries relevant to data "
                        "manipulation (like pandas) and visualization (such as matplotlib or seaborn). Ensure "
                        "you understand the context of the dataset and the visualization needs to select the "
                        "appropriate libraries.\n2. **<stub>:** This part requires you to define the body of "
                        "a function that creates the visualization. You'll need to:\n- Understand the structure "
                        "and content of the relevant columns in the [DATASET] to determine the best type of "
                        "visualization (bar chart, line graph, scatter plot, etc.).\n- Write Python code that takes "
                        "the dataset as input and outputs a visualization. This code should include setting up the "
                        "plot (size, labels, title), plotting the data, and any necessary formatting to make the "
                        "visualization clear and informative.\n3. **<question>:** Develop an analytical question "
                        "that a user should be able to answer by looking at the visualization you've defined in "
                        "the `<stub>`. This question should be directly related to the key insights or patterns "
                        "you intend the visualization to reveal from the [DATASET], as highlighted in the "
                        "[SUMMARY].\n4. **<answer>:** Provide a clear and concise answer to the question posed in "
                        "the `<question>` section. This answer should be something a user can infer directly from "
                        "the visualization without needing additional data or explanations. Ensure the "
                        "visualization you've designed in the `<stub>` section is capable of providing the "
                        "necessary information to answer this question.\nRemember, the goal of these instructions "
                        "is to guide the creation of a self-contained piece of content that leverages the [DATASET] "
                        "and [SUMMARY] to produce a meaningful visualization. The user should be able to understand "
                        "a specific aspect of the data through the visualization, answer the analytical question "
                        "posed, and confirm the answer with the information provided in the visualization itself.")


        general_instructions = (f"If using a <field> where " +
                                f"semantic_type=date, YOU MUST APPLY the following transform before using that " +
                                f"column i) convert date fields to date types using " +
                                f"data[''] = pd.to_datetime(data[<field>], errors='coerce'), " +
                                f"ALWAYS use  errors='coerce' ii) drop the rows with NaT values " +
                                f"data = data[pd.notna(data[<field>])] iii) convert field to right time format " +
                                f"for plotting.  Solve the task  carefully by completing ONLY the <imports>," +
                                f" <stub>, <question> (i.e., an analytical question that the user will be able to " +
                                f"solve by analyzing the visualization such as 'what is the max value X takes per " +
                                f"day?'), <answer> (i.e., the solution to the <question>) sections. Given the " +
                                f"dataset summary, the plot(data) " +
                                f"method should generate a {library} chart ({task.description}) " +
                                f"that enables the user to answer an analytical question based on the <question> " +
                                f" you come up with (based on the dataset you receive " +
                                f". DO NOT WRITE ANY CODE TO LOAD THE DATA. The data is already loaded and " +
                                f"available in the variable data .")

        matplotlib_instructions = (f" {general_instructions} DO NOT include plt.show(). The plot method must return " +
                                   f"a matplotlib object (plt). Think step by step. \n")

        if library == "matplotlib":
            instructions = {
                "role": "assistant",
                "content": f"  {matplotlib_instructions}. Use BaseMap for charts that require a map. "}
            template = \
                f"""
import matplotlib.pyplot as plt
import pandas as pd
<imports>

# question: <question>
# answer: <answer>
# solution plan
# i.  ..
def plot(data: pd.DataFrame):
    <stub> # only modify this section
    plt.title('<question> -> <answer>', wrap=True)
    return plt;

chart = plot(data) # data already contains the data to be plotted. Always include this line. No additional code beyond this line."""
        elif library == "seaborn":
            instructions = {
                "role": "assistant",
                "content": f"{matplotlib_instructions}. Use BaseMap for charts that require a map. "}

            template = \
                f"""
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
<imports>

# question: <question>
# answer: <answer>
# solution plan
# i.  ..
def plot(data: pd.DataFrame):
    <stub> # only modify this section
    plt.title('<question> -> <answer>', wrap=True)
    return plt;

chart = plot(data) # data already contains the data to be plotted. Always include this line. No additional code beyond this line."""

        elif library == "ggplot":
            instructions = {
                "role": "assistant",
                "content": f"{general_instructions}. The plot method must return a ggplot object (chart)`. Think step by step.p. \n",
            }

            template = \
                f"""
import plotnine as p9
<imports>
def plot(data: pd.DataFrame):
    chart = <stub>

    return chart;

chart = plot(data) # data already contains the data to be plotted. Always include this line. No additional code beyond this line.. """

        elif library == "altair":
            instructions = {
                "role": "system",
                "content": f"{general_instructions}. Always add a type that is BASED on semantic_type to each field such as :Q, :O, :N, :T, :G. Use :T if semantic_type is year or date. The plot method must return an altair object (chart)`. Think step by step. \n",
            }
            template = \
                """
import altair as alt
<imports>
def plot(data: pd.DataFrame):
    <stub> # only modify this section
    return chart
chart = plot(data) # data already contains the data to be plotted.  Always include this line. No additional code beyond this line..
"""

        elif library == "plotly":
            instructions = {
                "role": "system",
                "content": f"{general_instructions} If calculating metrics such as mean, median, mode, etc. ALWAYS use the option 'numeric_only=True' when applicable and available, AVOID visualizations that require nbformat library. DO NOT inlcude fig.show(). The plot method must return an plotly figure object (fig)`. Think step by step. \n.",
            }
            template = \
                """
import plotly.express as px
<imports>
def plot(data: pd.DataFrame):
    fig = <stub> # only modify this section

    return chart
chart = plot(data) # variable data already contains the data to be plotted and should not be loaded again.  Always include this line. No additional code beyond this line..
"""

        elif library == "vegalite":
            instructions = {
                "role": "user",
                "content": f"Create EXACTLY {n} well-designed Vega-Lite visualization specs (v4 schema) that, " +
                           f"individually, help answer the analysis task: \"{task.description}\". Each visualization " +
                           f"should enable answering the analysis task. Here are the details you need to incorporate:" +
                           f"\n\n- **Title**: Each plot should have the same title, which is the analysis task " +
                           f"aforementioned.\n\n- The dataset url for the specs is: {data_path}. Make sure this is " +
                           f"always present.\n- The $schema is \"https://vega.github.io/schema/vega-lite/v4.json\"" +
                           f"\n\nThe visualizations need to show the same variables which are relevant to the " +
                           f"analysis task but still be different from each other, so make sure to vary them as " +
                           f"necessary along these features: " +
                           f"(1) chart type (ideally vary them from the 12 chart types studied in the 2017 paper " +
                           f"\"VLAT: Development of a Visualization Literacy Assessment Test\"), " +
                           f"(2) encoding channels (position, color, size, shape, text labels, opacity), " +
                           f"(3) customizing axes (titles, labels, ticks, format), and " +
                           f"(4) configuring legends (position, title, labels, layout). Note: if a encoding channel " +
                           f"is used, make sure it is representing a third variable other than the ones in the axis, " +
                           f"and add a legend for it. Ensure each plot function generates a " +
                           f"Vega-Lite spec that adheres to these guidelines. it's crucial to consider the nature of " +
                           f"the variables involved in the visualization to ensure the resulting chart is readable " +
                           f"and informative. For example, If a categorical variable has a large number of unique " +
                           f"values (e.g., more than 10), your code should include logic to filter this down to a " +
                           f"more manageable subset before creating the Vega-Lite spec. For example, you might " +
                           f"choose to focus on the top X categories and group the remaining categories into an " +
                           f"'Other' category. The program must strictly use dataset fields related to the " +
                           f"aforementioned analysis task and include a legend where appropriate for each " +
                           f"visualization. Do not add any explanation outside the code."
            }

            """
            - **Answers**: Incorporate the correct answer and three wrong answers into each plot, either as labels or integrated within the visualization, ensuring they help in answering the analysis task. The correct and wrong answers are:\n  - Correct answer: <correct_answer>\n  - Wrong answer 1: <wrong_answer1>\n  - Wrong answer 2: <wrong_answer2>\n  - Wrong answer 3: <wrong_answer3>
            """

            spec_template = ''
            for i in range(n):
                spec_template += f'    spec{i+1} = <stub_{i+1}> # modify this section\n    vega_lite_specs.append(vega_lite_spec{i+1})\n'

            template = f'```python\nimport pandas as pd\n\ndef plot(data: pd.DataFrame):\n# Include comments in the code explaining your entire thought process\n<stub_0> # any logic to filter data ONLY IF NECESSARY\nvega_lite_specs = []\n{spec_template}    return vega_lite_spec\n\nvega_lite_spec = plot(data)  # data already contains the data to be plotted.  Always include this line uncommented as this code will be executed as is. No additional code beyond this line.\n```'
            # print()
            # print("template")
            # print(template)


        else:
            raise ValueError(
                "Unsupported library. Choose from 'matplotlib', 'seaborn', 'plotly', 'bokeh', 'ggplot', 'altair', 'vegalite'."
            )

        return template, instructions