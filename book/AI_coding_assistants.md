# Coding with AI

## Using AI coding assistants

The advent of AI coding assistants based on large language models (LLMs) has fundamentally changed the landscape of computer programming.  Until Github released its Copilot AI assistant in 2021, most coders leaned heavily on internet searches, and at some point there was a meme that computer programming would be officially renamed "Googling Stackoverflow" (a popular question-and-answer site for programming questions).  With integrated AI coding assistants, the language model (which has ingested large amounts of text including Stack Overflow) can synthesize answers much more quickly than one could find them by searching online. 

In the previous chapter we described the concepts behind the LLMs that coding assistants are based upon.  Early coding assistants (like OpenAI's Codex) used models that had been trained specifically on large amounts of source code, but the developers of language models subsequently realized that training their models on code seemed to actually help them do a better job on non-coding tasks.  Subsequently, large models such as GPT-4o and Claude 3.5 Sonnet are now trained on large amounts of code and non-code text and can perform well on both coding and non-coding tasks.   

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

This is effectively the same as the previous code, but you can see differences in the function, such as the presence of a docstring and use of a different variable name. This highlights the fact that there is a degree of randomness in the outputs of an LLM (as discussed in the previous chapter), but the results seem fairly close here in terms of the computation itself. 

Now let's see an example of in-context learning. As we discussed previously, this is a form of learning that occurs within a single chat session, through the buildup of information across the session.  We start a new chat window, in which we first give the following prompts:  "why are type hints important when creating a python function?", followed by "Please give an example of how to use type hints effectively".  We then provide the same prompt as above for a linear algebra function, with the following result:

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

Unlike the previous examples, the code now includes type hints.  It's always a bad idea to generalize from a single result, so we ran these prompts through ChatGPT 10 times each (using the openai API to generate them programmatically; see the [notebook](../src/coding_for_science/incontext_learning_example.ipynb)).  Here are the function signatures generated for each of the 10 runs without mentioning type hints:

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

Note a couple of interesting things here.  First, 9 out of the 10 signatures here include type hints, showing that introducing the idea of type hints into the context changed the result even using the same code generation prompt. Second, notice that the function signatures differ much more from one to another in terms of the names of the functions and variables. Third, notice that on Run 3 it seems to have generated incorrect code, which we can confirm by looking at the full function that was generated on that run:

```
def compute_average(numbers: List[int]) -> float:
    return sum(numbers) / len(numbers)
```

In this case the LLM simply misunderstood the problem that was being solved, highlighting that one can't simply take the results from LLMs at face value

## Cautions regarding large language models

LLMs remain controversial for several reasons.  First, they are known to perpetuate the biases that exist in human language. A large body of research has shown that these models tend to demonstrate bias towards gender and racial minorities, and in general to perpetuate stereotypes that are present in human language.  The models have in some cases been fine-tuned to avoid this, but the biases nonetheless still persist.  Second, there are ongoing arguments regarding whether some models have misused copyrighted materials, or violated the license terms of open-source software.

Most importantly, there are continuing concerns regarding the tendency of LLMs to generate inaccurate material, which has come to be known as "hallucination".  One of us (RP) has been continually amused at the inability of ChatGPT to distinguish between himself and his father, Wayne Poldrack, a retired accountant and not a neuroscientist.  Given the prompt "Who is Wayne Poldrack", GPT-4o responds:

>Wayne Poldrack is a prominent neuroscientist and psychologist known for his work in cognitive neuroscience, neuroinformatics, and open science. He has made significant contributions to understanding brain function, particularly in areas like decision-making, learning, and memory, using neuroimaging techniques such as functional MRI (fMRI). Poldrack is also an advocate for open science and reproducibility in research, promoting the sharing of data and methods to improve scientific transparency.

> One of his most influential contributions is the development of the OpenNeuro platform, which provides free and open access to brain imaging data, allowing researchers worldwide to share, analyze, and collaborate on neuroimaging studies. Poldrack has also been involved in efforts to improve data-sharing standards in the field and has published extensively on topics related to brain function and the methodology of neuroscience research.

> As of recent years, he has been a professor at Stanford University, where he continues to lead research initiatives in cognitive neuroscience, and neuroimaging, and the use of data science techniques in understanding brain processes.


When further prompted "Who is Russell Poldrack?", it continues:

> It seems there might be some confusion here, as Wayne Poldrack is the well-known neuroscientist, and there is no widely recognized individual named “Russell Poldrack” in the fields of neuroscience, psychology, or related disciplines. If you’re referring to someone connected to Wayne Poldrack or seeking more specific information, feel free to clarify, and I can look into it further.

On other occasions, ChatGPT has instead stated that Russell Poldrack and Wayne Poldrack are the same person.  To restate the conclusion from the GPT-4 Technical Report stated in the Introduction: "Care should be taken when using the outputs of GPT-4, particularly in contexts where reliability is important."  

Fortunately, coding seems to be a best case scenario for the use of LLMs, since we can relatively easily write tests that can verify that the solutions generated by the system are correct.  This is the reason for our heavy focus on testing and test-driven development in this book; see Chapter XXX for more.

## AI assistant workflows

There are two primary workflows that one can use to take advantage of LLMs for coding.  The first is the *chatbot* model, in which one uses an interactive chatbot interface (such as ChatGPT) to prompt the system.  This is the approach initially used for the coding prompts presented above, and can sometimes work well for generating code *de novo*.  Alternatively, one can use the integrated AI assistant features of one's IDE, which will generally allow one to prompt the system by writing code comments.  The following is the output generated by Copilot within VSCode when given the prompt in the comment at the top:

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

Most IDEs now present a chat window that provides access to LLMs that is integrated with the editor, providing the best of both worlds.  Importantly, the chatbot has the ability to load currently open code files into its context window, which allows it to give answers that are more directly relevant to the code.  For example, let's say that we have a Pandas dataframe that was generated from a data file, and we wish to select a particular set of rows and then sort by one of the columns.  Starting with the following code:

```
import pandas as pd

astro_data = pd.read_csv('data/astro.csv')
astro_data.columns = ['planet', 'distance', 'mass', 'diameter', 'moons']
```

We then open the Copilot chat window within VSCode while this code is in the active window, and give it the following prompt: "select planets with only one moon and then sort by distance", resulting in:

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

When working with an existing codebase, the autocompletion feature of AI assistants provides yet another way that one can leverage their power seamlessly within the IDE.  In our experience, these tools are particularly good at autocompleting code for common coding problems where the code to be written is obvious but will take a bit of time for the coder to complete accurately.  In this way, these tools can remove some of the drudgery of coding, allowing the code to focus on more thoughtful aspects of coding.  They do of course make mistakes on occasion, so it's always important to closely examine the autocompleted code and apply the relevant tests.


## Language model prompting

The ability to leverage the power of language models for coding depends heavily on one's ability to effectively prompt them, whether using a chatbot or an integrated LLM assistant.  The most important aspect of prompting is to give the model sufficient context so that it can narrow its probability distribution over answers to the specific domain of interest.  Here are some basic prompting strategies that can enhance the effectiveness of AI-assisted coding; note that the development of prompting strategies rapidly developing, and that these may well outdated by the time of publication.

- few-shot prompting with examples

- prompt formatting with delimiters

- chain of thought


## Leveraging LLM coding for reproducibility

LLM-based chatbots can be very useful for solving many problems beyond coding.  For example, we recently worked on a paper with more than 100 authors, and needed to harmonize the affiliation listings across authors.  This would have been immensely tedious for a human, but working with an LLM we were able to solve the problem with only a few manual changes needed.  Other examples where we have used LLMs in the research process include data reformatting and summarization of text for meta-analyses.  However, as noted above, the use of chatbots in scientific research is challenging from the standpoint of reproducibility, since it is generally impossible to guarantee the ability to reproduce an LLM output; even if the random seed is fixed, the commercial models change regularly, without the ability to go back to a specific model version.  

The ability to LLMs to write code to solve problems provides a solution to the reproducibility challenge: instead of simply using a chatbot to solve a problem, ask the chatbot to generate code to solve the problem, which makes the result testable and reproducible.  This is also a way to solve problems with information that you don't want to submit to the LLM for privacy reasons.

For example, ...


## AI Agents for software development

- Claude code

