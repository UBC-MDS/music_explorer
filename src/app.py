from dash import Dash, html, dcc, Input, Output
import altair as alt
import dash_bootstrap_components as dbc
import pandas as pd

alt.data_transformers.disable_max_rows()

df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-01-21/spotify_songs.csv", 
index_col=0).rename(
    columns={'playlist_genre': 'genre',  
    'duration_ms': 'duration(ms)', 'track_popularity':'popularity'}, inplace=False)

genre = sorted(list(df["genre"].dropna().unique()))
#subgenre = sorted(list(df["subgenre"].dropna().unique()))

# plot bar plot for genres
def plot_bar(genre,pop_range):
    plot_df = df[df.genre.isin(genre)]

    pop_min = pop_range[0]
    pop_max = pop_range[1]


    chart = (
        (
            alt.Chart(plot_df[plot_df["popularity"].between(pop_min,pop_max)])
            .mark_bar(opacity=0.7)
            .encode(
                y=alt.Y("genre", title="Genre", sort="-x"),
                x="count()",
                color="genre",
                tooltip='count()'
            ).interactive()
        )
        .properties(width=400, height=250)
        .configure_axis(labelFontSize=20, titleFontSize=20)
    )
    return chart.to_html()


#app Dash and server
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


#Layout
app.layout = dbc.Container([
    dbc.Row(
        html.Div(html.H1(children="Spotify Music Explorer",
            style={'font-size': "300%", 'color':'#107a53','text-aligh':'center'}),
        )),
    html.Br(),
   dbc.Row([
       dbc.Col([
           #Slider and checklist
           dbc.Card([
               dbc.CardHeader(
                   html.Label("What kinds of music do you like to explore?",
                   style={"font-size":16})),
               dbc.CardBody([
                   dcc.Loading([
           html.Div(
               html.P("Popularity range"),
                style={'text_aligh': 'left', 'color': '#0c5e45', 'font-family': 'sans-serif'}),
           html.Br(),
           dcc.RangeSlider(
               #className="slider_class",
                id="pop_slider",
                #count=1,
                #step=1,
                min=0,
                max=100,
                value=[50, 100],
                marks={0:{"label":"0"}, 25:{"label":"25"}, 50: {"label": "50"}, 75:{"label":"75"}, 100: {"label": "100"}}
                ),
            html.Br(),
            html.Div(html.P("Select the music genre"),
            style={'text_aligh': 'left', 'color': '#0c5e45', 'font-family': 'sans-serif'}),
            #html.Br(),
            dcc.Checklist(
                id="genre_checklist",                    
                className="genre-container",
                inputClassName="genre-input",
                labelClassName="genre-label",
                options=[{"label": i, "value": i} for i in genre],                        
                value=["pop","rock"],
                labelStyle={"display":"block",
                            "margin-left": "10px"}),
            ])
            ])
            ])
        ]),
        html.Br(), 
        #plot graphs
       dbc.Col([
            dbc.Card([
               dbc.CardHeader(html.Label("How many songs in the genres selected?",style={"font-size":16})),
               html.Iframe(
                   id = "plot_bar",
                   srcDoc = plot_bar(genre=["pop","rock"], pop_range=[50,100]),
                   style={'border-width': '10', 'width': '500px', 'height': '340px'})      
           ])
        ])
        ]),
   html.Br(),
  dbc.Col([
   dbc.Row([
       dbc.Col([
           dbc.Card([
               dbc.CardHeader(html.Label("plot 2"), style={'font-size':16}),
               html.Iframe(id="plot_2",style={"width" : "200%", "height":"300px"})
           ])
       ]),

       dbc.Col([
           dbc.Card([
               dbc.CardHeader(html.Label("plot 3"), style={'font-size':16}),
               html.Iframe(id="plot_3",style={'width': '200%', 'height': '300px'})
           ])
       ])

   ])
  ])

])

@app.callback(
    Output('plot_bar', 'srcDoc'),
    Input('genre_checklist', 'value'),
    Input('pop_slider', 'value')
    
)



def update_output(genre, pop_range):
    return plot_bar(genre, pop_range)

if __name__ == '__main__':
    app.run_server(debug=True)