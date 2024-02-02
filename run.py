#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import typing as t

import html
import gradio as gr
from dotenv import load_dotenv
from googletrans import Translator
from openai import OpenAI

# Parse a .env file and then load all the variables found as environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -----
# OpenAI API Key, get yours here: https://platform.openai.com/api-keys
# -----
openai_api_key = os.getenv("API_KEY")

# -----
# Support Functions
# -----
def load_data() -> t.Dict[str,str]:
    """
    Load data for the program.

    This function should be replaced by the user to suit their needs.
    According to the default config, this function should not take in any parameters.
    This function must return a dictionary data type for the program to work.

    Returns:
        dict: A dictionary containing data for the program.
            Keys are Sinhala phrases and values are their corresponding English translations.
    """
    data = {
            "දීර්ග බෙදීම": "long division",
            "මගින්": "using it",
            "බහුපද": "polynomials",
            "ප්‍රකාශනයන්": "expressions",
            "ශේෂය": "remainder",
            "ලබ්ධිය": "quotient",
        }
    return data

def load_prompt() -> str:
    txt = "**Math Question Correction:**\n\n " 
    txt += "Please correct the following math question. "
    txt += "The question is originally in Sinhala but has been translated into English. "
    txt += "Ensure the grammar, syntax, and clarity of the question. "
    txt += "Also, make sure the question has proper meaning. "
    txt += "If there are any mathematical errors, correct them as well. "
    txt += "Your response should be a properly formatted math question. "
    txt +=  "\n\n**Original Question (Translated from Sinhala):**\n\n"
    txt += "(This is for Sri Lankan GCE Andvanced Level High School Examination). "
    txt += "Dont add anything additional. "
    txt += "This prompt might not include the questions, and it may be a part of a question, so, just keep that in mind. "
    txt += "These are questions. Make sure the question makes sense. "
    txt += "You may swap its order or order of words if needed."
    txt += "\"{prompt}\""
    txt += "\n\n**Corrected Question:**\n\n"
    
    return txt


client = OpenAI(api_key=openai_api_key)

data = load_data()

def translate_words(text: str):
    try:
        translator = Translator()
        translation = translator.translate(text, src='si', dest='en')
        return translation.text
    except Exception as e:
        logging.error(f"Translation failed: {e}")
        return None


def replace_words(text: str):
    try:
        for k, v in data.items():
            text = text.replace(k, v)
        return text
    except Exception as e:
        logging.error(f"Word replacement failed: {e}")
        return None


def ai(prompt: str):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": load_prompt().format(prompt=prompt),
                }
            ],
            model="gpt-4-0125-preview",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"AI completion failed: {e}")
        return None


def main(prompt: str):
    try:
        # Sanitize user input
        sanitized_prompt = html.escape(prompt)
        
        replaced = replace_words(text=sanitized_prompt)
        if replaced is None:
            return "Error occurred during word replacement."
        
        translated = translate_words(replaced)
        if translated is None:
            return "Error occurred during translation."
        
        fixed = ai(translated)
        if fixed is None:
            return "Error occurred during AI completion."
        
        return fixed
    except Exception as e:
        logging.error(f"Main function failed: {e}")
        return "An error occurred."


iface = gr.Interface(
    fn=main, 
    inputs="text", outputs="text",
    title="Sinhala Math Question to English Translator",
    description="Translate Sinhala math questions from Sinhala to English for Sri Lankan GCE Advanced Level Examination.",
    examples=[
        ["දීර්ග බෙදීම මගින් පහත බහුපද ඉදිරියෙන් දැක්වෙන ප්‍රකාශනයන් බෙදූ විට ලැබෙන ශේෂය හා ලබ්ධිය සොයන්න"]
    ],
    allow_flagging=True,
    flagging_dir="flagged",
    api_name="translate",
)
iface.launch()