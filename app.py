import sys
import os  # 用于操作系统相关的操作，例如读取环境变量
import io  # 用于处理流式数据（例如文件流）
import gradio as gr

from dotenv import load_dotenv, find_dotenv
from llm_sdk.call_llm import get_completion
from database.create_db import create_db_info
from qa_chain.chat_qa_chain_self import Chat_QA_Chain_Self
from qa_chain.qa_chain_self import QA_Chain_Self

load_dotenv(find_dotenv())
LLM_MODEL_DICT = {
    "openai": ["gpt-3.5-turbo", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0613", "gpt-4", "gpt-4-32k"],
    "baidu": ["ERNIE-4.0-8K", "ERNIE-3.5-8K", "ERNIE-3.5-8K-0205"],
    "spark": ["Spark-3.5", "Spark-3.0"],
    "zhipu": ["glm-4", "glm-4v", "glm-3-turbo"]
}

LLM_MODEL_LIST = sum(list(LLM_MODEL_DICT.values()), [])
INIT_LLM = "glm-4"
EMBEDDING_MODEL_LIST = ['openai', 'zhipu', 'm3e', 'gte']
INIT_EMBEDDING_MODEL = "openai"
# 关于法律问题的本地知识库和向量数据库的默认路径
DEFAULT_DB_PATH = "C:\\Users\YUI\PycharmProjects\TabLLM-Copilot\database\laws_knowledgebase"
DEFAULT_PERSIST_PATH = "C:\\Users\YUI\PycharmProjects\TabLLM-Copilot\database\chromadb\laws_vertordb_openai"
EXAMPLE_AVATAR_PATH = "doc/favicons/logo.png"
EXTRA_AVATAR_PATH = "doc/favicons/logo.png"
EXAMPLE_LOGO_PATH = "doc/favicons/logo.png"
EXTRA_LOGO_PATH = "doc/favicons/logo.png"


def get_model_by_platform(platform):
    return LLM_MODEL_DICT.get(platform, "")


class Model_Center():
    """
    存储问答 Chain 的对象

    - chat_qa_chain_self: 以 (model, embedding) 为键存储的带历史记录的问答链。
    - qa_chain_self: 以 (model, embedding) 为键存储的不带历史记录的问答链。
    """

    def __init__(self):
        self.chat_qa_chain_self = {}
        self.qa_chain_self = {}

    def chat_qa_chain_self_answer(self, question: str, chat_history: list = [], model: str = "openai",
                                  embedding: str = "openai", temperature: float = 0.0, top_k: int = 4,
                                  history_len: int = 3, file_path: str = DEFAULT_DB_PATH,
                                  persist_path: str = DEFAULT_PERSIST_PATH):
        """
        调用带历史记录的问答链进行回答
        """
        if question is None or len(question) < 1:
            return "", chat_history
        try:
            if (model, embedding) not in self.chat_qa_chain_self:
                self.chat_qa_chain_self[(model, embedding)] = Chat_QA_Chain_Self(model=model, temperature=temperature,
                                                                                 top_k=top_k, chat_history=chat_history,
                                                                                 file_path=file_path,
                                                                                 persist_path=persist_path,
                                                                                 embedding=embedding)
            chain = self.chat_qa_chain_self[(model, embedding)]
            return "", chain.answer(question=question, temperature=temperature, top_k=top_k)
        except Exception as e:
            return e, chat_history

    def qa_chain_self_answer(self, question: str, chat_history: list = [], model: str = "openai", embedding="openai",
                             temperature: float = 0.0, top_k: int = 4, file_path: str = DEFAULT_DB_PATH,
                             persist_path: str = DEFAULT_PERSIST_PATH):
        """
        调用不带历史记录的问答链进行回答
        """
        if question is None or len(question) < 1:
            return "", chat_history
        try:
            if (model, embedding) not in self.qa_chain_self:
                self.qa_chain_self[(model, embedding)] = QA_Chain_Self(model=model, temperature=temperature,
                                                                       top_k=top_k, file_path=file_path,
                                                                       persist_path=persist_path, embedding=embedding)
            chain = self.qa_chain_self[(model, embedding)]
            chat_history.append(
                (question, chain.answer(question, temperature, top_k)))
            return "", chat_history
        except Exception as e:
            return e, chat_history

    def clear_history(self):
        if len(self.chat_qa_chain_self) > 0:
            for chain in self.chat_qa_chain_self.values():
                chain.clear_history()


def format_chat_prompt(message, chat_history):
    """
    该函数用于格式化聊天 prompt。

    参数:
    message: 当前的用户消息。
    chat_history: 聊天历史记录。

    返回:
    prompt: 格式化后的 prompt。
    """
    # 初始化一个空字符串，用于存放格式化后的聊天 prompt。
    prompt = ""
    # 遍历聊天历史记录。
    for turn in chat_history:
        # 从聊天记录中提取用户和机器人的消息。
        user_message, bot_message = turn
        # 更新 prompt，加入用户和机器人的消息。
        prompt = f"{prompt}\nUser: {user_message}\nAssistant: {bot_message}"
    # 将当前的用户消息也加入到 prompt中，并预留一个位置给机器人的回复。
    prompt = f"{prompt}\nUser: {message}\nAssistant:"
    # 返回格式化后的 prompt。
    return prompt


def respond(message, chat_history, llm, history_len=3, temperature=0.1, max_tokens=2048):
    """
    该函数用于生成机器人的回复。

    参数:
    message: 当前的用户消息。
    chat_history: 聊天历史记录。

    返回:
    "": 空字符串表示没有内容需要显示在界面上，可以替换为真正的机器人回复。
    chat_history: 更新后的聊天历史记录
    """
    if message is None or len(message) < 1:
        return "", chat_history
    try:
        # 限制 history 的记忆长度
        chat_history = chat_history[-history_len:] if history_len > 0 else []
        # 调用上面的函数，将用户的消息和聊天历史记录格式化为一个 prompt。
        formatted_prompt = format_chat_prompt(message, chat_history)
        # 使用llm对象的predict方法生成机器人的回复（注意：llm对象在此代码中并未定义）。
        bot_message = get_completion(
            formatted_prompt, llm, temperature=temperature, max_tokens=max_tokens)
        # 将用户的消息和机器人的回复加入到聊天历史记录中。
        chat_history.append((message, bot_message))
        # 返回一个空字符串和更新后的聊天历史记录（这里的空字符串可以替换为真正的机器人回复，如果需要显示在界面上）。
        return "", chat_history
    except Exception as e:
        return e, chat_history


model_center = Model_Center()

block = gr.Blocks()
with block as demo:
    with gr.Row(equal_height=True):
        gr.Image(value=EXAMPLE_LOGO_PATH, scale=1, min_width=10, show_label=False, show_download_button=False,
                 container=False)

        with gr.Column(scale=2):
            gr.Markdown("""<h1><center>TabLLM-Copilot</center></h1>
                <h3><center>Maintained by Tsumugii https://github.com/Tsumugii24/TabLLM-Copilot 😊</center></h3>
                """)
        gr.Image(value=EXTRA_LOGO_PATH, scale=1, min_width=10, show_label=False, show_download_button=False,
                 container=False)

    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(height=400, show_copy_button=True, show_share_button=True,
                                 avatar_images=(EXAMPLE_AVATAR_PATH, EXTRA_AVATAR_PATH))
            # 创建一个文本框组件，用于输入 prompt。
            msg = gr.Textbox(label="your question", placeholder="Type your message here...", )

            with gr.Row():
                # 创建提交按钮。
                db_with_his_btn = gr.Button("Chat DB with history")
                db_wo_his_btn = gr.Button("Chat DB without history")
                llm_btn = gr.Button("Chat with LLM")
            with gr.Row():
                # 创建一个清除按钮，用于清除聊天机器人组件的内容。
                clear = gr.ClearButton(
                    components=[chatbot], value="Clear Console")

        with gr.Column(scale=1):
            file = gr.File(label='Knowledgebase Uploading', file_count='directory',
                           file_types=['.txt', '.md', '.docx', '.pdf'])  # todo .jpg .png .jpeg的添加和处理
            with gr.Row():
                init_db = gr.Button("Documents Vectorization")
            model_argument = gr.Accordion("Parameter Configuration", open=False)
            with model_argument:
                temperature = gr.Slider(0,
                                        1,
                                        value=0.01,
                                        step=0.01,
                                        label="llm temperature",
                                        interactive=True)

                top_k = gr.Slider(1,
                                  10,
                                  value=3,
                                  step=1,
                                  label="vectordb search top k",
                                  interactive=True)

                history_len = gr.Slider(0,
                                        5,
                                        value=3,
                                        step=1,
                                        label="history length",
                                        interactive=True)

            model_select = gr.Accordion("model selection", open=True)
            with model_select:
                llm = gr.Dropdown(
                    LLM_MODEL_LIST,
                    label="Large Language Model (ChatModel)",
                    value=INIT_LLM,
                    interactive=True)

                embeddings = gr.Dropdown(EMBEDDING_MODEL_LIST,
                                         label="Embedding Model",
                                         value=INIT_EMBEDDING_MODEL)

        # 设置初始化向量数据库按钮的点击事件。当点击时，调用 create_db_info 函数，并传入用户的文件和希望使用的 Embedding 模型。
        init_db.click(create_db_info,
                      inputs=[file, embeddings], outputs=[msg])

        # 设置按钮的点击事件。当点击时，调用上面定义的 chat_qa_chain_self_answer 函数，并传入用户的消息和聊天历史记录，然后更新文本框和聊天机器人组件。
        db_with_his_btn.click(model_center.chat_qa_chain_self_answer, inputs=[
            msg, chatbot, llm, embeddings, temperature, top_k, history_len], outputs=[msg, chatbot])
        # 设置按钮的点击事件。当点击时，调用上面定义的 qa_chain_self_answer 函数，并传入用户的消息和聊天历史记录，然后更新文本框和聊天机器人组件。
        db_wo_his_btn.click(model_center.qa_chain_self_answer, inputs=[
            msg, chatbot, llm, embeddings, temperature, top_k], outputs=[msg, chatbot])
        # 设置按钮的点击事件。当点击时，调用上面定义的 respond 函数，并传入用户的消息和聊天历史记录，然后更新文本框和聊天机器人组件。
        llm_btn.click(respond, inputs=[
            msg, chatbot, llm, history_len, temperature], outputs=[msg, chatbot], show_progress="minimal")

        # 设置文本框的提交事件（即按下Enter键时）。功能与上面的 llm_btn 按钮点击事件相同。
        msg.submit(respond, inputs=[
            msg, chatbot, llm, history_len, temperature], outputs=[msg, chatbot], show_progress="hidden")
        # 点击后清空后端存储的聊天记录
        clear.click(model_center.clear_history)
    gr.Markdown("""Tips：<br>
    1. You may upload your own directory of documents to create a knowledge base, otherwise we will use default knowledge base that comes with the project. <br>
    2. It may take a while to vectorize your documents, so please be patient. <br>
    3. If there is any error or abnormality while running, it will be displayed in the text input box, you can copy the info and open a github issue. <br>
    """)
# threads to consume the request
gr.close_all()
# 启动新的 Gradio 应用，设置分享功能为 True，并使用环境变量 PORT1 指定服务器端口。
# demo.launch(share=True, server_port=int(os.environ['PORT1']))
# 直接启动
# todo 编码问题 gbk / 使用ignore errors之后路径解析存在问题
demo.launch(inbrowser=True,  # 自动打开默认浏览器
            share=False,  # 项目暂不共享，其他设备目前不能访问
            favicon_path="C:\\Users\\YUI\\PycharmProjects\\TabLLM-Copilot\\doc\\favicons\\favicon.ico",  # 网页图标
            show_error=True,  # 在浏览器控制台中显示错误信息
            quiet=True,  # 禁止大多数打印语句
            )
