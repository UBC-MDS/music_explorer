from dash import Dash, html, dcc, Input, Output, State
import altair as alt
import dash_bootstrap_components as dbc
import pandas as pd

alt.data_transformers.disable_max_rows()

df = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-01-21/spotify_songs.csv", 
index_col=0).rename(
    columns={'playlist_genre': 'genre',  
    'duration_ms': 'duration(ms)', 'track_popularity':'popularity'}, inplace=False).dropna()

genre = sorted(list(df["genre"].dropna().unique()))


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


def plot_2(artist, genre, pop_range):
    """creating plot_2"""
    pop_min = pop_range[0]
    pop_max = pop_range[1]
    filtered_df = df.query("genre in @genre and popularity > @pop_min and popularity < @pop_max").copy()
    if artist == None:
        artist = filtered_df.groupby("track_artist")["track_artist"].size().nlargest(5).reset_index(name="count")["track_artist"].tolist()
    filtered_df = filtered_df.query("track_artist in @artist").copy()
    filtered_df["year"]= filtered_df["track_album_release_date"].str[:4]

    # Create plot 2 scatter
    chart = (
        alt.Chart(filtered_df)
        .mark_point(size=20)
        .encode(
            y=alt.Y("popularity", title="Popularity", scale = alt.Scale(zero=False)),
            x=alt.X("year", title="Year"),
            color=alt.Color("track_artist", title = "Artist", legend=None),
            tooltip=[alt.Tooltip("track_artist", title="Artist"), alt.Tooltip("track_name",title="Song title"), alt.Tooltip("genre",title="Genre")]
        )
    )
    # Use direct labels
    order = filtered_df.groupby(["track_artist","year"]).mean("popularity").reset_index().sort_values('year', ascending=False).drop_duplicates("track_artist").copy()
    text = (
        alt.Chart(order)
        .mark_text(dx=50)
        .encode(
            x=alt.X("year", title="Year"),
            y=alt.Y("popularity", title="Popularity"),
            text="track_artist",
            color="track_artist",
        )
    )
    
    # Adding plot 2 line
    chart = ((chart + (chart.mark_line(size=3).encode(
        y=alt.Y("mean(popularity)", title="Popularity"), 
        tooltip=[
            alt.Tooltip("track_artist", title="Artist"), 
            alt.Tooltip("mean(popularity)",title="Average popularity")
            ])) +text )
    .properties(width=400, height=250)
    .configure_axisX(labelAngle=-45, labelFontSize=12, titleFontSize=18)
    .configure_axisY(labelFontSize=16, titleFontSize=18))

    return chart.to_html()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server



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
                marks={0:{"label":"0"}, 50: {"label": "50"}, 100: {"label": "100"}}
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
               dbc.CardHeader(html.Label("What are the most prolific artists' popularity overtime (within the selected range)? Or specify artist name(s) of interest."), style={'font-size':16}),
               dcc.Dropdown(id="artist_names", multi=True),
            #    dbc.Input(id='artist_name', type='text', list='list-suggested-inputs', value='', placeholder="Enter a specifc artist name"),
            #    html.Div(id="warning"),
            #    html.Datalist(id='list-suggested-inputs', children=[html.Option(value=name) for name in  suggested_list]),

               html.Iframe(id="plot_2",
               style={'border-width': '10', 'width': '500px', 'height': '340px'})
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



# Receive input from user and create plot
@app.callback(
    Output('plot_bar', 'srcDoc'),
    #Output('plot_3','srcDoc'),
    Input('genre_checklist', 'value'),
    Input('pop_slider', 'value'),
)
def update_output(genre, pop_range):
    return plot_bar(genre, pop_range)

# Receive input from user and update dropdown list options
@app.callback(
    Output("artist_names", "options"),
    Input('genre_checklist', 'value'),
    Input('pop_slider', 'value'),
)
def update_multi_options(genre, pop_range):
    pop_min = pop_range[0]
    pop_max = pop_range[1]
    suggested_list = (
        df.query("genre in @genre and popularity > @pop_min and popularity < @pop_max")
        .copy()['track_artist'].explode().value_counts().reset_index(name="count")["index"].tolist())
    return [
        o for o in suggested_list
    ]
# Receive input from user & dropdown list and create plot 2
@app.callback(
    # Output("warning", "children"),
    Output('plot_2','srcDoc'), 
    Input('genre_checklist', 'value'),
    Input('pop_slider', 'value'),
    Input("artist_names", "value"),
)
def update_output(genre, pop_range, artist):
    return  plot_2(artist, genre, pop_range)

if __name__ == '__main__':
    app.run_server(debug=True)