## for Intro

- discuss Naur, "Programming as theory building"

## from AI-assisted coding chapter

## github spec kit

## More on MCP?

## AI-human pair programming

We often view AI coding agents as autonomous 

## Leveraging LLM coding for reproducibility

LLM-based chatbots can be very useful for solving many problems beyond coding.  For example, we recently worked on a paper with more than 100 authors, and needed to harmonize the affiliation listings across authors.  This would have been immensely tedious for a human, but working with an LLM we were able to solve the problem with only a few manual changes needed.  Other examples where we have used LLMs in the research process include data reformatting and summarization of text for meta-analyses.  However, as noted above, the use of chatbots in scientific research is challenging from the standpoint of reproducibility, since it is generally impossible to guarantee the ability to reproduce an LLM output; even if the random seed is fixed, the commercial models change regularly, without the ability to go back to a specific model version.  

The ability to LLMs to write code to solve problems provides a solution to the reproducibility challenge: instead of simply using a chatbot to solve a problem, ask the chatbot to generate code to solve the problem, which makes the result testable and reproducible.  This is also a way to solve problems with information that you don't want to submit to the LLM for privacy reasons.

For example, ...

