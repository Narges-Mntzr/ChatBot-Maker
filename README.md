## ChatBot-Builder

In this project, we aim to develop a website where users can create their own chatbots for their specific data. Users start by entering their desired data (knowledge base) into the software and then create a chatbot that responds to user queries based on the entered data. Other users can engage in conversations with these created bots and ask them questions based on their content.

## Technologies we used in our project:

1.The main section of the project have been implemented using the Django framework. <br />
2.The database used in the project is PostgreSQL. (The ankane/pgvector image has been utilized for using the pgvector extension.)<br /><br />

## Users:

### Admin
The website admin has access to information about all users, bots, content, and created conversations, and can add, delete, or edit them.

### Chatbot Maker
A group of users to whom the website admin has granted access to create new bots. This group of users can view the bots and content they have created and, if necessary, edit them

### Normal User
This category includes all website users who can register on the site and, upon logging in, initiate new conversations with the available bots on the site. They can also view their previous conversations and continue the conversation if the bot is still active.

## Main Processes of the Website:

### Creating a New Chatbot
The main distinction of this site compared to others like chatGPT is evident at this stage. A group of users can create a chatbot for their business and place content relevant to their work in it. Then, all of that content is transformed into an array, and at each stage, the user's response is provided based on the most similar content.

### Home Page + Full Text Search
The first page the user sees consists of a list of past conversations. At this stage, the user can search through their conversations based on the sender's name and the text of the messages. In this search, not only the exact phrase but also all related root words are considered.

### Conversation Start
The user can continue their previous conversations or initiate a new one with any of the active bots at any time. After starting a conversation, each user message sent to the bot is first transformed into an array based on the content of the user's question. Then, the most similar content of the bot is identified using the specified algorithm and placed in the message's prompt structure as follows.

    "{self.related_botcontent.text}"
    Based on the above document and your own information, give a step-by-step and acceptable answer to the following question.
    Question: {self.text}

### Asking Questions and Receiving Answers
After preparing the question prompt, the question is sent to GPT according to the following structure, and after receiving the answer, it is displayed to the user.

    messages: system prompt + prompt of preQuestion + answer of preQuestion + prompt of this question
* The system prompt is determined by the bot creator at the time of bot creation and is always placed at the beginning of the messages. The system prompt specifies the considerations that the chatbot should take into account in its responses.


## OpenAI Methods
Further details regarding the interaction with OpenAI are explained below.

### embedding
After creation, the stored contents for the bot and messages are transformed into an array with 1536 dimensions using the 'text-embedding-ada-002' model. Subsequently, this array is stored using the pgvector extension.

### similarity
The similarity between user questions and contents is examined using the CosineDistance function, and the most similar content is placed alongside the question.

<p align="center">
  <img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/15d11df2d48da4787ee86a4b8c14551fbf0bc96a" width="800" height="100" alt="accessibility text">
</p>



### prompts
After finding the most similar content, a request is made to the gpt-3.5-turbo model. The request includes the saved system prompt in the bot, the user's previous question, the similar content, the model's previous response, the current user's question, and the related content.

### test similarity
The performance of the similarity function is measured using a dataset with 584 contents and questions. A test class has been written, which randomly selects 100 contents and adds them to a bot. It then starts asking these 100 questions, and for each question where the output of the similar_content function matches the content within the dataset, it increments the value of trueAnswers by one.

After completing one hundred questions, the value of trueAnswers is logged in the django.log file. The performance of this function in three test runs is as follows:

 | trueAnswers | 97/100 | 97/100 | 99/100 |
 | ----------- | ------ | ------ | ------ |

And the performance of the function was examined once on the entire dataset, resulting in the following output:

 | trueAnswers | 557/584 |
 | ----------- | ------- |

 ## Usage
 1. docker build -t DOCKER_IMAGE .
 2. set DOCKER_IMAGE and OPENAI_API_KEY in docker compose
 3. docker compose up -d