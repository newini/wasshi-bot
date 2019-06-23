#!/usr/bin/env python3
# -*- coding: utf-8 -*
from configs.imports import *

PAGE_NAME = "plot_graph"

plot_graph_api = Blueprint('plot_graph_api', __name__)

@plot_graph_api.route("/plot_graph", methods=['GET'])
def plot_graph():
    text = []
    if request.args.get("city"): city = request.args.get("city")
    if request.args.get("x"): x = request.args.getlist("x")
    if request.args.get("y"): y = request.args.getlist("y")
    if request.args.get("text"): text = request.args.getlist("text")

    if not city or not x or not y: return "ERROR!"

    graph = dict(
            data = [
                dict(
                    x = x,
                    y = y,
                    type="scatter",
                    name = city,
                    mode='lines+markers+text',
                    text=text,
                    textposition='top center',
                    textfont=dict(
                        family='sans serif',
                        size=32,
                        color='#ff7f0e'
                    )
                )
            ]
        )
    layout = dict(
            title = "Weather of " + city,
            titlefont = dict(
                    size = 18
                ),
            xaxis = dict(
                title = 'Date',
                nticks = 4,
                    titlefont = dict(
                            size = 18
                        ),
                    tickfont = dict(
                            size = 18
                        )
                ),
            yaxis = dict(
                    ticksuffix = '°C',
                    title = 'Temperature',
                    titlefont = dict(
                            size = 18
                        ),
                    tickfont = dict(
                            size = 18
                        )
                ),
            legend = dict(
                    font = dict(
                            size = 18
                        )
                )
        )

    graph_json = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)
    layout_json = json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder)

    figure = Figure(data=graph, layout=layout)
    plotly.plotly.image.save_as(figure, filename='tmp/'+city, format='jpeg')
    #plotly.io.write_image(figure, "tmp/"+city+"ho", format="jpeg") # Need plotly-orca installed by conda!

    return render_template("plot_graph.html", graph_json=graph_json, layout_json=layout_json)
