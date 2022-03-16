from dash import Dash, html, dcc, Input, Output, callback
import altair as alt
import dash_bootstrap_components as dbc
import pandas as pd

alt.data_transformers.disable_max_rows()

df = pd.read_csv("https://raw.githubusercontent.com/UBC-MDS/music_explorer/main/data/spotify_songs.csv", 
index_col=0).rename(
    columns={'playlist_genre': 'genre',  
    'duration_ms': 'duration(ms)', 'track_popularity':'popularity'}, inplace=False).dropna()

genre = sorted(list(df["genre"].dropna().unique()))
features = ["danceability","energy","mode","speechiness","acousticness","liveness","valence","loudness"]


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
                color=alt.Color("genre",legend=None),
                tooltip='count()'
            ).interactive()
        )
        .properties(width=370, height=250)
        .configure_axis(labelFontSize=20, titleFontSize=20)
        .configure_view(fill='#E4EBF5')
    )
    return chart.to_html()


#app Dash and server
def plot_2(artist, genre, pop_range):
    """creating plot_2"""
    pop_min = pop_range[0]
    pop_max = pop_range[1]
    filtered_df = df.query("genre in @genre and popularity > @pop_min and popularity < @pop_max").copy()
    if artist == None or artist == []:
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
            
            color=alt.Color("track_artist", title = "Artist", legend=None, scale=alt.Scale(scheme='dark2')),
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
    .properties(width=370, height=250)
    .configure_axisX(labelAngle=-45, labelFontSize=12, titleFontSize=18)
    .configure_axisY(labelFontSize=16, titleFontSize=18)
    .configure_view(fill='#E4EBF5')
    )
    

    return chart.to_html()


#Plot 3 scatter

def plot_3(feature, genre, pop_range):
    """creating plot_3"""
    pop_min = pop_range[0]
    pop_max = pop_range[1]
    #filtered_df = df.query("genre in @genre and popularity > @pop_min and popularity < @pop_max").copy()

    plot_df = df[df.genre.isin(genre)]
    if feature == None or feature == []:
        feature = "danceability"
   
    chart = ((alt.Chart(plot_df[plot_df["popularity"].between(pop_min,pop_max)]).mark_point(opacity=0.2, size=18).encode(
        x=alt.X(feature, title=feature.capitalize()),
        y=alt.Y("popularity", title="Popularity", scale = alt.Scale(zero=False)),
        color='genre',
        tooltip=[alt.Tooltip("genre", title="Genre"),
        alt.Tooltip("track_name",title="Song title"),
        alt.Tooltip("track_artist", title="Artist")]).interactive()
    ).properties(width=370, height=250)
    ).configure_axis(labelFontSize=20, titleFontSize=20).configure_view(fill='#E4EBF5')

    return chart.to_html()


app = Dash(__name__, title = "Music Explorer", external_stylesheets=[dbc.themes.MORPH])
server = app.server
#Layout


