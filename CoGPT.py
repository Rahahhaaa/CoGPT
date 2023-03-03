from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

import openai
import argparse

import json

data_db = pd.read_csv("./data.csv")
app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Data(BaseModel):
    data: str = None,
    key: int = None,


@app.post("/add-data/")
async def add_data(item: Data):
    global data_db
    data_db = data_db.append({'data': item.data + '.'}, ignore_index=True)
    data_db.to_csv("./data.csv", index=False)


@app.post("/delete-data/")
async def delete_dat(item: Data):
    global data_db
    data_db.drop([data_db.index[item.key]], axis=0, inplace=True)
    data_db.to_csv("./data.csv", index=False)


@app.post("/modify-data/")
async def modify_data(item: Data):
    global data_db
    data_db.iloc[item.key, 0] = item.data
    data_db.to_csv("./data.csv", index=False)


@app.get("/data/")
async def data():
    res = json.loads(data_db.to_json(orient="records"))
    return res


@app.post("/question/")
async def question(item: Data):
    base_data = ""
    with open("./data.csv", encoding='UTF8') as data:
        line = data.readline()
        while True:
            line = data.readline()
            if not line:
                break
            base_data += line + "\n"
    return {"answer": create_answer(base_data, input_data=item.data)}


def chatGPT(prompt, API_KEY="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"):

    openai.api_key = API_KEY

    completion = openai.Completion.create(
        engine='text-davinci-003', prompt=prompt, temperature=0.5, max_tokens=1024, top_p=1, frequency_penalty=0, presence_penalty=0)

    return completion['choices'][0]['text']


def create_answer(base_data, input_data):
    data = base_data + "\n" + input_data

    prompt = data
    return chatGPT(prompt).strip()
