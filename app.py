import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_openai_output_table(prompt):
    """Returns the output of the OpenAI API. """
    response_table = openai.Completion.create(
        model='text-davinci-003',
        prompt=prompt,
        temperature=0,
        max_tokens=2000,
    )
    return response_table.choices[0].text


def get_openai_output_text(country):
    """Returns the output of the OpenAI API. """
    response_table = openai.Completion.create(
        model='text-davinci-003',
        prompt=f"""Act as if you are a travel agent. Someone is going on a solo backpacking trip to {country}. 
        Write a catchy text that could be in a travel booklet with all the most important information about this 
        country. Include for example the local language, currency, safety issues, the weather, and any other things 
        that you find important. Include some fun trivia about the country.""",
        temperature=0.3,
        max_tokens=2000,
    )
    return response_table.choices[0].text


def get_openai_output_title(country):
    """Returns the output of the OpenAI API. """
    response_table = openai.Completion.create(
        model='text-davinci-003',
        prompt=f"""Think of a enthusing title for a travel guide for a solo backpacking trip. Example: Gorgeous 
        Guatemala, Exploring Estonia, Alpine Adventures, Getting lost in Lithuania. Do this for {country}""",
        temperature=0
    )
    return response_table.choices[0].text


def get_openai_output_packinglist(prompt):
    """Returns the output of the OpenAI API. """
    response_table = openai.Completion.create(
        model='text-davinci-003',
        prompt=f"""Write the output of the following question in HTML list format. Read the following travel guide: {prompt}. For this trip, generate an extensive, complete packing list. Include essentials, but also some comfort items (e.g. neck pillow) and some fun items (e.g. a small game).""",
        temperature=0,
        max_tokens=1000
    )
    return response_table.choices[0].text


def generate_prompt_table(country, days, budget_accommodation, budget_activities, hotel_requirement,
                          restaurant_budget, restaurant_best, car):
    res = f"""Write the output of the following question in HTML table format, with one day per row.
    Plan a solo backpacking trip in {country} for {days} days.
    For each day, specify the location of the trip.  
    For each day, suggest accommodation including the cost, my budget is {budget_accommodation}$ per day."""
    if hotel_requirement:
        res = res + f"""Recommend only hotels with three stars or better. """

    res = res + f"""At each location, suggest activities including the cost, my budget is {budget_activities}$ per day. """
    if restaurant_budget:
        res = res + f"""Recommend a budget-friendly place to eat at every location"""
    if restaurant_budget and restaurant_best:
        res = res + f""" and """
    if restaurant_best:
        res = res + f"""recommend a top-rated place to eat at every location"""
    res = res + f""". I do """
    if not car:
        res = res + f"""not"""
    res = res + f""" have a car. Add total cost of the trip at the bottom of the table. """

    return res


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        country = request.form["country"]
        days = request.form["days"]
        budget_accommodation = request.form["budget_accomodation"]
        budget_activities = request.form["budget_activities"]
        reqs = request.form.getlist('reqs')
        hotel_requirement = restaurant_budget = restaurant_best = car = False
        if 'hotel_requirement' in reqs:
            hotel_requirement = True
        if 'restaurant_budget' in reqs:
            restaurant_budget = True
        if 'restaurant_best' in reqs:
            restaurant_best = True
        if 'car' in reqs:
            car = True

        prompt = generate_prompt_table(country, days, budget_accommodation, budget_activities, hotel_requirement,
                                       restaurant_budget, restaurant_best, car)
        table = get_openai_output_table(prompt)
        text = get_openai_output_text(country)
        title = get_openai_output_title(country)
        packing_list = get_openai_output_packinglist(text)
        return redirect(url_for("index", table=table, text=text, title=title, packing_list=packing_list))

    table = request.args.get("table")
    text = request.args.get("text")
    title = request.args.get("title")
    packing_list = request.args.get("packing_list")
    return render_template("index.html", table=table, text=text, title=title, packing_list=packing_list)