app.layout = dbc.Container([
            dbc.Toast(
            [html.A(
                "GitHub",
                href="https://github.com/UBC-MDS/music_explorer",
                style={ "text-decoration": "underline"},
            ),
            html.P(
                "The dashboard was created by Dongxiao Li, Rong Li, Zihan Zhou. It is licensed under the terms of the MIT license."
            ),
            html.A(
                "Data",
                href="https://raw.githubusercontent.com/UBC-MDS/music_explorer/main/data/spotify_songs.csv",
                style={"text-decoration": "underline"},
            ),
            html.P(
                "The dataset was derived from the open Spotify music database."
            ),],
            id="toast",
            header="About",
            is_open=False,
            dismissable=True,

            style={
                "position": "fixed", 
                "top": 75, 
                "right": 10, 
                "width": 350, 
                "z-index": "1"},
        ),


    dbc.Row([

    html.Div(
        html.Img(src="assets/icon.png", height="60px"),
        style ={"position" : "absolute",
                "top": "10px", 
                "left": 0, 
                "width": 70, }
                        ),

            html.Div("Spotify Music Explorer",
            style={'font-size': "260%", 'color':"#FFF",'text-aligh':'left', 
            "padding": "0",
            "white-space":"nowrap",
            "position" : "absolute",
            "top": 10, 
            "left": 90, 
            "width": 800, 
            },),

            dbc.Button(
            "Learn more",
            id="toast-toggle",
            color="#074983",
            n_clicks=0,
            style={

                "white-space":"nowrap",
                "top": 9,
                "position" : "absolute",
                "right":"20px",
                'text-aligh':'center',
                "width": 160, 
            }
            )

        ],
        id="header",
        className="g-0",
        style={
            "background-image": "linear-gradient(to right, #074983,#9198e5)",
            "width":"100%",
            "height":80
            }),
    dbc.Col(
    dbc.Row(
        [
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.P(
                "The music explorer dashboard is designed for the purpose of helping music lovers and members of Spotify music platform to explore the trends of songs and artists.",
            style = {"font-size":20,
                    "position": "absolute",
                    "top": 40,
                    "left": 0,
                    "bottom": 0,
                    "width":"18%",}),
                        html.Br(),

        ],
    ),
     width=2,
    style={
        "position": "absolute",
    "top": 80,
    "left": 0,
    "bottom": 0,
    "width":"100%",
    "height":900,
    "padding": "2rem 1rem",
    "background-image": "url(/assets/background.jpg)",
    "background-color": "#E4EBF5",
    "background-blend-mode": "overlay",
    },
), 
        
    dbc.Container([
        

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
                value=[20, 100],
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
                value=["pop","rap","rock"],
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
               html.Br(),
               html.Iframe(
                   id = "plot_bar",
                   srcDoc = plot_bar(genre=["pop","rap","rock"], pop_range=[50,100]),
                   style={'border-width': '10', 'width': '100%', 'height': '337px'})      
           ])
        ])
        ]),
   html.Br(),
  dbc.Col([
   dbc.Row([
       dbc.Col([
           dbc.Card([
               dbc.CardHeader(html.Label("What are some artists' popularity trend, within the selected range and genres? "), style={'font-size':16}),
               dcc.Dropdown(id="artist_names", multi=True),
            #    dbc.Input(id='artist_name', type='text', list='list-suggested-inputs', value='', placeholder="Enter a specifc artist name"),
            #    html.Div(id="warning"),
            #    html.Datalist(id='list-suggested-inputs', children=[html.Option(value=name) for name in  suggested_list]),

               html.Iframe(id="plot_2",
               style={'border-width': '10', 'width': '200%', 'height': '350px'})
           ])
       ]),

       dbc.Col([
           dbc.Card([
               dbc.CardHeader(html.Label("What's the relationship between songs' features and the popularity? "), style={'font-size':16}),
               dcc.Dropdown(id="features",
               value='danceability',
               options=[{'label': col, 'value': col} for col in features]),
            

               html.Iframe(id="plot_3",
               style={'border-width': '10', 'width': '100%', 'height': '350px'})
               
           ])
       ])

   ]),
   html.Br(),
   html.Br(),
  ])

    ],
    style={ 
        "position": "absolute",
        "left": "17%",
        "max-width": "83%",
        "top": "80px",
        
        }
    )
],
style={
    "max-width": "100%",
    "padding": "0",
    
})



# Receive input from user and create plot
@app.callback(
    Output('plot_bar', 'srcDoc'),
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
    return plot_2(artist, genre, pop_range)

# Receive input from user & dropdown list and create plot 3
@app.callback(
    Output('plot_3', 'srcDoc'),
    Input('features', 'value'),
    Input('genre_checklist', 'value'),
    Input('pop_slider', 'value')
)

def update_output(features, genre, pop_range):
    return plot_3(features, genre, pop_range)

@app.callback(
    Output("toast", "is_open"),
    [Input("toast-toggle", "n_clicks")],
)
def open_toast(n):
    if n:
        return True
    return False


if __name__ == '__main__':
    app.run_server(debug=True)
