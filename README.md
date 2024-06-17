# Bank of Italy AI based report generator software

The core feature of the Bank of Italy AI-Based Report Generator software is its AI-powered article and audio-derived text summarization capabilities. Leveraging the advanced capabilities of ChatGPT 4.0 (Da Vinci 2.0), the software scrapes real-time articles from various domestic sources (Japan in this peculiar case) based on specified topics. It then processes these articles to generate concise and informative summaries, enabling users to stay informed with the latest news and make data-driven decisions with ease. A similar elaboration process is then applied to audio tracks, from which a textual input is extracted and provided to the AI for further analysis. Eventually, the program is also equipped with textual sentiment analysis features through the deployment of the Natural Language Toolkit (NLTK) package and the Loughran McDonald Sentiment Dictionary.


## Data Retrieval:
The Bank of Italy AI-Based Report Generator software boasts powerful data retrieval capabilities, enabling users to access the latest information from trusted sources. Three key API keys are utilized to connect to essential datasets:
- **eStat Japan API Key**: Provides access to comprehensive data from eStat Japan, a valuable resource for economic and demographic statistics in Japan.
- **FRED API Key**: Grants access to the Federal Reserve Economic Data (FRED), a vast repository of economic data maintained by the Federal Reserve Bank of St. Louis.
- **World Bank API Key**: Enables access to the World Bank's extensive database, offering a wealth of economic, social, and environmental data from around the world.
With these API keys securely integrated into the software, users can effortlessly retrieve the latest datasets from eStat Japan, FRED, and the World Bank, ensuring that all data remain current and accurate.


## Data Plotting:
Once data is retrieved, the software offers intuitive data plotting functionalities, allowing users to visualize trends and patterns effortlessly. Graphs and tables are dynamically generated based on the retrieved datasets, providing users with clear and insightful visual representations of the data.


## AI-Powered Article Summarization:
The core feature of the Bank of Italy AI-Based Report Generator software is its AI-powered article summarization capabilities. Leveraging the advanced capabilities of ChatGPT 4.0 (Da Vinci 2.0), the software scrapes real-time articles from various sources based on specified topics. It then processes these articles to generate concise and informative summaries, enabling users to stay informed with the latest news and make data-driven decisions with ease. With its seamless integration of data retrieval, plotting, and AI-powered summarization, the Bank of Italy AI-Based Report Generator software is poised to revolutionize the way reports are generated and insights are derived. Thank you for your interest in our project, and we look forward to your exploration and feedback.

## Textual Sentiment Analysis
The project aims to conduct textual analysis of the BoJ Monetary Policy Reports through the deployment of Python-based software. First, we develop a web scraping script to extract textual data from the BoJ's website. Subsequently, we use the Natural Language Toolkit (NLTK) package to preprocess the text, including tokenization, stemming, and converting words to lowercase. Next, the Loughran McDonald Sentiment Dictionary is employed to transform the cleaned qualitative text data into a quantitative measure of the BoJ's communication tone. This communication measure is then be regressed against the output gap and inflation gap, obtained via API, to assess the sensitivity of the FED's communication to these macroeconomic variables. Throughout the project, we employ various visualisation and analysis packages to explore the data and conduct preliminary analysis.
