from pathlib import Path
import pandas as pd
from openai import OpenAI

system_prompt = """
我会提供一些我关注的新闻数据，以JsonArray的格式给你，示例如下：
[
    {
        "source": "{示例新闻来源}",
        "category": "{示例类别}",
        "pub_time": "{示例发布日期}",
        "title": "{示例标题}",
        "content": "{示例内容}"
    }
]
基于这些新闻数据，需要你通过仔细阅读分析，为我完成以下任务。
"""


def read_csv(file_str: Path):
    try:
        return pd.read_csv(file_str)
    except Exception as e:
        print(f"read csv failed: {file_str}, {e}")


def load_news(date_str: str, category: str):
    if category == 'all':
        data_path = Path.cwd() / "data" / date_str
    else:
        data_path = Path.cwd() / "data" / date_str / f"{category}.csv"
    print(f'load data {data_path}')
    if not data_path.exists():
        return None
    result = []
    if data_path.is_dir():
        for file in data_path.glob("**/*.csv"):
            item = read_csv(file)
            if item is not None:
                result.append(item)
    else:
        item = read_csv(data_path)
        if item is not None:
            result.append(item)
    return result


def analysis_chunk(chunk, key: str):
    try:
        if key == 'reasoning_content':
            return chunk.choices[0].delta.reasoning_content
        elif key == 'content':
            return chunk.choices[0].delta.content
    except Exception as e:
        print(f"analysis_chunk failed for {key}, {e}")


def generate_response(input_text: str,
                      prompt: str,
                      api_key: str,
                      base_url: str,
                      model_name: str):
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": f"{system_prompt}, 我的任务是：{prompt}"},
            {"role": "assistant", "content": "好呀，请你提供一些相关的新闻，这样我就能按照要求进行分析啦。"},
            {"role": "user", "content": f"新闻数据如下，开始完成你的任务：{input_text}"},
        ],
        temperature=0.6,
        stream=True
    )
    thinking = False
    try:
        for chunk in response:
            if reasoning_content := analysis_chunk(chunk, 'reasoning_content'):
                if not thinking:
                    thinking = True
                    yield "<思考中>"
                yield reasoning_content
            elif content := analysis_chunk(chunk, 'content'):
                if thinking:
                    thinking = False
                    yield "</思考结束>"
                yield content
    except Exception as e:
        print(f"出现错误：{e}")
