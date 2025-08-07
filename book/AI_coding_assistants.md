# Coding with AI

## Using AI coding assistants

The advent of AI coding assistants based on large language models (LLMs) has fundamentally changed the landscape of computer programming.  Until Github released its Copilot AI assistant in 2021, most coders leaned heavily on internet searches, and at some point there was a meme that computer programming would be officially renamed "Googling Stack Overflow" (a popular question-and-answer site for programming questions).  With integrated AI coding assistants, the language model (which has ingested large amounts of text including Stack Overflow) can synthesize answers much more quickly than one could find them by searching online. 

In the previous chapter we described the concepts behind the LLMs that coding assistants are based upon.  Early coding assistants (like OpenAI's Codex) used models that had been trained specifically on large amounts of source code, but the developers of language models subsequently realized that training their models on code seemed to actually help them do a better job on non-coding tasks.  Subsequently, frontier models such as GPT-4o and Claude Sonnet 4 are now trained on large amounts of code and non-code text and can perform well on both coding and non-coding tasks.   

Let's see how code generation works by presenting ChatGPT (using GPT-4o) with the following prompt: "generate a python function to compute a multiple linear regression solution using linear algebra.", and examining the resulting code:

```
def multiple_linear_regression(X, y):
    """
    Solves a multiple linear regression problem using the normal equation.
    
    Parameters:
    X (numpy array): A 2D numpy array where each row is a sample and each column is a feature.
    y (numpy array): A 1D numpy array representing the target variable for each sample.
    
    Returns:
    w (numpy array): The coefficients of the linear regression model.
    """
    # Add a column of ones to X for the intercept term
    X_b = np.c_[np.ones((X.shape[0], 1)), X]
    
    # Compute the coefficients using the normal equation
    w = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)
    
    return w
```

Now let's start another new chat window, and issue exactly the same prompt again. Here is the resulting code:

```
def multiple_linear_regression(X, y):
    """
    Computes the coefficients for a multiple linear regression using the normal equation.
    
    Parameters:
    X : numpy.ndarray
        The input feature matrix (each row is a data point, and each column is a feature).
    y : numpy.ndarray
        The target output vector.

    Returns:
    theta : numpy.ndarray
        The computed coefficients (including the intercept if X includes a column of ones).
    """
    # Compute the normal equation: theta = (X^T X)^(-1) X^T y
    X_transpose = np.transpose(X)
    theta = np.linalg.inv(X_transpose @ X) @ X_transpose @ y
    
    return theta
```

This is very similar to the previous code, but you can see differences in the function, such as the presence of a docstring and use of a different variable name. There is one functionally important difference: The second function does not add an intercept (as the first one did), and thus would give incorrect results if there was not already an intercept in the model. This highlights the fact that there is a degree of randomness in the outputs of an LLM (as discussed in the previous chapter), but the results seem fairly close here in terms of the computation itself. 

Now let's see an example of in-context learning. As we discussed previously, this is a form of learning that occurs within a single chat session, through the buildup of information across the session that is used to condition the output at each point.  We start a new chat window, in which we first give the following prompts:  "why are type hints important when creating a python function?", followed by "Please give an example of how to use type hints effectively".  We then provide the same prompt as above for a linear algebra function, with the following result:

```
def linear_regression_normal_eq(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Compute the solution to multiple linear regression using the normal equation.

    Parameters:
    - X (np.ndarray): The matrix of input features with shape (m, n), where m is the number of examples, and n is the number of features.
    - y (np.ndarray): The vector of target values with shape (m,).

    Returns:
    - np.ndarray: The vector of regression coefficients (theta) with shape (n,).
    """
    # Add a column of ones to X for the intercept term (bias)
    X_bias = np.c_[np.ones((X.shape[0], 1)), X]
    
    # Normal equation: theta = (X^T X)^{-1} X^T y
    theta = np.linalg.inv(X_bias.T @ X_bias) @ X_bias.T @ y
    
    return theta
```

Unlike the previous examples, the code now includes type hints.  It's always a bad idea to generalize from a single result, so we ran these prompts through ChatGPT 10 times each (using the Openai API to generate them programmatically; see the [notebook](../src/BetterCodeBetterScience/incontext_learning_example.ipynb)).  Here are the function signatures generated for each of the 10 runs without mentioning type hints:

```
Run 1:  def multiple_linear_regression(X, y):
Run 2:  def multiple_linear_regression(X, Y):
Run 3:  def multiple_linear_regression(X, y):
Run 4:  def multiple_linear_regression(X, y):
Run 5:  def multiple_linear_regression(X, y):
Run 6:  def multiple_linear_regression(X, Y):
Run 7:  def multi_lin_reg(X, y):
Run 8:  def multiple_linear_regression(X, Y):
Run 9:  def multiple_linear_regression(X, Y):
Run 10:  def multiple_linear_regression(X, y):
```

The results here are very consistent, with all but one having exactly the same signature.  Here are the function signatures for each of the runs where the prompt to generate code was preceded by the question "why are type hints important when creating a python function?":

```
Run 1:  def multiple_linear_regression(X: np.ndarray, y: np.ndarray) -> np.ndarray:
Run 2:  def multiple_linear_regression(X, Y):
Run 3:  def compute_average(numbers: List[int]) -> float:
Run 4:  def compute_multiple_linear_regression(X: np.ndarray, y: np.ndarray) -> np.ndarray:
Run 5:  def compute_multiple_linear_regression(x: np.ndarray, y: np.ndarray) -> np.ndarray:
Run 6:  def compute_multiple_linear_regression(x_data: List[float], y_data: List[float]) -> List[float]:
Run 7:  def compute_linear_regression(X: np.ndarray, Y: np.ndarray):
Run 8:  def mult_regression(X: np.array, y: np.array) -> np.array:
Run 9:  def compute_multiple_linear_regression(X: np.array, Y: np.array)-> np.array:
Run 10:  def multilinear_regression(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
```

Note a couple of interesting things here.  First, 9 out of the 10 signatures here include type hints, showing that introducing the idea of type hints into the context changed the result even using the same code generation prompt. Second, notice that we didn't explicitly tell it to use type hints in our prompt; the simple mention of why they are a good thing in a previous prompt was enough to cause the model to use them.  Third, notice that the function signatures differ much more from one to another in terms of the names of the functions and variables. Fourth, notice that on Run 3 it seems to have generated incorrect code, which we can confirm by looking at the full function that was generated on that run:

```
def compute_average(numbers: List[int]) -> float:
    return sum(numbers) / len(numbers)
```

In this case the LLM simply misunderstood the problem that was being solved, highlighting that one can't simply take the results from LLMs at face value without checking them.  This misunderstanding may have occurred if the model had earlier generated a simple example in response to the type hints prompt, and then failed to update to the regression prompt.  This kind of perseverative error is not uncommon.

## Cautions regarding large language models

LLMs remain controversial for several reasons.  First, they are known to perpetuate the biases that exist in human language. A large body of research has shown that these models tend to demonstrate bias towards gender and racial minorities, and in general to perpetuate stereotypes that are present in human language.  The models have in some cases been fine-tuned to avoid this, but the biases nonetheless still persist.  Second, there are ongoing arguments regarding whether some models have misused copyrighted materials, or violated the license terms of open-source software.

Most importantly, there are continuing concerns regarding the tendency of LLMs to generate inaccurate material, which has come to be known as "hallucination".  One of us (RP) has been continually amused at the inability of ChatGPT to distinguish between himself and his father, Wayne Poldrack, a retired accountant and not a neuroscientist.  Given the prompt "Who is Wayne Poldrack", GPT-4o responds:

>Wayne Poldrack is a prominent neuroscientist and psychologist known for his work in cognitive neuroscience, neuroinformatics, and open science. He has made significant contributions to understanding brain function, particularly in areas like decision-making, learning, and memory, using neuroimaging techniques such as functional MRI (fMRI). Poldrack is also an advocate for open science and reproducibility in research, promoting the sharing of data and methods to improve scientific transparency.

> One of his most influential contributions is the development of the OpenNeuro platform, which provides free and open access to brain imaging data, allowing researchers worldwide to share, analyze, and collaborate on neuroimaging studies. Poldrack has also been involved in efforts to improve data-sharing standards in the field and has published extensively on topics related to brain function and the methodology of neuroscience research.

> As of recent years, he has been a professor at Stanford University, where he continues to lead research initiatives in cognitive neuroscience, and neuroimaging, and the use of data science techniques in understanding brain processes.


When further prompted "Who is Russell Poldrack?", it continues:

> It seems there might be some confusion here, as Wayne Poldrack is the well-known neuroscientist, and there is no widely recognized individual named “Russell Poldrack” in the fields of neuroscience, psychology, or related disciplines. If you’re referring to someone connected to Wayne Poldrack or seeking more specific information, feel free to clarify, and I can look into it further.

On other occasions, ChatGPT has instead stated that Russell Poldrack and Wayne Poldrack are the same person, and even the latest Google Gemini 2.5 Pro provides a detailed description of a Wayne Poldrack who does not seem to exist. To restate the conclusion from the GPT-4 Technical Report stated in the Introduction: "Care should be taken when using the outputs of GPT-4, particularly in contexts where reliability is important."  

Fortunately, coding seems to be a best case scenario for the use of LLMs, since we can relatively easily write tests that can verify that the solutions generated by the system are correct.  This is the reason for our heavy focus on testing and test-driven development in this book, as you saw earlier in the book.

## AI coding approaches

As of the time of writing (Summer 2025) there are four primary approaches that one can use to take advantage of LLMs for coding: chatbots, integrated IDE assistants, API submission, and agentic coding tools.

### Chatbots

The first approach is the *chatbot* model, in which one uses an interactive chatbot interface (such as ChatGPT) to prompt the system.  This is the approach initially used for the coding prompts presented above, and can sometimes work well for generating code *de novo*, but I generally advise against it. The main reason for this is that it's not a particularly efficient way to interact with the LLM; given that one will almost certainly be using a code editor/IDE, the code from the chatbot will need to be copied there anyway. As we will note below, use of LLMs integrated into the IDE are also more effective because they allow fine-grained control of which code files are placed into the context of the model. 

Where I do often find chatbots useful is in reviewing code; I'll discuss this later when we dive more deeply into code review.

### IDE assistants

A second and probably most common model is the *IDE* model, where one uses a coding assistant that is integrated into one's IDE, such as Copilot for VSCode (my preferred choice).  This provides inline code completion suggestions as you type, as well as providing a chat window that allows the inclusion of selected code files into the model's context.  The IDEs also now include access to *coding agents*, which I will describe in more detail below.

One way to prompt the system within an IDE is by writing code comments, which then trigger code generation.  The following is the output generated by Copilot within VSCode when given the prompt in the comment at the top:

```
# generate a python function to compute a multiple linear regression solution using linear algebra

def multiple_linear_regression(X, y):
    """
    Compute the multiple linear regression solution using linear algebra.

    Parameters
    ----------
    X : numpy.ndarray
        The input data matrix with shape (n_samples, n_features).
    y : numpy.ndarray
        The target data vector with shape (n_samples,).

    Returns
    -------
    numpy.ndarray
        The regression coefficients with shape (n_features,).
    """
    # compute the regression coefficients
    return np.linalg.inv(X.T @ X) @ X.T @ y
    
```

Most IDEs now also present a chat window that provides access to LLMs that is integrated with the editor, providing the best of both worlds.  Importantly, the chatbot has the ability to load currently open code files into its context window, which allows it to give answers that are more directly relevant to the code.  For example, let's say that we have a Pandas dataframe that was generated from a data file, and we wish to select a particular set of rows and then sort by one of the columns.  Starting with the following code:

```
import pandas as pd

astro_data = pd.read_csv('data/astro.csv')
astro_data.columns = ['planet', 'distance', 'mass', 'diameter', 'moons']
```

We then open the Copilot chat window within VSCode while this code is in the active window, and give it the following prompt: "select planets with only one moon and then sort by distance", resulting in the addition of several lines:

```
import pandas as pd

astro_data = pd.read_csv('data/astro.csv')
astro_data.columns = ['planet', 'distance', 'mass', 'diameter', 'moons']

# Filter planets with only one moon
one_moon_planets = astro_data[astro_data['moons'] == 1]

# Sort by distance
sorted_planets = one_moon_planets.sort_values(by='distance')

print(sorted_planets)
```

Because the chat window has access to the code file, it was able to generate code that uses the same variable names as those in the existing code, saving time and prevent potential errors in renaming of variables.

When working with an existing codebase, the autocompletion feature of AI assistants provides yet another way that one can leverage their power seamlessly within the IDE.  In my experience, these tools are particularly good at autocompleting code for common coding problems where the code to be written is obvious but will take a bit of time for the coder to complete accurately.  In this way, these tools can remove some of the drudgery of coding, allowing the programmer to focus on more thoughtful aspects of coding.  They do of course make mistakes on occasion, so it's always important to closely examine the autocompleted code and apply the relevant tests.  Personally I have found myself using autocompletion less and less often, as the chat tools built into the IDE have become increasingly powerful. I also find them rather visually cluttery and distracting when I am coding.

### Programmatic access via API

Whenever one needs to submit multiple prompts to a language model, it's worth considering the use of programmatic access via API.  As an example, Jamie Cummins wrote in a [Bluesky post](https://bsky.app/profile/did:plc:iukzqhazgtp4mp2lfbitdtuz/post/3lsbyzwpq6c2y) about a [published study](https://doi.org/10.1073/pnas.2501823122) that seemingly performed about 900 experimental chats manually via ChatGPT, taking 4 people more than a week to complete.  Cummins pointed out in the thread that "if the authors had used the API, they could have run this study in about 4 hours".  Similarly, in our first experiments with GPT-4 coding back in 2023, I initially used the ChatGPT interface, simply because I didn't yet have access to the GPT-4 API, which was very scarce at the time.  Running the first set of 32 problems by hand took several hours, and there was no way that I was going to do the next set of experiments by hand, so I found someone who had access to the API, and we ran the remainder of the experiments using the API.  In addition to the time and labor of running things by hand, it is also a recipe for human error; automating as much as possible can help remove the chances of human errors.

You might be asking at this point, "What's an API"?  The acronym stands for "Application Programming Interface", which is a method by which one can programmatically send commands to and receive responses from a computer system, which could be local or remote[^1]. To understand this better, let's see how to send a chat command and receive a response from the Claude language model.  The full outline is in [the notebook](https://github.com/poldrack/BetterCodeBetterScience/blob/main/src/BetterCodeBetterScience/language_model_api_prompting.ipynb).  Coding agents are very good at generating code to perform API calls, so I used Claude Sonnet 4 to generate the example code in the notebook:

```python
import anthropic
import os

# Set up the API client
# Requires setting your API key as an environment variable: ANTHROPIC
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC")
)
```

This code first imports the necessary libraries, including the `anthropic` module that provides functions to streamline interactions with the model.  It then sets up a `client` object, which has methods to allow prompting and receiving output from the model. Note that we have to specify an "API key" to use the API; this is a security token that tells the model which account should be charged for usage of the model.  Depending on the kind of account that you have, you may need to pay for API access on a per-token basis, or you may have a specific allocation of tokens to be used in a particular amount of time; check with your preferred model provider for more information on this.

It might be tempting to avoid the extra hassle of specifying the API key as an environment variable by simply pasting it directly into the code, but you should **never** do this.  Even if you think the code may be private, it's all too easy for it to become public in the future, at which point someone could easily steal your key and rack up lots of charges.  See the section in Chapter 3 on [Coding Portably](https://poldrack.github.io/BetterCodeBetterScience/software_engineering.html#coding-portably) for more on the ways to solve this problem.

Now that we have the client specified, we can submit a prompt and examine the result:

```python
model = "claude-3-5-haiku-latest"
max_tokens = 1000 
prompt = "What is the capital of France?"

message = client.messages.create(
    model=model,
    max_tokens=max_tokens,
    messages=[
        {"role": "user", "content": prompt}
    ]
)
```

Examining the content of the `message` object, we see that it contains information about the API call and resource usage as well as a response:

```python
Message(
    id='msg_016H1QzGNPKdsLmXRZog78kU',
    content=[
        TextBlock(
            citations=None,
            text='The capital of France is Paris.',
            type='text'
        )
    ],
    model='claude-3-5-haiku-20241022',
    role='assistant',
    stop_reason='end_turn',
    stop_sequence=None,
    type='message',
    usage=Usage(
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0,
        input_tokens=14,
        output_tokens=10,
        server_tool_use=None,
        service_tier='standard'
    )
)
```

The key part of the response is in the `content` field, which contains the answer:  

```python
print(message.content[0].text)
```

```bash
"The capital of France is Paris."
```

#### Customizing API output

By default, the API will simply return text, just as a chatbot would. However, it's possible to instruct the model to return results in a format that is much easier to programmatically process.  The preferred format for this is generally JSON (JavaScript Object Notation), which has very similar structure to a Python dictionary. Let's see how we could get the previous example to return a JSON object containing just the name of the capital.  Here we will use a function called `send_prompt_to_claude()` that wraps the call to the model object and returns the text from the result:

```python
from BetterCodeBetterScience.llm_utils import send_prompt_to_claude

json_prompt = """
What is the capital of France? 

Please return your response as a JSON object with the following structure:
{
    "capital": "city_name",
    "country": "country_name"
}
"""

result = send_prompt_to_claude(json_prompt, client)
result
```

```bash
'{\n    "capital": "Paris",\n    "country": "France"\n}'
```

The result is returned as a JSON object that has been encoded as a string, so we need to convert it from a string to a JSON object:

```python
import json

result_dict = json.loads(result)
result_dict
```

```python
{'capital': 'Paris', 'country': 'France'}
```

The output is now in a standard Python dictionary format.  We can easily use this pattern to expand to multiple calls to the API.  Let's say that we wanted to get the capitals for ten different countries. There are two ways that we might do this.  First, we might loop through ten API calls with each country individually:

```python
countries = ["France", "Germany", "Spain", "Italy", "Portugal", "Netherlands", "Belgium", "Sweden", "Norway", "Finland"]

for country in countries:
    json_prompt = f"""
    What is the capital of {country}? 

    Please return your response as a JSON object with the following structure:
    {{
        "capital": "city_name",
        "country": "country_name"
    }}
    """
    result = send_prompt_to_claude(json_prompt, client)
    result_dict = json.loads(result)
    print(result_dict)
```

```python
{'capital': 'Paris', 'country': 'France'}
{'capital': 'Berlin', 'country': 'Germany'}
{'capital': 'Madrid', 'country': 'Spain'}
{'capital': 'Rome', 'country': 'Italy'}
{'capital': 'Lisbon', 'country': 'Portugal'}
{'capital': 'Amsterdam', 'country': 'Netherlands'}
{'capital': 'Brussels', 'country': 'Belgium'}
{'capital': 'Stockholm', 'country': 'Sweden'}
{'capital': 'Oslo', 'country': 'Norway'}
{'capital': 'Helsinki', 'country': 'Finland'}
```

Alternatively, we could submit all of the countries together in a single prompt. Here is the first prompt I tried:

```python
json_prompt_all = f"""
Here is a list of countries:
{', '.join(countries)}

For each country, please provide the capital city 
in a JSON object with the country name as the key 
and the capital city as the value.  
"""
result_all, ntokens_prompt = send_prompt_to_claude(
    json_prompt_all, client, return_tokens=True)
```

The output was not exactly what I was looking for, as it included extra text that caused the JSON conversion to fail:

```bash
'Here\'s the JSON object with the countries and their respective capital cities:\n\n{\n    "France": "Paris",\n    "Germany": "Berlin",\n    "Spain": "Madrid",\n    "Italy": "Rome",\n    "Portugal": "Lisbon",\n    "Netherlands": "Amsterdam",\n    "Belgium": "Brussels",\n    "Sweden": "Stockholm",\n    "Norway": "Oslo",\n    "Finland": "Helsinki"\n}'
```

This highlights an important aspect of prompting: One must often be much more explicit and detailed than you expect.  As the folks at Anthropic said in their [guide to best practices for coding using Claude Code](https://www.anthropic.com/engineering/claude-code-best-practices?curius=2107) (a product discussed further below): "Claude can infer intent, but it can't read minds. Specificity leads to better alignment with expectations."  In this case, we change the prompt to include an explicit directive to only return the JSON object:

```python
json_prompt_all = f"""
Here is a list of countries:
{', '.join(countries)}

For each country, please provide the capital city in a 
JSON object with the country name as the key and the 
capital city as the value.  

IMPORTANT: Return only the JSON object without any additional text.
"""
result_all, ntokens_prompt = send_prompt_to_claude(
    json_prompt_all, client, return_tokens=True)
```

```python
'{\n    "France": "Paris",\n    "Germany": "Berlin",\n    "Spain": "Madrid",\n    "Italy": "Rome",\n    "Portugal": "Lisbon",\n    "Netherlands": "Amsterdam",\n    "Belgium": "Brussels",\n    "Sweden": "Stockholm",\n    "Norway": "Oslo",\n    "Finland": "Helsinki"\n}'
```

Why might we prefer one of these solutions to the other?  One reason has to do with the amount of LLM resources required by each. If you look back at the full output of the client above, you will see that it includes fields called `input_tokens` and `output_tokens` that quantify the amount of information fed into and out of the model.  Because LLM costs are generally based on the number of tokens used, we would like to minimize this.  If we add these up, we see that the looping solution uses a total of 832 tokens, while the single-prompt solution uses only 172 tokens. At this scale this wouldn't make a difference, but for large analyses this could result in major cost differences for the two analyses.  Note, however, that the difference between these models in part reflects the short nature of the prompt, which means that most of the tokens being passed are what one might consider to be overhead tokens which are required for any prompt (such as the system prompt).  As the length of the user prompt increases, the proportional difference between looping and a single compound prompt will decrease.

It's also important to note that there is a point at which very long prompts may begin to degrade performance.  In particular, LLM researchers have identified a phenomenon that has come to be called *context rot*, in which performance of the model is degraded as the amount of information in context grows. [Analyses of performance as a function of context](https://research.trychroma.com/context-rot) have shown that model performance can begin to degrade on some benchmarks when the context extends beyond 1000 tokens and can sometimes degrade very badly as the context goes beyond 100,000 tokens.    Later in this chapter we will discuss *retrieval-augmented generation*, which is a method that can help alleviate the impact of context rot by focusing the context on the most relevant information for the task at hand.


[^1]: Confusingly, the term "API" is used in two different ways in different contexts.  In this chapter we are using it to refer to an actual system that one can interact with to send and receive messages.  However, in other contexts the term is used to refer to a specification for how to interact with a system.  For example, many software packages present an "API Reference" (for example, [scikit-learn](https://scikit-learn.org/stable/api/index.html)), which specifies the interfaces to all of the classes and functions in the package.  It's important to distinguish these two uses of the term to avoid confusion.  