# Workflow Management

- discuss fit-transform model somewhere

https://workflowhub.eu/


### Russ's First Law of Scientific Data Management

> "Don't use spreadsheets to manage scientific data."

In this chapter I will talk in detail about best practices for data management, but I start by discussing a data management "anti-pattern", which is the use of spreadsheets for data management.  Spreadsheet software such as Microsoft Excel is commonly used by researchers for all sorts of data management and processing operations.  Why are spreadsheets problematic?

- They encourage manual manipulation of the data, which makes the operations non-reproducible by definition.
- Spreadsheet tools will often automatically format data, sometimes changing things in important but unwanted ways.  For example, gene names such as "SEPT2" and "MARCH1" are converted to dates by Microsoft Excel, and some accession numbers (e.g., "2310009E13") are converted to floating point numbers.  An analysis of published genomics papers {cite:p}`Ziemann:2016aa` found that roughly twenty percent of supplementary gene lists created using Excel contained errors in gene names due to these conversions.
- It is very easy to make errors when performing operations on a spreadsheet, and these errors can often go unnoticed.  A well known example occurred in the paper  ["Growth in the time of debt"](https://www.nber.org/papers/w15639) by the prominent economists Carmen Reinhart and Kenneth Rogoff. This paper claimed to have found that high levels of national debt led to decreased economic growth, and was used as a basis for promoting austerity programs after the 2008 financial crisis.  However, [researchers subsequently discovered](https://academic.oup.com/cje/article/38/2/257/1714018) that the authors had made an error in their Excel spreadsheet, excluding data from several countries; when the full data were used, the relationship between growth and debt became much weaker. 
- Spreadsheet software can sometimes have limitations that can cause problems.  For example, the use of an outdated Microsoft Excel file format (.xls) [caused underreporting of COVID-19 cases](https://www.bbc.com/news/technology-54423988) due to limitations on the number of rows in that file format, and the lack of any warnings when additional rows in the imported data files were ignored.
- Spreadsheets do not easily lend themselves to version control and change tracking, although some spreadsheet tools (such as Google Sheets) do provide the ability to clearly label versions of the data.

I will occasionally use Microsoft Excel to examine a data file, but I think that spreadsheet tools should *never* be used as part of a scientific data workflow.



## Simple workflow management with Makefiles


## Workflow management systems for complex workflows


## Building a workflow management system from scratch
