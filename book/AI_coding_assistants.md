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
